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
    rng, ds = ctx.rng, ctx.ds
    ctx.fill(BG)
    n = ctx.noise(0.12 * ds, 5)
    ctx.tint((48, 54, 46), np.clip((n - 0.5) * 3, 0, 1), 0.8)   # plaques plus claires
    ctx.tint((12, 14, 12), np.clip((0.45 - n) * 3, 0, 1), 0.7)  # crasse
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for _ in range(260):  # rayures
        x, z = ctx.rand_extent()
        ln = rng.uniform(0.02, 0.09) * ds
        a = rng.uniform(-0.4, 0.4)
        d.line([ctx.P(x, z), ctx.P(x + ln * math.cos(a), z + ln * math.sin(a))], fill=(95, 105, 92, 150), width=2)
    ctx.over(lay)

    # bandes de danger en bas des pièces
    for zone, c1, k in (("handguard", YEL, 0.2), ("stock", YEL, 0.1), ("mag", ACID, 0.14)):
        x0, z0, x1, z1 = ctx.zones[zone]
        hazard_band(ctx, x0, z0, x1, z0 + k * (z1 - z0), c1, (20, 20, 18), step=0.06 * ds)

    # flaques de slime + coulures (depuis le haut des pièces)
    slime = ctx.layer()
    d = ImageDraw.Draw(slime)
    for zone in ("receiver", "handguard", "stock", "mag", "grip"):
        x0, _, x1, ztop = ctx.zones[zone]
        ztop += 0.03 * ds
        pts = [ctx.P(x0, ztop + 0.02 * ds)]
        x = x0
        while x < x1:
            pts.append(ctx.P(x, ztop - rng.uniform(0.02, 0.05) * ds))
            x += rng.uniform(0.03, 0.07) * ds
        pts += [ctx.P(x1, ztop - 0.03 * ds), ctx.P(x1, ztop + 0.02 * ds)]
        d.polygon(pts, fill=rgba(ACID))
        ln = min(0.22 * ds, 0.6 * ctx.zh(zone))
        drips(ctx, d, x0 + 0.02 * ds, x1 - 0.02 * ds, ztop - 0.03 * ds, ACID, max(3, int((x1 - x0) / ds * 22)),
              ln, 0.02 * ds, highlight=ACID_L)
    for _ in range(40):  # bulles
        x, z = ctx.rand_in(rng.choice(("receiver", "handguard", "stock", "mag")))
        r = ctx.L(rng.uniform(0.006, 0.02) * ds)
        px, py = ctx.P(x, z)
        d.ellipse([px - r, py - r, px + r, py + r], outline=rgba(ACID), width=max(2, int(r * 0.25)))
    ctx.glow(slime, 0.025 * ds, 0.55)

    biohazard(ctx, *ctx.at("receiver", 0.45, 0.48), min(0.12 * ds, 0.33 * ctx.zh("receiver")), ACID, glow=0.02 * ds)
    biohazard(ctx, *ctx.at("mag", 0.5, 0.5), min(0.07 * ds, 0.3 * min(ctx.zw("mag"), ctx.zh("mag"))), ACID,
              glow=0.015 * ds)
    biohazard(ctx, *ctx.at("handguard", 0.86, 0.55), min(0.055 * ds, 0.28 * ctx.zh("handguard")), DARKG)
    biohazard(ctx, *ctx.at("stock", 0.85, 0.42), min(0.045 * ds, 0.25 * ctx.zh("stock")), DARKG)

    tx, tz = ctx.at("handguard", 0.42, 0.62)
    ts = min(0.11 * ds, 0.4 * ctx.zh("handguard"), 0.2 * ctx.zw("handguard"))
    text(ctx, "TOXIC", tx, tz, ts, ACID, stroke=(10, 20, 8), stroke_w=0.09 * ts)
    text(ctx, "C4H10FO2P", tx, tz - 0.65 * ts, 0.26 * ts, (120, 170, 90), kind="mono")
    text(ctx, "BIOHAZARD // LVL 4", *ctx.at("receiver", 0.82, 0.12), 0.026 * ds, (140, 190, 100), kind="mono")
    gs = min(0.05 * ds, 0.22 * min(ctx.zw("grip"), ctx.zh("grip")))
    text(ctx, "DANGER", *ctx.at("grip", 0.5, 0.5), gs, YEL, kind="black",
         angle=72 if ctx.zh("grip") > ctx.zw("grip") else 0, stroke=(10, 10, 8), stroke_w=0.12 * gs)
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    wx, wz = ctx.at("receiver", 0.95, 0.82)
    w = 0.035 * ds
    d.polygon([ctx.P(wx - w, wz - 0.03 * ds), ctx.P(wx + w, wz - 0.03 * ds), ctx.P(wx, wz + 0.03 * ds)],
              fill=rgba(YEL), outline=rgba((10, 10, 8)), width=3)
    ctx.over(lay)
    text(ctx, "!", wx, wz - 0.012 * ds, 0.04 * ds, (10, 10, 8), kind="black")

    triangle_emblem(ctx, ACID, outline=(10, 20, 8), glow=0.02 * ds)
    ctx.grain(8)
    return ctx.result()


SKIN = dict(
    name="Toxic",
    palette=dict(Motif="Toxic", Sombre="Noir", Clair="Gris", Accent="VertAcide", Accent2="VertSombre",
                 Verre="VerreVert", Lentille="LentilleVert", Gachette="VertAcide"),
    paint=paint,
)
