#!/usr/bin/env bash
# Full rebuild of Düymə olsa Ep01: textures → 3D plates (Blender/Cycles) → UI composite → MP4.
set -euo pipefail
cd "$(dirname "$0")"
python3 tools/make_textures.py
tools/render_bg.sh "${1:-0.6667}" "${2:-16}"
node tools/compose.js
