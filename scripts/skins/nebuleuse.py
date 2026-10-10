"""Nébuleuse : espace profond, nuages galactiques, étoiles, lignes lumineuses."""
import math

import numpy as np
from PIL import ImageDraw

from .common import rgba, text, triangle_emblem

MAG, VIO, BLUE, CYAN = (230, 60, 220), (140, 70, 255), (60, 90, 255), (60, 225, 255)


def paint(ctx):
    rng, ds = ctx.rng, ctx.ds
    ex0, ez0, ex1, ez1 = ctx.extent()
    ctx.vgradient((34, 12, 62), (6, 4, 22), z_top=ez1, z_bottom=ez0)
    n1, n2, n3 = ctx.noise(0.45 * ds, 6), ctx.noise(0.35 * ds, 6, 7), ctx.noise(0.18 * ds, 5, 13)
    ctx.tint(VIO, np.clip((n1 - 0.42) * 2.6, 0, 1) ** 1.3, 0.8)
    ctx.tint(BLUE, np.clip((n2 - 0.48) * 2.8, 0, 1) ** 1.3, 0.75)
    ctx.tint(MAG, np.clip((n1 * n2 - 0.28) * 4.5, 0, 1) ** 1.5, 0.8)
    ctx.tint(CYAN, np.clip((n3 - 0.6) * 4, 0, 1) ** 2 * np.clip((n2 - 0.45) * 4, 0, 1), 0.7)
    ctx.tint((255, 230, 255), np.clip((n1 * n2 * n3 - 0.2) * 9, 0, 1) ** 2, 0.6)   # cœurs brillants
    ctx.tint((4, 2, 12), np.clip((0.4 - n3) * 3, 0, 1) * 0.6, 0.7)                  # poussière sombre

    # étoiles
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for _ in range(4500):
        x, z = ctx.rand_extent()
        r = ctx.L(rng.uniform(0.0012, 0.004) * ds)
        px, py = ctx.P(x, z)
        c = rng.choice(((255, 255, 255), (200, 220, 255), (255, 210, 250)))
        d.ellipse([px - r, py - r, px + r, py + r], fill=rgba(c, rng.randint(140, 255)))
    ctx.over(lay)
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for _ in range(26):
        x, z = ctx.rand_in(rng.choice(("receiver", "handguard", "stock", "mag", "grip", "band")))
        px, py = ctx.P(x, z)
        L = ctx.L(rng.uniform(0.02, 0.05) * ds)
        d.line([(px - L, py), (px + L, py)], fill=(255, 255, 255, 230), width=2)
        d.line([(px, py - L), (px, py + L)], fill=(255, 255, 255, 230), width=2)
        r = L * 0.18
        d.ellipse([px - r, py - r, px + r, py + r], fill=(255, 255, 255, 255))
    ctx.glow(lay, 0.01 * ds, 0.9)

    # lignes lumineuses (courbes fluides + circuits)
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    bx0, bz0, bx1, bz1 = ctx.zones["band"]
    for v, amp, col, ph in ((0.08, 0.02, CYAN, 0.0), (0.88, 0.015, VIO, 1.3), (0.45, 0.03, MAG, 2.1)):
        z0 = bz0 + v * (bz1 - bz0)
        pts = [ctx.P(x, z0 + amp * ds * math.sin(x * 9 / ds + ph)) for x in np.arange(bx0 + 0.1 * ds, bx1, 0.01 * ds)]
        d.line(pts, fill=rgba(col), width=max(2, int(ctx.L(0.006 * ds))), joint="curve")
    for _ in range(12):
        x, z = ctx.rand_in(rng.choice(("receiver", "handguard", "stock")))
        pts = [(x, z)]
        for _ in range(3):
            if rng.random() < 0.5:
                x += rng.choice((-1, 1)) * rng.uniform(0.05, 0.12) * ds
            else:
                z += rng.choice((-1, 1)) * rng.uniform(0.03, 0.06) * ds
            pts.append((x, z))
        pp = [ctx.P(a, b) for a, b in pts]
        col = rng.choice((CYAN, VIO, MAG))
        d.line(pp, fill=rgba(col), width=max(2, int(ctx.L(0.004 * ds))))
        for px, py in (pp[0], pp[-1]):
            r = ctx.L(0.008 * ds)
            d.ellipse([px - r, py - r, px + r, py + r], outline=rgba(col), width=2)
    ctx.glow(lay, 0.01 * ds, 0.85)

    # planète à anneaux
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    cx, cy = ctx.P(*ctx.at("handguard", 0.7, 0.55))
    R = ctx.L(min(0.06 * ds, 0.28 * ctx.zh("handguard")))
    d.ellipse([cx - R * 2.0, cy - R * 0.55, cx + R * 2.0, cy + R * 0.55], outline=rgba((255, 200, 255)), width=max(2, int(R * 0.12)))
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=rgba((150, 80, 230)))
    d.ellipse([cx - R * 0.7, cy - R * 0.9, cx + R * 0.5, cy + R * 0.1], fill=rgba((200, 140, 255)))
    d.arc([cx - R * 2.0, cy - R * 0.55, cx + R * 2.0, cy + R * 0.55], 0, 180, fill=rgba((255, 200, 255)), width=max(2, int(R * 0.12)))
    ctx.glow(lay, 0.015 * ds, 0.6)
    ts = min(0.09 * ds, 0.35 * ctx.zh("receiver"), 0.2 * ctx.zw("receiver"))
    text(ctx, "NEBULA", *ctx.at("receiver", 0.5, 0.52), ts, (255, 255, 255), kind="bold", stroke=VIO, stroke_w=0.045 * ts)

    triangle_emblem(ctx, VIO, outline=(20, 8, 40), inner=CYAN, glow=0.02 * ds)
    return ctx.result()


SKIN = dict(
    name="Nebuleuse",
    palette=dict(Motif="Nebuleuse", Sombre="NoirViolet", Clair="Violet", Accent="VioletNeon", Accent2="CyanNeon",
                 Verre="VerreViolet", Lentille="LentilleViolet", Gachette="CyanNeon"),
    paint=paint,
)
