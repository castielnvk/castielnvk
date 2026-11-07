#!/usr/bin/env bash
# Final master: splice the rendered picture parts, burn captions, add the mix -> 1080x1920 H.264/AAC MP4.
# Usage: finalize.sh WORKDIR CAPTIONS.ass MIX.wav OUT.mp4
#   WORKDIR/picture_framed.mp4 supplies OT 0-44.4; WORKDIR/v2/p_44.mp4 (44.4-64), p_64.mp4 (64-82),
#   p_82.mp4 (82-100), p_100.mp4 (100-128.8). Each part starts exactly on its range start (30 fps grid).
set -euo pipefail
w=$1; ass=$2; mix=$3; out=$4
ffmpeg -v error -stats -y \
  -i "$w/picture_framed.mp4" -i "$w/v2/p_44.mp4" -i "$w/v2/p_64.mp4" -i "$w/v2/p_82.mp4" -i "$w/v2/p_100.mp4" -i "$mix" \
  -filter_complex "\
[0:v]trim=start_frame=0:end_frame=1332,setpts=PTS-STARTPTS[a];\
[1:v]trim=start_frame=0:end_frame=588,setpts=PTS-STARTPTS[b];\
[2:v]trim=start_frame=0:end_frame=540,setpts=PTS-STARTPTS[c];\
[3:v]trim=start_frame=0:end_frame=540,setpts=PTS-STARTPTS[d];\
[4:v]trim=start_frame=0:end_frame=864,setpts=PTS-STARTPTS[e];\
[a][b][c][d][e]concat=n=5:v=1:a=0,fps=30,ass='${ass}',format=yuv420p,setsar=1[v]" \
  -map "[v]" -map 5:a \
  -c:v libx264 -preset slow -crf 18 -maxrate 10M -bufsize 20M -profile:v high -level 4.2 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart -shortest \
  -metadata title="Zəfər Günü — Qəbul Vaxtı" "$out"
