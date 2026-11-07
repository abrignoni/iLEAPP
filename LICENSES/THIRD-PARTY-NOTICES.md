# Third-party licences

The source code in this repository is under the MIT licence (see LICENSE in the repository
root).

The packaged programs attached to each release also carry code from other projects. This folder
holds the licence texts for the code that reads HEIC images, and it ships inside every packaged
program, in a folder named LICENSES.

Each packaged program also carries LICENSES/bundled/, written when it is built from the files
the build put in it: the licence files of every Python package it holds, the licence of the
Python it runs on, PyInstaller's licence, and the licences of the code this repository
vendors. An index there lists them and names the packages under copyleft terms (the GNU LGPL,
for example) with a link to their source. LICENSES/packages/ holds the texts for packages
whose wheels ship no licence file; each says where its text came from.

Some files come from the build machine instead of a Python package: on Linux, system
libraries such as the Tcl/Tk toolkit the window uses, and on Linux and macOS a library a
package links when pip compiles it on that machine. The build traces each of them to the
system package that installed it (dpkg on Ubuntu, Homebrew on macOS), ships that package's
licence file under LICENSES/bundled/system/, and lists it in the index with its version and
source. A file it cannot trace stops the build. Windows builds leave out the Universal C
Runtime: Windows 10 and later always use the system's copy, and the Python the builds use
runs only on Windows 10 and later.

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
the one pillow-heif, the HEIC reader used before heicreader, bundled. It refuses libreadline
too: GNU Readline is GPL-3.0, and Python's readline module links it on Linux, so the build
leaves that module out.

HEVC is subject to patents. These licence texts do not mention patents, and this notice does
not address them.
