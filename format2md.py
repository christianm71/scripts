#!/usr/bin/python3

import re
import sys

file = sys.argv[1]

f = open(file)
buffer = f.read().strip()
f.close()

# replace $3 by S3
buffer = re.sub(r"([ ,\.])\$3([ ,\.])", r"\1S3\2", buffer)

n = 0

print()
for line in buffer.strip().split("\n"):
    columns = [re.sub(r"\"", r"", x.strip()) for x in line.split(",")]

    if n == 0:
        columns = [f"**{x}**" for x in columns]
    else:
        columns[0] = f"**{columns[0]}**"

    print(f"| {' | '.join(columns)} |")

    if n == 0:
        line = "----," * line.count(",") + "----"
        x = re.sub(r',', r' | ', line)
        print(f"| {x} |")

    n += 1
print()

for line in buffer.strip().split("\n"):
    if re.match(r"##\s", line):
        title = re.sub(r"^##\s+", r"", line)
        ref = re.sub(r"[\s]+", r"-", title)
        ref = re.sub(r"[\?\.\`\*\(\)<=>/]+", r"", ref)
        print(f"- [{title}](#{ref})")
print()

