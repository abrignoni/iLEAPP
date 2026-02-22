from datetime import datetime

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_mobileContainerManager(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_list = []
    file_found = ''

    for file_found in files_found:

        with open(file_found, 'r', encoding='utf-8') as fp:
            data = fp.readlines()

            for linecount, line in enumerate(data, 1):
                if '[MCMGroupManager _removeGroupContainersIfNeededforUser:groupContainerClass:identifiers:referenceCounts:]: Last reference to group container' in line:
                    txts = line.split()
                    month = txts[1]
                    day = txts[2]
                    time = txts[3]
                    year = txts[4]
                    group = txts[15]

                    datetime_object = datetime.strptime(month, "%b")
                    month_number = datetime_object.month
                    concat_date = year + "-" + str(month_number) + "-" + day + " " + time
                    dtime_obj = datetime.strptime(concat_date, '%Y-%m-%d %H:%M:%S')

                    data_list.append((str(dtime_obj), group, str(linecount)))

    data_headers = ('Datetime', 'Removed', 'Line')
    return data_headers, data_list, file_found

__artifacts_v2__ = {
    "get_mobileContainerManager": {
        "name": "Mobile Container Manager",
        "description": "",
        "author": "",
        "version": "0.1",
        "date": "2026-02-22",
        "requirements": "none",
        "category": "Mobile Container Manager",
        "notes": "",
        "paths": ('**/containermanagerd.log.*',),
        "output_types": "all",
        "artifact_icon": "alert-triangle"
    }
}
