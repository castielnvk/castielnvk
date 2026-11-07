"""Tiled Real-ESRGAN General x4v3 (ONNX, fixed 128x128 tiles) super-resolution, CPU.
Model: Qualcomm AI Hub export of Real-ESRGAN-General-x4v3 (BSD-3 licensed upstream)."""
import numpy as np, onnxruntime as ort

class SR:
    T, OV = 128, 12          # tile size, overlap (input px)
    def __init__(self, path, threads=4):
        o = ort.SessionOptions(); o.intra_op_num_threads = threads
        o.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.s = ort.InferenceSession(path, o, providers=['CPUExecutionProvider'])
        self.inp = self.s.get_inputs()[0].name
    def __call__(self, img):
        """img: HxWx3 uint8 RGB -> (4H)x(4W)x3 float32 0..255"""
        T, OV = self.T, self.OV
        h, w = img.shape[:2]
        step = T - 2 * OV
        ny = max(1, int(np.ceil((h - 2 * OV) / step))); nx = max(1, int(np.ceil((w - 2 * OV) / step)))
        ph, pw = ny * step + 2 * OV, nx * step + 2 * OV
        x = np.pad(img, ((0, ph - h), (0, pw - w), (0, 0)), mode='reflect').astype(np.float32) / 255.0
        out = np.zeros((ph * 4, pw * 4, 3), np.float32)
        for j in range(ny):
            for i in range(nx):
                y0, x0 = j * step, i * step
                tile = x[y0:y0 + T, x0:x0 + T].transpose(2, 0, 1)[None]
                r = self.s.run(None, {self.inp: tile})[0][0].transpose(1, 2, 0)
                # keep the centre (drop the overlap margins, except at outer edges)
                t0 = 0 if j == 0 else OV * 4; l0 = 0 if i == 0 else OV * 4
                b1 = T * 4 if j == ny - 1 else (T - OV) * 4; r1 = T * 4 if i == nx - 1 else (T - OV) * 4
                out[(y0 * 4 + t0):(y0 * 4 + b1), (x0 * 4 + l0):(x0 * 4 + r1)] = r[t0:b1, l0:r1]
        return np.clip(out[:h * 4, :w * 4] * 255.0, 0, 255)
