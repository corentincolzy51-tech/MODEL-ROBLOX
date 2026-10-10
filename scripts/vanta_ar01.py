"""Géométrie de la VANTA AR-01 (style « Phantom » : fusil moderne + viseur point rouge).

Convention du jeu :
  - canon vers +X, haut vers +Z, origine sur la poignée
  - même structure que « Phantom P » dans Roblox :
        Corps    -> Body_<Couleur>           + Body_Contour (Body_Verre... = verre du viseur)
        Chargeur -> Magazine_<Couleur>       + Magazine_Contour
        Gachette -> Trigger                  + Trigger_Contour
        Levier   -> ChargingHandle_<Couleur> + ChargingHandle_Contour
        Root     -> petit cube sur la poignée (repère de prise en main)
  - un objet = une couleur (ou la texture du skin pour Body_<Skin> / Magazine_<Skin>)
  - taille : 3,616 x 1,343 x 0,369 studs = 1,096 x 0,407 x 0,112 m

Les profils sont dessinés en vue de côté (X, Z) en studs, puis extrudés
en épaisseur (Y, demi-largeur en studs).
"""
from weapon_kit import STUD, Weapon, box, cyl_x, cyl_y, prism, root_marker  # noqa: F401

GRIP_POINT = (1.17, 0.42)  # centre de la poignée (studs design)

# ------------------------------------------------------------------ le fusil
# Rôles de couleur (chaque skin associe un rôle à une couleur nommée) :
#   Motif   surfaces décorées par la texture du skin (Body_<Skin>, Magazine_<Skin>)
#   Sombre  rail, boîtier du viseur, tube de crosse, frein de bouche...
#   Clair   canon, assistance de fermeture, tige du levier
#   Accent  plaque arrière, bague avant, liseré de crosse, cadre du viseur, ailes du levier
#   Accent2 bouton du garde-main, bagues du frein, bandes du chargeur
#   Verre   verre transparent du viseur
#   Gachette la gâchette (objet « Trigger »)
def pieces():
    """Liste (groupe, rôle, fonction_de_construction, biseau_studs)."""
    P = []
    add = lambda group, role, fn, bevel=0.014: P.append((group, role, fn, bevel))

    # ---- Corps : surfaces décorées
    add("Body", "Motif", lambda bm: (
        # crosse
        prism(bm, [(0.05, 0.50), (0.05, 1.00), (0.12, 1.04), (0.62, 1.00), (0.70, 0.94),
                    (0.70, 0.80), (0.45, 0.74), (0.30, 0.60), (0.14, 0.50)], 0.15),
        # carcasse inférieure + puits de chargeur
        prism(bm, [(1.04, 0.64), (1.04, 0.84), (2.02, 0.84), (2.02, 0.70), (1.88, 0.62),
                    (1.88, 0.52), (1.50, 0.52), (1.50, 0.64)], 0.11),
        # carcasse supérieure
        prism(bm, [(1.04, 0.84), (1.04, 1.02), (1.08, 1.06), (2.02, 1.06), (2.02, 0.84)], 0.105),
        # garde-main
        prism(bm, [(2.02, 0.72), (2.02, 1.06), (2.92, 1.06), (2.96, 1.02), (2.96, 0.76), (2.92, 0.72)], 0.13),
        # poignée
        prism(bm, [(1.12, 0.64), (1.36, 0.64), (1.31, 0.50), (1.22, 0.18), (1.03, 0.16),
                    (0.99, 0.22), (1.10, 0.50)], 0.085),
    ))
    add("Body", "Sombre", lambda bm: (
        box(bm, 0.0, 0.07, 0.49, 1.01, 0.155),                     # plaque de couche
        cyl_x(bm, 0.66, 1.06, 0.88, 0.075),                        # tube de crosse
        box(bm, 1.04, 2.95, 1.06, 1.10, 0.065),                    # rail
        *[box(bm, x, x + 0.06, 1.10, 1.14, 0.07) for x in [1.08 + 0.12 * i for i in range(16)]],
        # viseur point rouge : boîtier creux (on voit à travers en visée)
        box(bm, 1.44, 1.78, 1.12, 1.145, 0.11),                    # semelle
        prism(bm, [(1.46, 1.315), (1.49, 1.343), (1.73, 1.343), (1.76, 1.315)], 0.11),  # toit
        box(bm, 1.46, 1.76, 1.145, 1.315, 0.008, 0.102),           # flanc gauche
        box(bm, 1.46, 1.76, 1.145, 1.315, 0.008, -0.102),          # flanc droit
        box(bm, 1.48, 1.80, 0.88, 0.98, 0.006, -0.111),            # fenêtre d'éjection (droite)
        *[box(bm, x0, x1, 0.765, 0.835, 0.135) for x0, x1 in ((2.20, 2.40), (2.48, 2.68), (2.76, 2.86))],
        cyl_x(bm, 3.36, 3.616, 0.90, 0.095),                       # frein de bouche
        prism(bm, [(1.30, 0.53), (1.30, 0.56), (1.50, 0.56), (1.50, 0.64), (1.53, 0.64), (1.53, 0.53)], 0.03),
    ))
    add("Body", "Clair", lambda bm: (
        cyl_x(bm, 2.95, 3.40, 0.90, 0.06),                         # canon
        box(bm, 1.10, 1.30, 0.90, 0.98, 0.112),                    # assistance de fermeture
    ))
    add("Body", "Accent", lambda bm: (
        box(bm, 1.00, 1.06, 0.66, 1.06, 0.115),                    # plaque arrière de carcasse
        cyl_x(bm, 2.94, 3.00, 0.90, 0.085),                        # bague avant
        box(bm, 0.20, 0.60, 1.00, 1.035, 0.152),                   # liseré sur la crosse
    ))
    add("Body", "Accent2", lambda bm: (
        cyl_y(bm, 2.12, 0.95, 0.045, 0.14),                        # bouton du garde-main
        cyl_x(bm, 3.42, 3.45, 0.90, 0.10),                         # bagues du frein
        cyl_x(bm, 3.54, 3.57, 0.90, 0.10),
    ))
    # cadre intérieur + verre, à l'arrière du viseur (côté œil) pour une grande fenêtre
    add("Body", "Cadre", lambda bm: (
        box(bm, 1.47, 1.49, 1.145, 1.159, 0.094),
        box(bm, 1.47, 1.49, 1.301, 1.315, 0.094),
        box(bm, 1.47, 1.49, 1.159, 1.301, 0.003, 0.091),
        box(bm, 1.47, 1.49, 1.159, 1.301, 0.003, -0.091),
    ), 0.0)
    add("Body", "Verre", lambda bm: box(bm, 1.478, 1.482, 1.159, 1.301, 0.088), 0.0)

    # ---- Chargeur
    add("Magazine", "Motif", lambda bm: prism(bm, [(1.53, 0.60), (1.83, 0.60), (1.93, 0.10), (1.63, 0.10)], 0.085))
    add("Magazine", "Accent2", lambda bm: (
        prism(bm, [(1.585, 0.33), (1.885, 0.33), (1.895, 0.28), (1.595, 0.28)], 0.088),
        prism(bm, [(1.565, 0.43), (1.865, 0.43), (1.875, 0.38), (1.575, 0.38)], 0.088),
    ), 0.006)
    add("Magazine", "Accent", lambda bm: prism(bm, [(1.625, 0.14), (1.925, 0.14), (1.93, 0.10), (1.63, 0.10)], 0.09), 0.006)
    add("Magazine", "Sombre", lambda bm: box(bm, 1.61, 1.96, 0.0, 0.10, 0.095))

    # ---- Gâchette
    add("Trigger", "Gachette", lambda bm: prism(bm, [(1.38, 0.64), (1.42, 0.64), (1.435, 0.60), (1.415, 0.565),
                                                      (1.395, 0.57), (1.405, 0.60)], 0.014), 0.004)

    # ---- Levier d'armement (poignée en T à l'arrière du rail)
    add("ChargingHandle", "Clair", lambda bm: box(bm, 0.94, 1.06, 1.00, 1.06, 0.06), 0.008)
    add("ChargingHandle", "Accent", lambda bm: box(bm, 0.94, 1.00, 1.00, 1.06, 0.1845), 0.008)

    P.append(root_marker(GRIP_POINT))
    return P


WEAPON = Weapon(
    key="ar01", folder="VANTA_AR-01", file_prefix="Phantom", pieces=pieces,
    target=(3.616, 0.369, 1.343), grip=GRIP_POINT, contour=0.022, flower_scale=1.0,
    zones={  # studs : (x0, z0, x1, z1)
        "stock": (0.08, 0.54, 0.68, 1.00),
        "receiver": (1.06, 0.66, 2.00, 1.04),
        "handguard": (2.04, 0.74, 2.94, 1.04),
        "grip": (1.04, 0.22, 1.32, 0.62),
        "mag": (1.58, 0.14, 1.88, 0.56),
        "band": (0.0, 0.74, 3.0, 1.06),
        "bouquet": (0.10, 0.56, 0.52, 0.98),
        "branch": ((0.55, 0.80), (2.85, 0.96)),
        "top_band_z": 0.90,  # hauteur du dessin vue sur le dessus/dessous
    },
    emblem=(0.30, 0.82, 0.26),
)
