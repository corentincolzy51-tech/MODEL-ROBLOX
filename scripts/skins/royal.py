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


def _panel(ctx, poly_studs, ds=1.0):
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
    for i, x in enumerate(np.arange(min(xs), max(xs), 0.11 * ds)):
        for j, z in enumerate(np.arange(min(zs), max(zs), 0.1 * ds)):
            _damask(ctx, d, x + (0.055 * ds if j % 2 else 0), z, 0.04 * ds, (135, 12, 24))
    clip = Image.new("L", lay.size, 0)
    ImageDraw.Draw(clip).polygon(poly, fill=255)
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(clip))))
    ctx.over(lay)

    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    w = max(2, int(ctx.L(0.012 * ds)))
    d.line(poly + [poly[0]], fill=rgba(GOLD_D), width=w + 4, joint="curve")
    d.line(poly + [poly[0]], fill=rgba(GOLD), width=w, joint="curve")
    cx = sum(x for x, _ in poly_studs) / len(poly_studs)
    cz = sum(z for _, z in poly_studs) / len(poly_studs)
    inner = [(cx + (x - cx) * 0.86, cz + (z - cz) * 0.8) for x, z in poly_studs]
    ip = [ctx.P(x, z) for x, z in inner]
    d.line(ip + [ip[0]], fill=rgba(GOLD), width=max(1, w // 2), joint="curve")
    for (x, z) in inner:
        fx = 1 if x < cx else -1
        _scroll(ctx, d, x + fx * 0.03 * ds, z + (0.025 if z < cz else -0.025) * ds, 0.028 * ds, flip=fx,
                width=0.007 * ds)
    ctx.over(lay)


def _inset(ctx, zone, kx=0.06, kz=0.12):
    x0, z0, x1, z1 = ctx.zones[zone]
    dx, dz = (x1 - x0) * kx, (z1 - z0) * kz
    return [(x0 + dx, z0 + dz), (x0 + dx, z1 - dz), (x1 - dx, z1 - dz), (x1 - dx, z0 + dz)]


def paint(ctx):
    ds = ctx.ds
    ctx.fill(BG)
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    ex0, ez0, ex1, ez1 = ctx.extent(0.2)
    for j, z in enumerate(np.arange(ez0, ez1, 0.11 * ds)):
        for x in np.arange(ex0, ex1, 0.13 * ds):
            _damask(ctx, d, x + (0.065 * ds if j % 2 else 0), z, 0.045 * ds, DAMASK)
    ctx.over(lay)
    ctx.grain(5)

    # panneaux laqués (pas sur la zone de l'emblème)
    for zone in ("receiver", "handguard", "mag", "grip", "stock"):
        if not ctx.emblem_in(zone):
            _panel(ctx, _inset(ctx, zone), ds)

    # ornements dorés
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    crown(ctx, d, *ctx.at("receiver", 0.5, 0.5), min(0.15 * ds, 0.42 * ctx.zh("receiver")), GOLD, outline=GOLD_D,
          jewel=(240, 40, 50))
    crown(ctx, d, *ctx.at("mag", 0.5, 0.55), min(0.09 * ds, 0.4 * min(ctx.zw("mag"), ctx.zh("mag"))), GOLD,
          outline=GOLD_D, jewel=(240, 40, 50))
    for zone in ("receiver", "handguard", "stock"):
        x0, z0, x1, z1 = ctx.zones[zone]
        for zr in ((z1 - 0.012 * ds, ) if zone == "stock" else (z1 - 0.012 * ds, z0 + 0.012 * ds)):
            for x in np.arange(x0 + 0.02 * ds, x1 - 0.01 * ds, 0.06 * ds):  # rivets dorés
                px, py = ctx.P(x, zr)
                r = ctx.L(0.008 * ds)
                d.ellipse([px - r, py - r, px + r, py + r], fill=rgba(GOLD), outline=rgba(GOLD_D))
    # arabesques autour de l'emblème
    ex, ez, es = ctx.emblem
    for k in range(5):
        a = math.pi * (0.15 + 0.175 * k)
        _scroll(ctx, d, ex + math.cos(a) * es * 0.95, ez + math.sin(a) * es * 0.75, 0.02 * ds,
                flip=1 if k % 2 else -1, width=0.005 * ds)
    ctx.over(lay)
    vx, vz = ctx.at("handguard", 0.5, 0.62)
    vs = min(0.13 * ds, 0.5 * ctx.zh("handguard"))
    text(ctx, "V", vx, vz, vs, GOLD, kind="serif", stroke=GOLD_D, stroke_w=0.05 * vs, shadow=(60, 0, 8))
    text(ctx, "ROYAL", vx, vz - 0.55 * vs, 0.3 * vs, GOLD_L, kind="serif")

    # reflet métallique en haut
    sheen = ctx.layer()
    bx0, bz0, bx1, bz1 = ctx.zones["band"]
    ImageDraw.Draw(sheen).rectangle([0, ctx.P(0, bz1)[1], ctx.W, ctx.P(0, bz1 - 0.25 * (bz1 - bz0))[1]],
                                    fill=(255, 220, 160, 26))
    ctx.over(sheen.filter(ImageFilter.GaussianBlur(ctx.L(0.03 * ds))))

    triangle_emblem(ctx, GOLD, outline=(70, 45, 10), inner=RED_L)
    return ctx.result()


SKIN = dict(
    name="Royal",
    palette=dict(Motif="Royal", Sombre="Noir", Clair="GrisFonce", Accent="Or", Accent2="Rouge",
                 Verre="VerreRouge", Lentille="LentilleRouge", Gachette="Or"),
    paint=paint,
)
