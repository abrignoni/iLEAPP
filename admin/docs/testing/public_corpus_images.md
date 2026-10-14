# Public Images Behind `sample_data`

Artifacts record what they produced against a named corpus:

```python
"sample_data": {
    "hickman_ios15": "iOS 15.3.1 | 204 rows",
}
```

The key names an entry in a corpus registry (`samples.json`) that lives with the test data
rather than in this repository, because most extractions are not ours to distribute. That is
fine for `validate_sample_data.py`, which reads the registry directly, but it leaves anyone
reading an artifact with a bare key and no way to tell which image produced the count.

This document closes that gap for the keys that name **publicly available** images. If you want
to reproduce a recorded row count, this is where you find out what to download.

Keys naming non-public images are listed at the end so you know not to go looking.

## How to read the "correlated by" column

The identification is not equally strong for every row, and the difference matters if you are
relying on it.

- **MD5** means the file we hold was hashed and the digest equals the value the publisher
  distributes. That is a definitive identification.
- **Extraction metadata** means our copy is the inner image un-nested from the publisher's
  wrapper archive, so its hash cannot match the published wrapper by construction. The link
  comes from the Cellebrite or UFED metadata inside the extraction naming the event and the
  persona (`DeviceInfo.txt`, the `.ufd`, the folder structure).
- **Inferred** means neither of the above. Read the row note before relying on it.

The MD5 column is the publisher's own published value, not something measured here, except on
the rows marked MD5 where the two are known to agree.

## iOS images

| `sample_data` key | Device and OS | Published by | Published file | MD5 (as published) | Correlated by |
| --- | --- | --- | --- | --- | --- |
| `ctf2020_ios12` | iOS 12.4 | Magnet Forensics, Magnet Virtual Summit CTF 2020 | `2020 CTF - iOS.zip` | `8134DFB212393099573AB5C3123172F3` | Extraction metadata |
| `hickman_ios13` | iOS 13.3.1 | Josh Hickman, public images | `ios_13_3_1.zip` | `6641CE1395D392661921CB0CA321E4B7` | Extraction metadata |
| `hickman_ios14` | iPhone SE, iOS 14.3 | Josh Hickman, public images | `iOS 14-3 - Apple iPhone SE.tar` | `7E7CB4D7E6204089758BF41D5D2C5EFC` | **MD5** |
| `hickman_ios15` | iPhone 8, iOS 15.3.1 | Josh Hickman, public images | `iOS_15_Public_Image.tar.gz` | `B1EC40D5CD835621326B821D6FA12FF5` | **MD5** |
| `magnet_ios16` | iOS 16.1.1 | Magnet Forensics, Magnet Virtual Summit CTF 2023 | `00008101-0010541A1130001E_files_full-001.zip` | `067606649297D7ADCF6082E5ED0ACBB9` | **MD5** |
| `belkactf6` | iOS 16.3 | Belkasoft, BelkaCTF 6 | `BelkaCTF_6_CASE240405_D201AP.zip` | `874C9A9D0D274B9BA5245116AA6F2A67` | **MD5** |
| `abe_ios16` | iPhone X, iOS 16.5 | Cellebrite CTF 2023 ("Abe") | `CellebriteCTF23_Abe_.zip` | `E6AACE42D05F400889BC9B9BE31CEB46` | Extraction metadata |
| `felix23_ios16` | iPhone 8 Plus, iOS 16.5 | Cellebrite CTF 2023 ("Felix") | `CellebriteCTF23_Felix.zip` | `996A913B1301AB011CA7DD8CA93A9400` | Extraction metadata |
| `hexordia_ios1651` | iOS 16.5.1 | Hexordia, Magnet Virtual Summit CTF 2024 | `00008110-000925383620A01E_files_full.zip` | `56EBD62968D37B67E656AD58EEE7A985` | **MD5** |
| `iphone11_ios17` | iPhone 11, iOS 17.3 | Josh Hickman, public images | `iOS_17_Public_Image.tar.gz` | `E115F051D15178FA1334489E24C9F0FD` | Extraction metadata |
| `otto_ios17` | iPhone 11 Pro, iOS 17.5.1 | Cellebrite CTF 2024 ("Otto") | `CellebriteCTF24_Otto.zip` | `54E581D2209A62EB431B06CEFD786B1A` | Extraction metadata |
| `cookbook_ios1751` | iOS 17.5.1 | Cody Bounds, Digital Forensics Cookbook Datasets | `Apple iOS.7z` | `374891EAE84E4D380C632B9B47ACBB9D` | Extraction metadata |
| `felix_ios17` | iPhone 8, iOS 17.6.1 | Cellebrite CTF 2024 ("Felix") | `CellebriteCTF24_Felix.zip` | `986FB9022E9AF1BF143126BE4E65AAAF` | Extraction metadata |
| `iphone14plus_ios18` | iPhone 14 Plus, iOS 18.0 | Hexordia, Magnet Virtual Summit CTF 2026 | `iPhone14Plus.zip` | `23075789FE93781A9A99E1DB952F47C5` | **MD5** |
| `dexter_ios18` | iPhone 16, iOS 18.3.2 | Cellebrite CTF 2025 ("Dexter King") | `2025CellebriteCTF_DexterKing.zip` | `4D455F968C61EC43960AB6B66B55AC4A` | Extraction metadata |
| `iphone12_ios18` | iPhone 12, iOS 18.7 | MSAB, Mobile Forensics Digital Summit CTF 2026 | `iPhone12.zip` | `0E1D586E89098EC0EBC4E6C12852F462` | Extraction metadata |

Two of these need a word of explanation.

**`iphone14plus_ios18`.** The published `iPhone14Plus.zip` is a wrapper. The image LEAPP reads is
the `00008110-0008196A2299401E_files_full.zip` inside it. Note that Hexordia published a
*different* acquisition of the same device for the 2025 CTF, also iOS 18.0, under that same inner
filename but with MD5 `A8E9DF3FC94C5C66F8CA8824773C0332`. The two are not interchangeable, so
check the hash rather than the filename.

**`belkactf6`.** The Belkasoft download is an AES-encrypted zip. Python's `zipfile` cannot read
AES, so `ileapp.py -t zip` against it matches nothing and exits without error, scoring every
artifact as zero rows. Decrypt it first and run the tar inside with `-t tar`.

## Android images

These keys appear in ALEAPP rather than iLEAPP and are listed here only so the two cores can be
cross-referenced. See ALEAPP's `admin/docs/public_corpus_images.md`.

## Where to download

| Publisher | Source |
| --- | --- |
| Josh Hickman | <https://digitalcorpora.org/corpora/cell-phones/> and the release posts on <https://thebinaryhick.blog/> |
| Magnet Forensics, Magnet Virtual Summit 2023 | <https://cfreds.nist.gov/all/MagnetForensics/MagnetVirtualSummit2023> |
| Belkasoft, BelkaCTF 6 | <https://cfreds.nist.gov/all/Belkasoft/BelkaCTF6BogusBill> |
| Everything above, indexed together | The Evidence Locker, <https://theevidencelocker.github.io/> |

The Evidence Locker is the most convenient single index. It publishes a filename, size, MD5 and
download link per image, and its `data.json` is the same catalog in machine-readable form.

Two things to know before you verify a download against it. Its `filesize` values are GiB even
though the unit prints as "GB", so compare `bytes / 2**30`. And five of its hash values carry a
stray character (four Cellebrite CTF 2024 entries contain an embedded soft hyphen, U+00AD, and one
Magnet 2023 entry a trailing space). Those four Cellebrite hashes are reproduced above with the
soft hyphen removed, which is why they may not look like a byte-for-byte copy of the site.

## Keys that name non-public images

These appear in `sample_data` and cannot be downloaded. They are recorded so a reader knows the
count came from a real image rather than a synthetic fixture, and so nobody spends time hunting
for a file that was never distributed.

| Key | What it is |
| --- | --- |
| `hc_ios18_7` | iPhone full filesystem, iOS 18.7.8. Not distributed. |
| `hc_ios26` | iPhone full filesystem, iOS 26.5.2. Not distributed. |
| `hc_ios26_sysdiag` | Sysdiagnose from the same iOS 26 device. Not distributed. |
| `ai16_ios26_sysdiag` | iPhone 16 sysdiagnose, iOS 26.5.2, Apple Intelligence capable. Not distributed. |
| `rodeo_ios17_sysdiag` | Sysdiagnose, iOS 17.3. Not distributed. |
| `fsfull002_ios17` | GrayKey full filesystem, iOS 17.1. Not distributed. |
| `jess_ios15` | GrayKey full filesystem, iPhone 8, iOS 15.0.2, acquired 2022-02-14. Checked against the full Evidence Locker catalog by hash and it is not published there. |

If you hold an image that would let one of these counts be reproduced publicly, that is a
genuinely useful contribution. See [guide_adding_images.md](guide_adding_images.md).

## Relationship to `image_manifest.json`

[`admin/image_manifest.json`](../../image_manifest.json) exists so `make_test_data.py` can find
an image on a contributor's disk to generate committed test cases. Every publicly available
image above has an entry, and every entry carries a `sample_data_key` field naming the corpus
key used in `sample_data` and in this document, so `make_test_data.py --image` accepts either
name. Keys from the non-public table stay out of the manifest deliberately: a manifest entry is
a statement that the image can be obtained.

Machine-specific locations do not live in the manifest. Record yours in the git-ignored
`admin/image_manifest.local.json`; see [guide_adding_images.md](guide_adding_images.md). The
four oldest entries keep their original `image_name` vocabulary and their committed
`local_image_paths` for compatibility:

| `image_manifest.json` `image_name` | `sample_data` key |
| --- | --- |
| `josh_ios15_ffs` | `hickman_ios15` |
| `josh_ios17_ffs` | `iphone11_ios17` |
| `mvs_ios_2023` | `magnet_ios16` |
| `belkasoft_ctf6_ios_device1` | `belkactf6` |

The manifest's MD5 for `belkasoft_ctf6_ios_device1` is not the same as the one in the table above.
That is expected rather than wrong: the manifest points at the NIST CFReDS redistribution and the
table above at Belkasoft's own encrypted zip. They are the same case, packaged differently.
