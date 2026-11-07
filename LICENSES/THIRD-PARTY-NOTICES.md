# Third-party licences

The source code in this repository is under the MIT licence (see LICENSE in the repository
root).

The packaged programs attached to each release also carry code from other projects. This folder
holds the licence texts for the code that reads HEIC images, and it ships inside every packaged
program, in a folder named LICENSES.

## HEIC and HEIF images: heicreader

Packaged programs include heicreader 0.1.0 so that HEIC images found in an extraction can be
shown in the report. heicreader is MIT (heicreader-LICENSE.txt). Its helper program is built
from the code below; heicreader-THIRD-PARTY-NOTICES.md is its own list of it.

| Component | Licence | Licence text |
| --- | --- | --- |
| gen2brain/h265, the HEVC and HEIC decoder (built from abrignoni/h265) | MIT | gen2brain-h265-LICENSE.txt |
| roticv/rust_h265, which that decoder was ported from (MIT or Apache-2.0; used under MIT) | MIT | rust_h265-LICENSE-MIT.txt |
| OxideAV/oxideav-h265, which that decoder was ported from | MIT | oxideav-h265-LICENSE.txt |
| The Go runtime and standard library, compiled into the helper | BSD-3-Clause | go-LICENSE.txt |

All of these are permissive licences. The build also refuses to package any file whose name
contains x264, x265, xvid, rubberband, vidstab or frei0r. Those are GPL video codecs; x265 is
the one pillow-heif, the HEIC reader used before heicreader, bundled.

HEVC is subject to patents. These licence texts do not mention patents, and this notice does
not address them.
