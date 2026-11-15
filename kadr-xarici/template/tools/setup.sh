#!/bin/bash
# One-time setup in a fresh cloud container (run from the episode folder). Downloads only libraries/fonts.
pip install -q faster-whisper opencv-python-headless==4.10.0.84 scipy fonttools
mkdir -p fonts && cd fonts && npm pack @expo-google-fonts/playfair-display --silent && tar xzf expo-google-fonts-playfair-display-*.tgz && cd ..
ls /usr/share/fonts/opentype/inter/Inter-SemiBold.otf || echo "Inter missing: npm pack @fontsource/inter and point F_INT* in render.py to it"
