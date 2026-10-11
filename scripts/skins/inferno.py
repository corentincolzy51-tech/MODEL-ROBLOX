"""Inferno (Épique) : basalte calciné, fissures de lave qui pulsent, braises."""
import math

import numpy as np
from PIL import ImageDraw

from .common import rgba, text, triangle_emblem

LAVA_D, LAVA, LAVA_L = (150, 30, 6), (255, 100, 15), (255, 210, 90)


def paint(ctx):
    rng, ds = ctx.rng, ctx.ds
    ex0, ez0, ex1, ez1 = ctx.extent()
    ctx.vgradient((26, 20, 18), (40, 14, 8), z_top=ez1, z_bottom=ez0)
    n, n2 = ctx.noise(0.12 * ds, 6), ctx.noise(0.05 * ds, 4, 5)
    ctx.tint((58, 48, 44), np.clip((n - 0.5) * 3, 0, 1), 0.85)       # roche plus claire
    ctx.tint((10, 7, 6), np.clip((0.42 - n2) * 4, 0, 1), 0.7)        # pores sombres
    ctx.tint((90, 24, 8), np.clip((n * n2 - 0.32) * 6, 0, 1), 0.6)   # chaleur sous la roche

    # fissures peintes : halo sombre, lave, cœur clair
    paths = []
    for _ in range(30):
        zone = rng.choice(("receiver", "handguard", "stock", "mag", "grip", "receiver"))
        x, z = ctx.rand_in(zone)
        a = rng.uniform(0, math.tau)
        pts = [(x, z)]
        for _ in range(rng.randint(4, 8)):
            a += rng.uniform(-0.9, 0.9)
            x += math.cos(a) * rng.uniform(0.03, 0.07) * ds
            z += math.sin(a) * rng.uniform(0.02, 0.05) * ds
            pts.append((x, z))
        paths.append(pts)
    for col, wk, blur in ((LAVA_D, 0.03, 0.02), (LAVA, 0.012, 0.0), (LAVA_L, 0.004, 0.0)):
        lay = ctx.layer()
        d = ImageDraw.Draw(lay)
        for pts in paths:
            d.line([ctx.P(a, b) for a, b in pts], fill=rgba(col), width=max(2, int(ctx.L(wk * ds))), joint="curve")
        if blur:
            ctx.glow(lay, blur * ds, 0.7, passes=1)
        else:
            ctx.over(lay)

    # braises
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for _ in range(700):
        x, z = ctx.rand_extent()
        r = ctx.L(rng.uniform(0.002, 0.006) * ds)
        px, py = ctx.P(x, z)
        d.ellipse([px - r, py - r, px + r, py + r], fill=rgba(rng.choice((LAVA, LAVA_L, (255, 60, 10))), rng.randint(150, 255)))
    ctx.glow(lay, 0.008 * ds, 0.8)

    ts = min(0.09 * ds, 0.3 * ctx.zh("receiver"), 0.16 * ctx.zw("receiver"))
    text(ctx, "INFERNO", *ctx.at("receiver", 0.55, 0.2), ts, LAVA, kind="black", stroke=(30, 6, 2), stroke_w=0.08 * ts)
    triangle_emblem(ctx, LAVA, outline=(20, 6, 2), inner=LAVA_L, glow=0.02 * ds)
    ctx.grain(7)
    return ctx.result()


import phantom_variants  # noqa: E402

SKIN = dict(
    name="Inferno",
    rarity="Épique",
    weapons=("ar01",),
    pieces={"ar01": phantom_variants.inferno_pieces},
    palette=dict(Motif="Inferno", Sombre="Noir", Clair="GrisFonce", Accent="Lave", Accent2="OrangeBrule",
                 Verre="VerreOrange", Lentille="LentilleOrange", Gachette="Lave", Neon="Lave"),
    effect=dict(Effet="Inferno", NeonAnime="Lave", CouleurTraceur=(255, 140, 40), CouleurFlamme=(255, 110, 25)),
    paint=paint,
)
