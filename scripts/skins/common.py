"""Outils de dessin communs aux skins (texture « vue de côté » de l'arme).

Toutes les positions se donnent en studs du profil de design (voir vanta_ar01.py) :
x = 0 (crosse) -> 3,616 (bouche), z = 0 (bas du chargeur) -> 1,343 (haut du viseur).
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS = {
    "black": "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
    "bold": "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}

# Zones visibles du profil (studs) : (x0, z0, x1, z1)
ZONES = {
    "stock": (0.08, 0.54, 0.68, 1.00),
    "receiver": (1.06, 0.66, 2.00, 1.04),
    "handguard": (2.04, 0.74, 2.94, 1.04),
    "grip": (1.04, 0.22, 1.32, 0.62),
    "mag": (1.58, 0.14, 1.88, 0.56),
    "band": (0.0, 0.74, 3.0, 1.06),     # bande vue aussi sur le dessus/dessous
}
EMBLEM = (0.30, 0.82, 0.26)  # centre x, z et taille du triangle sur la crosse


def font(kind, size_px):
    return ImageFont.truetype(FONTS[kind], max(6, int(size_px)))


def rgba(c, a=255):
    return (int(c[0]), int(c[1]), int(c[2]), int(a))


class Ctx:
    """Toile de la texture + conversions studs -> pixels."""

    def __init__(self, W, H, w2p, ppm, design_to_world, stud_m, seed):
        self.W, self.H = W, H
        self._w2p, self._D = w2p, design_to_world
        self.ppm, self.stud_m = ppm, stud_m
        self.rng = random.Random(seed)
        self.nrng = np.random.default_rng(seed)
        self.img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        # flanc gauche de l'arme : la texture y est vue en miroir, on retourne donc
        # chaque texte sur lui-même pour qu'il reste lisible
        self.mirror_text = False
        # zones du profil, emblème et taille relative des motifs (fournis par l'arme)
        self.zones = dict(ZONES)
        self.emblem = EMBLEM
        self.flower_scale = 1.0
        self.label = "AR-01"

    # ---- conversions
    def P(self, x, z):
        return self._w2p(*self._D(x, z))

    def L(self, studs):
        return studs * self.stud_m * self.ppm

    def box(self, x0, z0, x1, z1):
        (a, b), (c, d) = self.P(x0, z1), self.P(x1, z0)
        return [a, b, c, d]

    # ---- placement relatif aux zones de l'arme
    @property
    def ds(self):
        """Échelle des détails (1 pour l'AR-01, plus petit pour les armes compactes)."""
        return self.flower_scale

    def at(self, zone, u, v):
        """Point à la fraction (u, v) de la zone (0,0 = bas gauche, 1,1 = haut droit)."""
        x0, z0, x1, z1 = self.zones[zone]
        return x0 + u * (x1 - x0), z0 + v * (z1 - z0)

    def zw(self, zone):
        x0, _, x1, _ = self.zones[zone]
        return x1 - x0

    def zh(self, zone):
        _, z0, _, z1 = self.zones[zone]
        return z1 - z0

    def extent(self, margin=0.08):
        """Rectangle qui englobe toutes les zones (studs)."""
        rects = [v for k, v in self.zones.items() if isinstance(v, tuple) and len(v) == 4 and k != "branch"]
        return (min(r[0] for r in rects) - margin, min(r[1] for r in rects) - margin,
                max(r[2] for r in rects) + margin, max(r[3] for r in rects) + margin)

    def rand_extent(self):
        x0, z0, x1, z1 = self.extent()
        return self.rng.uniform(x0, x1), self.rng.uniform(z0, z1)

    def emblem_in(self, zone):
        x, z, _ = self.emblem
        x0, z0, x1, z1 = self.zones[zone]
        return x0 <= x <= x1 and z0 <= z <= z1

    def rand_in(self, zone):
        x0, z0, x1, z1 = self.zones[zone] if isinstance(zone, str) else zone
        return self.rng.uniform(x0, x1), self.rng.uniform(z0, z1)

    # ---- calques
    def layer(self):
        return Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))

    def over(self, layer, opacity=1.0):
        if opacity < 1.0:
            a = layer.getchannel("A").point(lambda v: int(v * opacity))
            layer = layer.copy()
            layer.putalpha(a)
        self.img = Image.alpha_composite(self.img, layer)

    def glow(self, layer, radius_studs, strength=1.0, passes=2):
        """Halo lumineux autour d'un calque, puis le calque net par-dessus."""
        for i in range(passes):
            r = self.L(radius_studs) * (1 + i * 1.6)
            self.over(layer.filter(ImageFilter.GaussianBlur(r)), min(1.0, strength))
        self.over(layer)

    def add(self, layer, amount=1.0):
        """Mélange additif (lumière)."""
        base = np.asarray(self.img, np.float32)
        top = np.asarray(layer, np.float32)
        a = top[..., 3:4] / 255 * amount
        base[..., :3] = np.clip(base[..., :3] + top[..., :3] * a, 0, 255)
        self.img = Image.fromarray(base.astype(np.uint8), "RGBA")

    # ---- fonds
    def fill(self, color):
        self.img = Image.new("RGBA", (self.W, self.H), rgba(color))

    def vgradient(self, top, bottom, z_top=1.1, z_bottom=0.1):
        """Dégradé vertical entre deux hauteurs du profil."""
        y0, y1 = self.P(0, z_top)[1], self.P(0, z_bottom)[1]
        t = np.clip((np.arange(self.H, dtype=np.float32) - y0) / max(1, y1 - y0), 0, 1)[:, None, None]
        c = np.array(top, np.float32) * (1 - t) + np.array(bottom, np.float32) * t
        arr = np.repeat(c, self.W, axis=1)
        a = np.full((self.H, self.W, 1), 255, np.float32)
        self.img = Image.fromarray(np.concatenate([arr, a], axis=2).astype(np.uint8), "RGBA")

    def noise(self, cell_studs=0.25, octaves=4, seed_shift=0):
        """Bruit fractal [0,1] de la taille de la toile."""
        rng = np.random.default_rng(self.nrng.integers(1 << 30) + seed_shift)
        out = np.zeros((self.H, self.W), np.float32)
        amp, total = 1.0, 0.0
        cell = self.L(cell_studs)
        for _ in range(octaves):
            gw, gh = max(2, int(self.W / cell) + 2), max(2, int(self.H / cell) + 2)
            small = (rng.random((gh, gw)) * 255).astype(np.uint8)
            out += np.asarray(Image.fromarray(small).resize((self.W, self.H), Image.BICUBIC), np.float32) / 255 * amp
            total += amp
            amp *= 0.5
            cell /= 2
        return out / total

    def tint(self, color, mask, amount=1.0):
        """Peint une couleur selon un masque [0,1]."""
        base = np.asarray(self.img, np.float32)
        a = np.clip(mask, 0, 1)[..., None] * amount
        base[..., :3] = base[..., :3] * (1 - a) + np.array(color, np.float32) * a
        self.img = Image.fromarray(base.astype(np.uint8), "RGBA")

    def grain(self, amount=10, cell_studs=0.02):
        n = self.noise(cell_studs, 2) - 0.5
        base = np.asarray(self.img, np.float32)
        base[..., :3] = np.clip(base[..., :3] + n[..., None] * amount * 2, 0, 255)
        self.img = Image.fromarray(base.astype(np.uint8), "RGBA")

    def result(self):
        return self.img.convert("RGB")


# ------------------------------------------------------------------ formes
def triangle_emblem(ctx, color, outline=(10, 8, 12), inner=None, width=0.035, glow=None):
    """Triangle « V » de VANTA sur la crosse (comme sur les visuels)."""
    cx, cz, s = ctx.emblem
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    outer = [ctx.P(cx - s * 0.62, cz + s * 0.45), ctx.P(cx + s * 0.62, cz + s * 0.45), ctx.P(cx, cz - s * 0.62)]
    mid = [ctx.P(cx - s * 0.36, cz + s * 0.26), ctx.P(cx + s * 0.36, cz + s * 0.26), ctx.P(cx, cz - s * 0.33)]
    small = [ctx.P(cx - s * 0.17, cz + s * 0.13), ctx.P(cx + s * 0.17, cz + s * 0.13), ctx.P(cx, cz - s * 0.12)]
    w = int(ctx.L(width * ctx.ds))
    d.polygon(outer, fill=rgba(outline))
    d.polygon(_shrink(outer, w * 0.45), fill=rgba(color))
    d.polygon(mid, fill=rgba(outline))
    d.polygon(_shrink(mid, w * 0.45), fill=rgba(inner or (0, 0, 0, 0)) if inner else (0, 0, 0, 0))
    d.polygon(small, fill=rgba(color))
    if glow:
        ctx.glow(lay, glow, 0.9)
    else:
        ctx.over(lay)


def _shrink(poly, px):
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    out = []
    for x, y in poly:
        dx, dy = x - cx, y - cy
        l = math.hypot(dx, dy) or 1
        k = max(0.0, (l - px * 2) / l)
        out.append((cx + dx * k, cy + dy * k))
    return out


def text(ctx, s, x, z, size, fill, kind="black", stroke=None, stroke_w=0.0, angle=0.0,
         shadow=None, anchor="mm", layer=None, skew=0.0):
    """Texte centré en (x, z) studs, taille en studs, rotation en degrés."""
    f = font(kind, ctx.L(size))
    sw = int(ctx.L(stroke_w))
    bb = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), s, font=f, stroke_width=sw)
    w, h = bb[2] - bb[0] + sw * 4 + 8, bb[3] - bb[1] + sw * 4 + 8
    tile = Image.new("RGBA", (int(w * (1 + abs(skew))) + 10, int(h) + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    ox, oy = 5 + sw * 2 - bb[0] + (abs(skew) * h if skew < 0 else 0), 5 + sw * 2 - bb[1]
    if shadow:
        d.text((ox + sw * 0.8, oy + sw * 0.8), s, font=f, fill=rgba(shadow), stroke_width=sw, stroke_fill=rgba(shadow))
    d.text((ox, oy), s, font=f, fill=rgba(fill), stroke_width=sw, stroke_fill=rgba(stroke) if stroke else None)
    if skew:
        tile = tile.transform(tile.size, Image.AFFINE, (1, skew, -skew * tile.height if skew > 0 else 0, 0, 1, 0), Image.BICUBIC)
    if angle:
        tile = tile.rotate(angle, resample=Image.BICUBIC, expand=True)
    if ctx.mirror_text:
        tile = tile.transpose(Image.FLIP_LEFT_RIGHT)
    px, py = ctx.P(x, z)
    target = layer if layer is not None else ctx.layer()
    target.alpha_composite(tile, (int(px - tile.width / 2), int(py - tile.height / 2)))
    if layer is None:
        ctx.over(target)
    return tile.size


def star(ctx, d, x, z, r_out, r_in, color, points=5, rot=0.0, outline=None, width=0):
    cx, cy = ctx.P(x, z)
    ro, ri = ctx.L(r_out), ctx.L(r_in)
    pts = []
    for i in range(points * 2):
        a = rot + math.pi * i / points - math.pi / 2
        r = ro if i % 2 == 0 else ri
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=rgba(color) if color else None, outline=rgba(outline) if outline else None, width=width)


def crown(ctx, d, x, z, size, fill, outline=(10, 8, 12), width=0.012, jewel=None):
    """Couronne à trois pointes, centrée en (x, z)."""
    s = size
    pts = [(-0.5, -0.32), (-0.5, 0.18), (-0.28, -0.05), (0.0, 0.38), (0.28, -0.05), (0.5, 0.18), (0.5, -0.32)]
    poly = [ctx.P(x + a * s, z + b * s) for a, b in pts]
    d.polygon(poly, fill=rgba(fill), outline=rgba(outline), width=max(1, int(ctx.L(width))))
    band = [ctx.P(x - 0.5 * s, z - 0.2 * s), ctx.P(x + 0.5 * s, z - 0.32 * s)]
    d.rectangle([band[0][0], band[0][1], band[1][0], band[1][1]], outline=rgba(outline), width=max(1, int(ctx.L(width * 0.7))))
    for a, b in ((-0.5, 0.18), (0.0, 0.38), (0.5, 0.18)):
        cx, cy = ctx.P(x + a * s, z + b * s)
        r = ctx.L(s * 0.07)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgba(jewel or fill), outline=rgba(outline), width=max(1, int(ctx.L(width * 0.6))))


def drips(ctx, d, x0, x1, z_top, color, count, max_len, width, rng=None, highlight=None):
    """Coulures verticales (peinture, slime) qui partent d'une ligne."""
    rng = rng or ctx.rng
    for _ in range(count):
        x = rng.uniform(x0, x1)
        ln = rng.uniform(0.25, 1.0) * max_len
        w = ctx.L(width * rng.uniform(0.6, 1.3))
        (ax, ay), (bx, by) = ctx.P(x, z_top), ctx.P(x, z_top - ln)
        d.rounded_rectangle([ax - w / 2, ay, ax + w / 2, by], radius=w / 2, fill=rgba(color))
        d.ellipse([bx - w * 0.75, by - w * 0.9, bx + w * 0.75, by + w * 0.6], fill=rgba(color))
        if highlight:
            d.line([(ax - w * 0.2, ay + w), (bx - w * 0.2, by - w)], fill=rgba(highlight), width=max(1, int(w * 0.18)))


def splatter(ctx, d, x, z, radius, color, rng=None, dots=26):
    """Éclaboussure : tache centrale + gouttelettes."""
    rng = rng or ctx.rng
    cx, cy = ctx.P(x, z)
    r = ctx.L(radius)
    for _ in range(7):
        ox, oy = rng.gauss(0, r * 0.3), rng.gauss(0, r * 0.3)
        rr = r * rng.uniform(0.35, 0.7)
        d.ellipse([cx + ox - rr, cy + oy - rr, cx + ox + rr, cy + oy + rr], fill=rgba(color))
    for _ in range(dots):
        a = rng.uniform(0, math.tau)
        dist = r * rng.uniform(0.9, 2.2)
        rr = r * rng.uniform(0.03, 0.14)
        px, py = cx + math.cos(a) * dist, cy + math.sin(a) * dist
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=rgba(color))


def soft_blobs(ctx, blobs, color, blur_studs, amount=1.0, noise_mix=0.8, threshold=0.25):
    """Taches douces (nuages, peinture aérosol) en basse résolution."""
    q = 4
    w, h = ctx.W // q, ctx.H // q
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    for x, z, r in blobs:
        px, py = ctx.P(x, z)
        rr = ctx.L(r) / q
        for _ in range(5):
            ox, oy = ctx.rng.gauss(0, rr * 0.45), ctx.rng.gauss(0, rr * 0.45)
            k = ctx.rng.uniform(0.45, 0.95)
            d.ellipse([px / q + ox - rr * k, py / q + oy - rr * k * 0.75, px / q + ox + rr * k, py / q + oy + rr * k * 0.75], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(ctx.L(blur_studs) / q))
    a = np.asarray(m.resize((ctx.W, ctx.H), Image.BICUBIC), np.float32) / 255
    if noise_mix:
        n = ctx.noise(0.3, 4)
        a = np.clip((a * (1 - noise_mix * 0.5 + noise_mix * n) - threshold) * 1.9, 0, 1)
    ctx.tint(color, a, amount)
    return a


def sprite(ctx, d, rows, x, z, pixel, colors, shadow=None):
    """Dessine un sprite pixel-art (liste de chaînes) centré en (x, z)."""
    h, w = len(rows), max(len(r) for r in rows)
    p = ctx.L(pixel)
    cx, cy = ctx.P(x, z)
    ox, oy = cx - w * p / 2, cy - h * p / 2
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in colors:
                if shadow:
                    d.rectangle([ox + i * p + p * 0.25, oy + j * p + p * 0.25, ox + (i + 1) * p + p * 0.25, oy + (j + 1) * p + p * 0.25], fill=rgba(shadow))
                d.rectangle([ox + i * p, oy + j * p, ox + (i + 1) * p - 1, oy + (j + 1) * p - 1], fill=rgba(colors[ch]))


def pixel_text(ctx, s, x, z, pixel, color, shadow=None, kind="mono"):
    """Texte pixelisé (police rendue minuscule puis agrandie sans lissage)."""
    f = ImageFont.truetype(FONTS[kind], 10)
    bb = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), s, font=f)
    small = Image.new("L", (bb[2] - bb[0] + 2, bb[3] - bb[1] + 2), 0)
    ImageDraw.Draw(small).text((1 - bb[0], 1 - bb[1]), s, font=f, fill=255)
    small = small.point(lambda v: 255 if v > 110 else 0)
    p = max(1, int(ctx.L(pixel)))
    big = small.resize((small.width * p, small.height * p), Image.NEAREST)
    if ctx.mirror_text:
        big = big.transpose(Image.FLIP_LEFT_RIGHT)
    cx, cy = ctx.P(x, z)
    pos = (int(cx - big.width / 2), int(cy - big.height / 2))
    lay = ctx.layer()
    if shadow:
        sh = Image.new("RGBA", big.size, rgba(shadow))
        lay.paste(sh, (pos[0] + p, pos[1] + p), big)
    col = Image.new("RGBA", big.size, rgba(color))
    lay.paste(col, pos, big)
    return lay
