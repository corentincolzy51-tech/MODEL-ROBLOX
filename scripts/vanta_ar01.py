"""Géométrie de la VANTA AR-01 (fusil d'assaut style AK) pour Blender.

Convention du jeu :
  - canon vers +X, haut vers +Z, origine sur la poignée
  - pièces séparées : Body, Magazine, Trigger, ChargingHandle
  - taille finale : 1,096 x 0,407 x 0,112 m (3,616 x 1,343 x 0,369 studs)

Les profils sont dessinés en vue de côté (X, Z) en "mm de design"
puis extrudés en épaisseur (Y). Chaque morceau reçoit un nom de matériau,
utilisé ensuite par le skin.
"""
import math
import bpy  # noqa: F401  (doit être importé avant bmesh)
import bmesh
from mathutils import Matrix, Vector

TARGET = Vector((1.096, 0.112, 0.407))  # X longueur, Y épaisseur, Z hauteur
GRIP_POINT = (325.0, -55.0)             # centre de la poignée (mm design)
MM = 0.001
_scale = Vector((1, 1, 1))  # rempli par _normalize


def design_to_world(x, z):
    """Convertit un point du profil (mm design) en mètres monde."""
    return ((x - GRIP_POINT[0]) * MM * _scale.x, (z - GRIP_POINT[1]) * MM * _scale.z)


def _prism(bm, profile, y0, y1):
    """Extrude un polygone XZ (mm) entre y0 et y1 (m)."""
    low = [bm.verts.new((x * MM, y0, z * MM)) for x, z in profile]
    face = bm.faces.new(low)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    top = [v for v in res["geom"] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, y1 - y0, 0))
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])


def _cyl(bm, x0, x1, z, r, y=0.0, segs=16):
    """Cylindre le long de X (valeurs x0, x1, z, r en mm)."""
    length = (x1 - x0) * MM
    mat = Matrix.Translation(((x0 + x1) / 2 * MM, y, z * MM)) @ Matrix.Rotation(math.radians(90), 4, "Y")
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r * MM,
                          radius2=r * MM, depth=length, matrix=mat)


def _cyl_y(bm, y0, y1, x, z, r, segs=12):
    """Cylindre le long de Y (y en m, x/z/r en mm)."""
    mat = Matrix.Translation((x * MM, (y0 + y1) / 2, z * MM)) @ Matrix.Rotation(math.radians(90), 4, "X")
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r * MM,
                          radius2=r * MM, depth=abs(y1 - y0), matrix=mat)


def _piece(name, mat_name, build, bevel=0.0025):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    build(bm)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
    me.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
        mod.angle_limit = math.radians(35)
        mod.harden_normals = True
    return ob


def _mag_profile():
    """Chargeur banane : arc de cercle qui part vers l'avant."""
    cx, cz, r, half = 925.0, 8.0, 450.0, 34.0
    a0, a1, n = math.radians(180), math.radians(208), 14
    rear, front = [], []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        w = half + 4.0 * i / n  # s'élargit un peu vers le bas
        rear.append((cx + (r + w) * math.cos(a), cz + (r + w) * math.sin(a)))
        front.append((cx + (r - w) * math.cos(a), cz + (r - w) * math.sin(a)))
    return rear + front[::-1]


def _mag_floorplate():
    """Semelle du chargeur, collée au bas de l'arc."""
    cx, cz, r, a = 925.0, 8.0, 450.0, math.radians(208)
    t = (-math.sin(a), math.cos(a))  # direction "vers le bas" le long de l'arc
    pts = []
    for rad, push in ((r + 42, -2), (r + 42, 9), (r - 42, 9), (r - 42, -2)):
        x, z = cx + rad * math.cos(a), cz + rad * math.sin(a)
        pts.append((x + t[0] * push, z + t[1] * push))
    return pts


def build():
    """Construit les 4 objets et renvoie {nom: objet}."""
    parts = {}

    # ---------- Body : plusieurs morceaux joints ----------
    body_pieces = []

    def add(name, mat, fn, bevel=0.0025):
        body_pieces.append(_piece(name, mat, fn, bevel))

    # crosse + plaque de couche
    add("stock", "Skin", lambda bm: _prism(bm, [(14, -80), (14, 40), (250, 57), (262, 57), (262, 4), (238, -3)], -0.035, 0.035))
    add("buttplate", "Accent", lambda bm: _prism(bm, [(0, -82), (0, 41), (16, 41), (16, -81)], -0.036, 0.036), 0.002)
    # carcasse + couvercle
    add("receiver", "Skin", lambda bm: _prism(bm, [(255, 0), (255, 56), (272, 62), (522, 62), (536, 58), (536, 0)], -0.028, 0.028))
    # hausse (rear sight)
    add("rearsight", "Metal", lambda bm: _prism(bm, [(530, 50), (530, 70), (548, 80), (584, 77), (590, 60), (590, 50)], -0.02, 0.02))
    # poignée pistolet
    add("grip", "Skin", lambda bm: _prism(bm, [(318, 2), (362, 2), (354, -30), (340, -108), (300, -114), (290, -102), (306, -30)], -0.022, 0.022))
    # pontet (trigger guard)
    add("guard", "Metal", lambda bm: _prism(bm, [(350, -29), (422, -29), (422, 0), (434, 0), (434, -37), (350, -37)], -0.009, 0.009), 0.0015)
    # garde-main inférieur et supérieur
    add("handguard_low", "Skin", lambda bm: _prism(bm, [(540, 6), (540, 50), (716, 50), (716, 17), (700, 9), (562, 3)], -0.032, 0.032))
    add("handguard_up", "Skin", lambda bm: _prism(bm, [(592, 50), (592, 70), (604, 77), (712, 77), (722, 70), (722, 50)], -0.022, 0.022))
    # canon blanc + bloc d'emprunt + guidon + frein de bouche
    add("barrel", "Metal", lambda bm: _cyl(bm, 530, 862, 42, 10), 0)
    add("gasblock", "Dark", lambda bm: _prism(bm, [(718, 30), (718, 80), (764, 70), (764, 30)], -0.016, 0.016))
    add("gastube", "Metal", lambda bm: _cyl(bm, 760, 790, 66, 7), 0)
    add("frontsight", "Dark", lambda bm: _prism(bm, [(798, 28), (798, 60), (810, 98), (824, 98), (828, 60), (838, 56), (838, 28)], -0.013, 0.013))
    add("muzzle", "Dark", lambda bm: _prism(bm, [(855, 28), (855, 56), (888, 56), (880, 28)], -0.014, 0.014))
    add("rod", "Metal", lambda bm: _cyl(bm, 610, 800, 24, 3.5, segs=10), 0)
    # sélecteur (levier côté droit)
    add("selector", "Metal", lambda bm: _prism(bm, [(300, 30), (300, 42), (440, 50), (440, 42)], -0.031, -0.027), 0.001)

    bpy.ops.object.select_all(action="DESELECT")
    for ob in body_pieces:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = body_pieces[0]
    for ob in body_pieces:
        bpy.context.view_layer.objects.active = ob
        for m in ob.modifiers:
            bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.context.view_layer.objects.active = body_pieces[0]
    bpy.ops.object.join()
    body = bpy.context.object
    body.name = body.data.name = "Body"
    parts["Body"] = body

    # ---------- Magazine ----------
    mag = _piece("Magazine", "Skin", lambda bm: (
        _prism(bm, _mag_profile(), -0.024, 0.024),
        _prism(bm, _mag_floorplate(), -0.026, 0.026),  # semelle
    ))
    parts["Magazine"] = mag

    # ---------- Trigger ----------
    parts["Trigger"] = _piece("Trigger", "Metal", lambda bm: _prism(
        bm, [(380, 2), (390, 2), (393, -12), (386, -25), (378, -24), (384, -12)], -0.004, 0.004), 0.001)

    # ---------- ChargingHandle (côté droit = -Y) ----------
    def handle(bm):
        _prism(bm, [(420, 38), (420, 50), (512, 50), (512, 38)], -0.032, -0.027)  # plaque du porte-culasse
        _cyl_y(bm, -0.072, -0.03, 500, 44, 5)                                        # tige
        _cyl_y(bm, -0.077, -0.066, 500, 44, 8)                                       # bouton
    parts["ChargingHandle"] = _piece("ChargingHandle", "Metal", handle, 0.001)

    for ob in parts.values():
        bpy.context.view_layer.objects.active = ob
        for m in list(ob.modifiers):
            bpy.ops.object.modifier_apply(modifier=m.name)

    _normalize(parts)
    return parts


def _normalize(parts):
    """Met l'arme aux dimensions cibles et place l'origine sur la poignée."""
    pts = [ob.matrix_world @ v.co for ob in parts.values() for v in ob.data.vertices]
    lo = Vector((min(p[i] for p in pts) for i in range(3)))
    hi = Vector((max(p[i] for p in pts) for i in range(3)))
    size = hi - lo
    scale = Vector((TARGET[i] / size[i] for i in range(3)))
    _scale[:] = scale
    pivot = Vector((GRIP_POINT[0] * MM, 0.0, GRIP_POINT[1] * MM))
    m = Matrix.Diagonal((*scale, 1.0)) @ Matrix.Translation(-pivot)
    for ob in parts.values():
        ob.data.transform(m)
        ob.data.update()
        ob.location = (0, 0, 0)
