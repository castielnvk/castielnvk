"""Soft bottom gradient (for subtitle legibility) as an RGBA PNG."""
import numpy as np, sys
from PIL import Image
H, W = 1920, 1080
y = np.arange(H) / H
a = np.clip((y - 0.52) / 0.48, 0, 1) ** 1.6 * 0.58          # 0 above 52% height, up to ~58% at the bottom
img = np.zeros((H, W, 4), np.uint8); img[..., 3] = (a * 255).astype(np.uint8)[:, None]
img[..., :3] = np.array([8, 10, 14], np.uint8)
Image.fromarray(img, 'RGBA').save(sys.argv[1])
