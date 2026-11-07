"""Illustrative (clearly non-documentary) Azerbaijani-flag scenes, rendered procedurally.
Flag geometry follows the official construction (1:2, three equal bands, white crescent and
eight-pointed star centred in the red band). Colours: blue #00B5E2, red #EF3340, green #509E2F."""
import numpy as np, cv2, subprocess, sys
from PIL import Image, ImageDraw
W, H, FPS = 1080, 1920, 30
BLUE, RED, GREEN, WHITE = (0x00,0xB5,0xE2), (0xEF,0x33,0x40), (0x50,0x9E,0x2F), (255,255,255)

def flag_texture(scale=4):   # 1200x600 SVG units * scale
    w, h = 1200*scale, 600*scale
    im = Image.new('RGB', (w, h)); d = ImageDraw.Draw(im)
    d.rectangle([0,0,w,h/3], fill=BLUE); d.rectangle([0,h/3,w,2*h/3], fill=RED); d.rectangle([0,2*h/3,w,h], fill=GREEN)
    s = scale
    d.ellipse([(570-90)*s,(300-90)*s,(570+90)*s,(300+90)*s], fill=WHITE)
    d.ellipse([(590-75)*s,(300-75)*s,(590+75)*s,(300+75)*s], fill=RED)
    star = [(640,250),(649.567,276.903),(675.355,264.645),(663.097,290.433),(690,300),(663.097,309.567),
            (675.355,335.355),(649.567,323.097),(640,350),(630.433,323.097),(604.645,335.355),(616.903,309.567),
            (590,300),(616.903,290.433),(604.645,264.645),(630.433,276.903)]
    d.polygon([(x*s, y*s) for x, y in star], fill=WHITE)
    tex = np.asarray(im).astype(np.float32) / 255.0
    return cv2.GaussianBlur(tex, (0,0), 0.6*scale/2)   # anti-alias edges, slight fabric softness

def srgb_to_lin(c): return np.where(c <= 0.04045, c/12.92, ((c+0.055)/1.055)**2.4)
def lin_to_srgb(c): c = np.clip(c,0,1); return np.where(c <= 0.0031308, c*12.92, 1.055*c**(1/2.4)-0.055)

TEX = flag_texture(4); TH, TW = TEX.shape[:2]
TEXL = srgb_to_lin(TEX).astype(np.float32)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(7)

def grain(img, amt=0.012):
    return img + rng.normal(0, amt, img.shape[:2]).astype(np.float32)[..., None]

def wave_field(u, v, t, amp, speed):
    # travelling folds; u,v in flag units (0..1200, 0..600)
    ph1 = 0.0105*u - 0.0035*v - speed*1.9*t
    ph2 = 0.0062*u + 0.0051*v - speed*1.3*t + 1.7
    ph3 = 0.0170*u - 0.0011*v - speed*2.7*t + 0.6
    d = amp*(np.sin(ph1) + 0.6*np.sin(ph2) + 0.22*np.sin(ph3))
    du = amp*(0.0105*np.cos(ph1) + 0.6*0.0062*np.cos(ph2) + 0.22*0.0170*np.cos(ph3))
    dv = amp*(-0.0035*np.cos(ph1) + 0.6*0.0051*np.cos(ph2) - 0.22*0.0011*np.cos(ph3))
    return d, du, dv

def sample(u, v):
    mx = (u * TW / 1200.0).astype(np.float32); my = (v * TH / 600.0).astype(np.float32)
    return cv2.remap(TEXL, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def fullframe_flag(t, dur, cx, cy, flag_h_frac, rot_deg, push, amp, speed, sweep_dir=1, darken=0.0):
    """Frame filled by waving fabric. (cx,cy): flag-unit point at frame centre."""
    z = 1.0 + push * (t/dur)                         # slow push-in
    units_per_px = 600.0 / (H * flag_h_frac) / z
    a = np.deg2rad(rot_deg)
    X = (xx - W/2) * units_per_px; Y = (yy - H/2) * units_per_px
    u = cx + X*np.cos(a) - Y*np.sin(a); v = cy + X*np.sin(a) + Y*np.cos(a)
    d, du, dv = wave_field(u, v, t, amp, speed)
    col = sample(u + 0.35*d, v + 0.9*d)              # fabric displacement
    shade = 1.0 + 9.0*(du*0.8 - dv*0.6)              # folds catch the light
    shade = np.clip(shade, 0.62, 1.22)[..., None]
    sheen = np.clip(9.0*(du*0.8 - dv*0.6) - 0.08, 0, 1)[..., None] ** 2 * 0.35
    img = col * shade + sheen * 0.25
    # warm luminous sweep (dawn light passing over the fabric)
    s = (xx*0.55 + yy*0.35)/H - (sweep_dir*(t/dur)*1.2 - 0.2)
    sweep = np.exp(-(s**2)/0.02)[..., None]
    img = img * (1 + 0.28*sweep*np.array([1.0, 0.93, 0.80], np.float32))
    # vignette
    r = np.sqrt(((xx-W/2)/(W*0.75))**2 + ((yy-H/2)/(H*0.62))**2)
    img = img * (1 - 0.42*np.clip(r-0.35, 0, 1)[..., None]**1.5) * (1 - darken)
    return img

def sky_scene(t, dur):
    """Illustrative dawn: graded sky, low hills, flag on a pole waving in the wind."""
    z = 1.0 + 0.04*(t/dur)
    X = (xx - W/2)/z + W/2; Y = (yy - H*0.45)/z + H*0.45
    hy = 1330.0
    g = np.clip(Y/hy, 0, 1)[..., None]
    top = srgb_to_lin(np.array([0.10,0.15,0.30],np.float32)); mid = srgb_to_lin(np.array([0.42,0.47,0.64],np.float32))
    hor = srgb_to_lin(np.array([0.98,0.80,0.62],np.float32))
    sky = np.where(g < 0.6, top + (mid-top)*(g/0.6), mid + (hor-mid)*np.clip((g-0.6)/0.4,0,1)**1.3)
    sun = np.exp(-(((X-720)/260)**2 + ((Y-(hy-40+30*(1-t/dur)))/170)**2))[..., None]
    sky = sky + sun*srgb_to_lin(np.array([1.0,0.86,0.66],np.float32))*0.9
    # thin clouds
    cl = (np.sin(X*0.004 + Y*0.0006 + 0.15*t) * np.sin(Y*0.021 + 0.7) * 0.5 + 0.5)
    cl = (cl * np.exp(-((Y-900)/260)**2))[..., None]
    sky = sky*(1 - 0.10*cl) + 0.10*cl*srgb_to_lin(np.array([1.0,0.82,0.74],np.float32))
    # hills silhouette
    ridge = hy + 40*np.sin(X*0.004+1.2) + 22*np.sin(X*0.011) + 10*np.sin(X*0.031+0.4)
    hill = (Y > ridge)[..., None].astype(np.float32)
    hill = cv2.GaussianBlur(hill, (0,0), 1.2)[..., None] if hill.ndim == 3 else hill
    hcol = srgb_to_lin(np.array([0.13,0.12,0.16],np.float32)) * (1 + 0.6*np.exp(-((X-720)/420)**2)[..., None]*np.exp(-((Y-ridge)/60)**2)[..., None])
    img = sky*(1-hill) + hcol*hill
    # pole
    px, ptop, pbot = 250.0, 470.0, 1500.0
    pole = np.clip(1 - np.abs(X - px)/5.0, 0, 1) * ((Y > ptop) & (Y < pbot))
    poleL = (0.55 + 0.35*np.clip((X-px+5)/10,0,1))
    img = img*(1-pole[...,None]) + (pole*poleL)[...,None]*srgb_to_lin(np.array([0.78,0.78,0.80],np.float32))
    knob = np.exp(-(((X-px)/9)**2 + ((Y-ptop+4)/9)**2))[..., None]
    img = img*(1-knob) + knob*0.75
    # flag
    L = 660.0; FH = L/2; top_y = ptop + 12
    u = (X - px) / L                                   # 0..1 along fly
    ph = 7.5*u - 4.2*t
    uc = np.clip(u, 0, 1.2)
    amp = 26.0*uc**0.9
    dy = amp*np.sin(ph) + 0.4*amp*np.sin(2.3*ph + 1.1)
    slope = (amp*7.5*np.cos(ph) + 0.4*amp*7.5*2.3*np.cos(2.3*ph+1.1))/L
    vv = (Y - top_y - dy - 18*uc**1.4) / FH              # slight droop
    uu = u * (1 + 0.05*np.sin(ph*0.5))
    inside = np.clip(np.minimum.reduce([uu*L, (1-uu)*L, vv*FH, (1-vv)*FH]) + 0.5, 0, 1)
    inside = np.where((uu >= -0.01) & (uu <= 1.01) & (vv >= -0.01) & (vv <= 1.01), inside, 0)[..., None]
    col = sample(np.clip(uu,0,1)*1200, np.clip(vv,0,1)*600)
    shade = np.clip(1.0 - 1.6*slope, 0.6, 1.25)[..., None]
    backlight = 1 + 0.35*np.exp(-(((X-720)/380)**2))[..., None]
    img = img*(1-inside) + inside*col*shade*backlight*0.92
    # floating dust in the light
    for k in range(40):
        px0 = (k*97.3 + 13*t*(1+k%3)) % W; py0 = (300 + (k*211.7) % 1100 - 9*t*(1+k%2))
        d2 = ((X-px0)/3.0)**2 + ((Y-py0)/3.0)**2
        img = img + (np.exp(-d2)*0.35*np.exp(-((px0-720)/500)**2))[..., None]
    r = np.sqrt(((xx-W/2)/(W*0.8))**2 + ((yy-H/2)/(H*0.65))**2)
    img = img * (1 - 0.40*np.clip(r-0.35,0,1)[...,None]**1.5)
    return img

def render(name, dur, fn, fade_in=0.0, fade_out=0.0):
    n = int(round(dur*FPS))
    p = subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
                          '-c:v','libx264','-preset','medium','-crf','12','-pix_fmt','yuv420p',
                          '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709', name], stdin=subprocess.PIPE)
    for i in range(n):
        t = i/FPS
        img = fn(t, dur)
        a = 1.0
        if fade_in and t < fade_in: a = t/fade_in
        if fade_out and t > dur-fade_out: a = max(0.0, (dur-t)/fade_out)
        out = lin_to_srgb(img*a)
        out = grain(out, 0.010)
        out = np.nan_to_num(out)
        p.stdin.write((np.clip(out,0,1)*255+0.5).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    od = sys.argv[1]; which = sys.argv[2:] or ['title','dawn','end']
    if 'title' in which:   # title break + first support scene (6.2 s)
        render(f'{od}/flag_title.mp4', 6.2, lambda t,d: fullframe_flag(t,d, cx=600, cy=318, flag_h_frac=1.18, rot_deg=-5,
               push=0.07, amp=7.5, speed=1.0, darken=0.0))
    if 'dawn' in which:
        render(f'{od}/flag_dawn.mp4', 4.6, sky_scene)
    if 'end' in which:     # end card (8.4 s)
        render(f'{od}/flag_end.mp4', 8.4, lambda t,d: fullframe_flag(t,d, cx=612, cy=290, flag_h_frac=1.05, rot_deg=3,
               push=0.05, amp=6.0, speed=0.7, sweep_dir=1, darken=0.12), fade_out=1.4)
