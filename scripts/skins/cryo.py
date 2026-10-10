"""Cryo : glace cristalline à facettes, givre, flocons, reflets."""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .common import rgba, triangle_emblem

ICE_L, ICE, ICE_D, NAVY = (238, 250, 255), (150, 210, 245), (60, 130, 210), (22, 38, 78)


def _voronoi(ctx, cells_per_stud=8, q=5):
    """Facettes de cristal : renvoie (teinte [0,1], arêtes [0,1]) en pleine résolution."""
    w, h = ctx.W // q, ctx.H // q
    span = ctx.L(1.0)
    n = int((ctx.W / span * cells_per_stud) * (ctx.H / span * cells_per_stud))
    pts = ctx.nrng.random((n, 2)) * [w, h]
    light = ctx.nrng.random((n, 2)) - 0.5
    base = ctx.nrng.random(n)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    shade = np.zeros((h, w), np.float32)
    edge = np.zeros((h, w), np.float32)
    for y0 in range(0, h, 24):
        ys, xs = yy[y0:y0 + 24], xx[y0:y0 + 24]
        dx = xs[..., None] - pts[:, 0]
        dy = ys[..., None] - pts[:, 1]
        dist = np.sqrt(dx * dx + dy * dy)
        idx = np.argpartition(dist, 1, axis=-1)[..., :2]
        swap = np.take_along_axis(dist, idx[..., :1], -1) > np.take_along_axis(dist, idx[..., 1:2], -1)
        idx = np.where(swap, idx[..., ::-1], idx)
        d1 = np.take_along_axis(dist, idx[..., :1], -1)[..., 0]
        d2 = np.take_along_axis(dist, idx[..., 1:2], -1)[..., 0]
        i1 = idx[..., 0]
        # facette : dégradé orienté par cellule (impression de plan incliné)
        gx = np.take_along_axis(dx, idx[..., :1], -1)[..., 0]
        gy = np.take_along_axis(dy, idx[..., :1], -1)[..., 0]
        s = base[i1] * 0.6 + (gx * light[i1, 0] + gy * light[i1, 1]) / (w / cells_per_stud * 0.25)
        shade[y0:y0 + 24] = s
        edge[y0:y0 + 24] = np.clip(1 - (d2 - d1) / 2.2, 0, 1)
    shade = (shade - shade.min()) / (shade.max() - shade.min() + 1e-6)
    up = lambda a: np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((ctx.W, ctx.H), Image.BICUBIC), np.float32) / 255
    return up(shade), up(edge)


def snowflake(ctx, d, x, z, r, color, width):
    cx, cy = ctx.P(x, z)
    R = ctx.L(r)
    w = max(2, int(ctx.L(width)))
    for k in range(6):
        a = k * math.pi / 3
        ex, ey = cx + math.cos(a) * R, cy + math.sin(a) * R
        d.line([(cx, cy), (ex, ey)], fill=rgba(color), width=w)
        for t, l in ((0.45, 0.32), (0.72, 0.22)):
            bx, by = cx + math.cos(a) * R * t, cy + math.sin(a) * R * t
            for s in (-1, 1):
                b = a + s * math.pi / 4
                d.line([(bx, by), (bx + math.cos(b) * R * l, by + math.sin(b) * R * l)], fill=rgba(color), width=max(1, w - 1))
    d.ellipse([cx - w * 1.4, cy - w * 1.4, cx + w * 1.4, cy + w * 1.4], fill=rgba(color))


def paint(ctx):
    rng, ds = ctx.rng, ctx.ds
    ex0, ez0, ex1, ez1 = ctx.extent()
    ctx.vgradient(ICE_L, ICE_D, z_top=ez1, z_bottom=ez0 + 0.1 * (ez1 - ez0))
    shade, edge = _voronoi(ctx, cells_per_stud=8 / ds)
    ctx.tint(ICE_L, np.clip(shade - 0.45, 0, 1) * 1.6, 0.85)    # faces éclairées
    ctx.tint((40, 105, 190), np.clip(0.4 - shade, 0, 1) * 1.8, 0.65)  # faces dans l'ombre
    ctx.tint((255, 255, 255), edge ** 3, 0.9)                     # arêtes brillantes

    # glace plus profonde vers le bas
    n = ctx.noise(0.2 * ds, 4)
    zlow = ctx.zones["band"][1]
    lowz = np.clip((np.arange(ctx.H, dtype=np.float32)[:, None] - ctx.P(0, zlow)[1]) / ctx.L(0.4 * ds), 0, 1)
    ctx.tint((30, 80, 170), lowz * (0.5 + 0.5 * n), 0.55)
    # givre : paillettes blanches + fissures
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for _ in range(5000):
        x, z = ctx.rand_extent()
        r = ctx.L(rng.uniform(0.001, 0.0035) * ds)
        px, py = ctx.P(x, z)
        d.ellipse([px - r, py - r, px + r, py + r], fill=(255, 255, 255, rng.randint(120, 255)))
    for _ in range(26):
        x, z = ctx.rand_in(rng.choice(("receiver", "handguard", "stock", "mag", "grip")))
        pts = [ctx.P(x, z)]
        a = rng.uniform(0, math.tau)
        for _ in range(rng.randint(3, 6)):
            a += rng.uniform(-0.8, 0.8)
            x += math.cos(a) * 0.03 * ds
            z += math.sin(a) * 0.03 * ds
            pts.append(ctx.P(x, z))
        d.line(pts, fill=(255, 255, 255, 210), width=2)
    ctx.over(lay)

    # flocons
    flakes = []
    for zone, u, v, r in (("receiver", 0.47, 0.5, 0.11), ("handguard", 0.55, 0.55, 0.08), ("mag", 0.5, 0.5, 0.06),
                          ("handguard", 0.12, 0.25, 0.04), ("receiver", 0.17, 0.8, 0.035),
                          ("handguard", 0.9, 0.75, 0.035), ("grip", 0.5, 0.5, 0.04), ("stock", 0.85, 0.8, 0.035),
                          ("receiver", 0.9, 0.25, 0.03)):
        x, z = ctx.at(zone, u, v)
        flakes.append((x, z, min(r * ds, 0.4 * ctx.zh(zone), 0.4 * ctx.zw(zone))))
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for x, z, r in flakes:
        snowflake(ctx, d, x, z, r, (255, 255, 255), r * 0.09)
    ctx.glow(lay, 0.012 * ds, 0.8)
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for x, z, r in flakes[:3]:
        snowflake(ctx, d, x, z, r * 0.55, ICE_D, r * 0.05)
    ctx.over(lay)

    # éclats de lumière (étoiles à 4 branches)
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for _ in range(14):
        x, z = ctx.rand_in(rng.choice(("receiver", "handguard", "stock", "band")))
        px, py = ctx.P(x, z)
        L = ctx.L(rng.uniform(0.02, 0.05) * ds)
        d.polygon([(px, py - L), (px + L * 0.12, py), (px, py + L), (px - L * 0.12, py)], fill=(255, 255, 255, 255))
        d.polygon([(px - L, py), (px, py + L * 0.12), (px + L, py), (px, py - L * 0.12)], fill=(255, 255, 255, 255))
    ctx.glow(lay, 0.01 * ds, 0.9)

    # liserés lumineux en bas des pièces
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for zone in ("receiver", "handguard", "stock"):
        x0, z0, x1, z1 = ctx.zones[zone]
        zl = z0 + 0.1 * (z1 - z0)
        d.line([ctx.P(x0 + 0.02 * ds, zl), ctx.P(x1 - 0.02 * ds, zl)], fill=rgba((120, 220, 255)),
               width=max(2, int(ctx.L(0.008 * ds))))
    ctx.glow(lay, 0.012 * ds, 0.9)

    triangle_emblem(ctx, (120, 215, 255), outline=NAVY, glow=0.015 * ds)
    ctx.grain(4)
    return ctx.result()


SKIN = dict(
    name="Cryo",
    palette=dict(Motif="Cryo", Sombre="BleuNuit", Clair="Argent", Accent="BleuGlace", Accent2="Blanc",
                 Verre="VerreBleu", Lentille="LentilleBleu", Gachette="Blanc"),
    paint=paint,
)
