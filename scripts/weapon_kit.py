"""Boîte à outils commune à toutes les armes (géométrie Blender en vue de côté).

Chaque arme (vanta_ar01.py, vanta_de50.py, vanta_sr7.py, couteau.py) décrit :
  - ses pièces : (groupe, rôle de couleur, fonction de construction, biseau)
  - sa taille cible en studs, son point de poignée, ses groupes Roblox
  - les zones de son profil (pour placer les motifs des skins)
Convention du jeu : canon vers +X, haut vers +Z, origine sur la poignée.
Les profils se dessinent en studs dans le plan (X, Z) puis sont extrudés en Y.
"""
import math

import bpy  # noqa: F401  (doit être importé avant bmesh)
import bmesh
from mathutils import Matrix, Vector

STUD = 1.096 / 3.616  # mètres par stud (d'après le tableau des tailles)
ALL_GROUPS = {"Body": "Corps", "Magazine": "Chargeur", "Trigger": "Gachette", "ChargingHandle": "Levier"}


# ---------------------------------------------------------------- primitives
def prism(bm, profile, half, y_center=0.0):
    y0, y1 = (y_center - half) * STUD, (y_center + half) * STUD
    face = bm.faces.new([bm.verts.new((x * STUD, y0, z * STUD)) for x, z in profile])
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    top = [v for v in res["geom"] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, y1 - y0, 0))


def box(bm, x0, x1, z0, z1, half, y_center=0.0):
    prism(bm, [(x0, z0), (x0, z1), (x1, z1), (x1, z0)], half, y_center)


def cyl_x(bm, x0, x1, z, r, segs=16):
    mat = Matrix.Translation(((x0 + x1) / 2 * STUD, 0, z * STUD)) @ Matrix.Rotation(math.radians(90), 4, "Y")
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r * STUD, radius2=r * STUD,
                          depth=(x1 - x0) * STUD, matrix=mat)


def cone_x(bm, x0, x1, z, r0, r1, segs=16):
    """Tronc de cône le long de X (rayon r0 en x0, r1 en x1)."""
    mat = Matrix.Translation(((x0 + x1) / 2 * STUD, 0, z * STUD)) @ Matrix.Rotation(math.radians(90), 4, "Y")
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r0 * STUD, radius2=r1 * STUD,
                          depth=(x1 - x0) * STUD, matrix=mat)


def cyl_z(bm, x, z0, z1, r, segs=14, y_center=0.0):
    """Cylindre vertical (Z)."""
    mat = Matrix.Translation((x * STUD, y_center * STUD, (z0 + z1) / 2 * STUD))
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r * STUD, radius2=r * STUD,
                          depth=(z1 - z0) * STUD, matrix=mat)


def cyl_y(bm, x, z, r, half, segs=14, y_center=0.0):
    mat = Matrix.Translation((x * STUD, y_center * STUD, z * STUD)) @ Matrix.Rotation(math.radians(90), 4, "X")
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r * STUD, radius2=r * STUD,
                          depth=2 * half * STUD, matrix=mat)


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


class Weapon:
    """Une arme : ses pièces et ce qu'il faut pour la construire et l'exporter."""

    def __init__(self, key, folder, file_prefix, pieces, target, grip, zones, emblem,
                 groups=None, contour=0.022, flower_scale=1.0):
        self.key = key                    # nom court (ar01, de50, sr7, couteau)
        self.folder = folder              # dossier dans weapons/ et dans ReplicatedStorage.Armes
        self.file_prefix = file_prefix    # Phantom, Deagle, Sniper, Couteau
        self.pieces = pieces              # fonction -> [(groupe, rôle, fn, biseau)]
        self.target = target              # (longueur, épaisseur ou None, hauteur) en studs
        self.grip = grip                  # point de poignée (x, z) en studs design
        self.zones = zones                # zones du profil pour les skins (studs)
        self.emblem = emblem              # (x, z, taille) du triangle VANTA
        self.groups = groups or ALL_GROUPS
        self.contour = contour            # épaisseur du contour noir (studs)
        self.flower_scale = flower_scale  # taille relative des motifs (petites armes)
        self.scale = Vector((1, 1, 1))

    def design_to_world(self, x, z):
        """Point du profil (studs design) -> mètres monde (origine poignée)."""
        return ((x - self.grip[0]) * STUD * self.scale.x, (z - self.grip[1]) * STUD * self.scale.z)

    def build(self):
        """Construit toutes les pièces. Renvoie {(groupe, rôle): objet}."""
        objs = {}
        for group, role, fn, bevel in self.pieces():
            key = (group, role)
            ob = _make(f"{group}_{role}", fn, bevel)
            if key in objs:  # même groupe + même rôle déclaré deux fois : on fusionne
                _join(objs[key], ob)
            else:
                objs[key] = ob
        self._normalize(objs)
        return objs

    def add_contours(self, objs):
        """Contour noir par groupe (sans verre, lentille ni cadre). {groupe: objet}."""
        out = {}
        for prefix in self.groups:
            src = [o for (g, r), o in objs.items() if g == prefix and r not in ("Verre", "Cadre", "Lentille")]
            if src:
                out[prefix] = _inverted_hull(f"{prefix}_Contour", src, self.contour * STUD)
        return out

    def assemble(self, objs, contours, palette, model_name):
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
                _join(final[name], ob)
            else:
                final[name] = ob
        for group, ob in contours.items():
            final[f"{group}_Contour"] = ob
        for name, ob in final.items():
            ob.name = ob.data.name = name
        self.organize(final, model_name)
        return final

    def organize(self, objs, model_name):
        """Empties Model > Corps/Chargeur/... comme dans Roblox."""
        root = bpy.data.objects.new(model_name, None)
        bpy.context.collection.objects.link(root)
        empties = {}
        for prefix, gname in self.groups.items():
            e = bpy.data.objects.new(gname, None)
            bpy.context.collection.objects.link(e)
            e.parent = root
            empties[prefix] = e
        for name, ob in objs.items():
            ob.parent = root if name == "Root" else empties[name.split("_")[0]]
        return root

    def _normalize(self, objs):
        """Taille exacte (sans le Root) et origine sur la poignée."""
        pts = [v.co for (g, r), ob in objs.items() if g != "Root" for v in ob.data.vertices]
        size = Vector((max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)))
        L, T, H = self.target
        scale = Vector((L * STUD / size.x, (T * STUD / size.y) if T else 1.0, H * STUD / size.z))
        self.scale[:] = scale
        pivot = Vector((self.grip[0] * STUD, 0.0, self.grip[1] * STUD))
        m = Matrix.Diagonal((*scale, 1.0)) @ Matrix.Translation(-pivot)
        for ob in objs.values():
            ob.data.transform(m)
            ob.data.update()


def _join(dst, src):
    bpy.ops.object.select_all(action="DESELECT")
    src.select_set(True)
    dst.select_set(True)
    bpy.context.view_layer.objects.active = dst
    bpy.ops.object.join()


def root_marker(grip):
    """Petit cube « Root » sur la poignée."""
    return ("Root", "Root", lambda bm: box(bm, grip[0] - 0.1, grip[0] + 0.1, grip[1] - 0.1, grip[1] + 0.1, 0.1), 0.0)
