__artifacts_v2__ = {
    "zzBotTest": {
        "name": "Bot Test Placeholder",
        "description": "Temporary placeholder used to exercise the test-data bot end to end. This PR is never merged.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-24",
        "last_update_date": "2026-08-24",
        "requirements": "none",
        "category": "Identifiers",
        "paths": ('*/zz_bot_test_placeholder.plist',),
        "sample_data": {"hickman_ios15": "0 rows"},
        "output_types": "none",
        "artifact_icon": "device-mobile"
    }
}

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def zzBotTest(context):
    return (), [], ''
