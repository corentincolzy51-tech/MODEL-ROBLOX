"""VANTA SR-7 réaliste : fusil de précision à verrou sur châssis aluminium (teinte FDE),
canon lourd cannelé, gros frein de bouche, lunette 5-25x56 avec tourelles, bipied replié.

Levier = poignée de culasse (à droite, -Y). Gabarit : 4,862 studs de long.
"""
import math

from kit import Part, bezier, circle_pts, rect, rounded

NAME = "Sniper"
FOLDER = "Sniper"
LABEL = "SR-7"
GRIP = (1.235, 0.33)
BORE = 0.753
SCOPE = 1.14          # axe de la lunette
# repère d'animation : la poignée de culasse tourne autour de l'axe du verrou
ATTACHES = {"Verrou": ("ChargingHandle_Culasse", (1.73, -0.01, 0.805))}
VIEWS = [
    ("apercu", (-0.32, 1.0, 0.30), 1.45, 0.0),
    ("apercu_droite", (0.40, -1.0, 0.22), 1.5, 0.0),
]


def octagon(cy, cz, hw, hh, ch):
    return [(cy - hw + ch, cz - hh), (cy + hw - ch, cz - hh), (cy + hw, cz - hh + ch), (cy + hw, cz + hh - ch),
            (cy + hw - ch, cz + hh), (cy - hw + ch, cz + hh), (cy - hw, cz + hh - ch), (cy - hw, cz - hh + ch)]


def picatinny(part, x0, x1, z_base, half=0.07, pitch=0.0826, slot=0.034, h=0.04):
    zb, zt = z_base, z_base + h
    part.prism_x([(-half + 0.012, zb), (half - 0.012, zb), (half - 0.012, zb + 0.010), (half, zb + 0.020),
                  (half, zb + 0.028), (half - 0.012, zt), (-half + 0.012, zt), (-half, zb + 0.028),
                  (-half, zb + 0.020), (-half + 0.012, zb + 0.010)], x0, x1)
    n = int((x1 - x0 - 0.04) / pitch)
    start = x0 + (x1 - x0 - (n - 1) * pitch) / 2
    for i in range(n):
        x = start + i * pitch
        part.cut_box(x - slot / 2, x + slot / 2, zb + 0.016, zt + 0.01, half + 0.02)


def build():
    P = []

    # ------------------------------------------------------------ châssis (aluminium FDE)
    ch = Part("Body", "Chassis", "CerakoteFDE", bevel=0.008)
    # bloc central (logement du boîtier) + puits de chargeur + pontet
    ch.prism([(1.12, 0.56), (1.12, 0.80), (2.62, 0.80), (2.62, 0.56), (2.30, 0.545), (1.90, 0.545),
              (1.86, 0.56)], 0.122)
    ch.prism([(1.89, 0.42), (2.29, 0.42), (2.31, 0.56), (1.87, 0.56)], 0.108)             # puits
    ch.cut_prism(rect(1.93, 0.40, 2.26, 0.56), 0.092)
    ch.prism([(1.40, 0.56), (1.43, 0.56), (1.46, 0.43), (1.50, 0.40), (1.80, 0.40), (1.84, 0.43), (1.86, 0.56),
              (1.83, 0.56), (1.81, 0.44), (1.79, 0.432), (1.51, 0.432), (1.485, 0.45), (1.455, 0.56)], 0.035)
    ch.cut_prism(rect(1.48, 0.53, 1.80, 0.57), 0.02)                                       # fente de gâchette
    # évidements latéraux du châssis
    for x0, x1 in ((2.33, 2.58),):
        ch.cut_prism(rounded(x0, 0.61, x1, 0.74, 0.03), 0.2, 0.11)
        ch.cut_prism(rounded(x0, 0.61, x1, 0.74, 0.03), -0.11, -0.2)
    ch.cut_prism(rounded(1.15, 0.60, 1.38, 0.76, 0.03), 0.2, 0.11)
    # fenêtre d'éjection dans le châssis (côté droit)
    ch.cut_box(1.60, 2.10, 0.70, 0.82, -0.08, -0.2)
    # charnière de crosse
    ch.prism(rounded(1.04, 0.56, 1.14, 0.94, 0.02), 0.11)
    ch.lathe([(0.56, 0.028), (0.96, 0.028)], "Z", (1.09, 0.112, 0), 16)
    ch.engrave("VANTA ARMS", 2.56, 0.585, 0.032, 1, "sans")
    ch.engrave("SR-7  .338 LM", 2.56, 0.62, 0.024, 1, "cond")
    ch.engrave("SN SR7-00071", 2.20, 0.585, 0.02, -1, "mono")
    # garde-main M-LOK octogonal
    ch.prism_x(octagon(0.0, 0.70, 0.125, 0.155, 0.055), 2.60, 3.86)
    ch.cut_prism_x(octagon(0.0, 0.70, 0.108, 0.138, 0.048), 2.66, 3.95)
    for x in (2.72, 2.98, 3.24, 3.50):
        ch.cut_prism(rounded(x, 0.665, x + 0.17, 0.705, 0.02), 0.2)
        ch.cut_prism_z(rounded(x, -0.02, x + 0.17, 0.02, 0.02), 0.50, 0.58)
    picatinny(ch, 2.64, 3.84, 0.855, half=0.066, h=0.036)
    ch.engrave("SR-7", 3.80, 0.585, 0.03, 1, "sans")
    P.append(ch)

    # ------------------------------------------------------------ crosse squelette repliable (FDE) + talon
    sk = Part("Body", "Crosse", "CerakoteFDE", bevel=0.010)
    outline = [(0.07, 0.30), (0.07, 0.94), (0.30, 0.94), (0.42, 0.88), (0.98, 0.88), (1.05, 0.86), (1.05, 0.60),
               (0.95, 0.58), (0.52, 0.33), (0.46, 0.30)]
    sk.prism(outline, 0.07)
    sk.cut_prism([(0.20, 0.42), (0.40, 0.42), (0.86, 0.66), (0.92, 0.70), (0.92, 0.80), (0.20, 0.80)], 0.2)
    sk.prism(rect(0.07, 0.30, 0.17, 0.94), 0.11)                                          # plaque de couche (support)
    sk.prism(rect(0.86, 0.58, 1.05, 0.88), 0.10)                                          # bloc de charnière
    # monopode replié sous la crosse
    sk.lathe([(0.18, 0.0), (0.18, 0.026), (0.42, 0.026), (0.42, 0.0)], "Z", (0.36, 0, 0), 16)
    sk.lathe([(0.12, 0.0), (0.12, 0.040), (0.18, 0.040), (0.18, 0.0)], "Z", (0.36, 0, 0), 20)
    sk.engrave("VANTA", 0.80, 0.72, 0.04, 1, "sans")
    P.append(sk)

    pad = Part("Body", "Talon", "Caoutchouc", bevel=0.012, segs=3)
    pad.prism(rounded(0.0, 0.26, 0.075, 0.96, 0.03), 0.118)
    for z in [0.30 + 0.05 * i for i in range(13)]:
        pad.cut_box(-0.05, 0.012, z, z + 0.018, 0.2)
    P.append(pad)

    # appui-joue réglable (polymère noir) + poignée pistolet
    po = Part("Body", "Polymere", "PolymereNoir", bevel=0.016, segs=3, angle=25)
    po.prism([(0.28, 0.90), (0.32, 0.975), (0.40, 0.99), (0.90, 0.985), (0.96, 0.95), (0.96, 0.90)], 0.085)
    po.lathe([(0.0, 0.016), (0.10, 0.016)], "Z", (0.50, 0, 0.82), 12)                    # tiges
    po.lathe([(0.0, 0.016), (0.10, 0.016)], "Z", (0.80, 0, 0.82), 12)
    front = bezier((1.40, 0.56), (1.38, 0.46), (1.37, 0.36), (1.34, 0.28), 6)[:-1] + \
        bezier((1.34, 0.28), (1.33, 0.20), (1.335, 0.15), (1.31, 0.11), 4)
    back = bezier((1.12, 0.12), (1.11, 0.25), (1.13, 0.40), (1.15, 0.50), 6)
    po.prism([(1.15, 0.565), (1.40, 0.565)] + front + [(1.29, 0.09), (1.13, 0.09)] + back + [(1.12, 0.54)], 0.072)
    po.prism([(1.34, 0.44), (1.385, 0.44), (1.385, 0.40), (1.345, 0.38)], 0.066)
    po.stipple = [(1.05, 0.12, 1.45, 0.52)]
    P.append(po)

    # ------------------------------------------------------------ boîtier (acier noir) + rail 20 MOA
    rc = Part("Body", "Boitier", "AcierNoir", bevel=0.005)
    rc.lathe([(1.20, 0.0), (1.20, 0.085), (1.22, 0.098), (2.48, 0.098), (2.50, 0.09), (2.50, 0.0)], "X",
             (0, 0, 0.805), 28)
    rc.cut_prism(rounded(1.62, 0.79, 2.08, 0.89, 0.03), -0.2, -0.02)                       # fenêtre d'éjection
    picatinny(rc, 1.22, 2.50, 0.885, half=0.066, h=0.04)
    rc.prism(rect(1.22, 0.855, 2.50, 0.892), 0.06)
    # écrou de canon
    rc.lathe([(2.50, 0.0), (2.50, 0.078), (2.60, 0.078), (2.60, 0.0)], "X", (0, 0, BORE), 24)
    P.append(rc)

    # ------------------------------------------------------------ canon lourd cannelé + frein de bouche
    br = Part("Body", "Canon", "AcierNoir", bevel=0.003)
    br.lathe([(2.58, 0.068), (3.92, 0.068), (4.05, 0.060), (4.58, 0.056)], "X", (0, 0, BORE), 24)
    for k in range(6):
        a = math.radians(30 + 60 * k)
        cy, cz = 0.072 * math.cos(a), BORE + 0.072 * math.sin(a)
        br.cut_prism_x(circle_pts(cy, cz, 0.018, 10), 3.96, 4.48)
    mb = [(4.54, 0.0), (4.54, 0.07), (4.56, 0.096), (4.84, 0.096), (4.862, 0.082), (4.862, 0.0)]
    br.lathe(mb, "X", (0, 0, BORE), 28)
    for x in (4.60, 4.68, 4.76):
        br.cut_box(x, x + 0.05, BORE - 0.055, BORE + 0.055, 0.2)
    br.cut_cyl("X", (4.85, 0, BORE), 0.03, 0.2, 18)
    br.cut_box(4.54, 4.55, BORE - 0.1, BORE + 0.1, 0.2)
    P.append(br)

    # ------------------------------------------------------------ lunette (anodisé noir)
    sc = Part("Body", "Lunette", "AnodiseNoir", bevel=0.004)
    prof = [(1.03, 0.0), (1.03, 0.118), (1.045, 0.128), (1.10, 0.128), (1.12, 0.122), (1.20, 0.112),
            (1.30, 0.100), (1.32, 0.092), (1.34, 0.092), (1.34, 0.104), (1.46, 0.104), (1.46, 0.088),
            (2.38, 0.088), (2.40, 0.094), (2.66, 0.152), (2.70, 0.156), (2.78, 0.156), (2.80, 0.150),
            (2.80, 0.0)]
    sc.lathe(prof, "X", (0, 0, SCOPE), 36)
    # bague de grossissement : stries
    for k in range(18):
        a = 2 * math.pi * k / 18
        y, z = 0.104 * math.cos(a), SCOPE + 0.104 * math.sin(a)
        sc.cut_prism_x(circle_pts(y, z, 0.008, 6), 1.35, 1.45)
    # selle des tourelles
    sc.lathe([(1.76, 0.0), (1.76, 0.108), (2.06, 0.108), (2.06, 0.0)], "X", (0, 0, SCOPE), 32)
    sc.prism(rounded(1.80, SCOPE - 0.06, 2.02, SCOPE + 0.06, 0.03), 0.118)
    # tourelle d'élévation (haut), dérive (droite), parallaxe (gauche)
    sc.lathe([(0.0, 0.058), (0.13, 0.058), (0.135, 0.064), (0.22, 0.064), (0.225, 0.058), (0.23, 0.0)], "Z",
             (1.91, 0, SCOPE), 28)
    for k in range(20):
        a = 2 * math.pi * k / 20
        sc.cut_lathe([(SCOPE + 0.14, 0.006), (SCOPE + 0.215, 0.006)], "Z",
                     (1.91 + 0.064 * math.cos(a), 0.064 * math.sin(a), 0), 6)
    sc.lathe([(-0.10, 0.0), (-0.10, 0.05), (-0.17, 0.052), (-0.175, 0.046), (-0.18, 0.0)], "Y", (1.91, 0, SCOPE), 24)
    sc.lathe([(0.10, 0.0), (0.10, 0.045), (0.16, 0.047), (0.165, 0.040), (0.17, 0.0)], "Y", (1.91, 0, SCOPE), 24)
    sc.cut_lathe([(2.722, 0.142), (2.90, 0.142)], "X", (0, 0, SCOPE), 36)                # creux de l'objectif
    sc.cut_lathe([(0.95, 0.106), (1.072, 0.106)], "X", (0, 0, SCOPE), 32)                # creux de l'oculaire
    sc.engrave("VANTA OPTICS 5-25x56", 2.36, SCOPE - 0.012, 0.024, 1, "cond")
    sc.engrave("FFP  MRAD", 1.76, SCOPE - 0.012, 0.022, -1, "cond")
    P.append(sc)

    # colliers de lunette (acier noir)
    rg = Part("Body", "Colliers", "AcierNoir", bevel=0.004)
    for x in (1.56, 2.22):
        rg.lathe([(x - 0.045, 0.0), (x - 0.045, 0.106), (x + 0.045, 0.106), (x + 0.045, 0.0)], "X", (0, 0, SCOPE), 32)
        rg.prism([(x - 0.045, 0.92), (x + 0.045, 0.92), (x + 0.045, SCOPE - 0.06), (x - 0.045, SCOPE - 0.06)], 0.06)
        rg.prism(rect(x - 0.05, 0.90, x + 0.05, 0.935), 0.085)
        rg.cut_box(x - 0.06, x + 0.06, SCOPE - 0.004, SCOPE + 0.004, 0.2, 0.09)
        rg.cut_box(x - 0.06, x + 0.06, SCOPE - 0.004, SCOPE + 0.004, -0.09, -0.2)
        rg.lathe([(0.085, 0.0), (0.085, 0.014), (0.11, 0.014), (0.11, 0.0)], "Y", (x, 0, 0.918), 12)
    rg.cut_lathe([(1.40, 0.0884), (2.40, 0.0884)], "X", (0, 0, SCOPE), 36)
    P.append(rg)

    lens = Part("Body", "Lentille", "VerreLunette", bevel=0)
    lens.lathe([(1.066, 0.0), (1.066, 0.106), (1.072, 0.106), (1.072, 0.0)], "X", (0, 0, SCOPE), 32)
    lens.lathe([(2.722, 0.0), (2.722, 0.142), (2.728, 0.142), (2.728, 0.0)], "X", (0, 0, SCOPE), 36)
    P.append(lens)

    # ------------------------------------------------------------ bipied replié (noir)
    bp = Part("Body", "Bipied", "CerakoteNoir", bevel=0.005, weld=False)
    bp.prism(rounded(3.62, 0.46, 3.80, 0.54, 0.02), 0.07)
    for s in (1, -1):
        bp.lathe([(3.0, 0.0), (3.0, 0.018), (3.68, 0.018), (3.68, 0.0)], "X", (0, s * 0.045, 0.47), 12)
        bp.lathe([(2.90, 0.0), (2.90, 0.022), (3.04, 0.022), (3.04, 0.0)], "X", (0, s * 0.045, 0.47), 12)
    P.append(bp)

    # ------------------------------------------------------------ chargeur
    mg = Part("Magazine", "Chargeur", "AcierNoir", bevel=0.005)
    mg.prism(rect(1.945, 0.25, 2.245, 0.62), 0.084)
    mg.prism([(1.925, 0.185), (2.27, 0.185), (2.275, 0.215), (2.26, 0.26), (1.935, 0.26), (1.92, 0.215)], 0.098)
    mg.cut_box(1.98, 2.21, 0.29, 0.40, 0.2, 0.08)
    mg.cut_box(1.98, 2.21, 0.29, 0.40, -0.08, -0.2)
    mg.engrave(".338 LM  5RD", 2.22, 0.43, 0.022, 1, "cond")
    P.append(mg)

    # ------------------------------------------------------------ gâchette
    tg = Part("Trigger", "Gachette", "AcierNoir", bevel=0.003)
    tg.prism([(1.555, 0.555), (1.59, 0.555), (1.605, 0.51), (1.60, 0.475), (1.585, 0.445), (1.565, 0.44),
              (1.565, 0.455), (1.575, 0.48), (1.575, 0.515)], 0.016)
    P.append(tg)

    # ------------------------------------------------------------ culasse : corps visible + poignée (Levier)
    bo = Part("ChargingHandle", "Culasse", "AcierBrut", bevel=0.004)
    bo.lathe([(1.40, 0.0), (1.40, 0.07), (2.06, 0.07), (2.06, 0.0)], "X", (0, -0.01, 0.805), 24)
    for k in range(3):                                                                  # cannelures du verrou
        bo.cut_box(1.70 + k * 0.10, 1.76 + k * 0.10, 0.83, 0.90, -0.05, -0.12)
    bo.tube((1.50, -0.06, 0.80), (1.50, -0.22, 0.76), 0.026, 0.022, 16)                  # levier
    bo.tube((1.50, -0.21, 0.765), (1.47, -0.30, 0.715), 0.022, 0.020, 16)
    P.append(bo)
    kn = Part("ChargingHandle", "Boule", "PolymereNoir", bevel=0.006)
    kn.sphere((1.465, -0.33, 0.70), 0.052, 20, 1.0)
    kn.lathe([(0.0, 0.03), (0.04, 0.03)], "Y", (1.468, -0.29, 0.714), 16)
    P.append(kn)
    return P
