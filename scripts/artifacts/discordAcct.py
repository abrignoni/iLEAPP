__artifacts_v2__ = {
    "get_discordAcct": {  # This should match the function name exactly
        "name": "Discord - Account",
        "description": "Parses Discord accounts",
        "author": "",
        "creation_date": "",
        "last_updated": "2025-11-25",
        "requirements": "none",
        "category": "Discord",
        "notes": "",
        "paths": ('*/mobile/Containers/Data/Application/*/Documents/mmkv/mmkv.default'),
        "output_types": "standard",  # or ["html", "tsv", "timeline", "lava"]
    }
}

import string
from scripts.ilapfuncs import artifact_processor, logfunc

def strings(filename, min_length=4):
    with open(filename, "rb") as f:  # Python 3.x
	# with open(filename, "rb") as f:           # Python 2.x
        result = ""
        for c in f.read():
            char = chr(c)
            if char in string.printable:
                result += char
                continue
            if len(result) >= min_length:
                yield result
            result = ""
        if len(result) >= min_length:  # catch result at EOF
            yield result

@artifact_processor
def get_discordAcct(context):
    data_list = []
    data_headers = ('Key Name', 'Data Value', 'Source File')   
    for file_found in context.get_files_found():
        file_found = str(file_found)
        searchlist = []
        for s in strings(file_found):
            searchlist.append(str(s),)

        counter = 0
        for x in searchlist:
            counter += 1
            if 'user_id_cache' in x:
                wf = searchlist[counter].split('"')
                try:
                    data_list.append(('USER_ID_CACHE', wf[1], file_found))
                except (IndexError, TypeError) as e:
                    logfunc(f"Error parsing user_id_cache: {str(e)}")
                
            if 'email_cache' in x:
                #print(x)
                wfa = searchlist[counter].split('"')
                try:
                    data_list.append(('EMAIL_CACHE', wfa[1], file_found))
                except (IndexError, TypeError) as e:
                    logfunc(f"Error parsing email_cache: {str(e)}")

    return data_headers, data_list, 'see Source File for more info'
    