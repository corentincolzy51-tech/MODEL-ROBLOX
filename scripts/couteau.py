"""Couteau VANTA : lame à dos dentelé, garde, manche à bagues, pommeau.

Structure Roblox : tout dans « Corps » -> Body_<Couleur> + Body_Contour (+ Root).
Taille : 1,625 x 0,426 x 0,200 studs.
"""
from weapon_kit import Weapon, box, prism, root_marker

GRIP_POINT = (0.30, 0.215)


def pieces():
    P = []
    add = lambda group, role, fn, bevel=0.008: P.append((group, role, fn, bevel))

    add("Body", "Motif", lambda bm: (
        prism(bm, [(0.58, 0.11), (0.58, 0.34), (1.30, 0.34), (1.62, 0.16), (1.55, 0.12),
                   (1.30, 0.105), (0.62, 0.11)], 0.03),                                        # lame
        prism(bm, [(0.08, 0.15), (0.08, 0.28), (0.10, 0.30), (0.50, 0.30), (0.50, 0.13),
                   (0.10, 0.13)], 0.075),                                                      # manche
    ))
    add("Body", "Clair", lambda bm: (
        prism(bm, [(0.62, 0.11), (1.30, 0.105), (1.55, 0.12), (1.625, 0.15), (1.55, 0.095),
                   (1.30, 0.075), (0.62, 0.075)], 0.02),                                       # fil de la lame
        *[prism(bm, [(x, 0.338), (x + 0.03, 0.395), (x + 0.06, 0.338)], 0.025)
          for x in [0.66 + 0.065 * i for i in range(5)]],                                      # dents du dos
    ), 0.004)
    add("Body", "Sombre", lambda bm: box(bm, 0.50, 0.58, 0.04, 0.39, 0.09))                   # garde
    add("Body", "Accent", lambda bm: (
        box(bm, 0.49, 0.59, 0.0, 0.06, 0.10),                                               # embouts de garde
        box(bm, 0.49, 0.59, 0.366, 0.426, 0.10),
        box(bm, 0.0, 0.10, 0.10, 0.33, 0.095),                                              # pommeau
    ), 0.01)
    add("Body", "Accent2", lambda bm: (
        *[box(bm, x0, x1, 0.12, 0.31, 0.082) for x0, x1 in ((0.15, 0.20), (0.27, 0.32), (0.39, 0.44))],
        box(bm, 0.72, 1.18, 0.215, 0.245, 0.034),                                           # gouttière
    ), 0.005)

    P.append(root_marker(GRIP_POINT))
    return P


WEAPON = Weapon(
    key="couteau", folder="VANTA_Couteau", file_prefix="Couteau", pieces=pieces,
    target=(1.625, 0.2, 0.426), grip=GRIP_POINT, contour=0.014, flower_scale=0.38,
    groups={"Body": "Corps"},
    zones={
        "stock": (0.10, 0.14, 0.48, 0.29),
        "receiver": (0.62, 0.12, 1.30, 0.33),
        "handguard": (1.00, 0.13, 1.45, 0.30),
        "grip": (0.10, 0.14, 0.48, 0.29),
        "mag": (0.62, 0.12, 1.00, 0.33),
        "band": (0.0, 0.12, 1.6, 0.33),
        "bouquet": (0.66, 0.14, 0.98, 0.32),
        "branch": ((0.62, 0.20), (1.45, 0.25)),
        "top_band_z": 0.22,
    },
    emblem=(1.05, 0.22, 0.12),
)
