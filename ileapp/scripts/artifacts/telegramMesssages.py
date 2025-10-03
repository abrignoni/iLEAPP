__artifacts_v2__ = {
    "telegramMessages": {
        "name": "Telegram Messages",
        "description": "Parses Telegram messages, including text, media, and forwarding information from the local cache database.",
        "author": "Stek29 / Victor Oreshkin, updated by @AlexisBrignoni, @JamesHabben",
        "creation_date": "2023-05-01", # Placeholder, original date unknown
        "last_update_date": "2024-07-15",
        "requirements": "Python packages: mmh3",
        "category": "Telegram",
        "notes": "Original Gist: https://gist.github.com/stek29/8a7ac0e673818917525ec4031d77a713. "
                 "This module processes the db_sqlite file from Telegram's local cache (postbox/db). "
                 "Media files are linked from the postbox/media directory.",
        "paths": (
            '*/telegram-data/account-*/postbox/db/db_sqlite*',
            '*/telegram-data/account-*/postbox/media/**'
        ),
        "output_types": "standard"
    }
}


import sqlite3
import io
import struct
import enum
import mmh3
import datetime
import inspect
import os

from ileapp.scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media, logfunc

# Code courtesy of Stek29 / Victor Oreshkin
# Github: https://gist.github.com/stek29
# Code: https://gist.github.com/stek29/8a7ac0e673818917525ec4031d77a713

@artifact_processor
def telegramMessages(context):
    data_headers = [
        ('Timestamp', 'datetime'),
        'Direction',
        'Author ID',
        'Text',
        ('Forward Timestamp', 'datetime'),
        'Forward From',
        'Action Data',
        ('Thumbnail', 'media')
    ]
    report_file_path = 'Unknown'

    data_list = []
    
    # Initialize caches here to avoid mutable default argument issues
    # These caches will be passed to helper functions
    peer_cache_global = {}
    media_cache_global = {}

    # Inner classes and enums (byteutil, MessageDataFlags, FwdInfoFlags, etc.)
    # These are self-contained and should not need modification for this refactor.
    # Ensure they are defined within or accessible to telegramMessages if they weren't top-level already.
    # They are defined at the module level in the original script, so they are accessible.
    # (Definitions of byteutil, enums, MessageIndex, PostboxDecoder, Decodeable, and specific media classes follow)

    class byteutil:
        def __init__(self, buffer, endian='<'):
            self.endian = endian
            self.buf = buffer
            
        def read_fmt(self, fmt):
            fmt = self.endian + fmt
            data = self.buf.read(struct.calcsize(fmt))
            return struct.unpack(fmt, data)[0]
        
        def read_int8(self):
            return self.read_fmt('b')
        def read_uint8(self):
            return self.read_fmt('B')
        
        def read_int32(self):
            return self.read_fmt('i')
        def read_uint32(self):
            return self.read_fmt('I')
        
        def read_int64(self):
            return self.read_fmt('q')
        def read_uint64(self):
            return self.read_fmt('Q')
        
        def read_bytes(self):
            slen = self.read_int32()
            return self.buf.read(slen)
        def read_str(self):
            return self.read_bytes().decode('utf-8')
        
        def read_short_bytes(self):
            slen = self.read_uint8()
            return self.buf.read(slen)
        def read_short_str(self):
            return self.read_short_bytes().decode('utf-8')
        
        def read_double(self):
            return self.read_fmt('d')
                  
    def murmur(d):
        return mmh3.hash(d, seed=4157243346)
            
    class MessageDataFlags(enum.IntFlag):
        GloballyUniqueId = 1 << 0
        GlobalTags = 1 << 1
        GroupingKey = 1 << 2
        GroupInfo = 1 << 3
        LocalTags = 1 << 4
        ThreadId = 1 << 5
        
    class FwdInfoFlags(enum.IntFlag):
        SourceId = 1 << 1
        SourceMessage = 1 << 2
        Signature = 1 << 3
        PsaType = 1 << 4
        Flags = 1 << 5
        
    class MessageFlags(enum.IntFlag):
        Unsent = 1
        Failed = 2
        Incoming = 4
        TopIndexable = 16
        Sending = 32
        CanBeGroupedIntoFeed = 64
        WasScheduled = 128
        CountedAsIncoming = 256
        
    class MessageTags(enum.IntFlag):
        PhotoOrVideo = 1 << 0
        File = 1 << 1
        Music = 1 << 2
        WebPage = 1 << 3
        VoiceOrInstantVideo = 1 << 4
        UnseenPersonalMessage = 1 << 5
        LiveLocation = 1 << 6
        Gif = 1 << 7
        Photo = 1 << 8
        Video = 1 << 9
        Pinned = 1 << 10
                  
    class MessageIndex:
        def __init__(self, peerId, namespace, mid, timestamp):
            self.peerId = peerId
            self.namespace = namespace
            self.id = mid
            self.timestamp = timestamp
            
        @classmethod
        def from_bytes(cls, b):
            bio = byteutil(io.BytesIO(b), endian='>')
            peerId = bio.read_int64()
            namespace = bio.read_int32()
            timestamp = bio.read_int32()
            mid = bio.read_int32()
            return cls(peerId, namespace, mid, timestamp)
        
        def as_bytes(self):
            return struct.pack('>qiii', self.peerId, self.namespace, self.timestamp, self.id)
        
        def __repr__(self):
            return f'ns:{self.namespace} pr:{self.peerId} id:{self.id} ts:{self.timestamp}'
                    
    # Helper functions now take `con` and caches explicitly
    def get_peer(peer_id, con, cache):
        if peer_id in cache:
            return cache[peer_id]
        cur = con.cursor() 
        try:
            cur.execute("SELECT value FROM t2 WHERE key = ? ORDER BY key LIMIT 1", (peer_id,))
            v = cur.fetchone()
            if v is None:
                cache[peer_id] = None
                return None
            data = PostboxDecoder(v[0]).decodeRootObject()
            cache[peer_id] = data
            return data
        finally:
            cur.close()
            
    def get_ref_media(ns, mid, con, cache, message_idx_for_ref_lookup): # Added message_idx for context in read_media_entry
        key = (ns, mid)
        if key in cache:
            return cache[key]
        rawKey = struct.pack('>iq', ns, mid)
        
        cur = con.cursor() 
        try:
            cur.execute("SELECT value FROM t6 WHERE key = ? ORDER BY key LIMIT 1", (rawKey,))
            v = cur.fetchone()
            if v is None:
                cache[key] = None
                return None
            
            data_bytes = v[0]
            bio = byteutil(io.BytesIO(data_bytes))
            # Pass con and caches down if read_media_entry needs them for get_message
            media_data = read_media_entry(key, bio, con, cache, message_idx_for_ref_lookup) 
            cache[key] = media_data
            # refcnt = bio.read_int32() # refcnt not used elsewhere
            return media_data
        finally:
            cur.close()
            
    def get_message(idx: MessageIndex, con_param):
        cur = con_param.cursor() 
        try:
            cur.execute("SELECT value FROM t7 WHERE key = ? ORDER BY key LIMIT 1", (idx.as_bytes(),))
            v = cur.fetchone()
            if v is None:
                return None
            # Pass con_param to read_intermediate_message if it needs it for PostboxDecoder or further calls
            return read_intermediate_message(v[0], con_param) 
        finally:
            cur.close()                
            
    def get_all_messages(con_param, f=None, decode=True):
        cur = con_param.cursor()
        try:
            cur.execute("SELECT key, value FROM t7 ORDER BY key")
            for key, value in cur:
                idx = MessageIndex.from_bytes(key)
                
                if f is not None and not f(idx):
                    continue
                
                if decode:
                    # Pass con_param to read_intermediate_message
                    msg = read_intermediate_message(value, con_param)
                else:
                    msg = value
                yield idx, msg
        finally:
            cur.close()
                          
    class MediaEntryType(enum.Enum):
        Direct = 0
        MessageReference = 1
        
    def read_media_entry(key, bio, con_param, media_cache_param, message_idx_param): # Added con_param, media_cache_param, message_idx_param
        typ = MediaEntryType(bio.read_uint8())
        if typ == MediaEntryType.Direct:
            data_bytes = bio.read_bytes()
            # Pass con_param to PostboxDecoder if it needs it, assumed not for now
            data_obj = PostboxDecoder(data_bytes).decodeRootObject()
            return data_obj
        elif typ == MediaEntryType.MessageReference:
            idPeerId = bio.read_int64()
            idNamespace = bio.read_int32()
            idId = bio.read_int32()
            idTimestamp = bio.read_int32()
            idx_ref = MessageIndex(idPeerId, idNamespace, idId, idTimestamp)
            # Use get_message with passed con_param
            msg_ref = get_message(idx_ref, con_param)
            if msg_ref and 'embeddedMedia' in msg_ref:
                for m_item in msg_ref['embeddedMedia']:
                    if hasattr(m_item, 'mediaId') and m_item.mediaId == key:
                        return m_item
            # If not found in primary message, use the passed message_idx_param as context
            # This part is complex, original code used message_idx (from get_ref_media context) implicitly for exception
            # Let's try to find it in the original message context if not in the direct reference message
            if message_idx_param:
                msg_orig_context = get_message(message_idx_param, con_param)
                if msg_orig_context and 'embeddedMedia' in msg_orig_context:
                     for m_item_orig in msg_orig_context['embeddedMedia']:
                        if hasattr(m_item_orig, 'mediaId') and m_item_orig.mediaId == key:
                            return m_item_orig

            raise Exception(f'Referenced media {key} not found in message {idx_ref} or original context {message_idx_param}')
        else:
            raise Exception(f'Invalid mediaentrytype {typ}')
                               
    def peer_str(peerId, con_param, cache_param): # Added con_param, cache_param
        peer = get_peer(peerId, con_param, cache_param)
        if peer is None:
            return f"unknown peer {peerId}"
        if 'fn' in peer: # Check if 'fn' key exists
            peerName = f"{peer.get('fn', '')} {peer.get('ln', '')}".strip()
        elif 't' in peer: # Check if 't' key exists
            peerName = peer.get('t', '')
        else:
            peerName = 'WARN: UNK NAME'
        un_val = peer.get('un', '')
        return f"{peerName} (@{un_val} {peerId})" if un_val else f"{peerName} ({peerId})"

    def print_media_info(m): # Renamed from print_media to avoid confusion, returns dict
        text_for_report = ''
        searchable_filename = None

        if isinstance(m, TelegramMediaFile) and hasattr(m, 'resource') and isinstance(m.resource, CloudDocumentMediaResource):
            res = m.resource
            file_name_attr = getattr(res, 'fileName', 'N/A')
            mime_type_attr = getattr(m, 'mimeType', 'N/A')
            unique_id_attr = getattr(res, 'uniqueId', 'N/A')
            text_for_report = f"File: {file_name_attr} (MIME: {mime_type_attr}, ID: {unique_id_attr})"
            
            searchable_filename = unique_id_attr
            if not searchable_filename and file_name_attr != 'N/A': 
                searchable_filename = file_name_attr

        elif isinstance(m, TelegramMediaImage) and hasattr(m, 'representations'):
            reps = [rep for rep in m.representations if isinstance(rep, TelegramMediaImageRepresentation) and hasattr(rep, 'resource')]
            reps.sort(key=lambda x: getattr(x, 'height', 0) * getattr(x, 'width', 0), reverse=True)
            if reps and hasattr(reps[0], 'resource') and isinstance(reps[0].resource, CloudPhotoSizeMediaResource):
                res = reps[0].resource
                unique_id_attr = getattr(res, 'uniqueId', 'N/A')
                text_for_report = f"Image: ID {unique_id_attr}"
                searchable_filename = unique_id_attr 
            else:
                text_for_report = "Image: Malformed representation or resource"

        elif isinstance(m, TelegramMediaWebpage):
            url = getattr(m, 'url', None) or getattr(m, 'pendingUrl', 'N/A')
            text_for_report = f"Webpage: {url}"

        elif isinstance(m, TelegramMediaAction):
            text_for_report = f"Action: {m}"

        elif isinstance(m, dict) and 'la' in m and 'lo' in m:
            lat = m.get('la')
            lon = m.get('lo')
            location_type_str = "Location"
            # Format coords to a reasonable number of decimal places
            details = [f"Lat: {lat}", f"Lon: {lon}"] 

            heading = m.get('hdg')
            accuracy = m.get('acc')
            period_bt = m.get('bt') # Likely the 'period' for live locations
            
            # Fields often found in venue/static locations
            venue_title = m.get('venue_title') # Key based on common Telegram structures
            venue_address = m.get('address')   # Key based on common Telegram structures
            venue_provider = m.get('provider') # Key based on common Telegram structures
            venue_id = m.get('venue_id')       # Key based on common Telegram structures


            # Differentiate based on presence of fields common in live locations vs static/venue
            if period_bt is not None or heading is not None: # 'period' (bt) or 'heading' are good indicators of dynamic/live location
                location_type_str = "Dynamic Location Update"
                if heading is not None:
                    details.append(f"Hdg: {heading}°")
                if accuracy is not None:
                    details.append(f"Acc: {accuracy}m")
                if period_bt is not None: # 'bt' seems to be 'period' in seconds for live locations
                    details.append(f"Period: {period_bt}s")
            else:
                location_type_str = "Static Location"
                if venue_title:
                    details.append(f"Venue: {venue_title}")
                if venue_address:
                    details.append(f"Address: {venue_address}")
                if venue_provider: # e.g., "foursquare", "gplaces"
                    details.append(f"Provider: {venue_provider}")
                if venue_id:
                    details.append(f"Venue ID: {venue_id}")
                # Could also check for 'acc' (accuracy) here for static points if relevant
                if accuracy is not None:
                     details.append(f"Acc: {accuracy}m")

            text_for_report = f"{location_type_str}: {'; '.join(details)}"
            # No searchable_filename for these location dicts as they aren't separate files

        else:
            text_for_report = f"Media: Type {type(m).__name__}, content {str(m)[:100]}"

        return {'text_for_report': text_for_report, 'identifier_for_file_search': searchable_filename}
    
    def process_message_for_report(idx, msg_data, con_param, peer_cache_param, media_cache_param,
                                   files_found_param_main):
        direction = 'Incoming' if MessageFlags.Incoming in msg_data['flags'] else 'Outgoing'
        ts = datetime.datetime.fromtimestamp(idx.timestamp, tz=datetime.timezone.utc)
        author_id_str = peer_str(msg_data['authorId'], con_param, peer_cache_param) if msg_data.get('authorId') else "N/A"
        
        fwd_info = msg_data.get('fwd')
        forward_date_obj = ''
        forward_from_str = ''
        if fwd_info:
            forward_date_obj = datetime.datetime.fromtimestamp(fwd_info['date'], tz=datetime.timezone.utc)
            forward_from_str = peer_str(fwd_info.get('author'), con_param, peer_cache_param) if fwd_info.get('author') else "N/A"
            
        action_data_parts = []
        primary_media_search_id = None
        
        for m_emb in msg_data.get('embeddedMedia', []):
            details = print_media_info(m_emb)
            action_data_parts.append(details['text_for_report'])
            if details['identifier_for_file_search'] and not primary_media_search_id:
                primary_media_search_id = details['identifier_for_file_search']
        
        for mref_id_tuple in msg_data.get("referencedMediaIds", []):
            m_ref = get_ref_media(mref_id_tuple[0], mref_id_tuple[1], con_param, media_cache_param, idx)
            if m_ref:
                details = print_media_info(m_ref)
                action_data_parts.append(details['text_for_report'])
                if details['identifier_for_file_search'] and not primary_media_search_id:
                    primary_media_search_id = details['identifier_for_file_search']
            else:
                action_data_parts.append(f"Referenced media not found: ns={mref_id_tuple[0]}, id={mref_id_tuple[1]}")

        final_action_data_text = '; '.join(filter(None, action_data_parts))
        media_item_ref_id = ''

        if primary_media_search_id:
            found_media_file_path = None
            for f_path_item in files_found_param_main: 
                current_f_path_str = str(f_path_item)
                basename_matches = os.path.basename(current_f_path_str) == primary_media_search_id
                is_in_media_path = "/postbox/media/" in current_f_path_str
                
                if is_in_media_path and basename_matches:
                    is_file = os.path.isfile(current_f_path_str)
                    if is_file:
                        found_media_file_path = current_f_path_str
                        break 
            
            if found_media_file_path:
                media_item_ref_id = check_in_media(file_path=found_media_file_path)
            else:
                logfunc(f"INFO: No valid media file found for primary_media_search_id = '{primary_media_search_id}' after checking all files_found.")
                    
        text_content = msg_data.get('text', '')
        
        return (ts, direction, author_id_str, text_content, forward_date_obj, forward_from_str, final_action_data_text, media_item_ref_id)
                       
    def read_intermediate_fwd_info(buf): # No changes needed here, uses buf directly
        infoFlags = FwdInfoFlags(buf.read_int8())
        if infoFlags == 0:
            return None
        
        authorId = buf.read_int64()
        date = buf.read_int32()
        
        sourceId = None
        if FwdInfoFlags.SourceId in infoFlags:
            sourceId = buf.read_int64()
            
        sourceMessagePeerId = None
        sourceMessageNamespace = None
        sourceMessageIdId = None
        if FwdInfoFlags.SourceMessage in infoFlags:
            sourceMessagePeerId = buf.read_int64()
            sourceMessageNamespace = buf.read_int32()
            sourceMessageIdId = buf.read_int32()
            
        signature = None
        if FwdInfoFlags.Signature in infoFlags:
            signature = buf.read_str()
            
        psaType = None
        if FwdInfoFlags.PsaType in infoFlags:
            psaType = buf.read_str()
            
        flags = None
        if FwdInfoFlags.Flags in infoFlags:
            flags = buf.read_int32()
            
        return {
            'author': authorId,
            'date': date,
            'srcId': sourceId,
            'srcMsgPeer': sourceMessagePeerId,
            'srcMsgNs': sourceMessageNamespace,
            'srcMsgId': sourceMessageIdId,
            'signature': signature,
            'psaType': psaType,
            'flags': flags,
        }
           
    def read_intermediate_message(v: bytes, con_param): # Added con_param for PostboxDecoder if needed
        buf = byteutil(io.BytesIO(v))
        typ = buf.read_int8()
        if typ != 0:
            # print(f'wtf, type not 0 but {typ}') # Keep prints for debugging if necessary
            return None
        
        # stableId = buf.read_uint32() # Not used
        # stableVer = buf.read_uint32() # Not used
        buf.read_uint32() # stableId
        buf.read_uint32() # stableVer

        dataFlags = MessageDataFlags(buf.read_uint8())
        
        # globallyUniqueId = None # Not used
        if MessageDataFlags.GloballyUniqueId in dataFlags:
            # globallyUniqueId = buf.read_int64()
            buf.read_int64()
            
        # globalTags = None # Not used
        if MessageDataFlags.GlobalTags in dataFlags:
            # globalTags = buf.read_uint32()
            buf.read_uint32()
            
        # groupingKey = None # Not used
        if MessageDataFlags.GroupingKey in dataFlags:
            # groupingKey = buf.read_int64()
            buf.read_int64()
            
        # groupInfoStableId = None # Not used
        if MessageDataFlags.GroupInfo in dataFlags:
            # groupInfoStableId = buf.read_uint32()
            buf.read_uint32()
            
        # localTagsVal = None # Not used
        if MessageDataFlags.LocalTags in dataFlags:
            # localTagsVal = buf.read_uint32()
            buf.read_uint32()
            
        # threadId = None # Not used
        if MessageDataFlags.ThreadId in dataFlags:
            # threadId = buf.read_int64()
            buf.read_int64()
            
        flags = MessageFlags(buf.read_uint32())
        tags = MessageTags(buf.read_uint32())
        
        fwd_info = read_intermediate_fwd_info(buf) # This function is self-contained
        
        authorId = None
        hasAuthorId = buf.read_int8()
        if hasAuthorId == 1:
            authorId = buf.read_int64()
            
        text = buf.read_str()
        
        attributesCount = buf.read_int32()
        attributes = [None]*attributesCount
        for i in range(attributesCount):
            # Pass con_param to PostboxDecoder if it needs it, assumed not for now
            attributes[i] = PostboxDecoder(buf.read_bytes()).decodeRootObject() 
            
        embeddedMediaCount = buf.read_int32()
        embeddedMedia = [None]*embeddedMediaCount
        for i in range(embeddedMediaCount):
            # Pass con_param to PostboxDecoder if it needs it
            embeddedMedia[i] = PostboxDecoder(buf.read_bytes()).decodeRootObject()
            
        referencedMediaIds = []
        referencedMediaIdsCount = buf.read_int32()
        for _ in range(referencedMediaIdsCount):
            idNamespace = buf.read_int32()
            idId = buf.read_int64()
            referencedMediaIds.append((idNamespace, idId))
            
        # leftover = buf.buf.read() # Not used
        # if leftover != b'':
        #     print('huh, y no empty', leftover)
            
        return {
            'flags': flags,
            'tags': tags,
            'authorId': authorId,
            'fwd': fwd_info,
            'text': text,
            'referencedMediaIds': referencedMediaIds,
            'embeddedMedia': embeddedMedia,
            'attributes': attributes,
        }
              
    class PostboxDecoder: # This class and its methods appear self-contained, no con_param needed directly
        registry = {}
        
        @classmethod
        def registerDecoder(cls, t):
            cls.registry[murmur(t.__name__)] = t
            return t
        
        class ValueType(enum.Enum):
            Int32 = 0
            Int64 = 1
            Bool = 2
            Double = 3
            String = 4
            Object = 5
            Int32Array = 6
            Int64Array = 7
            ObjectArray = 8
            ObjectDictionary = 9
            Bytes = 10
            Nil = 11
            StringArray = 12
            BytesArray = 13
            
        def __init__(self, data):
            self.bio = byteutil(io.BytesIO(data), endian='<')
            self.size = len(data)
            
        def decodeRootObject(self):
            return self.decodeObjectForKey('_')
        
        def decodeObjectForKey(self, key):
            t, v = self.get(self.ValueType.Object, key)
            if v:
                return v
            return None # Explicitly return None if not found or value is None
            
        def get(self, valueType, key, decodeObjects=None):
            for k, t, v in self._iter_kv(decodeObjects=decodeObjects):
                if k != key:
                    pass
                elif valueType == None: # Typo? Should be valueType is None
                    return t, v
                elif t == valueType:
                    return t, v
                elif t == self.ValueType.Nil: # If value type is Nil, return it as None
                    return t, None # Ensure None is returned for Nil actual type
            return None, None
        
        def _iter_kv(self, decodeObjects=None, registry=None):
            self.bio.buf.seek(0, io.SEEK_SET)
            while True:
                pos = self.bio.buf.tell()
                if pos >= self.size:
                    break
                
                key = self.bio.read_short_str()
                valueType, value = self.readValue(decodeObjects=decodeObjects, registry=registry)
                yield key, valueType, value
                
        def _readObject(self, decode=None, registry=None): # Changed registry_param back to registry
            if decode is None:
                decode = True
            if registry is None:
                registry = self.registry
                
            typeHash = self.bio.read_int32()
            dataLen = self.bio.read_int32()
            data_bytes = self.bio.buf.read(dataLen)
            
            value = None
            if not decode:
                value = {'type': typeHash, 'data': data_bytes}
            elif typeHash in registry: # Changed registry_param to registry
                decoder = self.__class__(data_bytes)
                value = registry[typeHash](decoder) # Changed registry_param to registry
            else:
                decoder = self.__class__(data_bytes)
                value = {k: v for k, t, v in decoder._iter_kv()}
                value['@type'] = typeHash
                
            return value
        
        def readValue(self, decodeObjects=None, registry=None):
            valueType = self.ValueType(self.bio.read_uint8())
            value = None
            
            objectArgs = {'decode': decodeObjects, 'registry': registry}
            
            if valueType == self.ValueType.Int32:
                value = self.bio.read_int32()
            elif valueType == self.ValueType.Int64:
                value = self.bio.read_int64()
            elif valueType == self.ValueType.Bool:
                value = self.bio.read_uint8() != 0
            elif valueType == self.ValueType.Double:
                value = self.bio.read_double()
            elif valueType == self.ValueType.String:
                value = self.bio.read_str()
            elif valueType == self.ValueType.Object:
                value = self._readObject(**objectArgs)
            elif valueType == self.ValueType.Int32Array:
                alen = self.bio.read_int32()
                value = [self.bio.read_int32() for _ in range(alen)]
            elif valueType == self.ValueType.Int64Array:
                alen = self.bio.read_int32()
                value = [self.bio.read_int64() for _ in range(alen)]
            elif valueType == self.ValueType.ObjectArray:
                alen = self.bio.read_int32()
                value = [self._readObject(**objectArgs) for _ in range(alen)]
            elif valueType == self.ValueType.ObjectDictionary:
                dlen = self.bio.read_int32()
                value = [(self._readObject(**objectArgs), self._readObject(**objectArgs)) for _ in range(dlen)]
            elif valueType == self.ValueType.Bytes:
                value = self.bio.read_bytes()
            elif valueType == self.ValueType.Nil:
                pass # Value remains None
            elif valueType == self.ValueType.StringArray:
                alen = self.bio.read_int32()
                value = [self.bio.read_str() for _ in range(alen)]
            elif valueType == self.ValueType.BytesArray:
                alen = self.bio.read_int32()
                value = [self.bio.read_bytes() for _ in range(alen)]
            else:
                raise Exception(f'unknown value type: {valueType}')
            return valueType, value
            
    # Decodeable class and registered media types
    # These should also be self-contained and use the PostboxDecoder correctly.
    class Decodeable:
        def __init__(self, dec):
            for field, (key, typ) in self.FIELDS.items():
                _, val = dec.get(typ, key)
                setattr(self, field, val)
                
        def __repr__(self):
            return repr(self.__dict__)
            
    @PostboxDecoder.registerDecoder
    class TelegramMediaImage(Decodeable):
        FIELDS = {
            'imageId_raw': ('i', PostboxDecoder.ValueType.Bytes), # Renamed to avoid conflict
            'representations': ('r', PostboxDecoder.ValueType.ObjectArray),
            'videoRepresentations': ('vr', PostboxDecoder.ValueType.ObjectArray),
            'immediateThumbnailData': ('itd', PostboxDecoder.ValueType.Bytes),
            'reference': ('rf', PostboxDecoder.ValueType.Object),
            'partialReference': ('prf', PostboxDecoder.ValueType.Object),
            'flags': ('fl', PostboxDecoder.ValueType.Int32),
        }
        
        def __init__(self, dec):
            super().__init__(dec)
            if hasattr(self, 'imageId_raw') and self.imageId_raw:
                bio = byteutil(io.BytesIO(self.imageId_raw))
                self.imageId = (bio.read_int32(), bio.read_int64())
            else:
                self.imageId = (None, None) # Default if raw bytes are missing
            
        @property
        def mediaId(self):
            return self.imageId
            
    @PostboxDecoder.registerDecoder
    class TelegramMediaImageRepresentation(Decodeable):
        FIELDS = {
            'width': ('dx', PostboxDecoder.ValueType.Int32),
            'height': ('dy', PostboxDecoder.ValueType.Int32),
            'resource': ('r', PostboxDecoder.ValueType.Object),
            'progressiveSizes': ('ps', PostboxDecoder.ValueType.Int32Array),
        }
        
    @PostboxDecoder.registerDecoder
    class CloudPhotoSizeMediaResource(Decodeable):
        FIELDS = {
            'datacenterId': ('d', PostboxDecoder.ValueType.Int32),
            'photoId': ('i', PostboxDecoder.ValueType.Int64),
            'accessHash': ('h', PostboxDecoder.ValueType.Int64),
            'sizeSpec': ('s', PostboxDecoder.ValueType.String),
            'size': ('n', PostboxDecoder.ValueType.Int32),
            'fileReference': ('fr', PostboxDecoder.ValueType.Bytes)
        }
        
        @property
        def uniqueId(self):
            dc_id = getattr(self, 'datacenterId', 'unk_dc')
            ph_id = getattr(self, 'photoId', 'unk_photoid')
            sz_spec = getattr(self, 'sizeSpec', 'unk_spec')
            return f"telegram-cloud-photo-size-{dc_id}-{ph_id}-{sz_spec}"
            
    @PostboxDecoder.registerDecoder
    class CloudDocumentMediaResource(Decodeable):
        FIELDS = {
            'datacenterId': ('d', PostboxDecoder.ValueType.Int32),
            'fileId': ('f', PostboxDecoder.ValueType.Int64),
            'accessHash': ('a', PostboxDecoder.ValueType.Int64),
            'size': ('n', PostboxDecoder.ValueType.Int32), # Original field was 'n', not 'z'
            'fileReference': ('fr', PostboxDecoder.ValueType.Bytes),
            'fileName': ('fn', PostboxDecoder.ValueType.String)
        }
        
        @property
        def uniqueId(self):
            dc_id = getattr(self, 'datacenterId', 'unk_dc')
            f_id = getattr(self, 'fileId', 'unk_fileid')
            return f"telegram-cloud-document-{dc_id}-{f_id}"
            
    @PostboxDecoder.registerDecoder
    class TelegramMediaFile(Decodeable):
        FIELDS = {
            'fileId_raw': ('i', PostboxDecoder.ValueType.Bytes), # Renamed to avoid conflict
            'partialReference': ('prf', PostboxDecoder.ValueType.Object),
            'resource': ('r', PostboxDecoder.ValueType.Object),
            'previewRepresentations': ('pr', PostboxDecoder.ValueType.ObjectArray),
            'videoThumbnails': ('vr', PostboxDecoder.ValueType.ObjectArray), # Was 'videoThumbnails' in original, not 'vt'
            'immediateThumbnailData': ('itd', PostboxDecoder.ValueType.Bytes),
            'mimeType': ('mt', PostboxDecoder.ValueType.String),
            'size': ('s', PostboxDecoder.ValueType.Int32),
            'attributes': ('at', PostboxDecoder.ValueType.ObjectArray)
        }
        
        def __init__(self, dec):
            super().__init__(dec)
            if hasattr(self, 'fileId_raw') and self.fileId_raw:
                bio = byteutil(io.BytesIO(self.fileId_raw))
                self.fileId = (bio.read_int32(), bio.read_int64())
            else:
                self.fileId = (None, None)

        @property
        def mediaId(self):
            return self.fileId
            
    @PostboxDecoder.registerDecoder
    class TelegramMediaWebpage(Decodeable):
        FIELDS = {
            'webpageId_raw': ('i', PostboxDecoder.ValueType.Bytes), # Renamed
            'pendingUrl': ('pendingUrl', PostboxDecoder.ValueType.String),
            'url': ('u', PostboxDecoder.ValueType.String),
            # Add other fields like 'content', 'author', 'title', 'description', 'photo', 'embedUrl', etc. if needed from original schema
            # For now, keeping it simple based on original FIELDS provided in context.
        }
        
        def __init__(self, dec):
            super().__init__(dec)
            if hasattr(self, 'webpageId_raw') and self.webpageId_raw:
                bio = byteutil(io.BytesIO(self.webpageId_raw))
                self.webpageId = (bio.read_int32(), bio.read_int64())
            else:
                self.webpageId = (None, None)
                
        @property
        def mediaId(self):
            return self.webpageId
            
    @PostboxDecoder.registerDecoder
    class TelegramMediaAction:
        class Type(enum.Enum):
            unknown = 0; groupCreated = 1; addedMembers = 2; removedMembers = 3
            photoUpdated = 4; titleUpdated = 5; pinnedMessageUpdated = 6
            joinedByLink = 7; channelMigratedFromGroup = 8; groupMigratedToChannel = 9
            historyCleared = 10; historyScreenshot = 11; messageAutoremoveTimeoutUpdated = 12
            gameScore = 13; phoneCall = 14; paymentSent = 15; customText = 16
            botDomainAccessGranted = 17; botSentSecureValues = 18; peerJoined = 19
            phoneNumberRequest = 20; geoProximityReached = 21; groupPhoneCall = 22
            inviteToGroupPhoneCall = 23; setChatTheme = 24; joinedByRequest = 25
            webViewData = 26; giftPremium = 27; topicCreated = 28; topicEdited = 29
            suggestedProfilePhoto = 30; attachMenuBotAllowed = 31; requestedPeer = 32
            setChatWallpaper = 33; setSameChatWallpaper = 34; botAppAccessGranted = 35
            giftCode = 36; giveawayLaunched = 37; joinedChannel = 38; giveawayResults = 39
            boostsApplied = 40; paymentRefunded = 41; giftStars = 42; prizeStars = 43; starGift = 44
            
        def __init__(self, dec):
            raw = {k: v for k, t, v in dec._iter_kv()} # Get all key-value pairs
            raw_value = raw.get('_rawValue', 0) # Safely get _rawValue
            try:
                self.type = self.Type(raw_value)
            except ValueError:
                # print(f"ValueError: Unknown TelegramMediaAction.Type value '{raw_value}', defaulting to 'unknown'.")
                self.type = self.Type.unknown # Default to unknown if value is not in enum
            # Remove _rawValue if it exists, so it's not part of payload
            if '_rawValue' in raw:
                del raw['_rawValue']
            self.payload = raw # Store the rest of the decoded fields as payload
            
        def __repr__(self):
            payload_repr = ', '.join([f"{k}={v}" for k,v in self.payload.items()])
            return f"<{self.type.name} ({payload_repr if payload_repr else 'No payload'})>"


    # Main processing loop for database files
    for file_found_single_path in context.get_files_found():
        file_found_single_path = str(file_found_single_path)
        
        if (file_found_single_path.endswith('db_sqlite')) and ('media' not in file_found_single_path):
            report_file_path = file_found_single_path # This is the source_path for the report
            
            db_connection = None
            try:
                db_connection = open_sqlite_db_readonly(report_file_path)
                
                # Iterate over all messages using the helper
                for idx, msg_content in get_all_messages(db_connection):
                    if msg_content: # Ensure msg_content is not None
                        processed_row = process_message_for_report(
                            idx, msg_content, db_connection, 
                            peer_cache_global, media_cache_global,
                            context.get_files_found() # Pass main files_found
                        )
                        data_list.append(processed_row)
            
            except sqlite3.Error as e:
                # print(f"SQLite error processing {report_file_path}: {e}")
                pass # Or log error appropriately
            finally:
                if db_connection:
                    db_connection.close()

    return data_headers, data_list, report_file_path