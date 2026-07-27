"""
Copyright 2023, CCL Forensics

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os
import pathlib
from . import ccl_segb1
from . import ccl_segb2


def read_segb_file(file_path: pathlib.Path | os.PathLike | str):
    if ccl_segb1.file_matches_segbv1_signature(file_path):
        return ccl_segb1.read_segb1_file(file_path)
    elif ccl_segb2.file_matches_segbv2_signature(file_path):
        return ccl_segb2.read_segb2_file(file_path)
    else:
        raise ValueError("File is not a SEGB File", file_path)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print(f"USAGE: {pathlib.Path(sys.argv[0]).name} <SEGB file>")
        print()
        exit(1)

    if ccl_segb1.file_matches_segbv1_signature(sys.argv[1]):
        print("Processing SEGB1 File")
        ccl_segb1.run_command(sys.argv[1])
    elif ccl_segb2.file_matches_segbv2_signature(sys.argv[1]):
        print("Processing SEGB2 File")
        ccl_segb2.run_command(sys.argv[1])
    else:
        print(f"File is not a SEGB File")
        exit(1)
    print()
