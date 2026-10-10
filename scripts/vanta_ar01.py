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
import math

import bpy  # noqa: F401  (doit être importé avant bmesh)
import bmesh
from mathutils import Matrix, Vector

STUD = 1.096 / 3.616                  # mètres par stud (d'après le tableau des tailles)
TARGET = Vector((3.616, 0.369, 1.343))  # studs : longueur, épaisseur, hauteur
GRIP_POINT = (1.17, 0.42)             # centre de la poignée (studs design)
CONTOUR = 0.022                       # épaisseur du contour noir (studs)
GROUPS = {"Body": "Corps", "Magazine": "Chargeur", "Trigger": "Gachette", "ChargingHandle": "Levier"}
_scale = Vector((1, 1, 1))


def design_to_world(x, z):
    """Point du profil (studs design) -> mètres monde (origine poignée)."""
    return ((x - GRIP_POINT[0]) * STUD * _scale.x, (z - GRIP_POINT[1]) * STUD * _scale.z)


# ---------------------------------------------------------------- primitives
def _prism(bm, profile, half, y_center=0.0):
    y0, y1 = (y_center - half) * STUD, (y_center + half) * STUD
    face = bm.faces.new([bm.verts.new((x * STUD, y0, z * STUD)) for x, z in profile])
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    top = [v for v in res["geom"] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, y1 - y0, 0))


def _box(bm, x0, x1, z0, z1, half, y_center=0.0):
    _prism(bm, [(x0, z0), (x0, z1), (x1, z1), (x1, z0)], half, y_center)


def _cyl_x(bm, x0, x1, z, r, segs=16):
    mat = Matrix.Translation(((x0 + x1) / 2 * STUD, 0, z * STUD)) @ Matrix.Rotation(math.radians(90), 4, "Y")
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r * STUD, radius2=r * STUD,
                          depth=(x1 - x0) * STUD, matrix=mat)


def _cyl_y(bm, x, z, r, half, segs=14):
    mat = Matrix.Translation((x * STUD, 0, z * STUD)) @ Matrix.Rotation(math.radians(90), 4, "X")
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r * STUD, radius2=r * STUD,
                          depth=2 * half * STUD, matrix=mat)


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
        _prism(bm, [(0.05, 0.50), (0.05, 1.00), (0.12, 1.04), (0.62, 1.00), (0.70, 0.94),
                    (0.70, 0.80), (0.45, 0.74), (0.30, 0.60), (0.14, 0.50)], 0.15),
        # carcasse inférieure + puits de chargeur
        _prism(bm, [(1.04, 0.64), (1.04, 0.84), (2.02, 0.84), (2.02, 0.70), (1.88, 0.62),
                    (1.88, 0.52), (1.50, 0.52), (1.50, 0.64)], 0.11),
        # carcasse supérieure
        _prism(bm, [(1.04, 0.84), (1.04, 1.02), (1.08, 1.06), (2.02, 1.06), (2.02, 0.84)], 0.105),
        # garde-main
        _prism(bm, [(2.02, 0.72), (2.02, 1.06), (2.92, 1.06), (2.96, 1.02), (2.96, 0.76), (2.92, 0.72)], 0.13),
        # poignée
        _prism(bm, [(1.12, 0.64), (1.36, 0.64), (1.31, 0.50), (1.22, 0.18), (1.03, 0.16),
                    (0.99, 0.22), (1.10, 0.50)], 0.085),
    ))
    add("Body", "Sombre", lambda bm: (
        _box(bm, 0.0, 0.07, 0.49, 1.01, 0.155),                     # plaque de couche
        _cyl_x(bm, 0.66, 1.06, 0.88, 0.075),                        # tube de crosse
        _box(bm, 1.04, 2.95, 1.06, 1.10, 0.065),                    # rail
        *[_box(bm, x, x + 0.06, 1.10, 1.14, 0.07) for x in [1.08 + 0.12 * i for i in range(16)]],
        # viseur point rouge : boîtier creux (on voit à travers en visée)
        _box(bm, 1.44, 1.78, 1.12, 1.145, 0.11),                    # semelle
        _prism(bm, [(1.46, 1.315), (1.49, 1.343), (1.73, 1.343), (1.76, 1.315)], 0.11),  # toit
        _box(bm, 1.46, 1.76, 1.145, 1.315, 0.008, 0.102),           # flanc gauche
        _box(bm, 1.46, 1.76, 1.145, 1.315, 0.008, -0.102),          # flanc droit
        _box(bm, 1.48, 1.80, 0.88, 0.98, 0.006, -0.111),            # fenêtre d'éjection (droite)
        *[_box(bm, x0, x1, 0.765, 0.835, 0.135) for x0, x1 in ((2.20, 2.40), (2.48, 2.68), (2.76, 2.86))],
        _cyl_x(bm, 3.36, 3.616, 0.90, 0.095),                       # frein de bouche
        _prism(bm, [(1.30, 0.53), (1.30, 0.56), (1.50, 0.56), (1.50, 0.64), (1.53, 0.64), (1.53, 0.53)], 0.03),
    ))
    add("Body", "Clair", lambda bm: (
        _cyl_x(bm, 2.95, 3.40, 0.90, 0.06),                         # canon
        _box(bm, 1.10, 1.30, 0.90, 0.98, 0.112),                    # assistance de fermeture
    ))
    add("Body", "Accent", lambda bm: (
        _box(bm, 1.00, 1.06, 0.66, 1.06, 0.115),                    # plaque arrière de carcasse
        _cyl_x(bm, 2.94, 3.00, 0.90, 0.085),                        # bague avant
        _box(bm, 0.20, 0.60, 1.00, 1.035, 0.152),                   # liseré sur la crosse
    ))
    add("Body", "Accent2", lambda bm: (
        _cyl_y(bm, 2.12, 0.95, 0.045, 0.14),                        # bouton du garde-main
        _cyl_x(bm, 3.42, 3.45, 0.90, 0.10),                         # bagues du frein
        _cyl_x(bm, 3.54, 3.57, 0.90, 0.10),
    ))
    # cadre intérieur + verre, à l'arrière du viseur (côté œil) pour une grande fenêtre
    add("Body", "Cadre", lambda bm: (
        _box(bm, 1.47, 1.49, 1.145, 1.159, 0.094),
        _box(bm, 1.47, 1.49, 1.301, 1.315, 0.094),
        _box(bm, 1.47, 1.49, 1.159, 1.301, 0.003, 0.091),
        _box(bm, 1.47, 1.49, 1.159, 1.301, 0.003, -0.091),
    ), 0.0)
    add("Body", "Verre", lambda bm: _box(bm, 1.478, 1.482, 1.159, 1.301, 0.088), 0.0)

    # ---- Chargeur
    add("Magazine", "Motif", lambda bm: _prism(bm, [(1.53, 0.60), (1.83, 0.60), (1.93, 0.10), (1.63, 0.10)], 0.085))
    add("Magazine", "Accent2", lambda bm: (
        _prism(bm, [(1.585, 0.33), (1.885, 0.33), (1.895, 0.28), (1.595, 0.28)], 0.088),
        _prism(bm, [(1.565, 0.43), (1.865, 0.43), (1.875, 0.38), (1.575, 0.38)], 0.088),
    ), 0.006)
    add("Magazine", "Accent", lambda bm: _prism(bm, [(1.625, 0.14), (1.925, 0.14), (1.93, 0.10), (1.63, 0.10)], 0.09), 0.006)
    add("Magazine", "Sombre", lambda bm: _box(bm, 1.61, 1.96, 0.0, 0.10, 0.095))

    # ---- Gâchette
    add("Trigger", "Gachette", lambda bm: _prism(bm, [(1.38, 0.64), (1.42, 0.64), (1.435, 0.60), (1.415, 0.565),
                                                      (1.395, 0.57), (1.405, 0.60)], 0.014), 0.004)

    # ---- Levier d'armement (poignée en T à l'arrière du rail)
    add("ChargingHandle", "Clair", lambda bm: _box(bm, 0.94, 1.06, 1.00, 1.06, 0.06), 0.008)
    add("ChargingHandle", "Accent", lambda bm: _box(bm, 0.94, 1.00, 1.00, 1.06, 0.1845), 0.008)

    # ---- Root : repère sur la poignée
    add("Root", "Root", lambda bm: _box(bm, GRIP_POINT[0] - 0.1, GRIP_POINT[0] + 0.1,
                                        GRIP_POINT[1] - 0.1, GRIP_POINT[1] + 0.1, 0.1), 0.0)
    return P


def _make(name, fn, bevel):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    fn(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if bevel:
        mod = ob.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel * STUD
        mod.segments = 2
        mod.limit_method = "ANGLE"
        mod.angle_limit = math.radians(35)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob


def _inverted_hull(name, sources, thickness_m):
    """Contour façon cartoon : coque gonflée, faces retournées."""
    bm = bmesh.new()
    for ob in sources:
        bm.from_mesh(ob.data)
    # pas de remove_doubles : souder des pièces qui se touchent fausse les normales
    # (le contour du viseur venait boucher la visée)
    bm.normal_update()
    moves = []
    for v in bm.verts:
        if not v.link_faces:
            moves.append(Vector())
            continue
        n = Vector()
        for f in v.link_faces:
            n += f.normal * f.calc_area()
        n = n.normalized() if n.length > 1e-9 else v.normal
        d = min(max(n.dot(f.normal), 0.35) for f in v.link_faces)
        moves.append(n * thickness_m / d)
    for v, m in zip(bm.verts, moves):
        v.co += m
    bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def build():
    """Construit toutes les pièces. Renvoie {(groupe, rôle): objet}."""
    objs = {}
    for group, role, fn, bevel in pieces():
        objs[(group, role)] = _make(f"{group}_{role}", fn, bevel)
    _normalize(objs)
    return objs


def add_contours(objs):
    """Contour noir par groupe (sans le verre ni le cadre du viseur). {groupe: objet}."""
    out = {}
    for prefix in GROUPS:
        src = [o for (g, r), o in objs.items() if g == prefix and r not in ("Verre", "Cadre")]
        out[prefix] = _inverted_hull(f"{prefix}_Contour", src, CONTOUR * STUD)
    return out


def assemble(objs, contours, palette, model_name):
    """
    Renomme/fusionne les pièces selon la palette du skin.
    palette : {rôle: nom_de_couleur}. Motif -> nom du skin. Cadre suit Accent.
    Renvoie {nom_final: objet} rangés sous Model > Corps/Chargeur/Gachette/Levier.
    """
    final = {}
    for (group, role), ob in objs.items():
        if group == "Root":
            name = "Root"
        elif group == "Trigger":
            name = "Trigger"
        else:
            color = palette["Accent" if role == "Cadre" else role]
            name = f"{group}_{color}"
        if name in final:
            bpy.ops.object.select_all(action="DESELECT")
            ob.select_set(True)
            final[name].select_set(True)
            bpy.context.view_layer.objects.active = final[name]
            bpy.ops.object.join()
        else:
            final[name] = ob
    for group, ob in contours.items():
        final[f"{group}_Contour"] = ob
    for name, ob in final.items():
        ob.name = ob.data.name = name
    organize(final, model_name)
    return final


def organize(objs, model_name):
    """Empties Model > Corps/Chargeur/Gachette/Levier comme dans Roblox."""
    root = bpy.data.objects.new(model_name, None)
    bpy.context.collection.objects.link(root)
    empties = {}
    for prefix, gname in GROUPS.items():
        e = bpy.data.objects.new(gname, None)
        bpy.context.collection.objects.link(e)
        e.parent = root
        empties[prefix] = e
    for name, ob in objs.items():
        ob.parent = root if name == "Root" else empties[name.split("_")[0]]
    return root


def _normalize(objs):
    """Taille exacte (sans le Root) et origine sur la poignée."""
    pts = [v.co for (g, r), ob in objs.items() if g != "Root" for v in ob.data.vertices]
    size = Vector((max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)))
    scale = Vector((TARGET[i] * STUD / size[i] for i in range(3)))
    _scale[:] = scale
    pivot = Vector((GRIP_POINT[0] * STUD, 0.0, GRIP_POINT[1] * STUD))
    m = Matrix.Diagonal((*scale, 1.0)) @ Matrix.Translation(-pivot)
    for ob in objs.values():
        ob.data.transform(m)
        ob.data.update()
