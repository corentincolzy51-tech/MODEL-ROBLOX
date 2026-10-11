"""Variantes de modèle de la VANTA AR-01 pour les skins Rare / Épique / Légendaire.

  pulse_pieces()   : base Phantom + ~40 segments néon (double ligne sur les flancs, crosse,
                     chargeur, garde-main, anneaux du frein) + cellules d'énergie
  inferno_pieces() : arme volcanique (crosse en dents de roche, crête d'obsidienne,
                     garde-main fournaise à fentes de lave, chambre de magma, lame
                     d'obsidienne, embout fournaise, chargeur en roche)
  apex_pieces()    : fusil à rails (deux rails avec faisceau d'énergie et bobines qui
                     tournent, coque sculptée, aileron, crosse en lames flottantes,
                     chargeur cellule d'énergie)
La poignée, le chargeur, la gâchette, le levier et le viseur restent au même endroit que
sur la Phantom : les mains et la visée (repères du Root de Phantom P) restent justes.
"""
import math
import random

import vanta_ar01 as AR
from weapon_kit import box, cone_x, cyl_x, cyl_y, prism, root_marker


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



# ------------------------------------------------------------------ pièces communes
def _commun(P, add, sight=True, rail=(1.04, 2.95), ribs=16):
    """Pièces qui restent au même endroit que sur la Phantom (mains, visée, rechargement)."""
    add("Body", "Sombre", lambda bm: (
        box(bm, rail[0], rail[1], 1.06, 1.10, 0.065),
        *[box(bm, x, x + 0.06, 1.10, 1.14, 0.07) for x in [rail[0] + 0.04 + 0.12 * i for i in range(ribs)]],
        box(bm, 1.44, 1.78, 1.12, 1.145, 0.11),
        prism(bm, [(1.46, 1.315), (1.49, 1.343), (1.73, 1.343), (1.76, 1.315)], 0.11),
        box(bm, 1.46, 1.76, 1.145, 1.315, 0.008, 0.102),
        box(bm, 1.46, 1.76, 1.145, 1.315, 0.008, -0.102),
        box(bm, 1.48, 1.80, 0.88, 0.98, 0.006, -0.111),
        prism(bm, [(1.30, 0.53), (1.30, 0.56), (1.50, 0.56), (1.50, 0.64), (1.53, 0.64), (1.53, 0.53)], 0.03),
    ))
    add("Body", "Cadre", lambda bm: (
        box(bm, 1.47, 1.49, 1.145, 1.159, 0.094),
        box(bm, 1.47, 1.49, 1.301, 1.315, 0.094),
        box(bm, 1.47, 1.49, 1.159, 1.301, 0.003, 0.091),
        box(bm, 1.47, 1.49, 1.159, 1.301, 0.003, -0.091),
    ), 0.0)
    add("Body", "Verre", lambda bm: box(bm, 1.478, 1.482, 1.159, 1.301, 0.088), 0.0)
    add("Trigger", "Gachette", lambda bm: prism(bm, [(1.38, 0.64), (1.42, 0.64), (1.435, 0.60), (1.415, 0.565),
                                                      (1.395, 0.57), (1.405, 0.60)], 0.014), 0.004)
    add("ChargingHandle", "Clair", lambda bm: box(bm, 0.94, 1.06, 1.00, 1.06, 0.06), 0.008)
    add("ChargingHandle", "Accent", lambda bm: box(bm, 0.94, 1.00, 1.00, 1.06, 0.1845), 0.008)
    P.append(root_marker(AR.GRIP_POINT))


RECEIVER_LOW = [(1.04, 0.64), (1.04, 0.84), (2.02, 0.84), (2.02, 0.70), (1.88, 0.62),
                (1.88, 0.52), (1.50, 0.52), (1.50, 0.64)]
RECEIVER_UP = [(1.04, 0.84), (1.04, 1.02), (1.08, 1.06), (2.02, 1.06), (2.02, 0.84)]
GRIP = [(1.12, 0.64), (1.36, 0.64), (1.31, 0.50), (1.22, 0.18), (1.03, 0.16), (0.99, 0.22), (1.10, 0.50)]


def _quad_line(bm, a, b, w, half):
    """Bande fine entre deux points du profil, posée sur les deux flancs."""
    (x0, z0), (x1, z1) = a, b
    dx, dz = x1 - x0, z1 - z0
    ln = math.hypot(dx, dz) or 1
    nx, nz = -dz / ln * w, dx / ln * w
    quad = [(x0 + nx, z0 + nz), (x1 + nx, z1 + nz), (x1 - nx, z1 - nz), (x0 - nx, z0 - nz)]
    for side in (1, -1):
        prism(bm, quad, 0.004, side * half)


# ------------------------------------------------------------------ Pulse (rare)
def pulse_pieces():
    P = AR.pieces()
    segs = []  # (x milieu pour l'ordre de l'onde, fonction)

    def line(x0, x1, z0, z1, half_of_x, n_gap=0.016, length=0.11):
        x = x0
        while x < x1 - 0.03:
            xe = min(x + length, x1)
            h = half_of_x((x + xe) / 2)
            segs.append(((x + xe) / 2, lambda bm, a=x, b=xe, c=z0, d=z1, hh=h: (
                box(bm, a, b, c, d, 0.004, hh + 0.004), box(bm, a, b, c, d, 0.004, -hh - 0.004))))
            x = xe + n_gap

    half_body = lambda x: 0.105 if x < 2.02 else 0.131
    line(1.32, 2.92, 0.972, 1.002, half_body)            # ligne basse des flancs
    line(1.10, 2.92, 1.027, 1.047, half_body, length=0.07, n_gap=0.03)  # ligne haute (pointillés)
    line(0.15, 0.62, 0.950, 0.978, lambda x: 0.15)        # dessus de crosse
    for i in range(3):                                    # bord bas de la crosse (diagonale)
        t0, t1 = i / 3 + 0.02, (i + 1) / 3 - 0.02
        a = (0.16 + 0.27 * t0, 0.555 + 0.17 * t0)
        b = (0.16 + 0.27 * t1, 0.555 + 0.17 * t1)
        segs.append(((a[0] + b[0]) / 2, lambda bm, a=a, b=b: _quad_line(bm, a, b, 0.013, 0.154)))
    for x0 in (2.415, 2.695, 2.875):                      # barres verticales du garde-main
        segs.append((x0, lambda bm, a=x0: (box(bm, a, a + 0.028, 0.75, 0.94, 0.004, 0.135),
                                            box(bm, a, a + 0.028, 0.75, 0.94, 0.004, -0.135))))
    for z in (0.175, 0.235, 0.49, 0.54):                  # barres du chargeur (suivent la pente)
        xr = 1.53 + (0.60 - z) / 0.50 * 0.10
        segs.append((1.75, lambda bm, a=xr, c=z: _quad_line(bm, (a + 0.05, c), (a + 0.25, c), 0.012, 0.089)))
    for x0 in (3.385, 3.475, 3.565):                      # anneaux du frein
        segs.append((x0, lambda bm, a=x0: cyl_x(bm, a, a + 0.016, 0.90, 0.1, segs=16)))
    segs.sort(key=lambda s: s[0])
    for i, (_, fn) in enumerate(segs, start=1):
        P.append(("Body", f"Neon{i:02d}", fn, 0.0))
    # cellules d'énergie sur la crosse (néon fixe qui respire)
    P.append(("Body", "Neon", lambda bm: (
        box(bm, 0.22, 0.58, 0.78, 0.83, 0.004, 0.154), box(bm, 0.22, 0.58, 0.78, 0.83, 0.004, -0.154),
        box(bm, 1.58, 1.98, 0.70, 0.73, 0.004, 0.114), box(bm, 1.58, 1.98, 0.70, 0.73, 0.004, -0.114),
    ), 0.0))
    return P


# ------------------------------------------------------------------ Inferno (épique)
def inferno_pieces():
    P = []
    add = lambda group, role, fn, bevel=0.014: P.append((group, role, fn, bevel))
    stock = [(0.05, 0.50), (0.05, 1.00), (0.14, 1.03), (0.22, 0.98), (0.30, 1.06), (0.38, 0.98), (0.47, 1.07),
             (0.55, 0.98), (0.66, 1.02), (0.72, 0.93), (0.72, 0.80), (0.45, 0.74), (0.30, 0.60), (0.14, 0.50)]
    furnace = [(2.02, 0.70), (2.02, 1.08), (2.20, 1.10), (2.86, 1.10), (3.00, 1.04), (3.05, 0.92),
               (3.00, 0.76), (2.90, 0.70)]
    add("Body", "Motif", lambda bm: (
        prism(bm, stock, 0.15),
        prism(bm, RECEIVER_LOW, 0.11),
        prism(bm, RECEIVER_UP, 0.105),
        prism(bm, furnace, 0.14),
        prism(bm, GRIP, 0.085),
    ))
    _commun(P, add, rail=(1.04, 2.00), ribs=8)
    add("Body", "Sombre", lambda bm: (
        box(bm, 0.0, 0.07, 0.49, 1.01, 0.155),                                              # plaque de couche
        cyl_x(bm, 0.66, 1.06, 0.88, 0.075),                                                  # tube
        *[prism(bm, [(x, 1.09), (x + 0.05, 1.21), (x + 0.11, 1.09)], 0.035)
          for x in (2.10, 2.24, 2.38, 2.52, 2.66, 2.80)],                                   # crête d'obsidienne
        prism(bm, [(0.06, 0.95), (0.0, 1.13), (0.17, 1.00)], 0.045),                        # éperons de crosse
        prism(bm, [(0.40, 1.03), (0.44, 1.17), (0.52, 1.04)], 0.035),
        cyl_x(bm, 3.04, 3.50, 0.90, 0.14, segs=8),                                           # embout fournaise
        prism(bm, [(3.50, 0.79), (3.50, 1.01), (3.616, 0.97), (3.616, 0.83)], 0.10),
        prism(bm, [(2.70, 0.71), (3.30, 0.68), (3.58, 0.63), (3.30, 0.61), (2.95, 0.59), (2.70, 0.63)], 0.022),  # lame
        cyl_y(bm, 1.25, 0.745, 0.085, 0.116, segs=10),                                       # bord de la chambre
    ))
    add("Body", "Clair", lambda bm: box(bm, 1.10, 1.30, 0.90, 0.98, 0.112))
    add("Body", "Accent", lambda bm: (
        box(bm, 1.00, 1.06, 0.66, 1.06, 0.115),
        cyl_x(bm, 3.02, 3.06, 0.90, 0.148, segs=8),                                          # bague de l'embout
    ), 0.006)
    rng = random.Random(41)
    cracks = []
    for x0, x1, z0, z1, half, n in ((1.38, 1.95, 0.67, 0.82, 0.11, 3), (1.34, 1.98, 0.87, 0.97, 0.105, 2),
                                    (0.16, 0.62, 0.66, 0.95, 0.15, 4), (1.04, 1.30, 0.30, 0.58, 0.085, 1)):
        for path in _crack_paths(rng, x0, x1, z0, z1, n):
            cracks.append((path, half))
    add("Body", "Neon", lambda bm: (
        *[_crack(bm, path, half, w=0.01) for path, half in cracks],
        *[box(bm, x, x + 0.13, z, z + 0.028, 0.004, sgn * 0.143)
          for x in (2.18, 2.38, 2.58) for z in (0.84, 0.93) for sgn in (1, -1)],             # fentes de la fournaise
        cyl_y(bm, 1.25, 0.745, 0.06, 0.122, segs=12),                                        # chambre de magma
        cyl_x(bm, 3.606, 3.618, 0.90, 0.075, segs=8),                                        # gueule de l'embout
    ), 0.0)
    rock = [(1.53, 0.60), (1.83, 0.60), (1.90, 0.42), (1.96, 0.30), (1.92, 0.10), (1.63, 0.10), (1.59, 0.26), (1.55, 0.45)]
    add("Magazine", "Motif", lambda bm: prism(bm, rock, 0.09))
    add("Magazine", "Neon", lambda bm: _crack(bm, [(1.62, 0.52), (1.70, 0.44), (1.74, 0.36), (1.82, 0.30), (1.86, 0.20)], 0.09, w=0.01), 0.0)
    add("Magazine", "Accent2", lambda bm: prism(bm, [(1.565, 0.43), (1.875, 0.43), (1.885, 0.38), (1.575, 0.38)], 0.093), 0.006)
    add("Magazine", "Sombre", lambda bm: box(bm, 1.61, 1.96, 0.0, 0.10, 0.095))
    return P


# ------------------------------------------------------------------ Apex (légendaire)
def apex_pieces():
    P = []
    add = lambda group, role, fn, bevel=0.014: P.append((group, role, fn, bevel))
    shell = [(1.00, 0.64), (1.00, 1.02), (1.10, 1.08), (1.40, 1.10), (2.05, 1.10), (2.14, 1.02), (2.14, 0.80),
             (2.02, 0.70), (1.88, 0.62), (1.88, 0.52), (1.50, 0.52), (1.50, 0.64)]
    add("Body", "Motif", lambda bm: (
        prism(bm, shell, 0.12),                                                              # coque sculptée
        prism(bm, [(2.10, 0.72), (2.10, 1.08), (2.24, 1.08), (2.24, 0.72)], 0.12),          # pont des rails
        prism(bm, [(2.20, 0.98), (2.20, 1.08), (3.30, 1.045), (3.616, 0.995), (3.40, 0.975)], 0.07),  # rail haut
        prism(bm, [(2.20, 0.72), (2.20, 0.82), (3.40, 0.81), (3.616, 0.79), (3.30, 0.745)], 0.08),   # rail bas
        prism(bm, [(0.05, 0.52), (0.05, 1.02), (0.18, 1.04), (0.32, 0.96), (0.32, 0.70), (0.18, 0.54)], 0.13),
        prism(bm, [(0.38, 0.66), (0.38, 1.00), (0.50, 1.03), (0.64, 0.97), (0.64, 0.76), (0.50, 0.68)], 0.12),
        prism(bm, [(0.70, 0.78), (0.70, 0.99), (0.82, 1.02), (0.95, 0.97), (0.95, 0.84), (0.82, 0.79)], 0.11),
        prism(bm, GRIP, 0.085),
    ))
    _commun(P, add, rail=(1.30, 1.96), ribs=5)
    add("Body", "Sombre", lambda bm: (
        box(bm, 0.0, 0.055, 0.52, 1.04, 0.14),                                              # plaque de couche
        cyl_x(bm, 0.30, 1.02, 0.88, 0.045),                                                  # colonne de crosse
        cyl_x(bm, 2.24, 2.42, 0.90, 0.075, segs=12),                                         # culot du faisceau
        cone_x(bm, 3.50, 3.616, 0.90, 0.04, 0.012, segs=8),                                  # pointe émettrice
    ))
    add("Body", "Clair", lambda bm: box(bm, 1.10, 1.30, 0.92, 0.99, 0.124))
    add("Body", "Accent", lambda bm: (
        prism(bm, [(1.05, 1.08), (1.14, 1.25), (1.32, 1.10)], 0.022),                       # aileron
        _quad_line(bm, (2.22, 1.075), (3.30, 1.04), 0.007, 0.071),                          # liserés dorés des rails
        _quad_line(bm, (2.22, 0.727), (3.30, 0.75), 0.007, 0.081),
        box(bm, 2.10, 2.24, 1.06, 1.08, 0.122),
        box(bm, 1.00, 1.05, 0.66, 1.02, 0.123),
    ), 0.005)
    add("Body", "Accent2", lambda bm: (
        *[box(bm, x, x + 0.08, 0.99, 1.03, 0.072) for x in (2.50, 2.90)],                   # plaques des rails
        *[box(bm, x, x + 0.08, 0.755, 0.795, 0.082) for x in (2.50, 2.90)],
    ), 0.006)
    add("Body", "Neon00", lambda bm: cyl_x(bm, 2.42, 3.52, 0.90, 0.022, segs=10), 0.0)  # faisceau (étincelles)
    add("Body", "Neon", lambda bm: (
        box(bm, 1.40, 2.05, 0.95, 0.965, 0.004, 0.124), box(bm, 1.40, 2.05, 0.95, 0.965, 0.004, -0.124),
        box(bm, 1.10, 1.50, 0.76, 0.775, 0.004, 0.124), box(bm, 1.10, 1.50, 0.76, 0.775, 0.004, -0.124),
        cyl_x(bm, 0.06, 1.0, 0.88, 0.02, segs=8),                                            # colonne lumineuse de crosse
    ), 0.0)
    for i, x in enumerate((2.50, 2.78, 3.06, 3.34), start=1):                               # bobines
        add("Body", f"Neon{i:02d}", lambda bm, a=x: cyl_x(bm, a, a + 0.03, 0.90, 0.07, segs=6), 0.0)
    add("Magazine", "Motif", lambda bm: prism(bm, [(1.53, 0.60), (1.83, 0.60), (1.93, 0.10), (1.63, 0.10)], 0.085))
    add("Magazine", "Neon", lambda bm: (
        prism(bm, [(1.62, 0.50), (1.78, 0.50), (1.83, 0.22), (1.67, 0.22)], 0.088),         # cellule d'énergie
    ), 0.0)
    add("Magazine", "Accent", lambda bm: prism(bm, [(1.625, 0.14), (1.925, 0.14), (1.93, 0.10), (1.63, 0.10)], 0.09), 0.006)
    add("Magazine", "Accent2", lambda bm: prism(bm, [(1.555, 0.555), (1.845, 0.555), (1.855, 0.52), (1.56, 0.52)], 0.088), 0.006)
    add("Magazine", "Sombre", lambda bm: box(bm, 1.61, 1.96, 0.0, 0.10, 0.095))
    return P
