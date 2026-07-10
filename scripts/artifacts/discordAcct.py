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
        "output_types": "standard",
        "artifact_icon": "brand-discord",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | com.zhiliaoapp.musically | 0 rows",
            "dexter_ios18": "iOS 18.3.2 | Discord - Talk, Play, Hang Out 298.0, NFL 60.0.12, TikTok - Videos, Shop & LIVE 41.8.0 | 3 rows",
            "felix_ios17": "iOS 17.6.1 | Discord – Talk, Play, Hang Out 244.0 | 1 row",
            "fsfull002_ios17": "iOS 17.1 | TikTok 28.4.1 | 0 rows",
            "hc_ios18_7": "iOS 18.7.8 | Discord - Talk, Play, Hang Out 324.0 | 3 rows",
            "iphone11_ios17": "iOS 17.3 | Discord - Talk, Play, Hang Out 238.0, TikTok 35.1.0 | 2 rows",
            "iphone12_ios18": "iOS 18.7 | Evernote - Notes Organizer 10.167.1, Discord - Talk, Play, Hang Out 306.1, TikTok - Videos, Shop & LIVE 42.7.0 | 1 row",
            "iphone14plus_ios18": "iOS 18.0 | Untappd: Find Drinks You Love 4.7.0 | 0 rows",
            "otto_ios17": "iOS 17.5.1 | TikTok 35.6.0 | 0 rows",
        },  # or ["html", "tsv", "timeline", "lava"]
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
                    data_list.append(('USER_ID_CACHE', wf[1], context.get_relative_path(file_found)))
                except (IndexError, TypeError) as e:
                    logfunc(f"Error parsing user_id_cache: {str(e)}")
                
            if 'email_cache' in x:
                #print(x)
                wfa = searchlist[counter].split('"')
                try:
                    data_list.append(('EMAIL_CACHE', wfa[1], context.get_relative_path(file_found)))
                except (IndexError, TypeError) as e:
                    logfunc(f"Error parsing email_cache: {str(e)}")

    return data_headers, data_list, 'see Source File for more info'
    