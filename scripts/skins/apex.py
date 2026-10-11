"""Apex (Légendaire) : céramique blanche et graphite, filets dorés, noyau d'énergie,
anneaux qui tournent, inspection (F) et effet d'élimination."""
import numpy as np
from PIL import ImageDraw

from .common import rgba, text, triangle_emblem

WHITE, WHITE_D = (238, 240, 244), (200, 204, 212)
GRAPH, GRAPH_L = (38, 40, 46), (62, 65, 74)
GOLD, GOLD_D = (232, 178, 52), (150, 105, 25)
CORE = (150, 240, 255)


def _panel(ctx, d, zone, u0, v0, u1, v1, col, line, ch=0.12):
    """Panneau à coins coupés, bordé d'une fine ligne de découpe."""
    x0, z0 = ctx.at(zone, u0, v0)
    x1, z1 = ctx.at(zone, u1, v1)
    c = min(x1 - x0, z1 - z0) * ch
    poly = [(x0 + c, z0), (x1, z0), (x1, z1 - c), (x1 - c, z1), (x0, z1), (x0, z0 + c)]
    pp = [ctx.P(a, b) for a, b in poly]
    d.polygon(pp, fill=rgba(col))
    d.line(pp + [pp[0]], fill=rgba(line), width=max(2, int(ctx.L(0.005 * ctx.ds))))


def paint(ctx):
    rng, ds = ctx.rng, ctx.ds
    ex0, ez0, ex1, ez1 = ctx.extent()
    ctx.vgradient(WHITE, WHITE_D, z_top=ez1, z_bottom=ez0)
    n = ctx.noise(0.25 * ds, 4)
    ctx.tint((255, 255, 255), np.clip((n - 0.55) * 3, 0, 1), 0.25)

    # panneaux graphite dans le bas des pièces + découpes
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for zone in ("receiver", "handguard", "stock"):
        _panel(ctx, d, zone, 0.04, 0.0, 0.96, 0.42, GRAPH, (20, 20, 24))
        _panel(ctx, d, zone, 0.08, 0.55, 0.45, 0.92, WHITE, (170, 174, 184))
        _panel(ctx, d, zone, 0.52, 0.55, 0.92, 0.92, WHITE, (170, 174, 184))
    for zone in ("mag", "grip"):
        _panel(ctx, d, zone, 0.1, 0.05, 0.9, 0.55, GRAPH, (20, 20, 24))
    ctx.over(lay)

    # trame hexagonale discrète sur le graphite
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    s = 0.03 * ds
    for zone in ("receiver", "handguard", "stock", "mag", "grip"):
        x0, z0, x1, z1 = ctx.zones[zone]
        zt = z0 + 0.42 * (z1 - z0) if zone in ("receiver", "handguard", "stock") else z0 + 0.55 * (z1 - z0)
        j = 0
        z = z0
        while z < zt:
            x = x0 + (s * 0.87 if j % 2 else 0)
            while x < x1:
                pts = [ctx.P(x + s * 0.5 * np.cos(a), z + s * 0.5 * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 7)]
                d.line(pts, fill=rgba(GRAPH_L), width=1)
                x += s * 1.74
            z += s * 0.75
            j += 1
    ctx.over(lay, 0.8)

    # filets dorés et marquages
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    w = max(2, int(ctx.L(0.007 * ds)))
    for zone in ("receiver", "handguard", "stock"):
        x0, z0, x1, z1 = ctx.zones[zone]
        zz = z0 + 0.46 * (z1 - z0)
        d.line([ctx.P(x0 + 0.03 * ds, zz), ctx.P(x1 - 0.03 * ds, zz)], fill=rgba(GOLD), width=w)
        d.line([ctx.P(x1 - 0.12 * ds, zz), ctx.P(x1 - 0.08 * ds, zz + 0.04 * ds), ctx.P(x1 - 0.02 * ds, zz + 0.04 * ds)],
               fill=rgba(GOLD), width=w)
    ctx.over(lay)
    ts = min(0.13 * ds, 0.33 * ctx.zh("receiver"), 0.2 * ctx.zw("receiver"))
    text(ctx, "APEX", *ctx.at("receiver", 0.5, 0.74), ts, GOLD, kind="black", stroke=GOLD_D, stroke_w=0.04 * ts,
         shadow=(120, 124, 134))
    text(ctx, "A-01 // CORE ONLINE", *ctx.at("receiver", 0.5, 0.2), 0.026 * ds, CORE, kind="mono")
    text(ctx, "VANTA", *ctx.at("handguard", 0.3, 0.74), 0.045 * ds, GRAPH, kind="black")
    text(ctx, "Ⅰ Ⅱ Ⅲ", *ctx.at("handguard", 0.75, 0.74), 0.03 * ds, GOLD_D, kind="serif")
    triangle_emblem(ctx, GOLD, outline=GRAPH, inner=CORE)
    ctx.grain(3)
    return ctx.result()


import phantom_variants  # noqa: E402

SKIN = dict(
    name="Apex",
    rarity="Légendaire",
    weapons=("ar01",),
    pieces={"ar01": phantom_variants.apex_pieces},
    palette=dict(Motif="Apex", Sombre="Graphite", Clair="Blanc", Accent="Or", Accent2="Graphite",
                 Verre="VerreBleu", Lentille="LentilleBleu", Gachette="Or", Neon="ApexNoyau"),
    effect=dict(Effet="Apex", NeonAnime="ApexNoyau", CouleurTraceur=(170, 240, 255), CouleurFlamme=(150, 230, 255),
                Inspection=True, EffetElimination="Apex"),
    paint=paint,
)
