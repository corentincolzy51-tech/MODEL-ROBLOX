"""Toxic : acide fluo, slime qui coule, symboles biohazard, bandes de danger."""
import math

import numpy as np
from PIL import Image, ImageDraw

from .common import drips, rgba, text, triangle_emblem

BG = (24, 27, 24)
ACID, ACID_D, ACID_L = (160, 255, 30), (70, 150, 20), (225, 255, 170)
DARKG, YEL = (38, 84, 30), (225, 240, 40)


def biohazard(ctx, x, z, r, color, glow=None):
    """Symbole biohazard (trois croissants + anneau)."""
    size = int(ctx.L(r) * 2.6)
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    c = size / 2
    R = ctx.L(r)
    for k in range(3):
        a = -math.pi / 2 + k * math.tau / 3
        ox, oy = c + math.cos(a) * R * 0.48, c + math.sin(a) * R * 0.48
        d.ellipse([ox - R * 0.52, oy - R * 0.52, ox + R * 0.52, oy + R * 0.52], fill=255)
    for k in range(3):
        a = -math.pi / 2 + k * math.tau / 3
        ox, oy = c + math.cos(a) * R * 0.66, c + math.sin(a) * R * 0.66
        d.ellipse([ox - R * 0.38, oy - R * 0.38, ox + R * 0.38, oy + R * 0.38], fill=0)
    d.ellipse([c - R * 0.36, c - R * 0.36, c + R * 0.36, c + R * 0.36], fill=255)
    d.ellipse([c - R * 0.2, c - R * 0.2, c + R * 0.2, c + R * 0.2], fill=0)
    for k in range(3):
        a = math.pi / 2 + k * math.tau / 3
        d.line([(c, c), (c + math.cos(a) * R * 1.1, c + math.sin(a) * R * 1.1)], fill=0, width=max(2, int(R * 0.09)))
    d.ellipse([c - R * 0.12, c - R * 0.12, c + R * 0.12, c + R * 0.12], fill=0)
    lay = ctx.layer()
    px, py = ctx.P(x, z)
    lay.paste(Image.new("RGBA", m.size, rgba(color)), (int(px - c), int(py - c)), m)
    if glow:
        ctx.glow(lay, glow, 0.8)
    else:
        ctx.over(lay)


def hazard_band(ctx, x0, z0, x1, z1, c1, c2, step=0.06):
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    h = z1 - z0
    x = x0 - h
    i = 0
    while x < x1:
        poly = [ctx.P(x, z0), ctx.P(x + step / 2, z0), ctx.P(x + step / 2 + h, z1), ctx.P(x + h, z1)]
        d.polygon(poly, fill=rgba(c1 if i % 2 == 0 else c2))
        x += step / 2
        i += 1
    clip = Image.new("L", lay.size, 0)
    ImageDraw.Draw(clip).rectangle(ctx.box(x0, z0, x1, z1), fill=255)
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(clip))))
    ctx.over(lay)


def paint(ctx):
    rng = ctx.rng
    ctx.fill(BG)
    n = ctx.noise(0.12, 5)
    ctx.tint((48, 54, 46), np.clip((n - 0.5) * 3, 0, 1), 0.8)   # plaques plus claires
    ctx.tint((12, 14, 12), np.clip((0.45 - n) * 3, 0, 1), 0.7)  # crasse
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for _ in range(260):  # rayures
        x, z = rng.uniform(0, 3.0), rng.uniform(0.1, 1.1)
        ln = rng.uniform(0.02, 0.09)
        a = rng.uniform(-0.4, 0.4)
        d.line([ctx.P(x, z), ctx.P(x + ln * math.cos(a), z + ln * math.sin(a))], fill=(95, 105, 92, 150), width=2)
    ctx.over(lay)

    # bandes de danger
    hazard_band(ctx, 2.06, 0.74, 2.94, 0.80, YEL, (20, 20, 18))
    hazard_band(ctx, 0.16, 0.56, 0.66, 0.60, YEL, (20, 20, 18))
    hazard_band(ctx, 1.62, 0.14, 1.90, 0.19, ACID, (20, 20, 18), step=0.05)

    # flaques de slime + coulures (depuis le haut des pièces)
    slime = ctx.layer()
    d = ImageDraw.Draw(slime)
    for x0, x1, ztop in ((1.06, 2.0, 1.06), (2.04, 2.94, 1.06), (0.10, 0.66, 1.02), (1.56, 1.86, 0.60), (1.06, 1.34, 0.64)):
        pts = [ctx.P(x0, ztop + 0.02)]
        x = x0
        while x < x1:
            pts.append(ctx.P(x, ztop - rng.uniform(0.02, 0.05)))
            x += rng.uniform(0.03, 0.07)
        pts += [ctx.P(x1, ztop - 0.03), ctx.P(x1, ztop + 0.02)]
        d.polygon(pts, fill=rgba(ACID))
        drips(ctx, d, x0 + 0.02, x1 - 0.02, ztop - 0.03, ACID, int((x1 - x0) * 22), 0.22, 0.02, highlight=ACID_L)
    for _ in range(40):  # bulles
        x, z = ctx.rand_in(rng.choice(("receiver", "handguard", "stock", "mag")))
        r = ctx.L(rng.uniform(0.006, 0.02))
        px, py = ctx.P(x, z)
        d.ellipse([px - r, py - r, px + r, py + r], outline=rgba(ACID), width=max(2, int(r * 0.25)))
    ctx.glow(slime, 0.025, 0.55)

    biohazard(ctx, 1.50, 0.85, 0.12, ACID, glow=0.02)
    biohazard(ctx, 1.735, 0.36, 0.07, ACID, glow=0.015)
    biohazard(ctx, 2.80, 0.90, 0.055, DARKG)
    biohazard(ctx, 0.58, 0.73, 0.045, DARKG)

    text(ctx, "TOXIC", 2.42, 0.945, 0.11, ACID, stroke=(10, 20, 8), stroke_w=0.01)
    text(ctx, "C4H10FO2P", 2.42, 0.872, 0.028, (120, 170, 90), kind="mono")
    text(ctx, "BIOHAZARD // LVL 4", 1.85, 0.72, 0.026, (140, 190, 100), kind="mono")
    text(ctx, "DANGER", 1.18, 0.42, 0.05, YEL, kind="black", angle=72, stroke=(10, 10, 8), stroke_w=0.006)
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    a, b, c = ctx.P(1.92, 0.98), ctx.P(1.99, 0.98), ctx.P(1.955, 1.04)  # triangle attention
    d.polygon([a, b, c], fill=rgba(YEL), outline=rgba((10, 10, 8)), width=3)
    ctx.over(lay)
    text(ctx, "!", 1.955, 0.995, 0.04, (10, 10, 8), kind="black")

    triangle_emblem(ctx, ACID, outline=(10, 20, 8), glow=0.02)
    ctx.grain(8)
    return ctx.result()


SKIN = dict(
    name="Toxic",
    palette=dict(Motif="Toxic", Sombre="Noir", Clair="Gris", Accent="VertAcide", Accent2="VertSombre",
                 Verre="VerreVert", Lentille="LentilleVert", Gachette="VertAcide"),
    paint=paint,
)
