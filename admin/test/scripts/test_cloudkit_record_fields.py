"""CloudKit Shares and Participants read every field of a record, not only RecordID.

ZSERVERRECORDDATA and ZSERVERSHAREDATA decode, through nska_deserialize, as a list of one-key
dicts, one per field of a single record. The artifacts took the dict holding RecordID (or
Participants) and read RecordType, RecordCtime, the creator and the share fields from that
same dict, which holds nothing else, so every column but Record ID was always empty.
"""
import datetime
import unittest

from scripts.artifacts import cloudkitSharing


class CloudkitRecordFieldsTest(unittest.TestCase):

    def test_one_key_dicts_merge_into_one_record(self):
        created = datetime.datetime(2022, 1, 31, 15, 0)
        decoded = [{'RecordType': 'Note'}, {'RecordCtime': created},
                   {'RecordID': {'RecordName': 'R1', 'ZoneID': {}}},
                   {'CreatorUserRecordID': {'RecordName': '_defaultOwner_'}}]

        records = cloudkitSharing.merged_records(decoded)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['RecordType'], 'Note')
        self.assertEqual(records[0]['RecordCtime'], created)
        self.assertEqual(cloudkitSharing.deep_get(records[0], ['RecordID', 'RecordName']), 'R1')

    def test_other_shapes_are_returned_as_before(self):
        whole = {'RecordID': {'RecordName': 'R1'}, 'RecordType': 'Note'}
        self.assertEqual(cloudkitSharing.merged_records(whole), [whole])
        two = [whole, {'RecordID': {'RecordName': 'R2'}, 'RecordType': 'Folder'}]
        self.assertEqual(cloudkitSharing.merged_records(two), two)
        self.assertEqual(cloudkitSharing.merged_records('not a record'), [])


if __name__ == '__main__':
    unittest.main()
