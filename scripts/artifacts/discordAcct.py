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
from scripts.ilapfuncs import artifact_processor

def strings(filename, min=4):
	with open(filename, errors="ignore") as f:  # Python 3.x
	# with open(filename, "rb") as f:           # Python 2.x
		result = ""
		for c in f.read():
			if c in string.printable:
				result += c
				continue
			if len(result) >= min:
				yield result
			result = ""
		if len(result) >= min:  # catch result at EOF
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
                except:
                    pass
                
            if 'email_cache' in x:
                #print(x)
                wfa = searchlist[counter].split('"')
                try:
                    data_list.append(('EMAIL_CACHE', wfa[1], file_found))
                except:
                    pass

    return data_headers, data_list, 'see Source File for more info'
    