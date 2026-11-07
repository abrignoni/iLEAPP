# Third-party licences

heicreader is MIT (LICENSE in the repository root). The helper program it ships is built
from the code below, and its licence texts are in this folder. Every one of them is a
permissive licence: none is the GPL or the LGPL.

| Component | Licence | Text |
| --- | --- | --- |
| gen2brain/h265, the HEVC and HEIC decoder, built from abrignoni/h265 at the commit in go.mod | MIT | gen2brain-h265-LICENSE.txt |
| roticv/rust_h265, which that decoder was ported from (offered as MIT or Apache-2.0; used under MIT) | MIT | rust_h265-LICENSE-MIT.txt |
| OxideAV/oxideav-h265, which that decoder was ported from | MIT | oxideav-h265-LICENSE.txt |
| The Go runtime and standard library, compiled into the helper | BSD-3-Clause | go-LICENSE.txt |

HEVC is covered by patents held by several patent pools and by companies outside them.
These licences cover copyright only. They give no rights under those patents.
