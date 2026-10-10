"""Nébuleuse : espace profond, nuages galactiques, étoiles, lignes lumineuses."""
import math

import numpy as np
from PIL import ImageDraw

from .common import rgba, text, triangle_emblem

MAG, VIO, BLUE, CYAN = (230, 60, 220), (140, 70, 255), (60, 90, 255), (60, 225, 255)


def paint(ctx):
    rng = ctx.rng
    ctx.vgradient((34, 12, 62), (6, 4, 22), z_top=1.1, z_bottom=0.1)
    n1, n2, n3 = ctx.noise(0.45, 6), ctx.noise(0.35, 6, 7), ctx.noise(0.18, 5, 13)
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
        x, z = rng.uniform(0, 3.1), rng.uniform(0.05, 1.15)
        r = ctx.L(rng.uniform(0.0012, 0.004))
        px, py = ctx.P(x, z)
        c = rng.choice(((255, 255, 255), (200, 220, 255), (255, 210, 250)))
        d.ellipse([px - r, py - r, px + r, py + r], fill=rgba(c, rng.randint(140, 255)))
    ctx.over(lay)
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for _ in range(26):
        x, z = ctx.rand_in(rng.choice(("receiver", "handguard", "stock", "mag", "grip", "band")))
        px, py = ctx.P(x, z)
        L = ctx.L(rng.uniform(0.02, 0.05))
        d.line([(px - L, py), (px + L, py)], fill=(255, 255, 255, 230), width=2)
        d.line([(px, py - L), (px, py + L)], fill=(255, 255, 255, 230), width=2)
        r = L * 0.18
        d.ellipse([px - r, py - r, px + r, py + r], fill=(255, 255, 255, 255))
    ctx.glow(lay, 0.01, 0.9)

    # lignes lumineuses (courbes fluides + circuits)
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for z0, amp, col, ph in ((0.76, 0.02, CYAN, 0.0), (1.02, 0.015, VIO, 1.3), (0.88, 0.03, MAG, 2.1)):
        pts = [ctx.P(x, z0 + amp * math.sin(x * 9 + ph)) for x in np.arange(0.12, 2.94, 0.01)]
        d.line(pts, fill=rgba(col), width=max(2, int(ctx.L(0.006))), joint="curve")
    for _ in range(12):
        x, z = ctx.rand_in(rng.choice(("receiver", "handguard", "stock")))
        pts = [(x, z)]
        for _ in range(3):
            if rng.random() < 0.5:
                x += rng.choice((-1, 1)) * rng.uniform(0.05, 0.12)
            else:
                z += rng.choice((-1, 1)) * rng.uniform(0.03, 0.06)
            pts.append((x, z))
        pp = [ctx.P(a, b) for a, b in pts]
        col = rng.choice((CYAN, VIO, MAG))
        d.line(pp, fill=rgba(col), width=max(2, int(ctx.L(0.004))))
        for px, py in (pp[0], pp[-1]):
            r = ctx.L(0.008)
            d.ellipse([px - r, py - r, px + r, py + r], outline=rgba(col), width=2)
    ctx.glow(lay, 0.01, 0.85)

    # planète à anneaux
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    cx, cy = ctx.P(2.66, 0.91)
    R = ctx.L(0.06)
    d.ellipse([cx - R * 2.0, cy - R * 0.55, cx + R * 2.0, cy + R * 0.55], outline=rgba((255, 200, 255)), width=max(2, int(R * 0.12)))
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=rgba((150, 80, 230)))
    d.ellipse([cx - R * 0.7, cy - R * 0.9, cx + R * 0.5, cy + R * 0.1], fill=rgba((200, 140, 255)))
    d.arc([cx - R * 2.0, cy - R * 0.55, cx + R * 2.0, cy + R * 0.55], 0, 180, fill=rgba((255, 200, 255)), width=max(2, int(R * 0.12)))
    ctx.glow(lay, 0.015, 0.6)
    text(ctx, "NEBULA", 1.55, 0.86, 0.09, (255, 255, 255), kind="bold", stroke=VIO, stroke_w=0.004)

    triangle_emblem(ctx, VIO, outline=(20, 8, 40), inner=CYAN, glow=0.02)
    return ctx.result()


SKIN = dict(
    name="Nebuleuse",
    palette=dict(Motif="Nebuleuse", Sombre="NoirViolet", Clair="Violet", Accent="VioletNeon", Accent2="CyanNeon",
                 Verre="VerreViolet", Gachette="CyanNeon"),
    paint=paint,
)
