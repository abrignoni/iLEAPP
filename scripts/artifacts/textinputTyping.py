import os
import nska_deserialize as nd
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly 


def get_textinputTyping(files_found, report_folder, seeker, wrap_text, timezone_offset):
    count = 0
    for file_found in files_found:
        count = count + 1
        data_list = []
        with open(file_found, 'rb') as f:
            try:
                deserialized_plist = nd.deserialize_plist(f)
                #print(deserialized_plist)
            except (nd.DeserializeError, 
                    nd.biplist.NotBinaryPlistException, 
                    nd.biplist.InvalidPlistException,
                    plistlib.InvalidFileException,
                    nd.ccl_bplist.BplistError, 
                    ValueError, 
                    TypeError, OSError, OverflowError) as ex:
                # These are all possible errors from libraries imported
            
                print('Had exception: ' + str(ex))
                deserialized_plist = None
        
        lenofjson = len(deserialized_plist['alignedEntries'])
        testrun = deserialized_plist['alignedEntries'][lenofjson -1]
        for x, y in testrun['originalWord'].items():
            #print(x)
            if x == 'documentState':
                finalvalue = (y['contextBeforeInput'])
                
            if x == 'keyboardState':
                for a, b in y.items():
                    if a == 'inputContextHistory':
                        for c, d in b.items():
                            if c == 'pendingEntries': 
                                #print(d) #this is a list
                                for e in d:
                                    data_list.append((e['timestamp'], e['senderIdentifier'], e['text'], '' ))
        
        data_list.append(('','', finalvalue, 'True'))

        
        entries = len(data_list)
        if entries > 0:
            report = ArtifactHtmlReport('Text Input Typing')
            report.start_artifact_report(report_folder, f'Messages {count}')
            report.add_script()
            data_headers = ('Timestamp','Sender Identifier','Text','contextBeforeInput' )
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Messages {count}'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Messages {count}'
            timeline(report_folder, tlactivity, data_list, data_headers)
    
        else:
            logfunc(f"No Messages {count} available")

__artifacts__ = {
    "textinputTyping": (
        "Text Input Messages",
        ('*/DES/Records/com.apple.TextInput.TypingDESPlugin/*.desdata'),
        get_textinputTyping)
}