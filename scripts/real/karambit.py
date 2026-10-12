"""Karambit réaliste : lame en griffe (acier satiné, émouture plate), anneau, plaquettes G10, vis Torx.

Tenu comme le couteau du jeu : manche dans le poing, anneau à l'arrière, lame vers l'avant
qui plonge en griffe. Gabarit : 1,625 studs de long. Tout est dans Corps.
"""
import math

from kit import Part, bezier, circle_pts

NAME = "Couteau"
FOLDER = "Couteau"
LABEL = "KARAMBIT"
GRIP = (0.45, 0.305)
RING = (0.115, 0.31, 0.125, 0.078)     # centre x, z, rayon extérieur, rayon intérieur
T = 0.021                              # demi-épaisseur de l'acier
# repère d'animation : les tours de lame se font autour de l'anneau (index dans l'anneau)
ATTACHES = {"Anneau": ("Body_Lame", (RING[0], 0.0, RING[1]))}

VIEWS = [
    ("apercu", (-0.15, 1.0, 0.22), 1.5, 0.0),
    ("apercu_droite", (0.30, -1.0, 0.35), 1.55, 0.0),
]


def _sample(curve_pts, n):
    """Rééchantillonne une polyligne en n points régulièrement espacés."""
    d = [0.0]
    for a, b in zip(curve_pts, curve_pts[1:]):
        d.append(d[-1] + math.dist(a, b))
    out = []
    for i in range(n):
        t = d[-1] * i / (n - 1)
        k = max(j for j in range(len(d)) if d[j] <= t + 1e-12)
        k = min(k, len(curve_pts) - 2)
        u = (t - d[k]) / max(d[k + 1] - d[k], 1e-12)
        a, b = curve_pts[k], curve_pts[k + 1]
        out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
    return out


SPINE = bezier((0.62, 0.415), (1.12, 0.53), (1.70, 0.36), (1.555, -0.125), 40)
EDGE = bezier((0.70, 0.205), (1.00, 0.27), (1.42, 0.22), (1.555, -0.125), 40)


def blade_sections(n=36, grind=0.62, edge_t=0.0016):
    """Sections (anneaux de 6 points) de la lame : dos, émouture, fil."""
    sp, ed = _sample(SPINE, n), _sample(EDGE, n)
    secs = []
    for i in range(n - 1):
        (sx, sz), (ex, ez) = sp[i], ed[i]
        f = 1 - (i / (n - 1)) ** 3            # l'épaisseur diminue vers la pointe
        t = T * (0.35 + 0.65 * f)
        gx, gz = ex + (sx - ex) * grind, ez + (sz - ez) * grind
        secs.append([(sx, t, sz), (gx, t, gz), (ex, edge_t, ez), (ex, -edge_t, ez), (gx, -t, gz), (sx, -t, sz)])
    tip = sp[-1]
    secs.append([(tip[0], 0.0015, tip[1]), (tip[0], 0.0012, tip[1]), (tip[0], 0.0006, tip[1]),
                 (tip[0], -0.0006, tip[1]), (tip[0], -0.0012, tip[1]), (tip[0], -0.0015, tip[1])])
    return secs


HANDLE_TOP = bezier((0.20, 0.405), (0.36, 0.43), (0.52, 0.425), (0.66, 0.42), 8)
HANDLE_BOT = [(0.74, 0.215)] + bezier((0.72, 0.205), (0.62, 0.17), (0.58, 0.245), (0.52, 0.215), 5)[1:] + \
    bezier((0.52, 0.215), (0.46, 0.18), (0.40, 0.25), (0.34, 0.21), 5)[1:] + [(0.24, 0.21)]


def build():
    P = []
    cx, cz, ro, ri = RING

    # ------------------------------------------------------------ acier : lame + soie + anneau (une pièce)
    bl = Part("Body", "Lame", "Lame", bevel=0.004, segs=2, angle=40)
    bl.loft(blade_sections())
    # soie (manche) : profil du manche, pleine épaisseur
    bl.prism(HANDLE_TOP + [(0.70, 0.415), (0.78, 0.36), (0.80, 0.27), (0.76, 0.215)] + HANDLE_BOT +
             [(0.20, 0.215)], T)
    # anneau
    bl.prism(circle_pts(cx, cz, ro, 40), T)
    bl.cut_prism(circle_pts(cx, cz, ri, 32), 0.1)
    # crans de pouce sur le dos (jimping) et sur l'anneau
    for i in range(7):
        x = 0.70 + i * 0.022
        z = 0.42 + 0.06 * (x - 0.70) / 0.14
        bl.cut_prism([(x, z - 0.004), (x + 0.008, z - 0.004), (x + 0.008, z + 0.05), (x, z + 0.05)], 0.1)
    for k in range(9):
        a = math.radians(100 + 14 * k)
        px, pz = cx + ro * math.cos(a), cz + ro * math.sin(a)
        bl.cut_prism(circle_pts(px, pz, 0.006, 8), 0.1)
    # trous de vis des plaquettes (visibles sur l'anneau : non) + trou de dragonne
    bl.cut_prism(circle_pts(0.27, 0.31, 0.012, 12), 0.1)
    bl.engrave("VANTA", 1.02, 0.355, 0.034, 1, "sans")
    bl.engrave("D2 STEEL", 0.98, 0.325, 0.018, 1, "cond")
    bl.engrave("KARAMBIT", 0.90, 0.33, 0.02, -1, "cond")
    P.append(bl)

    # ------------------------------------------------------------ plaquettes G10 (gauche / droite)
    sc = Part("Body", "Manche", "G10", bevel=0.012, segs=3, angle=25, weld=False)
    inner = [(0.25, 0.395), (0.40, 0.413), (0.55, 0.41), (0.665, 0.405), (0.715, 0.37), (0.725, 0.27),
             (0.70, 0.228)] + [(x, z + 0.012) for x, z in HANDLE_BOT[2:]] + [(0.255, 0.225), (0.235, 0.31)]
    for s in (1, -1):
        sc.prism(inner, s * (T - 0.001), s * (T + 0.028))
    # rainures de préhension
    for x in (0.36, 0.44, 0.52):
        for s in (1, -1):
            sc.cut_prism([(x, 0.25), (x + 0.012, 0.25), (x + 0.03, 0.37), (x + 0.018, 0.37)],
                         s * (T + 0.022), s * 0.2)
    sc.engrave("V", 0.66, 0.29, 0.05, 1, "sans")
    P.append(sc)

    # ------------------------------------------------------------ vis Torx + tube de dragonne
    sw = Part("Body", "Vis", "AcierNoir", bevel=0, weld=False)
    for x, z in ((0.30, 0.31), (0.48, 0.315), (0.64, 0.32)):
        for s in (1, -1):
            sw.lathe([(0.0, 0.0), (0.0, 0.018), (0.004 * s, 0.017), (0.008 * s, 0.012), (0.008 * s, 0.0)], "Y",
                     (x, s * (T + 0.024), z), 12)
            sw.cut_prism([(x - 0.006, z - 0.002), (x + 0.006, z - 0.002), (x + 0.006, z + 0.002), (x - 0.006, z + 0.002)],
                         s * (T + 0.029), s * (T + 0.036))
            sw.cut_prism([(x - 0.002, z - 0.006), (x + 0.002, z - 0.006), (x + 0.002, z + 0.006), (x - 0.002, z + 0.006)],
                         s * (T + 0.029), s * (T + 0.036))
    P.append(sw)
    return P
