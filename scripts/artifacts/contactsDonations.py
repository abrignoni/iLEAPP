__artifacts_v2__ = {
    "contactsDonations": {
        "name": "Contacts Me Card Donations",
        "description": "Values donated to the Contacts me card store, with the donor, the donation and "
                       "expiration dates and the value's label",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Contacts",
        "notes": ('Read from the donations array in Library/Contacts/Donations/donations.plist, one row per '
                  'donation. Value Type is the key that held the value and Value is that value. The value keys on '
                  'the tested images were email-address, phone-number, postal-address and name-components; a '
                  'donation with a different value key gets a blank Value Type and Value and its keys are logged. '
                  'Postal address parts are joined with commas and name components with spaces, in a fixed field '
                  "order. Label, Donor Bundle ID, Donation ID and Cluster ID are label and the origin's "
                  'bundle-identifier, donation-identifier and cluster-identifier as stored (Contacts label '
                  "constants are not translated). Donation Date and Expiration Date are the origin's donation-date "
                  'and expiration-date. All 15 phone-number donations carried an expiration of 4001-01-01 00:00:00 '
                  'UTC, the value Foundation returns for NSDate.distantFuture (checked by calling it on macOS), so '
                  'Expiration Date is blank for them and Expiration Stored As Distant Future says Yes. The origin '
                  'carried no cluster-identifier key on the 15 phone-number and 5 postal-address donations, so '
                  'Cluster ID is blank there. Source-verified on iOS 12 code only (the ctf2020_ios12 shared cache '
                  'and donation agent): the donation API this file belongs to handles me card values '
                  "(donateMeCardValues:, meCardDonations), and the agent's solicitor classes are named for the SIM "
                  "card, the device's accounts (with email and name parsers) and app extensions. That each value is "
                  "the device owner's is that API's purpose, not something checked per value: in an earlier "
                  'comparison on 4 of these images, the donated email addresses were absent from AddressBook on 3 '
                  'and present on 1, and donated names were present on 2. Across the tested images the donors were '
                  'com.apple.contacts.donation.accounts (36 email and 36 name donations), '
                  'com.apple.contacts.donation.phonenumber (15 phone numbers) and com.apple.routined (5 postal '
                  'addresses). Keys on a donation, inside its value or inside its origin that this artifact does '
                  'not show are logged; none were on the tested images. The tested iTunes backup did not hold the '
                  'file.'),
        "paths": ('*/Library/Contacts/Donations/donations.plist',),
        "output_types": "standard",
        "artifact_icon": "user-check",
        "sample_data": {
            "hickman_ios15": "iOS 15.3.1 | 12 rows",
            "hexordia_ios1651": "iOS 16.5.1 | 11 rows",
            "cookbook_ios1751": "iOS 17.5.1 | 9 rows",
            "magnet_ios16": "iOS 16.1.1 | 9 rows",
            "hc_ios26": "iOS 26.5.2 | 8 rows",
            "hickman_ios14": "iOS 14.3 | 8 rows",
            "hickman_ios13": "iOS 13.3.1 | 7 rows",
            "iphone12_ios18": "iOS 18.7 | 7 rows",
            "ctf2020_ios12": "iOS 12.4 | 5 rows",
            "belkactf6_tar": "iOS 16.3 | 4 rows",
            "otto_ios17": "iOS 17.5.1 | 4 rows",
            "abe_ios16": "iOS 16.5 | 2 rows",
            "hc_ios17_2": "iOS 17.2.1 | 2 rows",
            "dexter_ios18": "iOS 18.3.2 | 1 row",
            "felix_ios17": "iOS 17.6.1 | 1 row",
            "hc_ios18_7": "iOS 18.7.8 | 1 row",
            "iphone11_ios17": "iOS 17.3 | 1 row",
            "hickman_ios14_itunes_backup_decrypted": "iOS 14.3 | 0 rows",
        },
    }
}

import os
import plistlib
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, logfunc

# The value keys a donation can carry, in the order they are tried
VALUE_KEYS = ('email-address', 'phone-number', 'postal-address', 'name-components')
POSTAL_FIELDS = ('street', 'subLocality', 'city', 'subAdministrativeArea', 'state', 'postalCode',
                 'country', 'isoCountryCode')
ORIGIN_KEYS = ('bundle-identifier', 'donation-identifier', 'donation-date', 'expiration-date',
               'cluster-identifier', 'version')
NAME_FIELDS = ('namePrefix', 'givenName', 'middleName', 'familyName', 'nameSuffix', 'nickname')


# NSDate.distantFuture, which Foundation returns as 4001-01-01 00:00:00 UTC
DISTANT_FUTURE = datetime(4001, 1, 1)


def _utc(value):
    return value.replace(tzinfo=timezone.utc) if isinstance(value, datetime) else ''


def _value(donation):
    """(value key as stored, value as text, keys not shown) for one donation."""
    for key in VALUE_KEYS:
        if key not in donation:
            continue
        value = donation[key]
        if isinstance(value, dict):
            fields = POSTAL_FIELDS if key == 'postal-address' else NAME_FIELDS
            shown = [str(value[f]) for f in fields if value.get(f) not in (None, '')]
            extra = sorted(k for k in value if k not in fields and k != 'version')
            return key, (', ' if key == 'postal-address' else ' ').join(shown), extra
        return key, str(value), []
    return '', '', []


@artifact_processor
def contactsDonations(context):
    data_headers = (('Donation Date', 'datetime'), ('Expiration Date', 'datetime'), 'Value Type',
                    'Value', 'Label', 'Donor Bundle ID', 'Donation ID', 'Cluster ID',
                    'Expiration Stored As Distant Future')
    data_list = []
    sources = []
    for file_found in sorted(str(f) for f in context.get_files_found()):
        if not os.path.isfile(file_found):
            continue
        try:
            with open(file_found, 'rb') as fp:
                store = plistlib.load(fp)
        except (OSError, plistlib.InvalidFileException, ValueError) as error:
            logfunc(f'Contacts Me Card Donations: could not read {os.path.basename(file_found)}: {error}')
            continue
        sources.append(file_found)
        donations = store.get('donations') if isinstance(store, dict) else None
        if not isinstance(donations, list):
            logfunc('Contacts Me Card Donations: no donations array')
            continue
        for donation in donations:
            if not isinstance(donation, dict):
                continue
            origin = donation.get('origin') if isinstance(donation.get('origin'), dict) else {}
            value_type, value, extra = _value(donation)
            # a key this artifact does not show is logged, so a new value type is not lost unseen
            extra += sorted(k for k in donation
                            if k not in VALUE_KEYS and k not in ('origin', 'label', 'version'))
            extra += sorted(f'origin.{k}' for k in origin if k not in ORIGIN_KEYS)
            if extra:
                logfunc(f'Contacts Me Card Donations: keys not reported: {", ".join(extra)}')
            expiration = origin.get('expiration-date')
            distant = expiration == DISTANT_FUTURE
            data_list.append((
                _utc(origin.get('donation-date')), '' if distant else _utc(expiration),
                value_type, value, donation.get('label', ''), origin.get('bundle-identifier', ''),
                origin.get('donation-identifier', ''), origin.get('cluster-identifier', ''),
                'Yes' if distant else 'No'))

    return data_headers, data_list, '\n'.join(sources)
