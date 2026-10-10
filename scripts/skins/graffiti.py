"""Graffiti : street art, tags, aérosol, coulures, couronnes."""
import math

from PIL import ImageDraw

from .common import crown, drips, rgba, soft_blobs, splatter, star, text, triangle_emblem

PINK, YEL, CYAN, PURP = (255, 45, 165), (255, 214, 40), (40, 200, 255), (140, 70, 255)
GREEN, BLACK, WHITE = (60, 230, 120), (15, 12, 18), (255, 255, 255)


def paint(ctx):
    rng = ctx.rng
    ctx.fill((246, 245, 242))
    n = ctx.noise(0.06, 4)
    ctx.tint((212, 209, 204), n ** 4 * 1.6, 0.7)  # grain de mur

    # nuages d'aérosol
    for col in (PURP, CYAN, YEL, PINK):
        blobs = []
        for zone in ("stock", "receiver", "handguard", "mag", "grip", "receiver", "handguard", "stock"):
            x, z = ctx.rand_in(zone)
            blobs.append((x, z, rng.uniform(0.07, 0.14)))
        soft_blobs(ctx, blobs, col, 0.025, amount=0.9, noise_mix=0.7, threshold=0.32)

    # poussière d'aérosol
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for _ in range(9000):
        x, z = ctx.rand_in("band") if rng.random() < 0.6 else (rng.uniform(0, 3.0), rng.uniform(0.1, 1.1))
        r = ctx.L(rng.uniform(0.0015, 0.005))
        px, py = ctx.P(x, z)
        d.ellipse([px - r, py - r, px + r, py + r], fill=rgba(rng.choice((PINK, YEL, CYAN, PURP, BLACK)), 200))
    ctx.over(lay, 0.7)

    # éclaboussures
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for zone, col in (("stock", CYAN), ("grip", PINK), ("mag", YEL), ("handguard", PURP), ("receiver", GREEN),
                      ("stock", PINK), ("handguard", YEL)):
        x, z = ctx.rand_in(zone)
        splatter(ctx, d, x, z, rng.uniform(0.025, 0.05), col)
    ctx.over(lay)

    # gribouillis au marqueur
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    for _ in range(14):
        x, z = ctx.rand_in(rng.choice(("stock", "receiver", "handguard", "mag")))
        pts = [ctx.P(x + i * 0.025, z + (0.02 if i % 2 else -0.02)) for i in range(rng.randint(4, 9))]
        d.line(pts, fill=rgba(BLACK), width=int(ctx.L(0.006)), joint="curve")
    for _ in range(10):  # flèches
        x, z = ctx.rand_in(rng.choice(("receiver", "handguard", "stock")))
        a, b = ctx.P(x, z), ctx.P(x + 0.12, z + rng.uniform(-0.04, 0.04))
        w = int(ctx.L(0.009))
        col = rng.choice((PINK, CYAN, YEL, PURP))
        d.line([a, b], fill=rgba(BLACK), width=w + 6)
        d.line([a, b], fill=rgba(col), width=w)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        hl = ctx.L(0.035)
        head = [b, (b[0] - hl * math.cos(ang - 0.5), b[1] - hl * math.sin(ang - 0.5)),
                (b[0] - hl * math.cos(ang + 0.5), b[1] - hl * math.sin(ang + 0.5))]
        d.polygon(head, fill=rgba(col), outline=rgba(BLACK), width=3)
    for _ in range(16):  # étoiles
        x, z = ctx.rand_in(rng.choice(("stock", "receiver", "handguard", "mag", "grip")))
        star(ctx, d, x, z, rng.uniform(0.018, 0.035), rng.uniform(0.008, 0.014), rng.choice((YEL, WHITE, CYAN, PINK)),
             rot=rng.uniform(0, 1), outline=BLACK, width=3)
    ctx.over(lay)

    # gros tags (lettres bulles avec ombre)
    text(ctx, "VANTA", 1.53, 0.86, 0.25, PINK, stroke=BLACK, stroke_w=0.018, angle=4, shadow=PURP)
    text(ctx, "VANTA", 1.53, 0.86, 0.25, (255, 140, 205), angle=4, kind="black", stroke=None)  # reflet
    text(ctx, "VANTA", 1.525, 0.865, 0.25, PINK, angle=4, kind="black")
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    drips(ctx, d, 1.18, 1.88, 0.77, PINK, 12, 0.14, 0.016, highlight=(255, 170, 215))
    drips(ctx, d, 2.15, 2.85, 0.83, YEL, 8, 0.1, 0.014, highlight=(255, 245, 170))
    ctx.over(lay)
    text(ctx, "AR-01", 2.50, 0.92, 0.16, YEL, stroke=BLACK, stroke_w=0.015, angle=-5, shadow=CYAN)
    text(ctx, "GG", 1.73, 0.36, 0.13, CYAN, stroke=BLACK, stroke_w=0.013, angle=-78, shadow=PURP)
    text(ctx, "WILD", 1.18, 0.40, 0.08, YEL, stroke=BLACK, stroke_w=0.01, angle=72, shadow=PINK)
    text(ctx, "STREET", 0.52, 0.96, 0.055, WHITE, stroke=BLACK, stroke_w=0.008, angle=3)
    text(ctx, "#1", 2.82, 0.80, 0.07, PINK, stroke=BLACK, stroke_w=0.009, angle=-12)

    # couronnes
    lay = ctx.layer()
    d = ImageDraw.Draw(lay)
    crown(ctx, d, 1.95, 1.00, 0.09, YEL, jewel=PINK)
    crown(ctx, d, 2.30, 1.00, 0.06, WHITE, jewel=CYAN)
    crown(ctx, d, 1.74, 0.52, 0.06, YEL, jewel=PINK)
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
