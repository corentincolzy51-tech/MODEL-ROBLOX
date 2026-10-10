"""VANTA DE-50 (deagle) : pistolet lourd, culasse = « Levier » (ChargingHandle).

Structure Roblox (comme Phantom P) :
    Corps    -> Body_<Couleur>  (carcasse, poignée, chien, pontet, bout du canon)
    Chargeur -> Magazine_<Couleur>  (chargeur dans la poignée + semelle)
    Gachette -> Trigger
    Levier   -> ChargingHandle_<Couleur>  (culasse + organes de visée, recule au tir)
Taille : 1,250 x 0,856 studs (longueur x hauteur), épaisseur naturelle.
"""
from weapon_kit import Weapon, box, cyl_x, prism, root_marker

GRIP_POINT = (0.18, 0.32)


def pieces():
    P = []
    add = lambda group, role, fn, bevel=0.01: P.append((group, role, fn, bevel))

    # ---- culasse (Levier)
    add("ChargingHandle", "Motif", lambda bm: prism(
        bm, [(0.05, 0.70), (0.05, 0.90), (0.08, 0.925), (1.15, 0.925), (1.18, 0.90), (1.18, 0.70)], 0.13))
    add("ChargingHandle", "Clair", lambda bm: box(bm, 0.22, 1.09, 0.925, 0.945, 0.04))           # bande du dessus
    add("ChargingHandle", "Sombre", lambda bm: (
        *[box(bm, x, x + 0.026, 0.73, 0.86, 0.134) for x in (0.116, 0.164, 0.212, 0.260)],  # stries
        box(bm, 0.54, 0.77, 0.79, 0.865, 0.006, -0.131),                                    # fenêtre d'éjection
        box(bm, 0.07, 0.14, 0.92, 0.99, 0.028, 0.085),                                      # hausse (2 plots)
        box(bm, 0.07, 0.14, 0.92, 0.99, 0.028, -0.085),
    ), 0.006)
    add("ChargingHandle", "Accent", lambda bm: box(bm, 1.10, 1.16, 0.92, 0.99, 0.03), 0.006)      # guidon
    add("ChargingHandle", "Accent2", lambda bm: box(bm, 0.58, 0.99, 0.727, 0.747, 0.134), 0.004)  # liseré

    # ---- carcasse (Corps)
    add("Body", "Motif", lambda bm: (
        prism(bm, [(0.13, 0.57), (0.13, 0.70), (1.15, 0.70), (1.15, 0.585), (1.12, 0.57)], 0.12),
        prism(bm, [(0.125, 0.58), (0.35, 0.58), (0.245, 0.06), (0.0, 0.06)], 0.115),      # poignée
    ))
    add("Body", "Sombre", lambda bm: (
        box(bm, 0.0, 0.06, 0.77, 0.87, 0.05),                                             # chien
        prism(bm, [(0.40, 0.38), (0.40, 0.43), (0.65, 0.43), (0.65, 0.57), (0.70, 0.57), (0.70, 0.38)], 0.03),
        prism(bm, [(0.142, 0.426), (0.256, 0.405), (0.22, 0.22), (0.099, 0.241)], 0.122),  # plaquettes
    ), 0.006)
    add("Body", "Clair", lambda bm: cyl_x(bm, 1.17, 1.245, 0.797, 0.05), 0.0)               # bout du canon
    add("Body", "Accent", lambda bm: (
        box(bm, 0.036, 0.145, 0.632, 0.70, 0.125),
        box(bm, 1.055, 1.135, 0.578, 0.69, 0.125),
    ), 0.008)

    # ---- chargeur
    add("Magazine", "Motif", lambda bm: prism(bm, [(0.14, 0.50), (0.30, 0.50), (0.22, 0.07), (0.04, 0.07)], 0.09))
    add("Magazine", "Accent", lambda bm: box(bm, -0.02, 0.26, 0.0, 0.065, 0.125), 0.008)       # semelle

    # ---- gâchette
    add("Trigger", "Gachette", lambda bm: prism(
        bm, [(0.50, 0.565), (0.555, 0.565), (0.545, 0.50), (0.525, 0.445), (0.50, 0.45), (0.515, 0.50)], 0.02), 0.003)

    P.append(root_marker(GRIP_POINT))
    return P


WEAPON = Weapon(
    key="de50", folder="VANTA_DE-50", file_prefix="Deagle", pieces=pieces,
    target=(1.25, None, 0.856), grip=GRIP_POINT, contour=0.016, flower_scale=0.45,
    zones={
        "stock": (0.06, 0.71, 0.45, 0.92),
        "receiver": (0.06, 0.71, 1.17, 0.92),
        "handguard": (0.14, 0.58, 1.14, 0.70),
        "grip": (0.03, 0.08, 0.33, 0.55),
        "mag": (0.05, 0.10, 0.30, 0.45),
        "band": (0.0, 0.58, 1.2, 0.93),
        "bouquet": (0.03, 0.10, 0.32, 0.52),
        "branch": ((0.10, 0.78), (1.12, 0.86)),
        "top_band_z": 0.82,
    },
    emblem=(0.18, 0.30, 0.16),
)
