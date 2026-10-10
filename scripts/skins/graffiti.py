"""Graffiti : street art, tags, aérosol, coulures, couronnes."""
import math

from PIL import ImageDraw

from .common import crown, drips, rgba, soft_blobs, splatter, star, text, triangle_emblem

PINK, YEL, CYAN, PURP = (255, 45, 165), (255, 214, 40), (40, 200, 255), (140, 70, 255)
GREEN, BLACK, WHITE = (60, 230, 120), (15, 12, 18), (255, 255, 255)
ZONES = ("stock", "receiver", "handguard", "mag", "grip")


def _angle(ctx, zone, tall_angle):
    """Texte vertical sur les zones hautes et étroites (chargeur, poignée)."""
    return tall_angle if ctx.zh(zone) > ctx.zw(zone) else 0


def paint(ctx):
    rng, ds = ctx.rng, ctx.ds
    ctx.fill((246, 245, 242))
    n = ctx.noise(0.06 * ds, 4)
    ctx.tint((212, 209, 204), n ** 4 * 1.6, 0.7)  # grain de mur

    # nuages d'aérosol
    for col in (PURP, CYAN, YEL, PINK):
        blobs = []
        for zone in ZONES + ("receiver", "handguard", "stock"):
            x, z = ctx.rand_in(zone)
            blobs.append((x, z, rng.uniform(0.07, 0.14) * ds))
        soft_blobs(ctx, blobs, col, 0.025 * ds, amount=0.9, noise_mix=0.7, threshold=0.32)

    # poussière d'aérosol
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for _ in range(9000):
        x, z = ctx.rand_in("band") if rng.random() < 0.6 else ctx.rand_extent()
        r = ctx.L(rng.uniform(0.0015, 0.005) * ds)
        px, py = ctx.P(x, z)
        d.ellipse([px - r, py - r, px + r, py + r], fill=rgba(rng.choice((PINK, YEL, CYAN, PURP, BLACK)), 200))
    ctx.over(lay, 0.7)

    # éclaboussures
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for zone, col in (("stock", CYAN), ("grip", PINK), ("mag", YEL), ("handguard", PURP), ("receiver", GREEN),
                      ("stock", PINK), ("handguard", YEL)):
        x, z = ctx.rand_in(zone)
        splatter(ctx, d, x, z, rng.uniform(0.025, 0.05) * ds, col)
    ctx.over(lay)

    # gribouillis, flèches, étoiles
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for _ in range(14):
        x, z = ctx.rand_in(rng.choice(ZONES[:4]))
        pts = [ctx.P(x + i * 0.025 * ds, z + (0.02 if i % 2 else -0.02) * ds) for i in range(rng.randint(4, 9))]
        d.line(pts, fill=rgba(BLACK), width=max(2, int(ctx.L(0.006 * ds))), joint="curve")
    for _ in range(10):
        x, z = ctx.rand_in(rng.choice(("receiver", "handguard", "stock")))
        a, b = ctx.P(x, z), ctx.P(x + 0.12 * ds, z + rng.uniform(-0.04, 0.04) * ds)
        w = max(2, int(ctx.L(0.009 * ds)))
        col = rng.choice((PINK, CYAN, YEL, PURP))
        d.line([a, b], fill=rgba(BLACK), width=w + 6)
        d.line([a, b], fill=rgba(col), width=w)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        hl = ctx.L(0.035 * ds)
        head = [b, (b[0] - hl * math.cos(ang - 0.5), b[1] - hl * math.sin(ang - 0.5)),
                (b[0] - hl * math.cos(ang + 0.5), b[1] - hl * math.sin(ang + 0.5))]
        d.polygon(head, fill=rgba(col), outline=rgba(BLACK), width=3)
    for _ in range(16):
        x, z = ctx.rand_in(rng.choice(ZONES))
        star(ctx, d, x, z, rng.uniform(0.018, 0.035) * ds, rng.uniform(0.008, 0.014) * ds,
             rng.choice((YEL, WHITE, CYAN, PINK)), rot=rng.uniform(0, 1), outline=BLACK, width=3)
    ctx.over(lay)

    # gros tag « VANTA » sur la carcasse (lettres bulles + reflet + coulures)
    tx, tz = ctx.at("receiver", 0.5, 0.52)
    ts = min(0.25 * ds, 0.62 * ctx.zh("receiver"), 0.3 * ctx.zw("receiver"))
    text(ctx, "VANTA", tx, tz, ts, PINK, stroke=BLACK, stroke_w=0.07 * ts, angle=4, shadow=PURP)
    text(ctx, "VANTA", tx, tz, ts, (255, 140, 205), angle=4)
    text(ctx, "VANTA", tx - 0.02 * ts, tz + 0.02 * ts, ts, PINK, angle=4)
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    drips(ctx, d, tx - 1.4 * ts, tx + 1.4 * ts, tz - 0.36 * ts, PINK, 12, 0.55 * ts, 0.065 * ts, highlight=(255, 170, 215))
    hx, hz = ctx.at("handguard", 0.5, 0.6)
    hs = min(0.16 * ds, 0.55 * ctx.zh("handguard"), 0.28 * ctx.zw("handguard"))
    drips(ctx, d, hx - 1.3 * hs, hx + 1.3 * hs, hz - 0.4 * hs, YEL, 8, 0.6 * hs, 0.085 * hs, highlight=(255, 245, 170))
    ctx.over(lay)
    text(ctx, ctx.label, hx, hz, hs, YEL, stroke=BLACK, stroke_w=0.09 * hs, angle=-5, shadow=CYAN)

    # petits tags
    ms = min(0.13 * ds, 0.45 * min(ctx.zw("mag"), ctx.zh("mag")))
    text(ctx, "GG", *ctx.at("mag", 0.5, 0.5), ms, CYAN, stroke=BLACK, stroke_w=0.1 * ms,
         angle=_angle(ctx, "mag", -78), shadow=PURP)
    gs = min(0.08 * ds, 0.3 * min(ctx.zw("grip"), ctx.zh("grip")))
    text(ctx, "WILD", *ctx.at("grip", 0.5, 0.5), gs, YEL, stroke=BLACK, stroke_w=0.12 * gs,
         angle=_angle(ctx, "grip", 72), shadow=PINK)
    text(ctx, "STREET", *ctx.at("stock", 0.72, 0.9), 0.055 * ds, WHITE, stroke=BLACK, stroke_w=0.008 * ds, angle=3)
    text(ctx, "#1", *ctx.at("handguard", 0.92, 0.2), 0.07 * ds, PINK, stroke=BLACK, stroke_w=0.009 * ds, angle=-12)

    # couronnes
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    crown(ctx, d, *ctx.at("receiver", 0.95, 0.9), min(0.09 * ds, 0.3 * ctx.zh("receiver")), YEL, jewel=PINK)
    crown(ctx, d, *ctx.at("handguard", 0.3, 0.87), min(0.06 * ds, 0.25 * ctx.zh("handguard")), WHITE, jewel=CYAN)
    crown(ctx, d, *ctx.at("mag", 0.55, 0.9), min(0.06 * ds, 0.25 * ctx.zh("mag")), YEL, jewel=PINK)
    ctx.over(lay)

    triangle_emblem(ctx, YEL, outline=BLACK)
    ctx.grain(7)
    return ctx.result()


SKIN = dict(
    name="Graffiti",
    palette=dict(Motif="Graffiti", Sombre="Noir", Clair="Blanc", Accent="RoseVif", Accent2="Jaune",
                 Verre="VerreViolet", Lentille="LentilleViolet", Gachette="Jaune"),
    paint=paint,
)
