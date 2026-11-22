#!/usr/bin/env bash
# Renders only the frames where the 3D scene moves (pour, lift). Held stretches reuse
# the last rendered frame in compositing, and the camera push is applied in 2D there.
# Usage: tools/render_bg.sh [res=0.6667] [samples=16]
set -euo pipefail
cd "$(dirname "$0")/.."
BLENDER=${BLENDER:-/opt/blender/blender-4.5.3-linux-x64/blender}
RES=${1:-0.6667}; SAMPLES=${2:-16}
read -r A0 A1 B0 B1 < <(python3 -c "
import json; e=json.load(open('episode.json')); s=e['scene']; F=lambda t: round(t*e['fps'])+1
print(1, F(s['teapot_exit'])+2, F(s['hand_enter'])-2, F(s['lift_stop'])+4)")
echo "$A0 $A1 $B0 $B1" > build/bg_ranges.txt
for r in "$A0 $A1" "$B0 $B1"; do
  set -- $r
  "$BLENDER" -b --factory-startup -P scene/build_scene.py -- --render --res "$RES" --samples "$SAMPLES" \
    --start "$1" --end "$2" --out build/bg 2>&1 | grep -E "^Saved|Error|Traceback" || true
done
echo "bg done"
