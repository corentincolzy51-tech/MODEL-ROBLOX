"""VANTA DE-50 réaliste : pistolet .50 à canon fixe (silhouette type Desert Eagle).

Culasse et canon en inox brossé, carcasse noire, plaquettes enveloppantes en caoutchouc.
Levier = culasse (elle recule au tir). Gabarit : 1,25 studs de long, ~0,86 de haut.
Côté gauche = +Y, fenêtre d'éjection à droite (-Y).
"""
import math

from kit import Part, bezier, rect, rounded

NAME = "Deagle"
FOLDER = "Deagle"
LABEL = "DE-50"
GRIP = (0.135, 0.33)
BORE = 0.775

VIEWS = [
    ("apercu", (-0.30, 1.0, 0.25), 1.75, 0.0),
    ("apercu_droite", (0.40, -1.0, 0.20), 1.8, 0.0),
]


def build():
    P = []

    # ------------------------------------------------------------ canon fixe (inox) + rail
    br = Part("Body", "Canon", "Inox", bevel=0.006)
    br.prism([(0.50, 0.70), (0.50, 0.872), (1.25, 0.872), (1.25, 0.672), (1.215, 0.655), (1.05, 0.655),
              (1.0, 0.70)], 0.084)
    # pans coupés du dessus (section triangulaire) : 2 découpes inclinées
    br.cut_prism_x([(0.05, 0.90), (0.20, 0.90), (0.20, 0.70), (0.084, 0.805)], 0.45, 1.30)
    br.cut_prism_x([(-0.05, 0.90), (-0.20, 0.90), (-0.20, 0.70), (-0.084, 0.805)], 0.45, 1.30)
    # rail (queue d'aronde) avec fentes
    br.prism_x([(-0.032, 0.862), (0.032, 0.862), (0.036, 0.885), (0.03, 0.896), (-0.03, 0.896),
                (-0.036, 0.885)], 0.55, 1.17)
    for i in range(7):
        x = 0.60 + i * 0.08
        br.cut_box(x, x + 0.022, 0.884, 0.92, 0.1)
    # gorges latérales + bloc de bouche
    br.cut_prism(rounded(0.62, 0.735, 1.16, 0.775, 0.018), 0.2, 0.078)
    br.cut_prism(rounded(0.62, 0.735, 1.16, 0.775, 0.018), -0.078, -0.2)
    br.cut_box(1.03, 1.045, 0.66, 0.70, 0.2)
    br.cut_cyl("X", (1.25, 0, BORE), 0.030, 0.12, 20)                                # âme
    br.cut_lathe([(-0.02, 0.0), (0.0, 0.045), (0.02, 0.045)], "X", (1.255, 0, BORE), 20)  # couronne
    # vis de démontage + guidon
    br.engrave(".50 AE", 1.14, 0.69, 0.034, 1, "sans")
    br.engrave("VANTA ARMS - DE-50", 0.64, 0.69, 0.022, -1, "cond")
    P.append(br)

    # ------------------------------------------------------------ carcasse (noire)
    fr = Part("Body", "Carcasse", "CerakoteNoir", bevel=0.006)
    fr.prism([(0.04, 0.575), (0.04, 0.665), (1.02, 0.665), (1.02, 0.60), (0.99, 0.585), (0.62, 0.585),
              (0.60, 0.565), (0.33, 0.565), (0.30, 0.575)], 0.08)
    # carcasse de poignée (sous les plaquettes) + queue de castor
    fr.prism([(0.30, 0.575), (0.25, 0.30), (0.215, 0.07), (0.005, 0.07), (0.005, 0.30), (0.03, 0.50),
              (-0.025, 0.575), (-0.035, 0.615), (0.04, 0.62)], 0.062)
    # pontet carré à crochet
    fr.prism([(0.30, 0.575), (0.33, 0.575), (0.36, 0.425), (0.39, 0.405), (0.585, 0.405), (0.61, 0.43),
              (0.62, 0.445), (0.60, 0.48), (0.60, 0.585), (0.565, 0.585), (0.565, 0.47), (0.575, 0.445),
              (0.565, 0.438), (0.40, 0.438), (0.385, 0.45), (0.355, 0.565)], 0.036)
    fr.cut_prism(rect(0.37, 0.545, 0.565, 0.58), 0.02)                              # fente de la gâchette
    fr.cut_box(0.80, 0.98, 0.60, 0.63, 0.2, 0.074)                                  # rainures de la carcasse
    fr.cut_box(0.80, 0.98, 0.60, 0.63, -0.074, -0.2)
    fr.engrave("VANTA", 0.80, 0.59, 0.02, -1, "cond")
    fr.engrave("SN DE 0050", 0.32, 0.585, 0.016, -1, "mono")
    P.append(fr)

    # petites pièces en acier noir : chien, levier d'arrêt, boutons, axes
    st = Part("Body", "Acier", "AcierNoir", bevel=0.003, weld=False)
    # chien à anneau
    st.prism([(-0.035, 0.66), (0.03, 0.66), (0.03, 0.74), (0.005, 0.80), (-0.04, 0.805), (-0.06, 0.78),
              (-0.05, 0.72)], 0.024)
    st.cut_cyl("Y", (-0.018, 0, 0.758), 0.022, 0.1, 16)
    # arrêtoir de culasse (gauche)
    st.prism([(0.33, 0.59), (0.52, 0.60), (0.53, 0.625), (0.46, 0.635), (0.34, 0.625)], 0.08, 0.094)
    # levier de démontage (gauche, au-dessus du pontet)
    st.prism(rounded(0.60, 0.59, 0.70, 0.635, 0.012), 0.08, 0.092)
    # bouton de chargeur (gauche)
    st.lathe([(0.062, 0.022), (0.075, 0.022), (0.078, 0.018)], "Y", (0.285, 0, 0.50), 16)
    # axes
    for x, z in ((0.10, 0.61), (0.38, 0.61), (0.85, 0.64)):
        st.lathe([(-0.083, 0.0), (-0.083, 0.010), (0.083, 0.010), (0.083, 0.0)], "Y", (x, 0, z), 12)
    P.append(st)

    # plaquettes enveloppantes (caoutchouc, doigts moulés)
    gp = Part("Body", "Plaquettes", "Caoutchouc", bevel=0.014, segs=3, angle=25)
    front = [(0.290, 0.555), (0.278, 0.50)] + bezier((0.278, 0.50), (0.300, 0.46), (0.268, 0.43), (0.262, 0.40), 3)[1:] + \
        bezier((0.262, 0.40), (0.285, 0.36), (0.250, 0.32), (0.246, 0.29), 3)[1:] + \
        bezier((0.246, 0.29), (0.268, 0.25), (0.232, 0.20), (0.228, 0.17), 3)[1:] + [(0.215, 0.085)]
    back = [(-0.002, 0.085), (-0.004, 0.20), (0.012, 0.36), (0.035, 0.50), (0.04, 0.555)]
    gp.prism(front + back, 0.084)
    gp.cut_prism(rect(0.055, 0.545, 0.27, 0.60), 0.2)
    gp.stipple = [(-0.1, 0.08, 0.35, 0.56)]
    gp.engrave("V", 0.16, 0.44, 0.06, 1, "sans")
    gp.engrave("V", 0.09, 0.44, 0.06, -1, "sans")
    P.append(gp)

    # ------------------------------------------------------------ culasse (Levier) : inox
    sl = Part("ChargingHandle", "Culasse", "Inox", bevel=0.006)
    sl.prism([(0.03, 0.665), (0.03, 0.845), (0.05, 0.872), (0.55, 0.872), (0.55, 0.665)], 0.088)
    sl.cut_prism_x([(0.05, 0.90), (0.20, 0.90), (0.20, 0.70), (0.088, 0.81)], 0.0, 0.6)
    sl.cut_prism_x([(-0.05, 0.90), (-0.20, 0.90), (-0.20, 0.70), (-0.088, 0.81)], 0.0, 0.6)
    for i in range(9):                                                                # stries de préhension
        x = 0.085 + i * 0.026
        sl.cut_prism([(x, 0.69), (x + 0.012, 0.69), (x + 0.012, 0.80), (x, 0.80)], 0.2, 0.08)
        sl.cut_prism([(x, 0.69), (x + 0.012, 0.69), (x + 0.012, 0.80), (x, 0.80)], -0.08, -0.2)
    sl.cut_prism(rounded(0.36, 0.745, 0.53, 0.85, 0.012), -0.2, -0.04)               # fenêtre d'éjection
    # sûretés ambidextres
    for s in (1, -1):
        sl.prism([(0.05, 0.775), (0.13, 0.775), (0.14, 0.79), (0.13, 0.81), (0.05, 0.81)],
                 s * 0.086, s * 0.108)
    # hausse (cran de mire)
    sl.prism([(0.06, 0.86), (0.16, 0.86), (0.16, 0.905), (0.13, 0.912), (0.09, 0.912), (0.06, 0.90)], 0.05)
    sl.cut_box(0.05, 0.17, 0.885, 0.93, 0.012)
    sl.engrave("VANTA", 0.54, 0.70, 0.04, 1, "sans")
    sl.engrave("DE-50  .50 AE", 0.54, 0.672, 0.02, 1, "cond")
    sl.engrave("MAGNUM", 0.34, 0.70, 0.028, -1, "sans")
    P.append(sl)

    # culasse mobile visible dans la fenêtre (acier noir, suit le Levier)
    bo = Part("ChargingHandle", "Verrou", "AcierNoir", bevel=0.003)
    bo.lathe([(0.34, 0.045), (0.545, 0.045)], "X", (0, -0.005, BORE + 0.02), 18)
    P.append(bo)

    # organes de visée à tritium (points verts)
    tr = Part("Body", "Tritium", "Tritium", bevel=0, weld=False)
    for y in (0.03, -0.03):
        tr.lathe([(0.0, 0.007), (0.004, 0.007)], "X", (0.058, y, 0.893), 10)
    tr.lathe([(0.0, 0.008), (0.004, 0.008)], "X", (1.168, 0, 0.917), 10)
    P.append(tr)
    gd = Part("Body", "Guidon", "AcierNoir", bevel=0.003)
    gd.prism([(1.17, 0.895), (1.21, 0.895), (1.21, 0.905), (1.195, 0.932), (1.17, 0.932)], 0.012)
    P.append(gd)

    # ------------------------------------------------------------ chargeur (acier) + cartouche
    mg = Part("Magazine", "Chargeur", "AcierNoir", bevel=0.004)
    mg.prism([(0.045, 0.54), (0.215, 0.54), (0.175, 0.07), (0.012, 0.07)], 0.05)
    mg.cut_prism(rounded(0.06, 0.20, 0.13, 0.45, 0.02), 0.06, 0.044)                # fenêtre témoin
    mg.prism([(-0.015, 0.005), (0.235, 0.005), (0.24, 0.035), (0.225, 0.075), (0.0, 0.075), (-0.02, 0.035)],
             0.07)                                                                     # semelle
    mg.cut_box(0.02, 0.20, 0.025, 0.05, 0.2, 0.066)
    mg.cut_box(0.02, 0.20, 0.025, 0.05, -0.066, -0.2)
    mg.engrave("VANTA .50", 0.03, 0.028, 0.018, -1, "cond")
    P.append(mg)
    am = Part("Magazine", "Cartouche", "Laiton", bevel=0.002)
    am.lathe([(0.06, 0.0), (0.06, 0.026), (0.07, 0.03), (0.16, 0.03), (0.175, 0.026), (0.215, 0.016), (0.225, 0.0)],
             "X", (0, 0, 0.555), 16)
    P.append(am)

    # ------------------------------------------------------------ gâchette
    tg = Part("Trigger", "Gachette", "AcierNoir", bevel=0.003)
    tg.prism([(0.455, 0.58), (0.49, 0.58), (0.50, 0.54), (0.495, 0.50), (0.48, 0.47), (0.462, 0.462),
              (0.458, 0.475), (0.468, 0.50), (0.47, 0.54)], 0.016)
    P.append(tg)
    return P
