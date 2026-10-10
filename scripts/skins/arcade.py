"""Arcade : rétro néon, grille synthwave, pixel art, scanlines."""
import math

import numpy as np
from PIL import ImageDraw

from .common import pixel_text, rgba, sprite, triangle_emblem

MAG, CYAN, BLUE, YEL, PURP = (255, 40, 205), (50, 225, 255), (70, 90, 255), (255, 220, 50), (150, 60, 255)

INVADER = ["  X     X  ", "   X   X   ", "  XXXXXXX  ", " XX XXX XX ", "XXXXXXXXXXX",
           "X XXXXXXX X", "X X     X X", "   XX XX   "]
HEART = [" XX XX ", "XXXXXXX", "XXXXXXX", " XXXXX ", "  XXX  ", "   X   "]
STAR = ["   X   ", "   X   ", "XXXXXXX", " XXXXX ", "  XXX  ", " XX XX ", "X     X"]
UFO = ["    WWW    ", "   WBBBW   ", "  XXXXXXX  ", " XXYXXYXXY ", "XXXXXXXXXXX", "  XX   XX  ", "   B   B   "]
COIN = [" XXXX ", "XXYYXX", "XYXXYX", "XYXXYX", "XXYYXX", " XXXX "]
CROSS = ["  XXX  ", "  XXX  ", "XXXXXXX", "XXXXXXX", "XXXXXXX", "  XXX  ", "  XXX  "]
SWORD = ["      X", "     X ", "    X  ", " X X   ", "  X    ", " X X   ", "X      "]


def paint(ctx):
    rng, ds = ctx.rng, ctx.ds
    ex0, ez0, ex1, ez1 = ctx.extent()
    ctx.vgradient((46, 10, 78), (10, 4, 28), z_top=ez1, z_bottom=ez0)

    # grille synthwave (perspective) sous l'horizon + soleil rétro
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    bx0, bz0, bx1, bz1 = ctx.zones["band"]
    horizon = bz0 + 0.2 * (bz1 - bz0)
    vx = (ex0 + ex1) / 2
    w = max(2, int(ctx.L(0.004 * ds)))
    for k in range(-40, 41):
        d.line([ctx.P(vx + k * 0.01 * ds, horizon), ctx.P(vx + k * 0.16 * ds, ez0 - 0.3)], fill=rgba(MAG, 200), width=w)
    z = horizon
    step = 0.012 * ds
    while z > ez0 - 0.2:
        d.line([ctx.P(ex0 - 0.2, z), ctx.P(ex1 + 0.2, z)], fill=rgba(MAG, 200), width=w)
        step *= 1.32
        z -= step
    ctx.glow(lay, 0.01 * ds, 0.8)
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    cx, cy = ctx.P(*ctx.at("handguard", 0.6, 0.6))
    R = ctx.L(min(0.105 * ds, 0.38 * ctx.zh("handguard")))
    for i in range(int(R * 2)):
        y = cy - R + i
        t = i / (R * 2)
        if t > 0.55 and int((t - 0.55) * 40) % 2 == 1:
            continue
        half = math.sqrt(max(0.0, R * R - (y - cy) ** 2))
        d.line([(cx - half, y), (cx + half, y)], fill=(255, int(220 - 170 * t), int(60 + 120 * t), 255))
    ctx.glow(lay, 0.02 * ds, 0.6)

    # pixel art (taille d'un pixel limitée par la hauteur de la zone)
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    sh = (10, 4, 20)
    for rows, zone, u, v, px, cols in (
        (INVADER, "receiver", 0.25, 0.62, 0.012, {"X": CYAN}),
        (INVADER, "receiver", 0.6, 0.8, 0.008, {"X": (120, 255, 140)}),
        (UFO, "receiver", 0.85, 0.55, 0.01, {"X": MAG, "W": (255, 255, 255), "B": CYAN, "Y": YEL}),
        (HEART, "stock", 0.8, 0.75, 0.009, {"X": (255, 50, 90)}),
        (HEART, "handguard", 0.2, 0.85, 0.007, {"X": (255, 50, 90)}),
        (STAR, "handguard", 0.92, 0.75, 0.008, {"X": YEL}),
        (STAR, "receiver", 0.05, 0.25, 0.006, {"X": YEL}),
        (COIN, "mag", 0.5, 0.75, 0.01, {"X": YEL, "Y": (200, 140, 20)}),
        (INVADER, "mag", 0.5, 0.3, 0.01, {"X": MAG}),
        (CROSS, "grip", 0.5, 0.7, 0.009, {"X": CYAN}),
        (HEART, "grip", 0.5, 0.25, 0.008, {"X": MAG}),
        (SWORD, "handguard", 0.88, 0.2, 0.007, {"X": (230, 230, 255)}),
    ):
        size = min(px * ds, ctx.zh(zone) / (len(rows) * 2.2), ctx.zw(zone) / (len(rows[0]) * 1.6))
        sprite(ctx, d, rows, *ctx.at(zone, u, v), size, cols, shadow=sh)
    bx0, bz0, bx1, bz1 = ctx.zones["band"]
    for _ in range(40):  # pixels étoiles
        x, z = rng.uniform(bx0, bx1), rng.uniform(bz0 + 0.25 * (bz1 - bz0), bz1)
        p = ctx.L(rng.choice((0.006, 0.009)) * ds)
        px, py = ctx.P(x, z)
        d.rectangle([px, py, px + p, py + p], fill=rgba(rng.choice((CYAN, MAG, YEL, (255, 255, 255)))))
    ctx.glow(lay, 0.008 * ds, 0.7)

    # textes rétro
    for s_, zone, u, v, p, col in (("1UP", "receiver", 0.1, 0.92, 0.006, CYAN),
                                   ("HI-SCORE 99999", "receiver", 0.55, 0.92, 0.005, YEL),
                                   ("INSERT COIN", "handguard", 0.3, 0.9, 0.005, MAG),
                                   ("PLAYER 1", "stock", 0.55, 0.9, 0.005, CYAN),
                                   ("GAME ON", "handguard", 0.1, 0.22, 0.0035, CYAN),
                                   ("LVL 99", "receiver", 0.55, 0.18, 0.005, MAG)):
        ctx.glow(pixel_text(ctx, s_, *ctx.at(zone, u, v), p * ds, col, shadow=(10, 4, 20)), 0.006 * ds, 0.6)

    # scanlines
    from PIL import Image
    arr = np.asarray(ctx.img, np.float32)
    step = max(2, int(ctx.L(0.006 * ds)))
    arr[::step, :, :3] *= 0.82
    ctx.img = Image.fromarray(arr.astype(np.uint8), "RGBA")

    triangle_emblem(ctx, CYAN, outline=(10, 4, 20), inner=MAG, glow=0.02 * ds)
    return ctx.result()


SKIN = dict(
    name="Arcade",
    palette=dict(Motif="Arcade", Sombre="NoirViolet", Clair="Bleu", Accent="MagentaNeon", Accent2="CyanNeon",
                 Verre="VerreMagenta", Lentille="LentilleMagenta", Gachette="CyanNeon"),
    paint=paint,
)
