"""Sakura : fleurs de cerisier, nuages roses aquarelle, branche brune."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import skin_sakura  # noqa: E402


def paint(ctx):
    D = ctx._D

    def rect(a, b, c, d):
        (xa, za), (xb, zb) = D(a, b), D(c, d)
        return (xa, za, xb, zb)

    zones = {
        "stock": rect(0.05, 0.50, 0.70, 1.04),
        "bouquet": rect(0.10, 0.56, 0.52, 0.98),
        "receiver": rect(1.04, 0.64, 2.02, 1.06),
        "grip": rect(1.00, 0.18, 1.34, 0.62),
        "mag": rect(1.55, 0.12, 1.92, 0.58),
        "handguard": rect(2.02, 0.74, 2.95, 1.05),
        "branch": (D(0.55, 0.80), D(2.85, 0.96)),
    }
    return skin_sakura.generate(ctx.W, ctx.H, ctx._w2p, ctx.ppm, zones)


SKIN = dict(
    name="Sakura",
    palette=dict(Motif="Sakura", Sombre="Noir", Clair="Blanc", Accent="Rose", Accent2="Rose",
                 Verre="Verre", Gachette="Blanc"),
    paint=paint,
)
