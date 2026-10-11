"""Variantes de modèle de la VANTA AR-01 pour les skins Rare / Épique / Légendaire.

  pulse_pieces()   : modèle de base + bandes néon en 16 segments (Neon01..Neon16),
                     animés en onde par le module EffetsSkins (rare : pas de changement de forme)
  inferno_pieces() : modèle de base + fissures de lave néon (Neon) + ailettes + cache-flamme
  apex_pieces()    : modèle exclusif (crosse squelette, garde-main ouvert sur un noyau
                     d'énergie Neon, anneaux hexagonaux Neon01..03 qui tournent, embout angulaire)
La poignée, le chargeur, la gâchette, le levier et le viseur restent au même endroit que
sur la Phantom : les mains et la visée (repères du Root de Phantom P) restent justes.
"""
import math
import random

import vanta_ar01 as AR
from weapon_kit import box, cyl_x, prism, root_marker


# ------------------------------------------------------------------ Pulse (rare)
def pulse_pieces():
    P = AR.pieces()
    segs = []
    # crosse : 4 segments (demi-largeur 0,15) ; carcasse haute (0,105) ; garde-main (0,13)
    for i in range(4):
        x0 = 0.16 + i * 0.112
        segs.append((x0, x0 + 0.095, 0.86, 0.88, 0.155))
    x = 1.32
    while x < 2.90:
        half = 0.109 if x < 2.02 else 0.135
        x1 = min(x + 0.115, 2.02 if x < 2.02 else 2.92)
        segs.append((x, x1, 0.985, 1.005, half))
        x = x1 + 0.018
    for i, (x0, x1, z0, z1, half) in enumerate(segs, start=1):
        P.append(("Body", f"Neon{i:02d}", lambda bm, a=x0, b=x1, c=z0, d=z1, h=half: (
            box(bm, a, b, c, d, 0.004, h),
            box(bm, a, b, c, d, 0.004, -h),
        ), 0.0))
    return P


# ------------------------------------------------------------------ Inferno (épique)
def _crack(bm, pts, half_surface, w=0.007):
    """Fissure : suite de petits quadrilatères fins posés sur les deux flancs."""
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        dx, dz = x1 - x0, z1 - z0
        ln = math.hypot(dx, dz) or 1
        nx, nz = -dz / ln * w, dx / ln * w
        quad = [(x0 + nx, z0 + nz), (x1 + nx, z1 + nz), (x1 - nx, z1 - nz), (x0 - nx, z0 - nz)]
        for side in (1, -1):
            prism(bm, quad, 0.003, side * (half_surface + 0.003))


def _crack_paths(rng, x0, x1, z0, z1, count):
    paths = []
    for _ in range(count):
        x, z = rng.uniform(x0, x1), rng.uniform(z0, z1)
        a = rng.uniform(0, math.tau)
        pts = [(x, z)]
        for _ in range(rng.randint(4, 7)):
            a += rng.uniform(-0.9, 0.9)
            x = min(max(x + math.cos(a) * rng.uniform(0.04, 0.08), x0), x1)
            z = min(max(z + math.sin(a) * rng.uniform(0.03, 0.06), z0), z1)
            pts.append((x, z))
        paths.append(pts)
        if rng.random() < 0.6:  # petite branche
            bx, bz = pts[len(pts) // 2]
            b = a + rng.choice((-1, 1)) * 1.2
            paths.append([(bx, bz), (bx + math.cos(b) * 0.05, bz + math.sin(b) * 0.04),
                          (bx + math.cos(b) * 0.09, bz + math.sin(b) * 0.05)])
    return paths


def inferno_pieces():
    P = AR.pieces()
    rng = random.Random(41)
    zones = (  # (x0, x1, z0, z1, demi-largeur de la surface, nombre)
        (1.10, 1.95, 0.67, 0.82, 0.11, 4),     # carcasse basse
        (1.34, 1.98, 0.87, 0.97, 0.105, 2),    # carcasse haute
        (2.08, 2.90, 0.86, 1.02, 0.13, 4),     # garde-main (au-dessus des fentes)
        (0.16, 0.60, 0.70, 0.95, 0.15, 3),     # crosse
        (1.04, 1.30, 0.30, 0.58, 0.085, 1),    # poignée
    )
    cracks = []
    for x0, x1, z0, z1, half, n in zones:
        for path in _crack_paths(rng, x0, x1, z0, z1, n):
            cracks.append((path, half))
    P.append(("Body", "Neon", lambda bm: [_crack(bm, path, half) for path, half in cracks], 0.0))
    # ailettes de refroidissement sur le garde-main + cache-flamme sur le frein
    P.append(("Body", "Sombre", lambda bm: [
        box(bm, x, x + 0.022, 0.86, 1.03, 0.147) for x in (2.30, 2.40, 2.50, 2.60, 2.70)], 0.004))
    P.append(("Body", "Sombre", lambda bm: (
        prism(bm, [(3.30, 0.80), (3.30, 1.00), (3.616, 1.02), (3.616, 0.78)], 0.11),   # cache-flamme
    ), 0.012))
    return P


# ------------------------------------------------------------------ Apex (légendaire)
def apex_pieces():
    P = []
    add = lambda group, role, fn, bevel=0.014: P.append((group, role, fn, bevel))

    add("Body", "Motif", lambda bm: (
        # crosse squelette (cadre triangulaire ouvert)
        prism(bm, [(0.05, 0.50), (0.05, 1.02), (0.16, 1.02), (0.16, 0.50)], 0.14),
        prism(bm, [(0.10, 0.94), (0.10, 1.02), (0.72, 1.00), (0.72, 0.93)], 0.12),
        prism(bm, [(0.10, 0.50), (0.10, 0.59), (0.72, 0.86), (0.72, 0.77)], 0.12),
        prism(bm, [(0.62, 0.76), (0.62, 1.00), (0.72, 1.00), (0.72, 0.76)], 0.13),
        # carcasse (identique à la Phantom : poignée, chargeur et mains au même endroit)
        prism(bm, [(1.04, 0.64), (1.04, 0.84), (2.02, 0.84), (2.02, 0.70), (1.88, 0.62),
                   (1.88, 0.52), (1.50, 0.52), (1.50, 0.64)], 0.11),
        prism(bm, [(1.04, 0.84), (1.04, 1.02), (1.08, 1.06), (2.02, 1.06), (2.02, 0.84)], 0.105),
        # garde-main ouvert : fenêtre sur le noyau
        prism(bm, [(2.02, 0.72), (2.02, 1.06), (2.12, 1.06), (2.12, 0.72)], 0.13),
        prism(bm, [(2.12, 0.95), (2.12, 1.06), (2.80, 1.06), (2.80, 0.95)], 0.13),
        prism(bm, [(2.12, 0.72), (2.12, 0.83), (2.80, 0.83), (2.80, 0.72)], 0.13),
        prism(bm, [(2.80, 0.72), (2.80, 1.06), (2.92, 1.06), (2.96, 1.02), (2.96, 0.76), (2.92, 0.72)], 0.13),
        prism(bm, [(1.12, 0.64), (1.36, 0.64), (1.31, 0.50), (1.22, 0.18), (1.03, 0.16),
                   (0.99, 0.22), (1.10, 0.50)], 0.085),                                       # poignée
    ))
    add("Body", "Sombre", lambda bm: (
        box(bm, 0.0, 0.06, 0.49, 1.03, 0.155),                                              # plaque de couche
        cyl_x(bm, 0.70, 1.06, 0.88, 0.07),                                                   # tube de crosse
        box(bm, 1.04, 2.95, 1.06, 1.10, 0.065),                                             # rail
        *[box(bm, x, x + 0.06, 1.10, 1.14, 0.07) for x in [1.08 + 0.12 * i for i in range(16)]],
        box(bm, 1.44, 1.78, 1.12, 1.145, 0.11),                                             # viseur
        prism(bm, [(1.46, 1.315), (1.49, 1.343), (1.73, 1.343), (1.76, 1.315)], 0.11),
        box(bm, 1.46, 1.76, 1.145, 1.315, 0.008, 0.102),
        box(bm, 1.46, 1.76, 1.145, 1.315, 0.008, -0.102),
        box(bm, 1.48, 1.80, 0.88, 0.98, 0.006, -0.111),                                     # fenêtre d'éjection
        prism(bm, [(1.30, 0.53), (1.30, 0.56), (1.50, 0.56), (1.50, 0.64), (1.53, 0.64), (1.53, 0.53)], 0.03),
        box(bm, 2.12, 2.80, 0.83, 0.95, 0.02),                                              # fond de la fenêtre
        prism(bm, [(3.30, 0.80), (3.30, 1.00), (3.58, 0.97), (3.616, 0.92), (3.616, 0.88), (3.58, 0.83)], 0.085),
    ))
    add("Body", "Clair", lambda bm: (
        cyl_x(bm, 2.95, 3.32, 0.90, 0.055),                                                  # canon
        box(bm, 1.10, 1.30, 0.90, 0.98, 0.112),                                             # assistance de fermeture
    ))
    add("Body", "Accent", lambda bm: (
        box(bm, 1.00, 1.06, 0.66, 1.06, 0.115),                                             # plaque arrière
        box(bm, 2.12, 2.80, 0.83, 0.845, 0.133),                                            # cadre doré de la fenêtre
        box(bm, 2.12, 2.80, 0.935, 0.95, 0.133),
        box(bm, 3.30, 3.335, 0.80, 1.00, 0.09),                                             # liseré de l'embout
        box(bm, 0.16, 0.66, 1.00, 1.025, 0.123),                                            # liseré de crosse
    ), 0.006)
    add("Body", "Accent2", lambda bm: (
        box(bm, 2.86, 2.93, 0.95, 1.00, 0.135),                                             # repère avant
        box(bm, 3.40, 3.55, 0.985, 1.005, 0.05),                                            # ailette d'embout
    ), 0.006)
    add("Body", "Neon", lambda bm: cyl_x(bm, 2.13, 2.79, 0.89, 0.045, segs=12), 0.0)          # noyau
    for i, x in enumerate((3.03, 3.12, 3.21), start=1):                                     # anneaux
        add("Body", f"Neon{i:02d}", lambda bm, a=x: cyl_x(bm, a, a + 0.026, 0.90, 0.088, segs=6), 0.0)
    add("Body", "Cadre", lambda bm: (
        box(bm, 1.47, 1.49, 1.145, 1.159, 0.094),
        box(bm, 1.47, 1.49, 1.301, 1.315, 0.094),
        box(bm, 1.47, 1.49, 1.159, 1.301, 0.003, 0.091),
        box(bm, 1.47, 1.49, 1.159, 1.301, 0.003, -0.091),
    ), 0.0)
    add("Body", "Verre", lambda bm: box(bm, 1.478, 1.482, 1.159, 1.301, 0.088), 0.0)

    add("Magazine", "Motif", lambda bm: prism(bm, [(1.53, 0.60), (1.83, 0.60), (1.93, 0.10), (1.63, 0.10)], 0.085))
    add("Magazine", "Accent2", lambda bm: (
        prism(bm, [(1.585, 0.33), (1.885, 0.33), (1.895, 0.28), (1.595, 0.28)], 0.088),
        prism(bm, [(1.565, 0.43), (1.865, 0.43), (1.875, 0.38), (1.575, 0.38)], 0.088),
    ), 0.006)
    add("Magazine", "Accent", lambda bm: prism(bm, [(1.625, 0.14), (1.925, 0.14), (1.93, 0.10), (1.63, 0.10)], 0.09), 0.006)
    add("Magazine", "Sombre", lambda bm: box(bm, 1.61, 1.96, 0.0, 0.10, 0.095))
    add("Trigger", "Gachette", lambda bm: prism(bm, [(1.38, 0.64), (1.42, 0.64), (1.435, 0.60), (1.415, 0.565),
                                                      (1.395, 0.57), (1.405, 0.60)], 0.014), 0.004)
    add("ChargingHandle", "Clair", lambda bm: box(bm, 0.94, 1.06, 1.00, 1.06, 0.06), 0.008)
    add("ChargingHandle", "Accent", lambda bm: box(bm, 0.94, 1.00, 1.00, 1.06, 0.1845), 0.008)
    P.append(root_marker(AR.GRIP_POINT))
    return P
