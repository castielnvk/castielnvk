#!/bin/bash
# Usage: mix.sh <dir with video.mp4 music.wav sfx.wav> <final.mp4>
set -e
D=$1; OUTF=$2
ffmpeg -v error -y -i $D/music.wav -i $D/sfx.wav -filter_complex \
 "[1:a]volume=3dB[s];[0:a][s]amix=inputs=2:normalize=0,highpass=f=30,alimiter=limit=0.8:level=0[m]" -map "[m]" $D/premix.wav
J=$(ffmpeg -i $D/premix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/{/,/}/p')
gv(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i $D/premix.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(gv input_i):measured_TP=$(gv input_tp):measured_LRA=$(gv input_lra):measured_thresh=$(gv input_thresh):offset=$(gv target_offset):linear=true,aresample=48000" $D/mix.wav
ffmpeg -v error -y -i $D/video.mp4 -i $D/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart $OUTF
