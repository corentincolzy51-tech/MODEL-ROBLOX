"""VANTA SR-7 (sniper) : fusil à verrou + lunette, levier = poignée de culasse (côté droit).

Structure Roblox (comme Phantom P) :
    Corps    -> Body_<Couleur>  (crosse, carcasse, garde-main, canon, lunette...)
               Body_Lentille<Teinte> = verres de la lunette (néon)
    Chargeur -> Magazine_<Couleur>
    Gachette -> Trigger
    Levier   -> ChargingHandle_<Couleur>  (poignée de culasse)
Taille : 4,862 x 1,329 studs (longueur x hauteur), épaisseur naturelle.
"""
from weapon_kit import Weapon, box, cone_x, cyl_x, cyl_y, cyl_z, prism, root_marker

GRIP_POINT = (1.24, 0.32)


def pieces():
    P = []
    add = lambda group, role, fn, bevel=0.016: P.append((group, role, fn, bevel))

    add("Body", "Motif", lambda bm: (
        prism(bm, [(0.12, 0.30), (0.12, 0.90), (0.94, 0.88), (1.14, 0.78), (1.14, 0.60),
                   (0.90, 0.556), (0.52, 0.30)], 0.14),                                        # crosse
        prism(bm, [(1.12, 0.54), (1.12, 0.92), (2.55, 0.92), (2.55, 0.54)], 0.13),           # carcasse
        prism(bm, [(2.63, 0.54), (2.63, 0.876), (3.78, 0.876), (3.81, 0.85), (3.81, 0.57),
                   (3.78, 0.54)], 0.135),                                                      # garde-main
        prism(bm, [(1.13, 0.55), (1.41, 0.55), (1.32, 0.10), (1.10, 0.10)], 0.09),           # poignée
    ))
    add("Body", "Sombre", lambda bm: (
        box(bm, 0.0, 0.12, 0.258, 0.947, 0.15),                                             # plaque de couche
        box(bm, 0.40, 0.66, 0.52, 0.63, 0.142),                                             # plaque crosse
        box(bm, 1.14, 2.53, 0.92, 0.975, 0.07),                                             # rail
        box(bm, 1.80, 2.16, 0.742, 0.831, 0.006, -0.131),                                   # fenêtre d'éjection
        *[box(bm, x0, x1, 0.684, 0.764, 0.138) for x0, x1 in ((2.87, 3.01), (3.13, 3.28), (3.40, 3.54))],
        box(bm, 3.07, 3.73, 0.498, 0.551, 0.06),                                            # rail de bipied
        cyl_x(bm, 3.84, 4.62, 0.753, 0.078),                                                 # canon
        *[box(bm, x, x + 0.03, 0.72, 0.81, 0.1) for x in (4.70, 4.76)],                      # fentes du frein
        prism(bm, [(1.41, 0.38), (1.41, 0.41), (1.80, 0.41), (1.80, 0.545), (1.83, 0.545), (1.83, 0.38)], 0.03),
        # lunette
        cyl_x(bm, 1.30, 2.41, 1.14, 0.11),
        cone_x(bm, 1.10, 1.30, 1.14, 0.155, 0.11),
        cyl_x(bm, 1.06, 1.10, 1.14, 0.155),
        cone_x(bm, 2.41, 2.73, 1.14, 0.11, 0.175),
        cyl_x(bm, 2.73, 2.76, 1.14, 0.178),
    ))
    add("Body", "Clair", lambda bm: (
        box(bm, 0.27, 0.93, 0.87, 0.975, 0.11),                                             # appui-joue
        box(bm, 1.47, 1.59, 0.975, 1.06, 0.06),                                             # colliers
        box(bm, 2.16, 2.28, 0.975, 1.06, 0.06),
        cyl_x(bm, 4.60, 4.862, 0.765, 0.098),                                                # frein de bouche
    ))
    add("Body", "Accent", lambda bm: (
        box(bm, 2.55, 2.63, 0.533, 0.924, 0.14),                                            # bague de carcasse
        cyl_x(bm, 3.79, 3.86, 0.753, 0.10),                                                  # bague du canon
        cyl_z(bm, 1.91, 1.24, 1.356, 0.055),                                                 # tourelle haute
        cyl_x(bm, 2.28, 2.35, 1.14, 0.118),                                                  # bague de lunette
        prism(bm, [(1.06, 0.06), (1.07, 0.13), (1.36, 0.10), (1.36, 0.04)], 0.095),         # talon de poignée
    ), 0.01)
    add("Body", "Accent2", lambda bm: cyl_y(bm, 1.91, 1.14, 0.05, 0.085, y_center=-0.085), 0.006)  # tourelle latérale
    add("Body", "Lentille", lambda bm: (
        cyl_x(bm, 1.052, 1.062, 1.14, 0.14),                                                 # oculaire
        cyl_x(bm, 2.758, 2.768, 1.14, 0.165),                                                # objectif
    ), 0.0)

    add("Magazine", "Motif", lambda bm: box(bm, 1.94, 2.25, 0.27, 0.545, 0.085))
    add("Magazine", "Accent2", lambda bm: box(bm, 1.93, 2.26, 0.444, 0.489, 0.088), 0.006)
    add("Magazine", "Accent", lambda bm: box(bm, 1.92, 2.27, 0.20, 0.29, 0.095), 0.01)

    add("Trigger", "Gachette", lambda bm: prism(
        bm, [(1.555, 0.545), (1.605, 0.545), (1.615, 0.49), (1.595, 0.43), (1.565, 0.44), (1.58, 0.49)], 0.016), 0.004)

    add("ChargingHandle", "Clair", lambda bm: (
        box(bm, 1.40, 1.62, 0.80, 0.86, 0.006, -0.132),                                     # culasse visible
        cyl_y(bm, 1.52, 0.83, 0.025, 0.09, y_center=-0.22),                                  # tige
    ), 0.004)
    add("ChargingHandle", "Accent", lambda bm: cyl_y(bm, 1.52, 0.83, 0.067, 0.035, segs=18, y_center=-0.33), 0.012)  # boule

    P.append(root_marker(GRIP_POINT))
    return P


WEAPON = Weapon(
    key="sr7", folder="VANTA_SR-7", file_prefix="Sniper", pieces=pieces,
    target=(4.862, None, 1.329), grip=GRIP_POINT, contour=0.022, flower_scale=0.9,
    zones={
        "stock": (0.14, 0.33, 1.10, 0.86),
        "receiver": (1.14, 0.56, 2.53, 0.91),
        "handguard": (2.65, 0.56, 3.78, 0.86),
        "grip": (1.12, 0.12, 1.39, 0.53),
        "mag": (1.95, 0.29, 2.24, 0.53),
        "band": (0.0, 0.55, 3.8, 0.93),
        "bouquet": (0.18, 0.36, 0.80, 0.84),
        "branch": ((0.45, 0.72), (3.70, 0.78)),
        "top_band_z": 0.75,
    },
    emblem=(0.55, 0.62, 0.30),
)
