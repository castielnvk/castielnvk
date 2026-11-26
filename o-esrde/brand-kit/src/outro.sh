#!/bin/bash
# Encodes the rendered outro frames + sound into the final MP4 (H.264 + AAC).
set -e; cd "$(dirname "$0")"; python3 audio.py
ffmpeg -y -loglevel error -framerate 30 -i _frames/outro_%04d.png -i _outro.wav \
  -c:v libx264 -pix_fmt yuv420p -crf 16 -preset slow -c:a aac -b:a 192k -shortest -movflags +faststart \
  ../video/O_Esrde_outro_1080x1920.mp4
cp _frames/outro_0164.png ../png/outro-last-frame.png
