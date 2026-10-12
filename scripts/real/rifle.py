"""VANTA AR-01 réaliste : carabine moderne (plateforme AR), garde-main M-LOK, viseur holographique.

Même gabarit que la VANTA AR-01 du jeu : 3,616 studs de long, canon à z = 0,90,
poignée vers (1,17 ; 0,42), verre du viseur vers x = 1,48, z = 1,23.
Côté gauche = +Y. Fenêtre d'éjection à droite (-Y).
"""
import math

from kit import Part, arc, bezier, circle_pts, rect, rounded

NAME = "Phantom"
FOLDER = "Phantom"
LABEL = "AR-01"
GRIP = (1.165, 0.42)       # centre de la paume (main droite)
BORE = 0.90
LENGTH = 3.616


def octagon(cy, cz, hw, hh, ch):
    """Section octogonale (y, z) : demi-largeur, demi-hauteur, chanfrein."""
    return [(cy - hw + ch, cz - hh), (cy + hw - ch, cz - hh), (cy + hw, cz - hh + ch), (cy + hw, cz + hh - ch),
            (cy + hw - ch, cz + hh), (cy - hw + ch, cz + hh), (cy - hw, cz + hh - ch), (cy - hw, cz - hh + ch)]


def picatinny(part, x0, x1, z_base, half=0.072, pitch=0.0826, slot=0.034, h=0.042):
    """Rail Picatinny : profil en queue d'aronde + fentes transversales."""
    zb, zt = z_base, z_base + h
    part.prism_x([(-half + 0.012, zb), (half - 0.012, zb), (half - 0.012, zb + 0.010), (half, zb + 0.020),
                  (half, zb + 0.030), (half - 0.012, zt), (-half + 0.012, zt), (-half, zb + 0.030),
                  (-half, zb + 0.020), (-half + 0.012, zb + 0.010)], x0, x1)
    n = int((x1 - x0 - 0.04) / pitch)
    start = x0 + (x1 - x0 - (n - 1) * pitch) / 2
    for i in range(n):
        x = start + i * pitch
        part.cut_box(x - slot / 2, x + slot / 2, zb + 0.016, zt + 0.01, half + 0.02)


def build():
    P = []

    # ------------------------------------------------------------ carcasse supérieure
    up = Part("Body", "Carcasse", "AnodiseNoir", bevel=0.006)
    up.prism([(1.04, 0.80), (1.04, 0.985), (1.065, 1.02), (2.03, 1.02), (2.03, 0.80)], 0.104)
    picatinny(up, 1.045, 2.03, 1.02)
    # logement de l'assistance de fermeture (côté droit)
    up.lathe([(1.10, 0.0), (1.10, 0.030), (1.12, 0.040), (1.36, 0.040), (1.42, 0.0)], "X", (0, -0.088, 0.93), 18)
    # déflecteur de douilles
    up.prism_z([(1.30, -0.09), (1.30, -0.128), (1.345, -0.132), (1.39, -0.11), (1.40, -0.09)], 0.87, 1.0)
    # fenêtre d'éjection (poche) + rainures latérales
    up.cut_prism(rounded(1.42, 0.855, 1.76, 0.955, 0.012), -0.2, -0.062)
    up.cut_box(1.10, 1.98, 0.795, 0.812, 0.2)   # joint carcasse haute / basse
    # nervures sur le flanc gauche
    for z in (0.86, 0.89):
        up.cut_box(1.48, 1.96, z, z + 0.012, 0.096, 0.2)
    P.append(up)

    # couvre-fenêtre ouvert (plaque fine sous la fenêtre) + culasse visible : acier
    st = Part("Body", "Acier", "AcierNoir", bevel=0.003, weld=False)
    st.prism(rect(1.425, 0.86, 1.755, 0.95), -0.075, -0.062)               # culasse dans la fenêtre
    st.prism(rect(1.50, 0.885, 1.62, 0.925), -0.08, -0.07)                 # tête de culasse
    st.prism([(1.43, 0.84), (1.75, 0.84), (1.75, 0.77), (1.43, 0.77)], -0.118, -0.110)   # couvre-fenêtre
    st.lathe([(1.40, 0.008), (1.78, 0.008)], "X", (0, -0.110, 0.845), 10)  # charnière
    # goupilles et axes (côté gauche et droit)
    for x, z, r in ((1.10, 0.765, 0.022), (1.975, 0.765, 0.022), (1.35, 0.70, 0.014), (1.43, 0.70, 0.014)):
        st.lathe([(-0.112, 0.0), (-0.112, r * 0.8), (-0.108, r), (0.108, r), (0.112, r * 0.8), (0.112, 0.0)],
                 "Y", (x, 0, z), 16)
    # sélecteur de tir (gauche) : axe + levier
    st.lathe([(0.10, 0.03), (0.118, 0.03), (0.122, 0.024)], "Y", (1.21, 0, 0.72), 18)
    st.prism([(1.20, 0.708), (1.31, 0.712), (1.315, 0.728), (1.20, 0.732)], 0.112, 0.128)
    # arrêtoir de culasse (gauche)
    st.prism([(1.78, 0.74), (1.86, 0.80), (1.88, 0.79), (1.83, 0.73), (1.80, 0.72)], 0.104, 0.118)
    # bouton de chargeur (droite)
    st.lathe([(-0.124, 0.0), (-0.124, 0.024), (-0.12, 0.03), (-0.10, 0.03)], "Y", (1.53, 0, 0.73), 18)
    # anneau de grenadière (attache de sangle) arrière
    st.lathe([(0.0, 0.032), (0.03, 0.032)], "Y", (0.93, 0.11, 0.87), 16)
    P.append(st)

    # ------------------------------------------------------------ carcasse inférieure
    lo = Part("Body", "Bas", "AnodiseNoir", bevel=0.006)
    lo.prism([(1.02, 0.80), (2.02, 0.80), (2.02, 0.71), (1.975, 0.66), (1.965, 0.56), (1.93, 0.535),
              (1.52, 0.535), (1.50, 0.56), (1.50, 0.64), (1.28, 0.64), (1.24, 0.66), (1.06, 0.66), (1.02, 0.70)], 0.096)
    # entonnoir du puits de chargeur (plus large en bas)
    lo.prism([(1.51, 0.535), (1.94, 0.535), (1.955, 0.60), (1.50, 0.60)], 0.108)
    # pontet intégré
    lo.prism([(1.26, 0.64), (1.30, 0.64), (1.315, 0.585), (1.36, 0.555), (1.50, 0.555), (1.52, 0.58),
              (1.52, 0.64), (1.50, 0.64), (1.495, 0.578), (1.37, 0.575), (1.325, 0.60), (1.31, 0.64)], 0.038)
    lo.cut_prism([(1.53, 0.62), (1.93, 0.62), (1.93, 0.79), (1.53, 0.79)], 0.086)       # puits (vide)
    lo.cut_prism(rect(1.335, 0.62, 1.495, 0.66), 0.02)                                  # fente de la gâchette
    # renfort du bouton de chargeur et du sélecteur (bossages)
    lo.lathe([(-0.096, 0.05), (-0.108, 0.05), (-0.112, 0.045)], "Y", (1.53, 0, 0.73), 20)
    lo.cut_prism(rect(1.80, 0.60, 1.90, 0.70), 0.12, 0.096)                             # creux de l'arrêtoir
    # gravures : flanc gauche (+Y) -> x = bout côté bouche
    lo.engrave("VANTA ARMS", 1.93, 0.705, 0.040, 1, "sans")
    lo.engrave("AR-01  CAL 5.56x45", 1.93, 0.655, 0.026, 1, "cond")
    lo.engrave("SAFE", 1.205, 0.775, 0.016, 1, "cond")
    lo.engrave("SEMI", 1.345, 0.745, 0.016, 1, "cond")
    lo.engrave("AUTO", 1.345, 0.685, 0.016, 1, "cond")
    lo.engrave("SN  VA-01 0451", 1.62, 0.665, 0.022, -1, "mono")
    lo.engrave("MADE FOR VANTA", 1.62, 0.70, 0.020, -1, "cond")
    P.append(lo)

    # ------------------------------------------------------------ poignée
    gp = Part("Body", "Poignee", "PolymereNoir", bevel=0.022, segs=3, angle=25)
    front = bezier((1.315, 0.645), (1.30, 0.53), (1.30, 0.47), (1.27, 0.40), 6)[:-1] + \
        bezier((1.27, 0.40), (1.25, 0.33), (1.265, 0.25), (1.235, 0.17), 6)
    back = bezier((1.02, 0.18), (1.005, 0.30), (1.03, 0.45), (1.045, 0.56), 7)
    gp.prism([(1.06, 0.66)] + [(1.28, 0.66)] + front + [(1.215, 0.150), (1.04, 0.150)] + back +
             [(1.025, 0.60), (0.995, 0.625), (1.005, 0.655)], 0.074)
    # renflements des doigts (léger) + ergot pour le majeur
    gp.prism([(1.255, 0.50), (1.30, 0.50), (1.305, 0.46), (1.26, 0.44)], 0.068)
    # bouchon inférieur
    gp.cut_prism(rounded(1.06, 0.135, 1.20, 0.175, 0.01), 0.05)
    gp.stipple = [(0.95, 0.17, 1.35, 0.60)]
    gp.engrave("V", 1.13, 0.535, 0.04, 1, "sans")
    # arrêtoir de main (sous le garde-main) : même polymère
    gp.prism([(2.70, 0.755), (2.92, 0.755), (2.93, 0.735), (2.86, 0.68), (2.80, 0.68)], 0.034)
    P.append(gp)

    # ------------------------------------------------------------ crosse (type réglable) + talon caoutchouc
    sk = Part("Body", "Crosse", "PolymereNoir", bevel=0.02, segs=3, angle=28)
    top = bezier((0.06, 1.035), (0.20, 1.06), (0.40, 1.05), (0.52, 1.025), 8)[:-1] + \
        bezier((0.52, 1.025), (0.62, 1.005), (0.70, 0.99), (0.745, 0.965), 4)
    under = bezier((0.745, 0.835), (0.60, 0.815), (0.45, 0.80), (0.36, 0.765), 5)[:-1] + \
        bezier((0.36, 0.765), (0.26, 0.70), (0.17, 0.57), (0.13, 0.475), 6)
    sk.prism(top + under + [(0.06, 0.465)], 0.105)
    sk.prism(top[:6] + [(0.40, 0.80), (0.30, 0.74), (0.20, 0.60), (0.13, 0.475), (0.06, 0.465)], 0.138)
    sk.cut_prism([(0.12, 0.58), (0.23, 0.70), (0.30, 0.80), (0.30, 0.93), (0.25, 0.975),
                  (0.135, 0.975), (0.11, 0.94), (0.11, 0.62)], 0.2)                  # évidement
    sk.cut_prism(rounded(0.40, 0.86, 0.66, 0.95, 0.02), 0.2, 0.094)                   # rainures latérales
    sk.cut_prism(rounded(0.40, 0.86, 0.66, 0.95, 0.02), -0.094, -0.2)
    sk.cut_cyl("X", (0.5, 0, BORE + 0.005), 0.064, 0.6)                               # passage du tube
    sk.cut_box(0.08, 0.12, 0.50, 0.56, 0.2)                                           # passant de sangle
    sk.lathe([(0.0, 0.026), (0.02, 0.026)], "Y", (0.62, 0.105, 0.87), 16)             # douille QD
    sk.cut_cyl("Y", (0.62, 0.13, 0.87), 0.014, 0.06, 12)
    sk.engrave("VANTA", 0.64, 0.885, 0.034, 1, "sans")
    P.append(sk)

    rb = Part("Body", "Talon", "Caoutchouc", bevel=0.012, segs=3)
    rb.prism([(0.0, 0.47), (0.0, 1.035), (0.03, 1.06), (0.065, 1.06), (0.065, 0.47), (0.03, 0.455)], 0.146)
    for z in [0.52 + 0.05 * i for i in range(10)]:
        rb.cut_box(-0.05, 0.006, z, z + 0.018, 0.2)
    P.append(rb)

    # tube de crosse + écrou crénelé : aluminium anodisé
    tb = Part("Body", "Tube", "AnodiseNoir", bevel=0.004)
    tb.lathe([(0.32, 0.0), (0.32, 0.055), (0.33, 0.062), (0.98, 0.062), (0.98, 0.07), (1.035, 0.07),
              (1.035, 0.0)], "X", (0, 0, BORE + 0.005), 28)
    for k in range(6):
        a = math.radians(30 + 60 * k)
        y, z = 0.07 * math.cos(a), BORE + 0.005 + 0.07 * math.sin(a)
        tb.cut_box(0.985, 1.03, z - 0.012, z + 0.012, y - 0.02, y + 0.02)
    # plaque de grenadière arrière
    tb.prism([(0.99, 0.80), (1.03, 0.80), (1.03, 1.0), (0.99, 1.0)], 0.112)
    tb.cut_cyl("X", (1.01, 0, BORE + 0.005), 0.075, 0.1)
    tb.lathe([(0.0, 0.07), (0.05, 0.07)], "X", (0.33, 0, BORE + 0.005), 28)
    # levier de réglage sous la crosse
    tb.prism([(0.40, 0.80), (0.58, 0.80), (0.60, 0.785), (0.42, 0.775)], 0.03)
    P.append(tb)

    # ------------------------------------------------------------ garde-main M-LOK
    hg = Part("Body", "Garde", "AnodiseNoir", bevel=0.006)
    sect = octagon(0.0, 0.89, 0.118, 0.13, 0.05)
    hg.prism_x(sect, 2.03, 3.06)
    hg.cut_prism_x(octagon(0.0, 0.89, 0.100, 0.112, 0.042), 2.08, 3.2)               # creux
    picatinny(hg, 2.03, 3.06, 1.02)
    # écrou de canon (bague arrière)
    hg.lathe([(2.02, 0.0), (2.02, 0.105), (2.06, 0.105), (2.08, 0.0)], "X", (0, 0, BORE), 24)
    # chanfrein avant + fentes M-LOK (flancs, bas)
    for x in (2.18, 2.38, 2.58, 2.78):
        hg.cut_prism(rounded(x, 0.84, x + 0.13, 0.875, 0.016), 0.2)                 # flancs (gauche + droit)
        hg.cut_prism_z(rounded(x, -0.016, x + 0.13, 0.016, 0.016), 0.70, 0.80)     # dessous
    for x in (2.20, 2.42, 2.64, 2.86):
        hg.cut_prism(rounded(x, 0.93, x + 0.09, 0.95, 0.01), 0.2)                   # fentes d'aération hautes
    hg.engrave("VANTA  ML-13", 2.98, 0.775, 0.022, 1, "cond")
    P.append(hg)

    # ------------------------------------------------------------ canon + frein de bouche
    br = Part("Body", "Canon", "AcierNoir", bevel=0.003)
    br.lathe([(2.06, 0.044), (2.95, 0.044), (2.97, 0.040), (3.30, 0.040)], "X", (0, 0, BORE), 22)
    # bloc d'emprunt de gaz visible entre les fentes
    br.prism_x(rounded(-0.045, BORE - 0.06, 0.045, BORE + 0.06, 0.012), 2.62, 2.74)
    # frein de bouche à 3 chambres
    mb = [(3.28, 0.0), (3.28, 0.050), (3.30, 0.058), (3.34, 0.066), (3.60, 0.066), (3.612, 0.060),
          (3.616, 0.045), (3.616, 0.0)]
    br.lathe(mb, "X", (0, 0, BORE), 24)
    for x in (3.38, 3.45, 3.52):
        br.cut_box(x, x + 0.045, BORE - 0.036, BORE + 0.036, 0.2)                    # fentes latérales
    for x in (3.40, 3.50):
        br.cut_cyl("Z", (x, 0.025, BORE + 0.05), 0.010, 0.06, 10)                   # évents du dessus
        br.cut_cyl("Z", (x, -0.025, BORE + 0.05), 0.010, 0.06, 10)
    br.cut_cyl("X", (3.6, 0, BORE), 0.024, 0.2, 16)                                  # âme
    br.cut_box(3.30, 3.316, BORE - 0.07, BORE + 0.07, 0.2)                           # rainure de l'écrou
    P.append(br)

    # ------------------------------------------------------------ viseur holographique + organes de visée
    def arch(hw, z0, zs, zt, n=10):
        """Section (y, z) en arche : flancs verticaux de z0 à zs, sommet à zt."""
        pts = [(-hw, z0), (hw, z0)]
        for i in range(n + 1):
            t = math.pi * i / n
            pts.append((hw * math.cos(t), zs + (zt - zs) * math.sin(t)))
        return pts

    op = Part("Body", "Optique", "CerakoteNoir", bevel=0.006)
    op.prism(rect(1.40, 1.062, 1.80, 1.112), 0.094)                                   # semelle sur le rail
    op.prism_x([(-0.11, 1.105), (0.11, 1.105), (0.11, 1.16), (0.092, 1.19), (-0.092, 1.19),
                (-0.11, 1.16)], 1.395, 1.80)                                          # corps (piles)
    op.prism_x(arch(0.118, 1.16, 1.29, 1.338), 1.465, 1.755)                          # capot en arche
    op.prism_x(arch(0.124, 1.16, 1.292, 1.346), 1.735, 1.772)                         # lèvre avant
    op.cut_prism_x(arch(0.090, 1.156, 1.28, 1.318), 1.40, 1.82)                       # fenêtre
    for x in (1.52, 1.60, 1.68):                                                      # nervures du capot
        op.cut_prism(rect(x, 1.20, x + 0.035, 1.28), 0.2, 0.112)
        op.cut_prism(rect(x, 1.20, x + 0.035, 1.28), -0.112, -0.2)
    # boutons (gauche), cache de pile (droite), levier de fixation rapide (gauche)
    for x in (1.43, 1.47):
        op.prism(rounded(x, 1.125, x + 0.03, 1.16, 0.008), 0.11, 0.122)
    op.lathe([(-0.108, 0.036), (-0.13, 0.036), (-0.136, 0.030)], "Y", (1.665, 0, 1.145), 24)
    op.cut_box(1.44, 1.54, 1.07, 1.10, 0.12, 0.09)
    op.prism([(1.56, 1.068), (1.72, 1.068), (1.745, 1.10), (1.58, 1.108)], 0.094, 0.116)  # levier QD
    op.engrave("VANTA HX-3", 1.785, 1.122, 0.022, 1, "cond")
    op.engrave("HOLO", 1.43, 1.13, 0.02, -1, "cond")
    # mire arrière repliée (sur le rail, à l'arrière)
    op.prism(rect(1.08, 1.062, 1.24, 1.105), 0.068)
    op.prism([(1.10, 1.105), (1.22, 1.105), (1.205, 1.128), (1.115, 1.128)], 0.055)
    op.cut_cyl("Y", (1.16, 0, 1.112), 0.012, 0.2, 12)
    # guidon replié (à l'avant du garde-main)
    op.prism(rect(2.88, 1.062, 3.02, 1.102), 0.066)
    op.prism([(2.90, 1.102), (3.0, 1.102), (2.985, 1.124), (2.915, 1.124)], 0.028)
    P.append(op)

    gl = Part("Body", "Verre", "Verre", bevel=0)
    gl.prism_x(arch(0.090, 1.156, 1.28, 1.318), 1.478, 1.483)
    gl.prism_x(arch(0.090, 1.156, 1.28, 1.318), 1.745, 1.750)
    P.append(gl)

    rt = Part("Body", "Reticule", "Tritium", bevel=0, weld=False)
    rt.lathe([(-0.0012, 0.032), (0.0012, 0.032)], "X", (1.61, 0, 1.232), 32)
    rt.cut_lathe([(-0.01, 0.0275), (0.01, 0.0275)], "X", (1.61, 0, 1.232), 32)
    rt.lathe([(-0.0012, 0.0045), (0.0012, 0.0045)], "X", (1.61, 0, 1.232), 12)
    P.append(rt)

    # ------------------------------------------------------------ chargeur (polymère, courbe)
    mg = Part("Magazine", "Chargeur", "PolymereNoir", bevel=0.010, segs=3)
    front = bezier((1.905, 0.70), (1.90, 0.50), (1.92, 0.30), (1.975, 0.085), 8)
    back = bezier((1.665, 0.085), (1.615, 0.30), (1.585, 0.50), (1.575, 0.70), 8)
    mg.prism(front + back, 0.082)
    # nervures de prise (haut) + panneau texturé
    for i in range(4):
        z = 0.48 - 0.035 * i
        mg.prism([(1.595 + 0.01 * i, z), (1.905 + 0.012 * i, z), (1.907 + 0.012 * i, z + 0.014),
                  (1.597 + 0.01 * i, z + 0.014)], 0.088)
    # semelle évasée
    mg.prism([(1.645, 0.0), (2.005, 0.0), (2.012, 0.03), (1.995, 0.10), (1.66, 0.10), (1.642, 0.03)], 0.098)
    mg.cut_box(1.70, 1.95, 0.035, 0.065, 0.2, 0.093)
    mg.cut_box(1.70, 1.95, 0.035, 0.065, -0.093, -0.2)
    mg.stipple = [(1.6, 0.14, 2.0, 0.34)]
    mg.engrave("5.56 NATO", 1.92, 0.25, 0.022, 1, "cond")
    mg.engrave("30", 1.80, 0.17, 0.04, 1, "sans")
    mg.engrave("VANTA", 1.70, 0.20, 0.024, -1, "cond")
    P.append(mg)

    # ------------------------------------------------------------ gâchette
    tg = Part("Trigger", "Gachette", "AcierNoir", bevel=0.003)
    tg.prism([(1.400, 0.655), (1.428, 0.655), (1.442, 0.62), (1.445, 0.59), (1.437, 0.565), (1.418, 0.553),
              (1.412, 0.566), (1.420, 0.59), (1.416, 0.62)], 0.016)
    P.append(tg)

    # ------------------------------------------------------------ levier d'armement (poignée en T ambidextre)
    ch = Part("ChargingHandle", "Levier", "AnodiseNoir", bevel=0.005)
    ch.prism_z([(0.95, -0.05), (1.07, -0.05), (1.07, 0.05), (0.95, 0.05)], 0.985, 1.025)
    ch.prism_z([(0.935, -0.155), (0.975, -0.165), (1.005, -0.13), (1.005, 0.13), (0.975, 0.165),
                (0.935, 0.155), (0.925, 0.10), (0.925, -0.10)], 0.982, 1.028)
    for s in (1, -1):
        ch.cut_box(0.93, 0.99, 0.99, 1.02, s * 0.12, s * 0.20)
    P.append(ch)
    return P
