"""Fantôme : minimaliste noir et gris, volutes de fumée blanche, filets argent."""
import math

import numpy as np
from PIL import Image, ImageDraw

from .common import rgba, text, triangle_emblem


def wisps(ctx, rng, n, z_range, width_range, color, amount, q=2):
    """Volutes de fumée douces : bandes gaussiennes qui ondulent le long de l'arme."""
    w, h = ctx.W // q, ctx.H // q
    ys = np.arange(h, dtype=np.float32)[:, None]
    xs = np.arange(w, dtype=np.float32)
    mask = np.zeros((h, w), np.float32)
    span = ctx.L(1.0) / q  # pixels par stud
    for _ in range(n):
        z0 = rng.uniform(*z_range)
        f1, f2 = rng.uniform(1.5, 3.5), rng.uniform(4, 7)
        a1, a2 = rng.uniform(0.03, 0.09), rng.uniform(0.01, 0.03)
        p1, p2 = rng.uniform(0, math.tau), rng.uniform(0, math.tau)
        xc, xl = rng.uniform(0.0, 3.0), rng.uniform(0.6, 1.6)
        xst = xs / span
        zc = z0 + a1 * np.sin(f1 * xst + p1) + a2 * np.sin(f2 * xst + p2)
        # conversion z(studs) -> y(pixels) : y = y(z=0) - z * pixels_par_stud
        yc = (ctx.P(0, 0)[1] / q) - zc * span
        wid = span * rng.uniform(*width_range) * (0.6 + 0.4 * np.sin(xst * rng.uniform(2, 5) + p2) ** 2)
        fade = np.exp(-((xst - xc) / (xl / 2)) ** 2)
        mask += fade[None, :] * np.exp(-((ys - yc[None, :]) / wid[None, :]) ** 2)
    m = np.asarray(Image.fromarray(np.clip(mask * 255, 0, 255).astype(np.uint8)).resize((ctx.W, ctx.H), Image.BICUBIC), np.float32) / 255
    ctx.tint(color, m, amount)


def paint(ctx):
    rng = ctx.rng
    ctx.vgradient((62, 62, 68), (8, 8, 10), z_top=1.08, z_bottom=0.2)
    n = ctx.noise(0.3, 6)
    ctx.tint((150, 150, 158), np.clip((n - 0.55) * 3, 0, 1) ** 1.5, 0.35)   # brume
    wisps(ctx, rng, 26, (0.1, 1.1), (0.04, 0.09), (200, 200, 210), 0.35)   # fumée large
    wisps(ctx, rng, 30, (0.15, 1.08), (0.012, 0.03), (235, 235, 242), 0.5)  # volutes
    wisps(ctx, rng, 22, (0.3, 1.05), (0.003, 0.007), (255, 255, 255), 0.75)  # filaments

    # filets argent
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for (x0, z0), (x1, z1) in (((1.08, 0.71), (1.98, 0.71)), ((1.08, 0.735), (1.70, 0.735)), ((2.06, 0.79), (2.92, 0.79)),
                               ((1.08, 1.02), (2.92, 1.02)), ((0.16, 0.58), (0.62, 0.86))):
        d.line([ctx.P(x0, z0), ctx.P(x1, z1)], fill=rgba((200, 202, 210)), width=max(2, int(ctx.L(0.004))))
    ctx.over(lay)
    text(ctx, "PHANTOM", 2.50, 0.935, 0.06, (210, 210, 218), kind="bold")
    text(ctx, "— silent —", 2.50, 0.88, 0.025, (140, 140, 148), kind="bold")
    text(ctx, "V", 1.52, 0.87, 0.14, (40, 40, 46), kind="black", stroke=(150, 150, 158), stroke_w=0.004)

    triangle_emblem(ctx, (235, 235, 242), outline=(10, 10, 12))
    ctx.grain(5)
    return ctx.result()


SKIN = dict(
    name="Fantome",
    palette=dict(Motif="Fantome", Sombre="Noir", Clair="Argent", Accent="Blanc", Accent2="GrisClair",
                 Verre="VerreBlanc", Gachette="GrisClair"),
    paint=paint,
)
