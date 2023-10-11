__artifacts_v2__ = {
    "adId": {
        "category": "Identifiers",
        "paths": ('*/containers/Shared/SystemGroup/*/Library/Caches/com.apple.lsdidentifiers.plist',),
        "function": 'get_adId'
    }
}

import datetime
import os
import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, is_platform_windows 

def get_adId(files_found, report_folder, seeker, wrap_text, timezone_offset):
    
    file_found = str(files_found[0])
    with open(file_found, "rb") as fp:
        pl = plistlib.load(fp)
        for key, val in pl.items():
            
            if key == 'LSAdvertiserIdentifier':
                adId = val
                logdevinfo(f"Advertiser Identifier: {adId}")
                
# __artifacts__ = {
#     "adId": (
#         "Identifiers",
#         ('*/containers/Shared/SystemGroup/*/Library/Caches/com.apple.lsdidentifiers.plist'),
#         get_adId)
# }
