"""Génère la texture « Sakura » (vue de côté de l'arme) avec PIL.

La texture est dessinée dans les coordonnées monde de l'arme (X, Z) :
on fournit une fonction w2p(x, z) -> (px, py) qui convertit des mètres
en pixels. Les zones (crosse, carcasse, chargeur...) sont données en
mètres par le script de build.
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WHITE = (250, 247, 250)
PETAL = (250, 196, 222)
PETAL_DEEP = (238, 128, 178)
OUTLINE = (96, 18, 62)
CLOUD = (236, 84, 150)
CLOUD_LIGHT = (246, 165, 205)
HAZE = (206, 196, 236)
BARK = (92, 44, 26)
BARK_HI = (206, 118, 42)


def _petal(cx, cy, ang, length, width):
    """Pétale de cerisier avec l'encoche au bout."""
    pts_l, pts_r = [], []
    n = 14
    for i in range(n + 1):
        t = i / n
        x = length * t
        w = width * math.sin(math.pi * 0.78 * t) ** 0.75
        pts_l.append((x, w))
        pts_r.append((x, -w))
    tip = [(length * 1.02, width * 0.45), (length * 0.86, 0.0), (length * 1.02, -width * 0.45)]
    pts = pts_l + tip + pts_r[::-1]
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]


def flower(radius, rng, petal=PETAL, deep=PETAL_DEEP, outline=OUTLINE):
    """Renvoie une fleur RGBA (sur-échantillonnée x4 puis réduite)."""
    ss = 4
    R = radius * ss
    size = int(R * 2.3)
    c = size / 2
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rot = rng.uniform(0, math.tau)
    lw = max(2, int(R / 20))
    for k in range(5):
        a = rot + k * math.tau / 5
        poly = _petal(c, c, a, R, R * 0.47)
        d.polygon(poly, fill=petal + (255,))
        d.line(poly + [poly[0]], fill=outline + (255,), width=lw, joint="curve")

    # cœur plus foncé, limité à la fleur
    glow = Image.new("L", (size, size), 0)
    ImageDraw.Draw(glow).ellipse([c - R * 0.5, c - R * 0.5, c + R * 0.5, c + R * 0.5], fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(R * 0.18))
    alpha = img.getchannel("A")
    glow = Image.fromarray((np.asarray(glow, np.float32) * np.asarray(alpha, np.float32) / 255 * 0.85).astype(np.uint8))
    deep_layer = Image.new("RGBA", (size, size), deep + (255,))
    deep_layer.putalpha(glow)
    img = Image.alpha_composite(img, deep_layer)
    d = ImageDraw.Draw(img)

    # étamines
    for k in range(9):
        a = rot + k * math.tau / 9 + rng.uniform(-0.15, 0.15)
        r = R * rng.uniform(0.3, 0.42)
        x, y = c + r * math.cos(a), c + r * math.sin(a)
        d.line([(c, c), (x, y)], fill=outline + (255,), width=max(1, lw // 2))
        dot = R * 0.035
        d.ellipse([x - dot, y - dot, x + dot, y + dot], fill=outline + (255,))
    cr = R * 0.07
    d.ellipse([c - cr, c - cr, c + cr, c + cr], fill=(200, 60, 120, 255))
    return img.resize((size // ss, size // ss), Image.LANCZOS)


def _noise(w, h, rng, octaves=4):
    """Bruit fractal simple dans [0, 1]."""
    out = np.zeros((h, w), np.float32)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        gw = 4 * 2 ** o
        gh = max(2, int(gw * h / w))
        small = (rng.random((gh, gw)) * 255).astype(np.uint8)
        out += np.asarray(Image.fromarray(small).resize((w, h), Image.BICUBIC), np.float32) / 255 * amp
        total += amp
        amp *= 0.5
    return out / total


def _cloud_mask(w, h, blobs, rng, blur):
    """Masque de nuages à l'aquarelle (en basse résolution)."""
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    for x, y, r in blobs:
        for _ in range(6):
            ox, oy = rng.normal(0, r * 0.5, 2)
            rr = r * rng.uniform(0.4, 0.9)
            d.ellipse([x + ox - rr, y + oy - rr * 0.7, x + ox + rr, y + oy + rr * 0.7], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(m, np.float32) / 255
    n = _noise(w, h, rng)
    a = np.clip((a * (0.55 + 0.9 * n) - 0.25) * 1.9, 0, 1)
    return a


def _composite(base, color, alpha):
    a = alpha[..., None]
    return base * (1 - a) + np.array(color, np.float32) * a


def branch(draw, pts, width, rng):
    """Branche brune avec reflets orangés, comme sur la référence."""
    for i in range(len(pts) - 1):
        w = max(2, int(width * (1 - 0.6 * i / len(pts))))
        draw.line([pts[i], pts[i + 1]], fill=BARK + (255,), width=w)
        draw.ellipse([pts[i + 1][0] - w / 2, pts[i + 1][1] - w / 2, pts[i + 1][0] + w / 2, pts[i + 1][1] + w / 2], fill=BARK + (255,))
        # reflets
        for _ in range(int(w * 1.5)):
            t = rng.random()
            x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t + rng.gauss(0, w * 0.22)
            y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t + rng.gauss(0, w * 0.22)
            r = rng.uniform(1, w * 0.12)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=BARK_HI + (255,))


def wiggle(p0, p1, n, amp, rng):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = p0[0] + (p1[0] - p0[0]) * t
        y = p0[1] + (p1[1] - p0[1]) * t + (math.sin(t * 7.3 + rng.uniform(0, 1)) * amp if 0 < i < n else 0)
        pts.append((x, y))
    return pts


def generate(width, height, w2p, px_per_m, zones, seed=7, scale=1.0):
    """
    zones : dict de rectangles monde (xmin, zmin, xmax, zmax) :
      stock, receiver, grip, mag, handguard, branch (p0, p1)
    """
    rng = random.Random(seed)
    nrng = np.random.default_rng(seed)
    S = lambda m: m * px_per_m * scale  # mètres -> pixels

    def rect_pt(r):
        x0, z0, x1, z1 = r
        return w2p(rng.uniform(x0, x1), rng.uniform(z0, z1))

    # 1) fond blanc + nuages roses (calculés en 1/4 de résolution)
    q = 4
    lw, lh = width // q, height // q
    base = np.full((lh, lw, 3), WHITE, np.float32)

    def blobs(zone, count, r_m):
        out = []
        for _ in range(count):
            x, y = rect_pt(zone)
            out.append((x / q, y / q, S(r_m) / q * rng.uniform(0.7, 1.3)))
        return out

    haze_blobs = blobs(zones["stock"], 6, 0.05) + blobs(zones["receiver"], 6, 0.04) + blobs(zones["handguard"], 4, 0.03)
    base = _composite(base, HAZE, _cloud_mask(lw, lh, haze_blobs, nrng, S(0.02) / q) * 0.55)
    light = blobs(zones["stock"], 8, 0.04) + blobs(zones["receiver"], 8, 0.03) + blobs(zones["grip"], 3, 0.02) \
        + blobs(zones["mag"], 5, 0.025) + blobs(zones["handguard"], 6, 0.025)
    base = _composite(base, CLOUD_LIGHT, _cloud_mask(lw, lh, light, nrng, S(0.012) / q) * 0.8)
    strong = blobs(zones["stock"], 6, 0.03) + blobs(zones["receiver"], 6, 0.022) + blobs(zones["mag"], 4, 0.02) \
        + blobs(zones["handguard"], 5, 0.02) + blobs(zones["grip"], 2, 0.015)
    base = _composite(base, CLOUD, _cloud_mask(lw, lh, strong, nrng, S(0.008) / q) * 0.9)
    img = Image.fromarray(base.clip(0, 255).astype(np.uint8)).resize((width, height), Image.BICUBIC).convert("RGBA")

    # 2) branches
    draw = ImageDraw.Draw(img)
    p0, p1 = zones["branch"]
    main = wiggle(w2p(*p0), w2p(*p1), 10, S(0.012), rng)
    branch(draw, main, int(S(0.016)), rng)
    for i in (3, 5, 7):
        a = main[i]
        tip = (a[0] + S(rng.uniform(0.05, 0.09)), a[1] + S(rng.choice([-1, 1]) * rng.uniform(0.025, 0.04)))
        branch(draw, wiggle(a, tip, 4, S(0.004), rng), int(S(0.007)), rng)

    def place(cx, cy, r_px):
        f = flower(r_px, rng)
        img.alpha_composite(f, (int(cx - f.width / 2), int(cy - f.height / 2)))

    # 3) fleurs : petites d'abord, grandes par-dessus
    plan = []
    for x, y in main[1:]:
        for _ in range(2):
            plan.append((x + S(rng.uniform(-0.02, 0.02)), y + S(rng.uniform(-0.025, 0.025)), S(rng.uniform(0.010, 0.018))))
    for zone, n, rmin, rmax in (
        ("stock", 9, 0.018, 0.034),
        ("receiver", 6, 0.010, 0.016),
        ("handguard", 10, 0.009, 0.016),
        ("grip", 7, 0.008, 0.013),
        ("mag", 10, 0.009, 0.016),
    ):
        for _ in range(n):
            x, y = rect_pt(zones[zone])
            plan.append((x, y, S(rng.uniform(rmin, rmax))))
    # gros bouquet sur la crosse (comme la référence)
    for _ in range(7):
        x, y = rect_pt(zones["bouquet"])
        plan.append((x, y, S(rng.uniform(0.026, 0.036))))
    plan.sort(key=lambda p: p[2])
    for x, y, r in plan:
        place(x, y, r)
    return img.convert("RGB")
