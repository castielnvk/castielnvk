#!/bin/bash
# Mux + encode the delivery MP4 and run QC. Usage: tools/finalize.sh OUT.mp4 [maxrate, default 7800k]
# video.mp4 (from render.py) + mix.wav (from mix.py + master step below) must exist.
set -e
OUT=$1; MR=${2:-7800k}
[ -f mix.wav ] || ffmpeg -v error -y -i premix.wav -af "volume=3.5dB,alimiter=limit=0.84:attack=3:release=80:level=false" -ar 48000 mix.wav
ffmpeg -v error -y -i video.mp4 -i mix.wav -c:v libx264 -preset medium -crf 22 -maxrate $MR -bufsize 15M -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 224k -ar 48000 -movflags +faststart -shortest "$OUT"
ffprobe -v error -show_entries format=duration,size,bit_rate:stream=codec_name,width,height,r_frame_rate,channels -of compact "$OUT"
ffmpeg -v error -i "$OUT" -f null - && echo decode-ok
mkdir -p qc; D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")
ffmpeg -v error -y -i "$OUT" -vf "fps=36/$D,scale=180:-2,tile=12x3" -frames:v 1 qc/final.jpg
ffmpeg -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E " I:|Peak:" | tail -2
