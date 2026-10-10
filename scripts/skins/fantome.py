"""Fantôme : minimaliste noir et gris, volutes de fumée blanche, filets argent."""
import math

import numpy as np
from PIL import Image, ImageDraw

from .common import rgba, text, triangle_emblem


def wisps(ctx, rng, n, z_range, width_range, color, amount, q=2, ds=1.0):
    """Volutes de fumée douces : bandes gaussiennes qui ondulent le long de l'arme."""
    w, h = ctx.W // q, ctx.H // q
    ys = np.arange(h, dtype=np.float32)[:, None]
    xs = np.arange(w, dtype=np.float32)
    mask = np.zeros((h, w), np.float32)
    span = ctx.L(1.0) / q  # pixels par stud
    for _ in range(n):
        z0 = rng.uniform(*z_range)
        f1, f2 = rng.uniform(1.5, 3.5) / ds, rng.uniform(4, 7) / ds
        a1, a2 = rng.uniform(0.03, 0.09) * ds, rng.uniform(0.01, 0.03) * ds
        p1, p2 = rng.uniform(0, math.tau), rng.uniform(0, math.tau)
        ex0, _, ex1, _ = ctx.extent()
        xc, xl = rng.uniform(ex0, ex1), rng.uniform(0.6, 1.6) * ds
        xst = xs / span
        zc = z0 + a1 * np.sin(f1 * xst + p1) + a2 * np.sin(f2 * xst + p2)
        # conversion z(studs) -> y(pixels) : y = y(z=0) - z * pixels_par_stud
        yc = (ctx.P(0, 0)[1] / q) - zc * span
        wid = span * rng.uniform(*width_range) * ds * (0.6 + 0.4 * np.sin(xst * rng.uniform(2, 5) / ds + p2) ** 2)
        fade = np.exp(-((xst - xc) / (xl / 2)) ** 2)
        mask += fade[None, :] * np.exp(-((ys - yc[None, :]) / wid[None, :]) ** 2)
    m = np.asarray(Image.fromarray(np.clip(mask * 255, 0, 255).astype(np.uint8)).resize((ctx.W, ctx.H), Image.BICUBIC), np.float32) / 255
    ctx.tint(color, m, amount)


def paint(ctx):
    rng, ds = ctx.rng, ctx.ds
    ex0, ez0, ex1, ez1 = ctx.extent()
    ctx.vgradient((62, 62, 68), (8, 8, 10), z_top=ez1, z_bottom=ez0 + 0.1 * (ez1 - ez0))
    n = ctx.noise(0.3 * ds, 6)
    ctx.tint((150, 150, 158), np.clip((n - 0.55) * 3, 0, 1) ** 1.5, 0.35)   # brume
    zr = (ez0, ez1)
    wisps(ctx, rng, 26, zr, (0.04, 0.09), (200, 200, 210), 0.35, ds=ds)   # fumée large
    wisps(ctx, rng, 30, zr, (0.012, 0.03), (235, 235, 242), 0.5, ds=ds)   # volutes
    wisps(ctx, rng, 22, zr, (0.003, 0.007), (255, 255, 255), 0.75, ds=ds)  # filaments

    # filets argent
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for zone, v in (("receiver", 0.13), ("receiver", 0.2), ("handguard", 0.15), ("stock", 0.15)):
        x0, z0, x1, z1 = ctx.zones[zone]
        zz = z0 + v * (z1 - z0)
        d.line([ctx.P(x0 + 0.02 * ds, zz), ctx.P(x1 - 0.02 * ds, zz)], fill=rgba((200, 202, 210)),
               width=max(2, int(ctx.L(0.004 * ds))))
    bx0, bz0, bx1, bz1 = ctx.zones["band"]
    d.line([ctx.P(bx0 + 0.1 * ds, bz1 - 0.04 * ds), ctx.P(bx1 - 0.1 * ds, bz1 - 0.04 * ds)], fill=rgba((200, 202, 210)),
           width=max(2, int(ctx.L(0.004 * ds))))
    ctx.over(lay)
    px_, pz_ = ctx.at("handguard", 0.5, 0.62)
    ps = min(0.06 * ds, 0.3 * ctx.zh("handguard"), 0.12 * ctx.zw("handguard"))
    text(ctx, "PHANTOM", px_, pz_, ps, (210, 210, 218), kind="bold")
    text(ctx, "— silent —", px_, pz_ - 0.9 * ps, 0.42 * ps, (140, 140, 148), kind="bold")
    vs = min(0.14 * ds, 0.45 * ctx.zh("receiver"))
    text(ctx, "V", *ctx.at("receiver", 0.5, 0.55), vs, (40, 40, 46), kind="black", stroke=(150, 150, 158),
         stroke_w=0.03 * vs)

    triangle_emblem(ctx, (235, 235, 242), outline=(10, 10, 12))
    ctx.grain(5)
    return ctx.result()


SKIN = dict(
    name="Fantome",
    palette=dict(Motif="Fantome", Sombre="Noir", Clair="Argent", Accent="Blanc", Accent2="GrisClair",
                 Verre="VerreBlanc", Lentille="LentilleBlanc", Gachette="GrisClair"),
    paint=paint,
)
