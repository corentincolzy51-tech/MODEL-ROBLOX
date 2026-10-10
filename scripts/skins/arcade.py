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
    rng = ctx.rng
    ctx.vgradient((46, 10, 78), (10, 4, 28), z_top=1.1, z_bottom=0.1)

    # grille synthwave (perspective) sur la moitié basse + soleil rétro
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    horizon = 0.80
    vx = 1.55
    w = max(2, int(ctx.L(0.004)))
    for k in range(-40, 41):
        d.line([ctx.P(vx + k * 0.01, horizon), ctx.P(vx + k * 0.16, -0.2)], fill=rgba(MAG, 200), width=w)
    z = horizon
    step = 0.012
    while z > -0.1:
        d.line([ctx.P(-0.1, z), ctx.P(3.2, z)], fill=rgba(MAG, 200), width=w)
        step *= 1.32
        z -= step
    ctx.glow(lay, 0.01, 0.8)
    # soleil rayé
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    cx, cy = ctx.P(2.56, 0.925)
    R = ctx.L(0.105)
    for i in range(int(R * 2)):
        y = cy - R + i
        t = i / (R * 2)
        if t > 0.55 and int((t - 0.55) * 40) % 2 == 1:
            continue
        half = math.sqrt(max(0.0, R * R - (y - cy) ** 2))
        col = (255, int(220 - 170 * t), int(60 + 120 * t), 255)
        d.line([(cx - half, y), (cx + half, y)], fill=col)
    ctx.glow(lay, 0.02, 0.6)

    # pixel art
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    sh = (10, 4, 20)
    sprite(ctx, d, INVADER, 1.30, 0.90, 0.012, {"X": CYAN}, shadow=sh)
    sprite(ctx, d, INVADER, 1.62, 0.95, 0.008, {"X": (120, 255, 140)}, shadow=sh)
    sprite(ctx, d, UFO, 1.86, 0.86, 0.01, {"X": MAG, "W": (255, 255, 255), "B": CYAN, "Y": YEL}, shadow=sh)
    sprite(ctx, d, HEART, 0.58, 0.92, 0.009, {"X": (255, 50, 90)}, shadow=sh)
    sprite(ctx, d, HEART, 2.20, 0.97, 0.007, {"X": (255, 50, 90)}, shadow=sh)
    sprite(ctx, d, STAR, 2.86, 0.96, 0.008, {"X": YEL}, shadow=sh)
    sprite(ctx, d, STAR, 1.10, 0.74, 0.006, {"X": YEL}, shadow=sh)
    sprite(ctx, d, COIN, 1.735, 0.46, 0.01, {"X": YEL, "Y": (200, 140, 20)}, shadow=sh)
    sprite(ctx, d, INVADER, 1.75, 0.27, 0.01, {"X": MAG}, shadow=sh)
    sprite(ctx, d, CROSS, 1.17, 0.48, 0.009, {"X": CYAN}, shadow=sh)
    sprite(ctx, d, HEART, 1.20, 0.30, 0.008, {"X": MAG}, shadow=sh)
    sprite(ctx, d, SWORD, 2.92 - 0.06, 0.80, 0.007, {"X": (230, 230, 255)}, shadow=sh)
    for _ in range(40):  # pixels étoiles
        x, z = rng.uniform(0.1, 2.95), rng.uniform(0.82, 1.06)
        p = ctx.L(rng.choice((0.006, 0.009)))
        px, py = ctx.P(x, z)
        d.rectangle([px, py, px + p, py + p], fill=rgba(rng.choice((CYAN, MAG, YEL, (255, 255, 255)))))
    ctx.glow(lay, 0.008, 0.7)

    # textes rétro
    for s, x, z, p, col in (("1UP", 1.14, 1.01, 0.006, CYAN), ("HI-SCORE 99999", 1.62, 1.01, 0.005, YEL),
                            ("INSERT COIN", 2.30, 1.01, 0.005, MAG), ("PLAYER 1", 0.40, 0.97, 0.005, CYAN),
                            ("GAME ON", 2.11, 0.80, 0.0035, CYAN), ("LVL 99", 1.62, 0.73, 0.005, MAG)):
        ctx.glow(pixel_text(ctx, s, x, z, p, col, shadow=(10, 4, 20)), 0.006, 0.6)

    # scanlines
    arr = np.asarray(ctx.img, np.float32)
    step = max(2, int(ctx.L(0.006)))
    arr[::step, :, :3] *= 0.82
    from PIL import Image
    ctx.img = Image.fromarray(arr.astype(np.uint8), "RGBA")

    triangle_emblem(ctx, CYAN, outline=(10, 4, 20), inner=MAG, glow=0.02)
    return ctx.result()


SKIN = dict(
    name="Arcade",
    palette=dict(Motif="Arcade", Sombre="NoirViolet", Clair="Bleu", Accent="MagentaNeon", Accent2="CyanNeon",
                 Verre="VerreMagenta", Lentille="LentilleMagenta", Gachette="CyanNeon"),
    paint=paint,
)
