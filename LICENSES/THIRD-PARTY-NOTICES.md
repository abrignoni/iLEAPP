# Third-party licences

The source code in this repository is under the MIT licence (see LICENSE in the repository
root). That does not change.

The packaged programs attached to each release also carry code from other projects. This folder
holds the licence texts for the parts that come with conditions on how they are shared. It
ships inside every packaged program, in a folder named LICENSES.

## HEIC and HEIF images: pillow-heif

Packaged programs include pillow-heif 1.8.1 so that HEIC images found in an extraction can
be shown in the report. The pillow-heif Python code is under the BSD-3-Clause licence
(pillow-heif-LICENSE.txt). Its binary builds bundle these libraries, as its own list says
(pillow-heif-LICENSES_bundled.txt):

| Library | Version | Licence | Licence text |
| --- | --- | --- | --- |
| libheif | 1.23.6 | LGPL-3.0 | libheif-COPYING.txt |
| libde265 | 1.1.3 | LGPL-3.0 | libde265-COPYING.txt |
| x265 | 4.3 | GPL-2.0-or-later | x265-COPYING.txt |
| MinGW-w64 libgcc and libstdc++ (Windows x64 only) | | GPL-3.0 with the GCC Runtime Library Exception 3.1 | GPL-3.0.txt, GCC-RUNTIME-LIBRARY-EXCEPTION.txt |
| MinGW-w64 winpthreads (Windows x64 only) | | MIT | mingw-w64-winpthreads-COPYING.txt |
| LLVM libc++ (Windows ARM only) | | Apache-2.0 with LLVM exceptions | llvm-libcxx-LICENSE.txt |

x265 is an HEVC encoder. These programs only decode images, but libheif loads x265 when it
starts, so it ships too. x265 is under the GPL version 2 or any later version, so each
packaged program as a whole is distributed under the GNU General Public License version 3
(GPL-3.0.txt; the LGPL-3.0 text is in LGPL-3.0.txt). Anyone who runs the code from this
repository under the MIT licence keeps doing so.

## Getting the source

Each release has these source archives attached next to the packaged programs, at the exact
versions listed above:

- source-libheif-1.23.6.tar.gz
- source-libde265-1.1.3.tar.gz
- source-x265-4.3.tar.gz
- source-pillow_heif-1.8.1.tar.gz

sources.json lists where each one comes from and its SHA-256. The source of the program
itself is the release tag in this repository. To run it with a changed libheif, libde265 or
x265, install your own build of pillow-heif and run from source, or build the packaged
program yourself with packaging/build.py.
