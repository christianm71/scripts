#!/usr/bin/python3

import os
import re
import sys

pct = 25
bit_rate = 1000000

for file in sys.argv[1:]:
    file_new = None

    if re.search(r"\.(jpe?g)$", file, flags=re.I):
        file_new = re.sub(r"\.(\w+)$", r".%d.\1" % pct, file)
        print(f"convert {file} -quality {pct}% {file_new}", end="")
    elif re.search(r"\.(mp4|mov|avi)$", file, flags=re.I):
        file_new = re.sub(r"\.(\w+)$", r".%d.\1" % bit_rate, file)
        print(f"ffmpeg -i {file} -b {bit_rate} {file_new}", end="")

    if file_new:
        print(f"; touch -r {file} {file_new}; ls -l {file} {file_new}")
    else:
        print(f"# skip file {file}")

