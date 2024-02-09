import sqlite3
import blackboxprotobuf
import re
from io import BytesIO

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, utf8_in_extended_ascii, media_to_html

class Tuppsub(tuple):
    pass
    
class ProtectedTuple(tuple):
    pass
    
    
class ProtectedList(list):
    pass
    
    
class ProtectedDict(dict):
    pass
    
    
class ProtectedSet(set):
    pass
def aa_flatten_dict_tu(
        v,
        listitem,
        forbidden=(list, tuple, set, frozenset),
        allowed=(
                str,
                int,
                float,
                complex,
                bool,
                bytes,
                type(None),
                ProtectedTuple,
                ProtectedList,
                ProtectedDict,
                ProtectedSet,
                Tuppsub,
        ),
):
    if isinstance(v, dict) or (
            hasattr(v, "items") and hasattr(v, "keys")
    ):  # we check right away if it is a dict or something similar (with keys/items). If we miss something, we will
        # only get the keys back.
        for k, v2 in v.items():
            newtu = listitem + (k,)  # we accumulate all keys in a tuple
            
            # and check if there are more dicts (nested) in this dict
            yield from aa_flatten_dict_tu(
                v2, listitem=newtu, forbidden=forbidden, allowed=allowed
            )
    elif isinstance(
            v, forbidden
    ):  # if we have an iterable without keys (list, tuple, set, frozenset) we have to enumerate them to be able to
        # access the original dict values later: di['blabla'][0] instead of di['blabla']
    
        for indi, v2 in enumerate(v):
            
            if isinstance(v2, allowed):
                yield v2, listitem
            #  if the value is not in our allowed data types, we have to check if it is an iterable
            else:
                yield from aa_flatten_dict_tu(
                    v2,
                    listitem=(listitem + (indi,)),
                    forbidden=forbidden,
                    allowed=allowed,
                )
    elif isinstance(v, allowed):
        #  if the datatype is allowed, we yield it
        yield Tuppsub((v, listitem))
        
    # Brute force to check if we have an iterable. We have to get all iterables!
    else:
        try:
            for indi2, v2 in enumerate(v):
                
                try:
                    if isinstance(v2, allowed):
                        yield v2, listitem
                        
                    else:
                        yield aa_flatten_dict_tu(
                            v2,
                            listitem=(listitem + (indi2,)),
                            forbidden=forbidden,
                            allowed=allowed,
                        )
                except Exception:
                    # if there is an exception, it is probably not an iterable, so we yield it
                    yield v2, listitem
        except Exception:
            # if there is an exception, it is probably not an iterable, so we yield it
            yield v, listitem
            
            
def fla_tu(
        item,
        walkthrough=(),  # accumulate nested keys
        forbidden=(list, tuple, set, frozenset),  # forbidden to yield, need to be flattened
        allowed=(  # Data types we don't want to touch!
                str,
                int,
                float,
                complex,
                bool,
                bytes,
                type(None),
                ProtectedTuple,  #
                ProtectedList,
                ProtectedDict,
                ProtectedSet,
                Tuppsub  # This is the secret - Inherit from tuple and exclude it from being flattened -
                # ProtectedTuple does the same thing
        ),
        dict_variation=(
        # we don't check with isinstance(), rather with type(), that way we don't have to import collections.
                "collections.defaultdict",
                "collections.UserDict",
                "collections.OrderedDict",
        ),
):
    if isinstance(item, allowed):  # allowed items, so let's yield them
        yield item, walkthrough
    elif isinstance(item, forbidden):
        for ini, xaa in enumerate(item):
            try:
                yield from fla_tu(
                    xaa,
                    walkthrough=(walkthrough + (ini,)),
                    forbidden=forbidden,
                    allowed=allowed,
                    dict_variation=dict_variation,
                )  # if we have an iterable, we check recursively for other iterables
                
            except Exception:
                
                yield xaa, Tuppsub(
                    (walkthrough + Tuppsub((ini,)))
                )  # we just yield the value (value, (key1,key2,...))  because it is probably not an iterable
    elif isinstance(
            item, dict
    ):  # we need to pass dicts to aa_flatten_dict_tu(), they need a special treatment, if not, we only get the keys from the dict back
    
        yield from aa_flatten_dict_tu(
            item, listitem=walkthrough, forbidden=forbidden, allowed=allowed
        )
    # let's try to catch all different dict variations by using ( hasattr(item, "items") and hasattr(item, "keys").
    # If we dont pass it to aa_flatten_dict_tu(), we only get the keys back.
    #
    # -> (hasattr(item, "items") and hasattr(item, "keys") -> Maybe better here:     elif isinstance( item, dict ):
    elif (str(type(item)) in dict_variation) or (
            hasattr(item, "items") and hasattr(item, "keys")
    ):
        yield from aa_flatten_dict_tu(
            dict(item), listitem=walkthrough, forbidden=forbidden, allowed=allowed
        )
    
    # isinstance(item, pd.DataFrame) maybe better?
    elif "DataFrame" in str(type(item)):
        
        yield from aa_flatten_dict_tu(
            item.copy().to_dict(),
            # pandas needs to be converted to dict first, if not, we only get the columns back. Copying might not be necessary
            listitem=walkthrough,
            forbidden=forbidden,
            allowed=allowed,
        )
        
    # # many iterables are hard to identify using isinstance() / type(), so we have to use brute force to check if it is
    # an iterable. If one iterable escapes, we are screwed!
    else:
        try:
            for ini2, xaa in enumerate(item):
                try:
                    if isinstance(xaa, allowed):  # yield only for allowed data types
                    
                        yield xaa, Tuppsub(
                            (walkthrough + (ini2,))
                        )  # yields (value, (key1,key2,...)) -> always same format -> first value, then all keys in another tuple
                    else:  # if it is not in the allowed data types, we check recursively for other iterables
                        yield from fla_tu(
                            xaa,
                            walkthrough=Tuppsub(
                                (walkthrough + Tuppsub(ini2, ))
                            ),  # yields (value, (key1,key2,...))
                            forbidden=forbidden,
                            allowed=allowed,
                            dict_variation=dict_variation,
                        )
                except Exception:
                    
                    yield xaa, Tuppsub(
                        (walkthrough + (ini2,))
                    )  # in case of an exception, we yield  (value, (key1,key2,...))
        except Exception:
            
            yield item, Tuppsub(
                (walkthrough + Tuppsub(item, ))
            )  # in case of an exception, we yield  (value, (key1,key2,...))
            
def get_googleChat(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('dynamite.db'):
            result = re.findall(r"([0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}+)", file_found)
            guid = result[0]
            break
            
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(topic_messages.create_time/1000000,'unixepoch') AS "Message Time",
    CASE
    WHEN group_type=1 THEN "Group Message"
    WHEN group_type=2 THEN "1-to-1 Message"
    ELSE group_type
    END AS "Group Type",
    Groups.name AS "Conversation Name",
    users.name AS "Message Author",
    topic_messages.text_body AS "Message",
    topic_messages.reactions AS "Message Reactions",
    topic_messages.annotation AS "Message Annotation (Possible Attachment Information)"
    FROM 
    topic_messages
    JOIN users ON users.user_id=topic_messages.creator_id
    JOIN Groups ON Groups.group_id=topic_messages.group_id
    ORDER BY "Message Time" ASC
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        
        for row in all_rows:
            thumb = ''
            protobufreactions = row[5]
            checkforempty = BytesIO(protobufreactions)
            check = checkforempty.read(3)
            
            if check == b'\xfe\xff\x00':
                reaction = ''
                reactionuser = ''
            else:
                protostuff, types = blackboxprotobuf.decode_message(protobufreactions)
                reaction = (protostuff['1']['1']['1']['1']).decode()
                reaction = (utf8_in_extended_ascii(reaction))[1]
                
                timestampofreaction = protostuff['1']['1']['4']
                reactionuser = protostuff['1'].get('2')
                if reactionuser is not None:
                    reactionuser = protostuff['1']['2']['1']
                    reactionuser = (reactionuser.decode())
                else:
                    reactionuser = ''
                    
            protobufmedia = row[6]
            checkforempty = BytesIO(protobufmedia)
            check = checkforempty.read(3)
            
            if check == b'\xfe\xff\x00':
                media = ''
                mediafilename = ''
            else:
                protostuff, types = blackboxprotobuf.decode_message(protobufmedia)
                aggregator = []
                if isinstance(protostuff['1'], list):
                    nested_whatever=list(fla_tu(protostuff['1']))
                    for x in nested_whatever:
                        if isinstance(x[0], bytes):
                            aggregator.append(x[0].decode())
                    mediafilename = 'Group List'
                    thumb = aggregator
                else:
                    checkkeyten = (protostuff['1'].get('10'))
                    if checkkeyten is not None:
                        mediafilename = (protostuff['1']['10']['3'])
                        mediafilename = (mediafilename.decode())
                        attachment = seeker.search('*/'+guid+'/tmp/'+mediafilename, return_on_first_hit=True)
                        
                        if len(attachment) < 1:
                            thumb = ''
                        else:
                            thumb = media_to_html(attachment[0], (attachment[0],), report_folder)
                    else:
                        mediafilename = ''
                        media = ''
            
            data_list.append((row[0],row[1],row[2],row[3],row[4],mediafilename,thumb,reaction,reactionuser))
            mediafilename = thumb = reaction = reactionuser = ''
            
        
        description = ''
        report = ArtifactHtmlReport('Google Chat')
        report.start_artifact_report(report_folder, 'Google Chat', description)
        report.add_script()
        data_headers = ('Timestamp','Group Type','Conversation Name','Message Author','Message','Filename','Media','Reaction','Reaction User' )     
        report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Media'])
        report.end_artifact_report()
        
        tsvname = 'Google Chat'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Google Chat data available')
    
    
__artifacts__ = {
    "googleChat": (
        "Google Chat",
        ('*/Documents/user_accounts/*/dynamite.db*'),
        get_googleChat)
}