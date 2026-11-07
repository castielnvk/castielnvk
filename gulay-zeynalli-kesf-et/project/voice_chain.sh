#!/bin/bash
# Voice repair chain used for the final mix. Input: original MOV. Output: voice_proc.wav (48 kHz mono float)
set -e
SRC=${1:-IMG_7215.MOV}
ffmpeg -y -i "$SRC" -map 0:a -af "pan=mono|c0=0.5*c0+0.5*c1,highpass=f=70:poles=2,bandreject=f=50:width_type=h:w=4,bandreject=f=100:width_type=h:w=5,volume=14dB" -ar 48000 -f f32le pre.f32
(cd tools/dfcli && cargo build --release)
tools/dfcli/target/release/dfcli pre.f32 df24.f32 24        # DeepFilterNet3, 24 dB attenuation cap
ffmpeg -y -f f32le -ar 48000 -ac 1 -i df24.f32 -af "highpass=f=85:poles=2,equalizer=f=220:t=q:w=1.0:g=-2.5,equalizer=f=450:t=q:w=1.5:g=-1,equalizer=f=3000:t=q:w=1.0:g=3.5,equalizer=f=6500:t=q:w=1.0:g=2,deesser=i=0.3:m=0.5:f=0.5,acompressor=threshold=-26dB:ratio=2.5:attack=10:release=160:knee=6:makeup=1,acompressor=threshold=-14dB:ratio=4:attack=3:release=60:knee=3" -c:a pcm_f32le voice_proc.wav
