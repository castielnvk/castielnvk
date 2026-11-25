import numpy as np, cv2, subprocess, sys
src, out, mpath, dpath = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
DD = np.load(dpath).astype(np.float32)
m = np.load(mpath); mb = m > 0
ring = (cv2.dilate(mb.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0) & ~mb
X0, Y0, PW, PH = 1034, 132, 800, 758
W, H = 1920, 1080
rd = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-vf', 'fps=30', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE, bufsize=10**8)
wr = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30', '-i', '-', '-i', src,
                       '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p',
                       '-c:a', 'pcm_s16le', '-ar', '48000', '-shortest', out], stdin=subprocess.PIPE)
n = W*H*3; i = 0; done = 0
while True:
    b = rd.stdout.read(n)
    if len(b) < n: break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    p = f[Y0:Y0+PH, X0:X0+PW]
    g = cv2.cvtColor(p, cv2.COLOR_BGR2GRAY).astype(np.float32)
    hp = g-cv2.GaussianBlur(g, (0, 0), 5)
    if hp[mb].mean()-hp[ring].mean() > 4:
        f[Y0:Y0+PH, X0:X0+PW] = np.clip(p.astype(np.float32)-DD, 0, 255).astype(np.uint8); done += 1
    wr.stdin.write(f.tobytes()); i += 1
wr.stdin.close(); wr.wait()
print('frames', i, 'cleaned', done)
