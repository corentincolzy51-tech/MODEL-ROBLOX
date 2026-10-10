"""Sakura : fleurs de cerisier, nuages roses aquarelle, branche brune."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import skin_sakura  # noqa: E402


def paint(ctx):
    D = ctx._D

    def rect(zone):
        x0, z0, x1, z1 = zone
        (xa, za), (xb, zb) = D(x0, z0), D(x1, z1)
        return (xa, za, xb, zb)

    Z = ctx.zones
    zones = {k: rect(Z[k]) for k in ("stock", "bouquet", "receiver", "grip", "mag", "handguard")}
    (b0, b1) = Z["branch"]
    zones["branch"] = (D(*b0), D(*b1))
    return skin_sakura.generate(ctx.W, ctx.H, ctx._w2p, ctx.ppm, zones, scale=ctx.flower_scale)


SKIN = dict(
    name="Sakura",
    palette=dict(Motif="Sakura", Sombre="Noir", Clair="Blanc", Accent="Rose", Accent2="Rose",
                 Verre="Verre", Lentille="LentilleRose", Gachette="Blanc"),
    paint=paint,
)
