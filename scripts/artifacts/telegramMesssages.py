__artifacts_v2__ = {
    "TelegramMessages": {
        "name": "Telegram Messages",
        "description": "",
        "author": "Stek29 / Victor Oreshkin",
        "version": "",
        "date": "",
        "requirements": "",
        "category": "Telegram",
        "notes": "Github: https://gist.github.com/stek29; "
                 "Code: https://gist.github.com/stek29/8a7ac0e673818917525ec4031d77a713",
        "paths": (
            '*/telegram-data/account-*/postbox/db/db_sqlite',
            '*/telegram-data/account-*/postbox/media/**'
        ),
        "function": "get_telegramMessages"
    }
}


import sqlite3
import io
import struct
import enum
import mmh3
import pprint
import datetime
import scripts.artifacts.artGlobals

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, timeline, kmlgen, tsv, is_platform_windows, open_sqlite_db_readonly, media_to_html

# Code courtesy of Stek29 / Victor Oreshkin
# Github: https://gist.github.com/stek29
# Code: https://gist.github.com/stek29/8a7ac0e673818917525ec4031d77a713

def get_telegramMessages(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if (file_found.endswith('db_sqlite')) and ('media' not in file_found):
            data_list= []
            
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
                
                
            # In[3]:
                
                
            def murmur(d):
                # seed from telegram
                return mmh3.hash(d, seed=-137723950)
            
            
            # In[4]:
            
            
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
                
                
            # In[5]:
                
                
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
                
                
            # In[6]:
                
                
            def get_peer(peer_id, cache={}):
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
                    
            def get_ref_media(ns, mid, cache={}):
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
                    
                    data = v[0]
                    bio = byteutil(io.BytesIO(data))
                    data = read_media_entry(key, bio)
                    cache[key] = data
                    refcnt = bio.read_int32()
                    return data
                finally:
                    cur.close()
                    
            def get_message(idx: MessageIndex):
                cur = con.cursor() 
                try:
                    cur.execute("SELECT value FROM t7 WHERE key = ? ORDER BY key LIMIT 1", (idx.as_bytes(),))
                    v = cur.fetchone()
                    if v is None:
                        return None
                    return read_intermediate_message(v[0])
                finally:
                    cur.close()
                    
                    
            # In[7]:
                    
                    
            def get_all_messages(f=None, decode=True):
                cur = con.cursor()
                try:
                    cur.execute("SELECT key, value FROM t7 ORDER BY key")
                    for key, value in cur:
                        idx = MessageIndex.from_bytes(key)
                        
                        # apply filter func
                        if f is not None and not f(idx):
                            continue
                        
                        if decode:
                            msg = read_intermediate_message(value)
                            #print(msg)
                            
                        else:
                            msg = value
                            #print(msg)
                        yield idx, msg
                finally:
                    cur.close()
                    
                    
            # In[8]:
                    
                    
            class MediaEntryType(enum.Enum):
                Direct = 0
                MessageReference = 1
                
            def read_media_entry(key, bio):
                typ = MediaEntryType(bio.read_uint8())
                if typ == MediaEntryType.Direct:
                    data = bio.read_bytes()
                    data = PostboxDecoder(data).decodeRootObject()
                    return data
                elif typ == MediaEntryType.MessageReference:
                    idPeerId = bio.read_int64()
                    idNamespace = bio.read_int32()
                    idId = bio.read_int32()
                    idTimestamp = bio.read_int32()
                    idx = MessageIndex(idPeerId, idNamespace, idId, idTimestamp)
                    msg = get_message(idx)
                    for m in msg['embeddedMedia']:
                        if hasattr(m, 'mediaId') and m.mediaId == key:
                            return m
                    raise Exception(f'refrerenced media not found in message {idx} {key}')
                else:
                    raise Exception(f'invalid mediaentrytype {typ}')
                    
                    
            # In[9]:
                    
                    
            def peer_str(peerId):
                peer = get_peer(peerId)
                if peer is None:
                    return f"unknown peer {peerId}"
                if 'fn' in peer:
                    peerName = f"{peer.get('fn', '')} {peer.get('ln', '')} "
                elif 't' in peer:
                    peerName = peer.get('t', '')
                else:
                    peerName = 'WARN: UNK NAME'
                return f"{peerName} (@{peer.get('un', '')} {peerId})"
            
            def print_media(m):
                if isinstance(m, TelegramMediaFile):
                    res = m.resource
                    if not isinstance(res, CloudDocumentMediaResource):
                        print(f"!!! WARN: has file without resource")
                        return True
                    filedata = (f"%%% file fn:{res.fileName} mt:{m.mimeType} {res.uniqueId}")
                elif isinstance(m, TelegramMediaImage):
                    reps = [rep for rep in m.representations if isinstance(rep, TelegramMediaImageRepresentation)]
                    reps.sort(key=lambda x: x.height * x.width, reverse=True)
                    rep = reps[0] if reps else None
                    if rep is None:
                        filedata = (f"!!! WARN: has image without representation[0]")
                        #return True
                    res = rep.resource
                    if not isinstance(res, CloudPhotoSizeMediaResource):
                        print(f"!!! WARN: has image without representation[0].resource")
                        #return True
                    filedata = (f"%%% image {res.uniqueId}")
                elif isinstance(m, TelegramMediaWebpage):
                    url = m.url or m.pendingUrl
                    filedata = (f"%%% webpage for {url}")
                elif isinstance(m, TelegramMediaAction):
                    filedata = (f"%%% action {m}")
                else:
                    filedata = (f"%%% unknown media {m}")
                    
                    
                return filedata
            
            def print_message(idx, msg):
                hadWarn = False
                #direction = '<=' if MessageFlags.Incoming in msg['flags'] else '=>'
                direction = 'Incoming' if MessageFlags.Incoming in msg['flags'] else 'Outgoing'
                ts = datetime.datetime.fromtimestamp(idx.timestamp)
                #print(f'=== {direction} {ts} peer:{idx.peerId} id:{idx.id}')
                
                #print(f"=== {peer_str(msg['authorId'])}")
                authorid = peer_str(msg['authorId'])
                
                fwd = msg['fwd']
                if fwd is not None:
                    fwdDate = datetime.datetime.fromtimestamp(fwd['date'])
                    #print(f"=== fwd {fwdDate} from {peer_str(fwd['author'])}")
                    forwarddate = fwdDate
                    forwardfrom = peer_str(fwd['author'])
                else:
                    forwarddate = ''
                    forwardfrom = ''
                    
                for m in msg['embeddedMedia']:
                    hadWarn = print_media(m) or hadWarn
                    
                    
                for mref in msg["referencedMediaIds"]:
                    m = get_ref_media(*mref)
                    if m is None:
                        print(f"!!! WARN: media reference not found")
                        hadWarn = True
                        continue
                    hadWarn = print_media(m) or hadWarn
                    
                if msg['text']:
                    text = msg['text']
                else:
                    text = ''
                    
                if hadWarn == False:
                    hadWarn = ''
                    thumb = ''
                
                if 'telegram-cloud' in hadWarn:
                    filename = hadWarn.split(' ')[-1]
                    thumb = media_to_html(filename, files_found, report_folder)
                else:
                    thumb = ''
                    
                data_list.append((ts,direction,authorid,text,forwarddate,forwardfrom,hadWarn,thumb))
            #     return hadWarn
                
                
            # In[10]:
                
                
            def read_intermediate_fwd_info(buf):
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
            
            
            # In[11]:
            
            
            def read_intermediate_message(v: bytes):
                buf = byteutil(io.BytesIO(v))
                typ = buf.read_int8()
                if typ != 0:
                    print(f'wtf, type not 0 but {typ}')
                    return None
                
                stableId = buf.read_uint32()
                stableVer = buf.read_uint32()
                
                dataFlags = MessageDataFlags(buf.read_uint8()) # int8 in swift
                
                globallyUniqueId = None
                if MessageDataFlags.GloballyUniqueId in dataFlags:
                    globallyUniqueId = buf.read_int64()
                    
                globalTags = None
                if MessageDataFlags.GlobalTags in dataFlags:
                    globalTags = buf.read_uint32()
                    
                groupingKey = None
                if MessageDataFlags.GroupingKey in dataFlags:
                    groupingKey = buf.read_int64()
                    
                groupInfoStableId = None
                if MessageDataFlags.GroupInfo in dataFlags:
                    groupInfoStableId = buf.read_uint32()
                    
                localTagsVal = None
                if MessageDataFlags.LocalTags in dataFlags:
                    localTagsVal = buf.read_uint32()
                    
                threadId = None
                if MessageDataFlags.ThreadId in dataFlags:
                    threadId = buf.read_int64()
                    
                flags = MessageFlags(buf.read_uint32())
                tags = MessageTags(buf.read_uint32())
                
                fwd_info = read_intermediate_fwd_info(buf)
                
                authorId = None
                hasAuthorId = buf.read_int8()
                if hasAuthorId == 1:
                    authorId = buf.read_int64()
                    
                text = buf.read_str()
            #     print(text)
                
                attributesCount = buf.read_int32()
                attributes = [None]*attributesCount
            #     print(f'attributesCount: {attributesCount}')
                
                for i in range(attributesCount):
                    attributes[i] = PostboxDecoder(buf.read_bytes()).decodeRootObject()
            #         print(f'attributes: {len(attributes[i])}', attributes[i])
                    
                embeddedMediaCount = buf.read_int32()
                embeddedMedia = [None]*embeddedMediaCount
            #     print(f'embeddedMediaCount: {embeddedMediaCount}')
                
                for i in range(embeddedMediaCount):
                    embeddedMedia[i] = PostboxDecoder(buf.read_bytes()).decodeRootObject()
            #         print(f'embeddedMedia: {len(embeddedMedia[i])}', embeddedMedia[i])
                    
                referencedMediaIds = []
                referencedMediaIdsCount = buf.read_int32()
                for _ in range(referencedMediaIdsCount):
                    idNamespace = buf.read_int32()
                    idId = buf.read_int64()
                    
                    referencedMediaIds.append((idNamespace, idId))
                    
                leftover = buf.buf.read()
                if leftover != b'':
                    print('huh, y no empty', leftover)
                    
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
            
            
            # In[12]:
            
            
            class PostboxDecoder:
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
                    
                def get(self, valueType, key, decodeObjects=None):
                    for k, t, v in self._iter_kv(decodeObjects=decodeObjects):
                        if k != key:
                            pass
                        elif valueType == None:
                            return t, v
                        elif t == valueType:
                            return t, v
                        elif t == self.ValueType.Nil:
                            return t, None
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
                        
                def _readObject(self, decode=None, registry=None):
                    if decode is None:
                        decode = True
                    if registry is None:
                        registry = self.registry
                        
                    typeHash = self.bio.read_int32()
                    dataLen = self.bio.read_int32()
                    data = self.bio.buf.read(dataLen)
                    
                    if not decode:
                        value = {'type': typeHash, 'data': data}
                    elif typeHash in self.registry:
                        decoder = self.__class__(data)
                        value = self.registry[typeHash](decoder)
                    else:
                        decoder = self.__class__(data)
                        value = {k: v for k, t, v in decoder._iter_kv()}
            #             value['@raw'] = data
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
                        value = [None]*alen
                        for i in range(alen):
                            value[i] = self.bio.read_int32()
                    elif valueType == self.ValueType.Int64Array:
                        alen = self.bio.read_int32()
                        value = [None]*alen
                        for i in range(alen):
                            value[i] = self.bio.read_int64()
                    elif valueType == self.ValueType.ObjectArray:
                        alen = self.bio.read_int32()
                        value = [None]*alen
                        for i in range(alen):
                            value[i] = self._readObject(**objectArgs)
                    elif valueType == self.ValueType.ObjectDictionary:
                        dlen = self.bio.read_int32()
                        value = [None]*dlen
                        for i in range(dlen):
                            dkey = self._readObject(**objectArgs)
                            dval = self._readObject(**objectArgs)
                            value[i] = (dkey, dval)
                    elif valueType == self.ValueType.Bytes:
                        value = self.bio.read_bytes()
                    elif valueType == self.ValueType.Nil:
                        pass # Nil is None
                    elif valueType == self.ValueType.StringArray:
                        alen = self.bio.read_int32()
                        value = [None]*alen
                        for i in range(alen):
                            value[i] = self.bio.read_str()
                    elif valueType == self.ValueType.BytesArray:
                        alen = self.bio.read_int32()
                        value = [None]*alen
                        for i in range(alen):
                            value[i] = self.bio.read_bytes()
                    else:
                        raise Exception('unknown value type')
                    return valueType, value
                
                
            # In[13]:
                
                
            class Decodeable:
                def __init__(self, dec):
                    for field, v in self.FIELDS.items():
                        key = v[0]
                        typ = v[1]
                        _, val = dec.get(typ, key)
                        setattr(self, field, val)
                        
                def __repr__(self):
                    return repr(self.__dict__)
                
            @PostboxDecoder.registerDecoder
            class TelegramMediaImage(Decodeable):
                FIELDS = {
                    'imageId': ('i', PostboxDecoder.ValueType.Bytes),
                    'representations': ('r', PostboxDecoder.ValueType.ObjectArray),
                    'videoRepresentations': ('vr', PostboxDecoder.ValueType.ObjectArray),
                    'immediateThumbnailData': ('itd', PostboxDecoder.ValueType.Bytes),
                    'reference': ('rf', PostboxDecoder.ValueType.Object),
                    'partialReference': ('prf', PostboxDecoder.ValueType.Object),
                    'flags': ('fl', PostboxDecoder.ValueType.Int32),
                }
                
                def __init__(self, dec):
                    super().__init__(dec)
                    bio = byteutil(io.BytesIO(self.imageId))
                    self.imageId = (bio.read_int32(), bio.read_int64())
                    
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
                    return f"telegram-cloud-photo-size-{self.datacenterId}-{self.photoId}-{self.sizeSpec}"
                
            @PostboxDecoder.registerDecoder
            class CloudDocumentMediaResource(Decodeable):
                FIELDS = {
                    'datacenterId': ('d', PostboxDecoder.ValueType.Int32),
                    'fileId': ('f', PostboxDecoder.ValueType.Int64),
                    'accessHash': ('a', PostboxDecoder.ValueType.Int64),
                    'size': ('n', PostboxDecoder.ValueType.Int32),
                    'fileReference': ('fr', PostboxDecoder.ValueType.Bytes),
                    'fileName': ('fn', PostboxDecoder.ValueType.String)
                }
                
                @property
                def uniqueId(self):
                    return f"telegram-cloud-document-{self.datacenterId}-{self.fileId}"
                
                
            @PostboxDecoder.registerDecoder
            class TelegramMediaFile(Decodeable):
                FIELDS = {
                    'fileId': ('i', PostboxDecoder.ValueType.Bytes),
                    'partialReference': ('prf', PostboxDecoder.ValueType.Object),
                    'resource': ('r', PostboxDecoder.ValueType.Object),
                    'previewRepresentations': ('pr', PostboxDecoder.ValueType.ObjectArray),
                    'videoThumbnails': ('vr', PostboxDecoder.ValueType.ObjectArray),
                    'immediateThumbnailData': ('itd', PostboxDecoder.ValueType.Bytes),
                    'mimeType': ('mt', PostboxDecoder.ValueType.String),
                    'size': ('s', PostboxDecoder.ValueType.Int32),
                    'attributes': ('at', PostboxDecoder.ValueType.ObjectArray)
                }
                
                def __init__(self, dec):
                    super().__init__(dec)
                    bio = byteutil(io.BytesIO(self.fileId))
                    self.fileId = (bio.read_int32(), bio.read_int64())
                    
                @property
                def mediaId(self):
                    return self.fileId
                
                
            @PostboxDecoder.registerDecoder
            class TelegramMediaWebpage(Decodeable):
                FIELDS = {
                    'webpageId': ('i', PostboxDecoder.ValueType.Bytes),
                    'pendingUrl': ('pendingUrl', PostboxDecoder.ValueType.String),
                    'url': ('u', PostboxDecoder.ValueType.String),
                }
                
                def __init__(self, dec):
                    super().__init__(dec)
                    bio = byteutil(io.BytesIO(self.webpageId))
                    self.webpageId = (bio.read_int32(), bio.read_int64())
                    
                @property
                def mediaId(self):
                    return self.webpageId
                
            @PostboxDecoder.registerDecoder
            class TelegramMediaAction:
                class Type(enum.Enum):
                    unknown = 0
                    groupCreated = 1
                    addedMembers = 2
                    removedMembers = 3
                    photoUpdated = 4
                    titleUpdated = 5
                    pinnedMessageUpdated = 6
                    joinedByLink = 7
                    channelMigratedFromGroup = 8
                    groupMigratedToChannel = 9
                    historyCleared = 10
                    historyScreenshot = 11
                    messageAutoremoveTimeoutUpdated = 12
                    gameScore = 13
                    phoneCall = 14
                    paymentSent = 15
                    customText = 16
                    botDomainAccessGranted = 17
                    botSentSecureValues = 18
                    peerJoined = 19
                    phoneNumberRequest = 20
                    geoProximityReached = 21
                    groupPhoneCall = 22
                    inviteToGroupPhoneCall = 23
                    
                def __init__(self, dec):
                    raw = {k: v for k, t, v in dec._iter_kv()}
                    self.type = self.Type(raw.get('_rawValue', 0))
                    if '_rawValue' in raw:
                        del raw['_rawValue']
                    self.payload = raw
                    
                def __repr__(self):
                    return f"{self.type} {self.payload}"
                
            # In[14]:
                
                
            con = sqlite3.connect(file_found)
            
            
            # In[15]:
            
            for idx, msg in get_all_messages(f=lambda idx: idx.timestamp > 1619557200):
                #print(msg)
                print_message(idx, msg)
                if MessageFlags.Incoming in msg['flags'] and 'web versions of Telegram' in msg['text']:
                    print_message(idx, msg)
                    #break
                    
            # In[16]:
                    
            for idx, msg in get_all_messages(f=lambda idx: idx.peerId == 9596437714 and idx.timestamp > 1617224400):
                print_message(idx, msg)
                            
            # In[17]:
                
            get_peer(9596437714)
    
            # In[18]:
    
            con.close()
    
    if len(data_list) > 0:    
        description = 'Telegram - Messages'
        report = ArtifactHtmlReport('Telegram - Messages')
        report.start_artifact_report(report_folder, 'Telegram - Messages')
        report.add_script()
        data_headers = (
            'Timestamp', 'Direction', 'Author ID', 'Text', 'Forward Timestamp', 'Forward From', 
            'Action Data', 'Thumb')  # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()    
        
        
        tsvname = f'Telegram - Messages'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Telegram - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Telegram - Messages data available')
        
__artifacts__ = {
    "TelegramMessages": (
        "Telegram",
        ('*/telegram-data/account-*/postbox/db/db_sqlite','*/telegram-data/account-*/postbox/media/**'),
        get_telegramMessages)
}