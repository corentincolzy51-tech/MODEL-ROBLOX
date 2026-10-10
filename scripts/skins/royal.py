"""Royal : laque noire et rouge, filigranes dorés, damas, couronnes."""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .common import crown, rgba, text, triangle_emblem

BG = (16, 9, 11)
DAMASK = (48, 14, 20)
RED_D, RED_L = (110, 8, 18), (220, 34, 46)
GOLD, GOLD_D, GOLD_L = (232, 178, 52), (150, 100, 22), (255, 232, 150)


def _damask(ctx, d, x, z, s, col):
    """Motif de damas : fleur à quatre pétales + losange."""
    cx, cy = ctx.P(x, z)
    r = ctx.L(s)
    for a in range(4):
        ang = a * math.pi / 2
        px, py = cx + math.cos(ang) * r * 0.45, cy + math.sin(ang) * r * 0.45
        d.ellipse([px - r * 0.3, py - r * 0.18 if a % 2 == 0 else py - r * 0.3,
                   px + r * 0.3, py + r * 0.18 if a % 2 == 0 else py + r * 0.3], fill=rgba(col))
    d.polygon([(cx, cy - r * 0.2), (cx + r * 0.2, cy), (cx, cy + r * 0.2), (cx - r * 0.2, cy)], fill=rgba(BG))
    for a in range(4):
        ang = math.pi / 4 + a * math.pi / 2
        px, py = cx + math.cos(ang) * r * 0.8, cy + math.sin(ang) * r * 0.8
        d.ellipse([px - r * 0.07, py - r * 0.07, px + r * 0.07, py + r * 0.07], fill=rgba(col))


def _scroll(ctx, d, x, z, size, flip=1, col=GOLD, width=0.007):
    """Volute de filigrane (spirale)."""
    pts = []
    for i in range(60):
        t = i / 59
        ang = flip * (t * 3.6 * math.pi)
        r = size * (1 - t * 0.85)
        pts.append(ctx.P(x + math.cos(ang) * r, z + math.sin(ang) * r * 0.9))
    d.line(pts, fill=rgba(col), width=max(2, int(ctx.L(width))), joint="curve")
    lx, ly = pts[-1]
    rr = ctx.L(width * 0.9)
    d.ellipse([lx - rr, ly - rr, lx + rr, ly + rr], fill=rgba(col))


def _panel(ctx, poly_studs, inset=0.018):
    """Panneau laqué rouge avec double liseré doré et volutes aux coins."""
    mask = Image.new("L", (ctx.W, ctx.H), 0)
    md = ImageDraw.Draw(mask)
    poly = [ctx.P(x, z) for x, z in poly_studs]
    md.polygon(poly, fill=255)
    m = np.asarray(mask, np.float32) / 255
    zs = [z for _, z in poly_studs]
    y0, y1 = ctx.P(0, max(zs))[1], ctx.P(0, min(zs))[1]
    t = np.clip((np.arange(ctx.H, dtype=np.float32) - y0) / max(1, y1 - y0), 0, 1)[:, None]
    shade = 1.0 - np.abs(t - 0.35) * 1.2
    base = np.asarray(ctx.img, np.float32)
    col = np.array(RED_D, np.float32) + (np.array(RED_L, np.float32) - np.array(RED_D, np.float32)) * np.clip(shade, 0, 1)[..., None]
    base[..., :3] = base[..., :3] * (1 - m[..., None]) + col * m[..., None]
    ctx.img = Image.fromarray(base.astype(np.uint8), "RGBA")

    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    # damas sombre dans le panneau
    xs = [x for x, _ in poly_studs]
    for i, x in enumerate(np.arange(min(xs), max(xs), 0.11)):
        for j, z in enumerate(np.arange(min(zs), max(zs), 0.1)):
            _damask(ctx, d, x + (0.055 if j % 2 else 0), z, 0.04, (135, 12, 24))
    clip = Image.new("L", lay.size, 0)
    ImageDraw.Draw(clip).polygon(poly, fill=255)
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(clip))))
    ctx.over(lay)

    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    w = max(2, int(ctx.L(0.012)))
    d.line(poly + [poly[0]], fill=rgba(GOLD_D), width=w + 4, joint="curve")
    d.line(poly + [poly[0]], fill=rgba(GOLD), width=w, joint="curve")
    cx = sum(x for x, _ in poly_studs) / len(poly_studs)
    cz = sum(z for _, z in poly_studs) / len(poly_studs)
    inner = [(cx + (x - cx) * 0.86, cz + (z - cz) * 0.8) for x, z in poly_studs]
    ip = [ctx.P(x, z) for x, z in inner]
    d.line(ip + [ip[0]], fill=rgba(GOLD), width=max(1, w // 2), joint="curve")
    for (x, z) in inner:
        fx = 1 if x < cx else -1
        _scroll(ctx, d, x + fx * 0.03, z + (0.025 if z < cz else -0.025), 0.028, flip=fx)
    ctx.over(lay)


def paint(ctx):
    ctx.fill(BG)
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for j, z in enumerate(np.arange(0.0, 1.45, 0.11)):
        for x in np.arange(-0.1, 3.8, 0.13):
            _damask(ctx, d, x + (0.065 if j % 2 else 0), z, 0.045, DAMASK)
    ctx.over(lay)
    ctx.grain(5)

    # panneaux laqués
    _panel(ctx, [(1.12, 0.70), (1.12, 1.00), (1.98, 1.00), (1.98, 0.74), (1.86, 0.70)])
    _panel(ctx, [(2.08, 0.78), (2.08, 1.01), (2.90, 1.01), (2.90, 0.80)])
    _panel(ctx, [(0.48, 0.80), (0.52, 0.98), (0.64, 0.96), (0.66, 0.84)])
    _panel(ctx, [(1.60, 0.54), (1.80, 0.54), (1.87, 0.18), (1.67, 0.18)])
    _panel(ctx, [(1.10, 0.58), (1.30, 0.58), (1.22, 0.26), (1.07, 0.26)])

    # ornements dorés
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    crown(ctx, d, 1.55, 0.86, 0.15, GOLD, outline=GOLD_D, jewel=(240, 40, 50))
    crown(ctx, d, 1.735, 0.38, 0.09, GOLD, outline=GOLD_D, jewel=(240, 40, 50))
    for x0, x1, z in ((1.08, 2.0, 1.035), (2.06, 2.92, 1.04), (0.12, 0.62, 1.01), (1.08, 2.0, 0.68)):
        for x in np.arange(x0, x1, 0.06):  # rivets dorés
            px, py = ctx.P(x, z)
            r = ctx.L(0.008)
            d.ellipse([px - r, py - r, px + r, py + r], fill=rgba(GOLD), outline=rgba(GOLD_D))
    # arabesques sur la crosse (autour de l'emblème)
    for k in range(5):
        _scroll(ctx, d, 0.15 + k * 0.065, 0.965, 0.02, flip=1 if k % 2 else -1, width=0.005)
    ctx.over(lay)
    text(ctx, "V", 2.49, 0.935, 0.13, GOLD, kind="serif", stroke=GOLD_D, stroke_w=0.006, shadow=(60, 0, 8))
    text(ctx, "ROYAL", 2.49, 0.865, 0.04, GOLD_L, kind="serif")

    # reflet métallique sur l'or : léger halo clair
    sheen = ctx.layer()
    ImageDraw.Draw(sheen).rectangle([0, ctx.P(0, 1.06)[1], ctx.W, ctx.P(0, 0.98)[1]], fill=(255, 220, 160, 26))
    ctx.over(sheen.filter(ImageFilter.GaussianBlur(ctx.L(0.03))))

    triangle_emblem(ctx, GOLD, outline=(70, 45, 10), inner=RED_L)
    return ctx.result()


SKIN = dict(
    name="Royal",
    palette=dict(Motif="Royal", Sombre="Noir", Clair="GrisFonce", Accent="Or", Accent2="Rouge",
                 Verre="VerreRouge", Lentille="LentilleRouge", Gachette="Or"),
    paint=paint,
)
