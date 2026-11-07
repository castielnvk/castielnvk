#!/usr/bin/env bash
# Final master: graded picture + legibility gradient + captions + mix -> 1080x1920 H.264/AAC MP4.
# Usage: finalize.sh PICTURE.mp4 GRADIENT.png CAPTIONS.ass MIX.wav OUT.mp4
set -euo pipefail
pic=$1; grad=$2; ass=$3; mix=$4; out=$5
ffmpeg -v error -stats -y -i "$pic" -loop 1 -i "$grad" -i "$mix" \
  -filter_complex "[0:v][1:v]overlay=shortest=1:format=auto,ass='${ass}',format=yuv420p,setsar=1[v]" \
  -map "[v]" -map 2:a \
  -c:v libx264 -preset slow -crf 18 -maxrate 10M -bufsize 20M -profile:v high -level 4.2 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart -shortest \
  -metadata title="Zəfər Günü — Qəbul Vaxtı" "$out"
