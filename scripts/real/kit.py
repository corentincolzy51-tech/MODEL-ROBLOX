"""Kit des armes réalistes (haute qualité, sans contour cartoon).

Unités : 1 unité Blender = 1 stud (comme les FBX du jeu). Canon vers +X, haut vers +Z,
côté gauche de l'arme = +Y (la fenêtre d'éjection est à droite, côté -Y).

Une pièce (Part) = un objet Roblox (MeshPart) = un matériau PBR cuit en 4 textures
(couleur, rugosité, métal, normales). Elle se construit avec des volumes :
  - prism   : profil vu de côté (X, Z) extrudé en Y
  - lathe   : profil de révolution (x, rayon) autour d'un axe X, Y ou Z
  - loft    : sections successives (pour les lames, crosses galbées...)
puis des découpes (cut_*) en booléen, un biseau d'usinage et des normales pondérées.
"""
import math

import bpy  # noqa: F401  (doit être importé avant bmesh)
import bmesh
from mathutils import Matrix, Vector

GROUPS = {"Body": "Corps", "Magazine": "Chargeur", "Trigger": "Gachette", "ChargingHandle": "Levier"}


# ------------------------------------------------------------------ volumes (bmesh)
def _bm_prism(bm, profile, y0, y1):
    """Profil (X, Z) fermé, sens quelconque, extrudé de y0 à y1."""
    pts = list(profile)
    # sens trigonométrique vu depuis +Y -> normales vers l'extérieur
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
               for i in range(len(pts)))
    if area < 0:
        pts.reverse()
    a = [bm.verts.new((x, y0, z)) for x, z in pts]
    b = [bm.verts.new((x, y1, z)) for x, z in pts]
    n = len(pts)
    bm.faces.new(list(reversed(b)))
    bm.faces.new(a)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], b[i], b[j], a[j]))


def _bm_prism_axis(bm, profile, a0, a1, axis):
    """Profil extrudé le long d'un axe. axis Y : (x, z) ; X : (y, z) ; Z : (x, y)."""
    tmp = bmesh.new()
    _bm_prism(tmp, profile, a0, a1)
    for v in tmp.verts:
        u, e, w = v.co
        if axis == "X":
            v.co = (e, u, w)
        elif axis == "Z":
            v.co = (u, w, e)
    bmesh.ops.recalc_face_normals(tmp, faces=tmp.faces[:])
    me = bpy.data.meshes.new("_tmp")
    tmp.to_mesh(me)
    tmp.free()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)


def _axis_matrix(axis, center):
    c = Vector(center)
    if axis == "X":
        rot = Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))  # z local -> X
    elif axis == "Y":
        rot = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    else:
        rot = Matrix.Identity(4)
    return Matrix.Translation(c) @ rot


def _bm_lathe(bm, profile, axis="X", center=(0, 0, 0), segs=24, phase=0.0, sx=1.0, sy=1.0):
    """Révolution. profile = [(t, r)] le long de l'axe (t croissant), r >= 0.

    Les rayons nuls ferment l'objet en pointe ; sinon les bouts sont bouchés.
    Repère local : axe = z local ; sx, sy étirent la section (ellipse).
    """
    m = _axis_matrix(axis, center)
    rings = []
    for t, r in profile:
        if r <= 1e-6:
            rings.append([bm.verts.new(m @ Vector((0, 0, t)))])
            continue
        ring = []
        for k in range(segs):
            a = phase + 2 * math.pi * k / segs
            ring.append(bm.verts.new(m @ Vector((r * math.cos(a) * sx, r * math.sin(a) * sy, t))))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        if len(r0) == 1 and len(r1) == 1:
            continue
        if len(r0) == 1:
            for k in range(segs):
                bm.faces.new((r0[0], r1[k], r1[(k + 1) % segs]))
        elif len(r1) == 1:
            for k in range(segs):
                bm.faces.new((r0[(k + 1) % segs], r0[k], r1[0]))
        else:
            for k in range(segs):
                bm.faces.new((r0[k], r0[(k + 1) % segs], r1[(k + 1) % segs], r1[k]))
    if len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    if len(rings[-1]) > 1:
        bm.faces.new(rings[-1])


def _bm_loft(bm, sections, closed_ends=True):
    """Sections = listes de points 3D de même taille (anneaux fermés), dans l'ordre."""
    rings = [[bm.verts.new(p) for p in s] for s in sections]
    n = len(sections[0])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(n):
            bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]))
    if closed_ends:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])


def _bm_tube(bm, p0, p1, r0, r1, segs=16):
    """Cylindre / tronc de cône entre deux points 3D."""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    q = d.to_track_quat("Z", "Y")
    m = Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r0, radius2=r1, depth=d.length, matrix=m)


def _bm_sphere(bm, c, r, segs=16, sz=1.0):
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=max(6, segs // 2), radius=r,
                              matrix=Matrix.Translation(Vector(c)) @ Matrix.Diagonal((1, 1, sz, 1)))


def _bm_box3(bm, c, size):
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector(c)) @ Matrix.Diagonal((*size, 1)))


def rect(x0, z0, x1, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def rounded(x0, z0, x1, z1, r, n=4):
    """Rectangle aux coins arrondis (profil)."""
    r = min(r, (x1 - x0) / 2, (z1 - z0) / 2)
    pts = []
    for cx, cz, a0 in ((x1 - r, z0 + r, -90), (x1 - r, z1 - r, 0), (x0 + r, z1 - r, 90), (x0 + r, z0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def arc(cx, cz, r, a0, a1, n):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append(tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d
                         for a, b, c, d in zip(p0, p1, p2, p3)))
    return out


def circle_pts(cx, cz, r, n=16, a0=0.0):
    return [(cx + r * math.cos(a0 + 2 * math.pi * i / n), cz + r * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]


# ------------------------------------------------------------------ objets
def _new_object(name, bm):
    me = bpy.data.meshes.new(name)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _apply_all(ob):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    for mod in list(ob.modifiers):
        bpy.ops.object.modifier_apply(modifier=mod.name)


def _boolean(ob, others, op):
    if not others:
        return
    coll = bpy.data.collections.new(f"{ob.name}_{op}")
    bpy.context.scene.collection.children.link(coll)
    for o in others:
        for c in o.users_collection:
            c.objects.unlink(o)
        coll.objects.link(o)
    mod = ob.modifiers.new(op, "BOOLEAN")
    mod.operation = op
    mod.operand_type = "COLLECTION"
    mod.collection = coll
    mod.solver = "MANIFOLD"
    _apply_all(ob)
    if len(ob.data.polygons) == 0:  # le solveur Manifold a refusé (maillage non fermé) : solveur exact
        raise RuntimeError(f"booléen vide sur {ob.name}")
    for o in list(coll.objects):
        me = o.data
        bpy.data.objects.remove(o)
        bpy.data.meshes.remove(me)
    bpy.data.collections.remove(coll)


class Part:
    """Une pièce = un objet = un matériau.

    group  : Body / Magazine / Trigger / ChargingHandle
    mat    : nom du matériau (voir materials.py)
    name   : suffixe Roblox (Body_<name>)
    """

    def __init__(self, group, name, mat, bevel=0.008, segs=2, angle=32, weld=True):
        self.group, self.name, self.mat = group, name, mat
        self.bevel, self.segs, self.angle, self.weld = bevel, segs, angle, weld
        self.solids = []      # bmesh fermés (unis entre eux)
        self.cuts = []        # bmesh fermés (soustraits)
        self.details = []     # bmesh ajoutés après le biseau (petites pièces sans booléen)
        self.engravings = []  # textes gravés : (texte, x, z, hauteur, côté, police, gras)
        self.stipple = None   # zones de texture granuleuse (x0, z0, x1, z1)
        self.knurl = None     # zones de moletage

    # -- volumes ajoutés
    def _solid(self, target, fn, *a, **k):
        bm = bmesh.new()
        fn(bm, *a, **k)
        target.append(bm)
        return self

    def prism(self, profile, y0, y1=None):
        if y1 is None:
            y0, y1 = -y0, y0
        return self._solid(self.solids, _bm_prism, profile, y0, y1)

    def prism_x(self, profile_yz, x0, x1):
        return self._solid(self.solids, _bm_prism_axis, profile_yz, x0, x1, "X")

    def prism_z(self, profile_xy, z0, z1):
        return self._solid(self.solids, _bm_prism_axis, profile_xy, z0, z1, "Z")

    def cut_prism_x(self, profile_yz, x0, x1):
        return self._solid(self.cuts, _bm_prism_axis, profile_yz, x0, x1, "X")

    def cut_prism_z(self, profile_xy, z0, z1):
        return self._solid(self.cuts, _bm_prism_axis, profile_xy, z0, z1, "Z")

    def detail_prism_x(self, profile_yz, x0, x1):
        return self._solid(self.details, _bm_prism_axis, profile_yz, x0, x1, "X")

    def detail_prism_z(self, profile_xy, z0, z1):
        return self._solid(self.details, _bm_prism_axis, profile_xy, z0, z1, "Z")

    def lathe(self, profile, axis="X", center=(0, 0, 0), segs=24, **k):
        return self._solid(self.solids, _bm_lathe, profile, axis, center, segs, **k)

    def loft(self, sections):
        return self._solid(self.solids, _bm_loft, sections)

    def box(self, x0, x1, z0, z1, y0, y1=None):
        return self.prism(rect(x0, z0, x1, z1), y0, y1)

    def cyl(self, axis, center, r, length, segs=20, r2=None):
        h = length / 2
        return self.lathe([(-h, r), (h, r if r2 is None else r2)], axis, center, segs)

    def tube(self, p0, p1, r0, r1=None, segs=16):
        return self._solid(self.solids, _bm_tube, p0, p1, r0, r0 if r1 is None else r1, segs)

    def sphere(self, c, r, segs=16, sz=1.0):
        return self._solid(self.solids, _bm_sphere, c, r, segs, sz)

    def cut_tube(self, p0, p1, r0, r1=None, segs=16):
        return self._solid(self.cuts, _bm_tube, p0, p1, r0, r0 if r1 is None else r1, segs)

    # -- détails sans booléen (vis, goupilles : posés après le biseau)
    def detail_lathe(self, profile, axis="X", center=(0, 0, 0), segs=16, **k):
        return self._solid(self.details, _bm_lathe, profile, axis, center, segs, **k)

    def detail_prism(self, profile, y0, y1=None):
        if y1 is None:
            y0, y1 = -y0, y0
        return self._solid(self.details, _bm_prism, profile, y0, y1)

    # -- découpes
    def cut_prism(self, profile, y0, y1=None):
        if y1 is None:
            y0, y1 = -y0, y0
        return self._solid(self.cuts, _bm_prism, profile, y0, y1)

    def cut_box(self, x0, x1, z0, z1, y0, y1=None):
        return self.cut_prism(rect(x0, z0, x1, z1), y0, y1)

    def cut_lathe(self, profile, axis="X", center=(0, 0, 0), segs=20, **k):
        return self._solid(self.cuts, _bm_lathe, profile, axis, center, segs, **k)

    def cut_cyl(self, axis, center, r, length, segs=16):
        h = length / 2
        return self.cut_lathe([(-h, r), (h, r)], axis, center, segs)

    def engrave(self, text, x, z, h, side=1, font="sans", bold=True, depth=1.0):
        """Texte gravé sur le flanc gauche (side=1, +Y) ou droit (side=-1). x, z = coin bas-gauche."""
        self.engravings.append((text, x, z, h, side, font, bold, depth))
        return self

    # -- construction
    def build(self):
        name = f"{self.group}_{self.name}" if self.group != "Trigger" else "Trigger"
        objs = [_new_object(f"{name}_{i}", bm) for i, bm in enumerate(self.solids)]
        ob = objs[0]
        ob.name = name
        ob.data.name = name
        if len(objs) > 1:
            if self.weld:
                _boolean(ob, objs[1:], "UNION")
            else:
                _join(ob, objs[1:])
        cutters = [_new_object(f"{name}_cut{i}", bm) for i, bm in enumerate(self.cuts)]
        _boolean(ob, cutters, "DIFFERENCE")
        if self.bevel:
            mod = ob.modifiers.new("Bevel", "BEVEL")
            mod.width = self.bevel
            mod.segments = self.segs
            mod.limit_method = "ANGLE"
            mod.angle_limit = math.radians(self.angle)
            mod.use_clamp_overlap = True
            mod.miter_outer = "MITER_ARC"
            mod.harden_normals = False
            _apply_all(ob)
        if self.details:
            dets = [_new_object(f"{name}_det{i}", bm) for i, bm in enumerate(self.details)]
            _join(ob, dets)
        triangulate(ob)
        finish_shading(ob)
        ob["mat"] = self.mat
        ob["group"] = self.group
        PARTS[ob.name] = self
        return ob


PARTS = {}  # nom d'objet -> Part (gravures, zones granuleuses...)


def triangulate(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(ob.data)
    bm.free()


def _join(dst, others):
    bpy.ops.object.select_all(action="DESELECT")
    for o in others:
        o.select_set(True)
    dst.select_set(True)
    bpy.context.view_layer.objects.active = dst
    bpy.ops.object.join()


def finish_shading(ob, angle=34):
    me = ob.data
    for p in me.polygons:
        p.use_smooth = True
    me.set_sharp_from_angle(angle=math.radians(angle))
    mod = ob.modifiers.new("WN", "WEIGHTED_NORMAL")
    mod.keep_sharp = True
    mod.weight = 50
    mod.mode = "FACE_AREA"
    _apply_all(ob)


def tri_count(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)
