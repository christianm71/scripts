#!/home/chris/venv/bin/python3

import os
import re
import sys

from pytubefix import YouTube
from pytubefix.cli import on_progress

if len(sys.argv) < 2:
    print("No urls !")
    sys.exit(1)

url = sys.argv[1]

yt = YouTube(url, on_progress_callback=on_progress)
name = re.sub(r"\W", r"_", yt.title)
name = re.sub(r"\s", r"_", name)
name = re.sub(r"_{2,}", r"_", name)
name = re.sub(r"^_", r"", name)
name = re.sub(r"_$", r"", name)

video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()

video_file = f"video_{name}.mp4"
audio_file = f"audio_{name}.mp4"
final_file = f"{name}.mp4"

video_stream.download(filename=video_file)
audio_stream.download(filename=audio_file)

cmd = f"ffmpeg -i {video_file} -i {audio_file} -c copy {final_file}"
os.system(cmd)
os.system(f"rm {video_file} {audio_file}")
print("\n" + final_file + "\n")

