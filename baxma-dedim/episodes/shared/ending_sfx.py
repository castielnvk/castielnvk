"""The standard BAXMA DEDİM. ending sound (from EP02, approved by the user; do not change).

Pairs with compose.LogoFlashEnding: a reverse swell into a 3-frame flash with a sharp hit,
total silence while it's black, then a low hit and a dark drone tail when the logo returns,
fading out with the logo.
"""
import os

import numpy as np

import compose as C
import sfx

SR = sfx.SR
LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx_library")


def _db(x):
    return 10 ** (x / 20)


def _env(points, n):
    t = np.arange(n) / SR
    ts, gs = zip(*points)
    return np.interp(t, ts, gs)[:, None].astype(np.float32)


def _placed(clip, at, gain_db, n):
    out = np.zeros((n, 2), np.float32)
    i = int(round(at * SR))
    j = min(n, i + len(clip))
    if j > i:
        out[i:j] = clip[: j - i] * _db(gain_db)
    return out


def _chop(x, at, fade=0.008):
    i, k = int(at * SR), int(fade * SR)
    x[i:i + k] *= np.linspace(1, 0, k)[:, None][: len(x[i:i + k])]
    x[i + k:] = 0
    return x


def build(end_in, dur):
    """Return the ending stems (full-length arrays, dur seconds) for an ending starting at end_in."""
    n = int(dur * SR)
    F = C.FLASH
    fl_on, fl_off, ret = end_in + F["FLASH_ON"], end_in + F["FLASH_OFF"], end_in + F["RETURN_AT"]
    im = sfx.load_file(os.path.join(LIB, "deep_impact_mixkit1687.mp3"))
    dr = sfx.load_file(os.path.join(LIB, "horror_drone_mixkit1775.mp3"))
    lg = sfx.load_file(os.path.join(LIB, "logo_hit_mixkit833.mp3"))

    suck = im[: int(1.1 * SR)][::-1] * _db(_env([(0, -40), (0.9, -6), (1.1, 0)], int(1.1 * SR)))
    swell = _placed(suck, end_in - 1.1, -11, n)
    flash_hit = _chop(_placed(im, fl_on, -1, n) + _placed(sfx.dry_tick(), fl_on, -4, n), fl_off + 0.01)
    src = dr[int(0.5 * SR):int(0.5 * SR) + int((dur - ret) * SR)]
    return_hit = _placed(lg, ret, -2, n) + _placed(im, ret, -6, n)
    return_drone = _placed(src * _db(_env([(0, -8), (dur - ret - 1.6, -12), (dur - ret - 0.15, -50),
                                          (dur - ret, -90)], len(src))), ret, -4, n)
    for x in (return_hit, return_drone):
        x[-int(1.2 * SR):] *= np.linspace(1, 0, int(1.2 * SR))[:, None] ** 2
    return dict(logo_reverse_swell=swell, logo_flash_hit=flash_hit, logo_return_hit=return_hit,
                logo_return_drone=return_drone)
