#!/bin/bash
# Contact sheets of every source clip (1 frame/s, 8 across) -> cs/cNN.jpg. Run from the episode folder.
mkdir -p cs
for f in src/c*.*; do n=$(basename "${f%.*}")
  ffmpeg -v error -y -i "$f" -map 0:v:0 -vf "fps=1,scale=240:426:force_original_aspect_ratio=decrease,pad=240:426:(ow-iw)/2:(oh-ih)/2,tile=8x1" -frames:v 1 cs/$n.jpg
  echo "$n $(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate:format=duration -of csv=p=0 "$f" | tr '\n' ' ')"
done
