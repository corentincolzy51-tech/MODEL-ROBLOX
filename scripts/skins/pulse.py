"""Pulse (Rare) : carbone sombre, pistes de circuit cyan ; les bandes néon en segments
sont parcourues par une onde de lumière (module EffetsSkins)."""
import math

import numpy as np
from PIL import Image, ImageDraw

from .common import rgba, text, triangle_emblem

CYAN, CYAN_D, WHITE = (0, 215, 255), (0, 120, 170), (220, 250, 255)


def carbon(ctx, cell_studs, c1, c2):
    """Tissage carbone : damier diagonal avec reflet par case."""
    cell = max(4, ctx.L(cell_studs))
    yy, xx = np.mgrid[0:ctx.H, 0:ctx.W].astype(np.float32)
    u, v = (xx + yy) / cell, (xx - yy) / cell
    check = ((np.floor(u) + np.floor(v)) % 2).astype(np.float32)
    fu, fv = u - np.floor(u), v - np.floor(v)
    sheen = np.where(check > 0, fu, fv)
    shade = 0.55 + 0.45 * np.sin(sheen * math.pi)
    a, b = np.array(c1, np.float32), np.array(c2, np.float32)
    col = (a * check[..., None] + b * (1 - check[..., None])) * shade[..., None]
    alpha = np.full((ctx.H, ctx.W, 1), 255, np.float32)
    ctx.img = Image.fromarray(np.concatenate([col, alpha], 2).clip(0, 255).astype(np.uint8), "RGBA")


def paint(ctx):
    rng, ds = ctx.rng, ctx.ds
    carbon(ctx, 0.022 * ds, (44, 48, 58), (24, 26, 33))
    n = ctx.noise(0.3 * ds, 4)
    ctx.tint((8, 10, 14), np.clip((0.5 - n) * 2, 0, 1), 0.5)

    # pistes de circuit (angles droits + pastilles)
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    w = max(2, int(ctx.L(0.006 * ds)))
    for _ in range(26):
        zone = rng.choice(("receiver", "handguard", "stock", "mag", "grip", "receiver", "handguard"))
        x, z = ctx.rand_in(zone)
        x0, z0, x1, z1 = ctx.zones[zone]
        pts = [(x, z)]
        horiz = rng.random() < 0.6
        for _ in range(rng.randint(2, 4)):
            if horiz:
                x = min(max(x + rng.choice((-1, 1)) * rng.uniform(0.06, 0.2) * ds, x0), x1)
            else:
                z = min(max(z + rng.choice((-1, 1)) * rng.uniform(0.03, 0.08) * ds, z0), z1)
            horiz = not horiz
            pts.append((x, z))
        pp = [ctx.P(a, b) for a, b in pts]
        d.line(pp, fill=rgba(CYAN), width=w, joint="curve")
        for px, py in (pp[0], pp[-1]):
            r = ctx.L(0.011 * ds)
            d.ellipse([px - r, py - r, px + r, py + r], outline=rgba(CYAN), width=w)
            r2 = r * 0.45
            d.ellipse([px - r2, py - r2, px + r2, py + r2], fill=rgba(WHITE))
    ctx.glow(lay, 0.012 * ds, 0.9)

    # chevrons vers le canon sur la bande
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    bx0, bz0, bx1, bz1 = ctx.zones["band"]
    zc = bz0 + 0.18 * (bz1 - bz0)
    x = bx0 + 0.2 * ds
    while x < bx1 - 0.1 * ds:
        h = 0.018 * ds
        d.line([ctx.P(x, zc + h), ctx.P(x + h, zc), ctx.P(x, zc - h)], fill=rgba(CYAN_D), width=w)
        x += 0.07 * ds
    ctx.over(lay, 0.8)

    ts = min(0.12 * ds, 0.42 * ctx.zh("receiver"), 0.22 * ctx.zw("receiver"))
    text(ctx, "PULSE", *ctx.at("receiver", 0.5, 0.45), ts, (16, 18, 24), kind="black", stroke=CYAN, stroke_w=0.06 * ts)
    text(ctx, "SYNC // 120 BPM", *ctx.at("handguard", 0.5, 0.35), 0.03 * ds, CYAN, kind="mono")
    triangle_emblem(ctx, CYAN, outline=(8, 10, 14), glow=0.02 * ds)
    ctx.grain(5)
    return ctx.result()


import phantom_variants  # noqa: E402

SKIN = dict(
    name="Pulse",
    rarity="Rare",
    weapons=("ar01",),
    pieces={"ar01": phantom_variants.pulse_pieces},
    palette=dict(Motif="Pulse", Sombre="Noir", Clair="GrisFonce", Accent="CyanPulse", Accent2="Carbone",
                 Verre="VerreBleu", Lentille="LentilleBleu", Gachette="CyanPulse", Neon="CyanPulse"),
    effect=dict(Effet="Pulse", NeonAnime="CyanPulse", CouleurTraceur=(90, 230, 255), CouleurFlamme=(120, 220, 255)),
    paint=paint,
)
