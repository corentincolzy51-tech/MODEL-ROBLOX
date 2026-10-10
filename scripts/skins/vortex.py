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
    rng, ds = ctx.rng, ctx.ds
    ctx.fill(BG)
    n = ctx.noise(0.25 * ds, 6)
    ctx.tint((48, 46, 52), np.clip((n - 0.45) * 2.5, 0, 1), 0.8)   # fumée
    ctx.tint((8, 8, 10), np.clip((0.42 - n) * 3, 0, 1), 0.7)

    # grand tourbillon sombre en fond
    ex0, ez0, ex1, ez1 = ctx.extent()
    vortex(ctx, (ex0 + ex1) / 2, (ez0 + ez1) / 2, 0.36 * (ex1 - ex0), 260, rng,
           ((60, 14, 20), (45, 45, 52), (80, 20, 28)), 0.014 * ds, turns=1.8, blur=0.01 * ds, opacity=0.6)
    # tourbillons : fumée grise floue, puis traînées rouges nettes
    for zone in ("receiver", "handguard", "mag", "stock", "grip"):
        cx, cz = ctx.at(zone, 0.5, 0.5)
        R = min(0.45 * max(ctx.zw(zone), ctx.zh(zone)), 1.1 * min(ctx.zw(zone), ctx.zh(zone)))
        vortex(ctx, cx, cz, R * 1.15, 150, rng, (GREY, (70, 70, 76), GREY_L), 0.01 * ds, blur=0.006 * ds, opacity=0.55)
        vortex(ctx, cx, cz, R, 120, rng, (RED, RED_D, RED, RED_L), 0.007 * ds, turns=1.8, opacity=0.9)
        lay = ctx.layer()
        d = ImageDraw.Draw(lay)
        px, py = ctx.P(cx, cz)
        r = ctx.L(R * 0.08)
        d.ellipse([px - r, py - r, px + r, py + r], fill=rgba((5, 5, 6)))
        d.ellipse([px - r * 1.6, py - r * 1.6, px + r * 1.6, py + r * 1.6], outline=rgba(RED), width=max(2, int(r * 0.2)))
        ctx.glow(lay, 0.01 * ds, 0.7)

    # lignes acérées en bas et en haut des pièces
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for zone, v, h in (("receiver", 0.1, 0.018), ("handguard", 0.1, 0.016), ("stock", 0.12, 0.014),
                       ("receiver", 0.95, 0.01), ("handguard", 0.95, 0.01)):
        x0, z0, x1, z1 = ctx.zones[zone]
        zz = z0 + v * (z1 - z0)
        hh, ins = h * ds, 0.04 * ds
        d.polygon([ctx.P(x0, zz), ctx.P(x1, zz), ctx.P(x1 - ins, zz + hh), ctx.P(x0 + ins, zz + hh)], fill=rgba(RED))
    cx, cz = ctx.at("handguard", 0.1, 0.68)
    for k in range(5):  # chevrons
        x = cx + k * 0.05 * ds
        d.line([ctx.P(x, cz + 0.03 * ds), ctx.P(x + 0.025 * ds, cz), ctx.P(x, cz - 0.03 * ds)], fill=rgba(GREY_L),
               width=max(2, int(ctx.L(0.007 * ds))))
    ctx.glow(lay, 0.008 * ds, 0.6)
    text(ctx, "VORTEX", *ctx.at("handguard", 0.65, 0.85), 0.045 * ds, GREY_L, kind="black")

    triangle_emblem(ctx, RED, outline=(8, 8, 10), glow=0.012 * ds)
    ctx.grain(6)
    return ctx.result()


SKIN = dict(
    name="Vortex",
    palette=dict(Motif="Vortex", Sombre="Noir", Clair="Gris", Accent="Rouge", Accent2="GrisClair",
                 Verre="VerreRouge", Lentille="LentilleRouge", Gachette="Rouge"),
    paint=paint,
)
