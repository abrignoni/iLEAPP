import glob
import os
import pathlib
import plistlib
import sqlite3
import json
import textwrap
import scripts.artifacts.artGlobals
 
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows 
from scripts.ccl import ccl_bplist
from scripts.parse3 import ParseProto
    
def get_knowCincept(files_found, report_folder, seeker):
    data_list = []
    iOSversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iOSversion) < version.parse("11"):
        logfunc("Unsupported version" + iOSversion)
        return ()

    extension = ".bplist"
    dump = True
    # create directories
    outpath = report_folder

    try:
        os.mkdir(report_folder + "/clean/")
        os.mkdir(report_folder+ "/dirty/")
    except OSError:
        logfunc("Error making directories")
    file_found = str(files_found[0])
    # connect sqlite databases
    db = sqlite3.connect(file_found)
    cursor = db.cursor()

    # variable initializations
    dirtcount = 0
    cleancount = 0
    intentc = {}
    intentv = {}

    cursor.execute(
        """
	SELECT
	Z_PK,
	Z_DKINTENTMETADATAKEY__SERIALIZEDINTERACTION,
	Z_DKINTENTMETADATAKEY__INTENTCLASS,
	Z_DKINTENTMETADATAKEY__INTENTVERB
	FROM ZSTRUCTUREDMETADATA
	WHERE Z_DKINTENTMETADATAKEY__SERIALIZEDINTERACTION is not null
	"""
    )

    all_rows = cursor.fetchall()

    for row in all_rows:
        pkv = str(row[0])
        pkvplist = pkv + extension
        f = row[1]
        intentclass = str(row[2])
        intententverb = str(row[3])
        output_file = open(
            outpath + "/dirty/D_Z_PK" + pkvplist, "wb"
        )  # export dirty from DB
        output_file.write(f)
        output_file.close()

        g = open(outpath + "/dirty/D_Z_PK" + pkvplist, "rb")
        plistg = ccl_bplist.load(g)

        if version.parse(iOSversion) < version.parse("12"):
            ns_keyed_archiver_objg = ccl_bplist.deserialise_NsKeyedArchiver(plistg)
            newbytearray = ns_keyed_archiver_objg
        else:
            ns_keyed_archiver_objg = ccl_bplist.deserialise_NsKeyedArchiver(plistg)
            newbytearray = ns_keyed_archiver_objg["NS.data"]

        dirtcount = dirtcount + 1

        binfile = open(outpath + "/clean/C_Z_PK" + pkvplist, "wb")
        binfile.write(newbytearray)
        binfile.close()

        # add to dictionaries
        intentc["C_Z_PK" + pkvplist] = intentclass
        intentv["C_Z_PK" + pkvplist] = intententverb

        cleancount = cleancount + 1
    '''
    h = open(outpath + "/StrucMetadata.html", "w")
    h.write("<html><body>")
    h.write(
        "<h2>iOS "
        + iOSversion
        + " - KnowledgeC ZSTRUCTUREDMETADATA bplist report</h2>"
    )
    h.write(
        "<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>"
    )
    h.write("<br/>")
    '''
    for filename in glob.glob(outpath + "/clean/*" + extension):
        p = open(filename, "rb")
        cfilename = os.path.basename(filename)
        plist = ccl_bplist.load(p)
        ns_keyed_archiver_obj = ccl_bplist.deserialise_NsKeyedArchiver(
            plist, parse_whole_structure=True
        )  # deserialize clean
        # Get dictionary values
        A = intentc.get(cfilename)
        B = intentv.get(cfilename)

        if A is None:
            A = "No value"
        if B is None:
            A = "No value"

        # logfunc some values from clean bplist
        if version.parse(iOSversion) >= version.parse("13"):
            try:
                NSdata = ns_keyed_archiver_obj["root"]["intent"]["backingStore"][
                    "bytes"
                ]
            except:
                NSdata = ns_keyed_archiver_obj["root"]["intent"]["backingStore"][
                    "data"
                ]["NS.data"]
                pass
        else:
            NSdata = ns_keyed_archiver_obj["root"]["intent"]["backingStore"][
                "data"
            ]["NS.data"]
            # logfunc(str(NSdata))

        parsedNSData = ""
        # Default true
        if dump == True:
            nsdata_file = outpath + "/clean/" + cfilename + "_nsdata.bin"
            binfile = open(nsdata_file, "wb")
            if version.parse(iOSversion) >= version.parse("13"):
                try:
                    binfile.write(
                        ns_keyed_archiver_obj["root"]["intent"]["backingStore"][
                            "bytes"
                        ]
                    )
                except:
                    binfile.write(
                        ns_keyed_archiver_obj["root"]["intent"]["backingStore"][
                            "data"
                        ]["NS.data"]
                    )
                    pass
            else:
                binfile.write(
                    ns_keyed_archiver_obj["root"]["intent"]["backingStore"]["data"][
                        "NS.data"
                    ]
                )
            binfile.close()
            messages = ParseProto(nsdata_file)
            messages_json_dump = json.dumps(
                messages, indent=4, sort_keys=True, ensure_ascii=False
            )
            parsedNSData = str(messages_json_dump).encode(
                encoding="UTF-8", errors="ignore"
            )

        NSstartDate = ccl_bplist.convert_NSDate(
            (ns_keyed_archiver_obj["root"]["dateInterval"]["NS.startDate"])
        )
        NSendDate = ccl_bplist.convert_NSDate(
            (ns_keyed_archiver_obj["root"]["dateInterval"]["NS.endDate"])
        )
        NSduration = ns_keyed_archiver_obj["root"]["dateInterval"]["NS.duration"]
        Siri = ns_keyed_archiver_obj["root"]["_donatedBySiri"]
        

        if parsedNSData:
            parsedf = str(parsedNSData).replace("\\n", "<br>")
        else:
            parsedf = str(NSdata).replace("\\n", "<br>")
        
        data_list.append((str(A), str(B), str(Siri), str(NSstartDate), str(NSendDate), str(NSduration), parsedf, (textwrap.fill(str(NSdata), width=50)), cfilename))

    logfunc("iOS - KnowledgeC ZSTRUCTUREDMETADATA bplist extractor")
    logfunc("By: @phillmoore & @AlexisBrignoni")
    logfunc("thinkdfir.com & abrignoni.com")
    logfunc("")
    logfunc("Bplists from the Z_DKINTENTMETADATAKEY__SERIALIZEDINTERACTION field.")
    logfunc("Exported bplists (dirty): " + str(dirtcount))
    logfunc("Exported bplists (clean): " + str(cleancount))
    logfunc("")
    logfunc("Incepted bplist extractions in KnowledgeC.db completed")
    
    description = ''
    report = ArtifactHtmlReport('KnowledgeC Intents')
    report.start_artifact_report(report_folder, 'KnowledgeC Intents', description)
    report.add_script()
    data_headers = ('Intent Class','Intent Verb','Siri?','NS Start Date','NS Send Date','NS Duration','NS Data Protobuf', 'NS Data', 'Traceback' )     
    report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
    report.end_artifact_report()
