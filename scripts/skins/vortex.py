"""Vortex : noir fumé, tourbillons rouges et gris, lignes acérées."""
import math

import numpy as np
from PIL import ImageDraw, ImageFilter

from .common import rgba, text, triangle_emblem

BG = (17, 17, 21)
RED, RED_D, RED_L = (215, 28, 40), (110, 10, 20), (255, 90, 90)
GREY, GREY_L = (95, 95, 102), (190, 190, 198)


def vortex(ctx, cx, cz, R, n, rng, cols, width, turns=1.4, blur=0.0, opacity=1.0):
    """Tourbillon : traînées en spirale logarithmique vers le centre."""
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        a0 = rng.uniform(0, math.tau)
        r0 = R * rng.uniform(0.25, 1.0)
        span = rng.uniform(0.4, turns) * math.pi
        pts = []
        for i in range(40):
            t = i / 39 * span
            r = r0 * math.exp(-0.32 * t)
            pts.append(ctx.P(cx + math.cos(a0 + t) * r, cz + math.sin(a0 + t) * r * 0.85))
        w = max(1, int(ctx.L(width * rng.uniform(0.4, 1.4))))
        d.line(pts, fill=rgba(rng.choice(cols)), width=w, joint="curve")
    if blur:
        lay = lay.filter(ImageFilter.GaussianBlur(ctx.L(blur)))
    ctx.over(lay, opacity)


def paint(ctx):
    rng = ctx.rng
    ctx.fill(BG)
    n = ctx.noise(0.25, 6)
    ctx.tint((48, 46, 52), np.clip((n - 0.45) * 2.5, 0, 1), 0.8)   # fumée
    ctx.tint((8, 8, 10), np.clip((0.42 - n) * 3, 0, 1), 0.7)

    # grand tourbillon sombre en fond
    vortex(ctx, 1.6, 0.8, 1.3, 260, rng, ((60, 14, 20), (45, 45, 52), (80, 20, 28)), 0.014, turns=1.8, blur=0.01, opacity=0.6)
    # tourbillons : fumée grise floue, puis traînées rouges nettes
    for cx, cz, R in ((1.52, 0.86, 0.42), (2.55, 0.90, 0.32), (1.735, 0.35, 0.2), (0.42, 0.82, 0.3), (1.19, 0.40, 0.14)):
        vortex(ctx, cx, cz, R * 1.15, 150, rng, (GREY, (70, 70, 76), GREY_L), 0.01, blur=0.006, opacity=0.55)
        vortex(ctx, cx, cz, R, 120, rng, (RED, RED_D, RED, RED_L), 0.007, turns=1.8, opacity=0.9)
        lay = ctx.layer()
        d = ImageDraw.Draw(lay)
        px, py = ctx.P(cx, cz)
        r = ctx.L(R * 0.08)
        d.ellipse([px - r, py - r, px + r, py + r], fill=rgba((5, 5, 6)))
        d.ellipse([px - r * 1.6, py - r * 1.6, px + r * 1.6, py + r * 1.6], outline=rgba(RED), width=max(2, int(r * 0.2)))
        ctx.glow(lay, 0.01, 0.7)

    # lignes acérées
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for x0, z0, x1, z1, h in ((1.06, 0.70, 1.98, 0.70, 0.018), (2.06, 0.77, 2.92, 0.77, 0.016), (0.16, 0.57, 0.62, 0.85, 0.014),
                              (1.10, 1.02, 1.60, 1.02, 0.01), (2.30, 1.03, 2.92, 1.03, 0.01)):
        poly = [ctx.P(x0, z0), ctx.P(x1, z1), ctx.P(x1 - 0.04, z1 + h), ctx.P(x0 + 0.04, z0 + h)]
        d.polygon(poly, fill=rgba(RED))
    for k in range(5):  # chevrons sur le garde-main
        x = 2.10 + k * 0.05
        d.line([ctx.P(x, 0.98), ctx.P(x + 0.025, 0.95), ctx.P(x, 0.92)], fill=rgba(GREY_L), width=max(2, int(ctx.L(0.007))))
    ctx.glow(lay, 0.008, 0.6)
    text(ctx, "VORTEX", 2.62, 0.99, 0.045, GREY_L, kind="black")

    triangle_emblem(ctx, RED, outline=(8, 8, 10), glow=0.012)
    ctx.grain(6)
    return ctx.result()


SKIN = dict(
    name="Vortex",
    palette=dict(Motif="Vortex", Sombre="Noir", Clair="Gris", Accent="Rouge", Accent2="GrisClair",
                 Verre="VerreRouge", Gachette="Rouge"),
    paint=paint,
)
