"""Construit les armes réalistes : géométrie, textures PBR cuites, aperçus, .blend et .fbx.

    python3 scripts/real/build_real.py rifle deagle sniper karambit   [--nobake] [--fast]

Sorties : weapons/Realiste/<Arme>/
    <Arme>_Realiste.fbx      1 unité = 1 stud (Scale Unit = Stud à l'import), textures intégrées
    <Arme>_Realiste.blend
    textures/<pièce>_{Couleur,Rugosite,Metal,Normal}.png
    <Arme>_apercu*.png
    info.json                (taille, triangles, point de prise, décalage pour le script d'installation)
"""
import argparse
import importlib
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import kit  # noqa: E402
import materials as M  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "weapons", "Realiste")
CARTOON = json.load(open(os.path.join(HERE, "cartoon_ref.json")))


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    kit.PARTS.clear()
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.unit_settings.system = "NONE"


def bbox(objs):
    pts = [ob.matrix_world @ v.co for ob in objs for v in ob.data.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    return lo, hi


# ------------------------------------------------------------------ éclairage studio
def studio(center, size, dark=True):
    sc = bpy.context.scene
    world = bpy.data.worlds.new("Studio")
    sc.world = world
    if world.node_tree is None:
        world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs[2], ramp.inputs[0])
    ramp.color_ramp.elements[0].position = 0.42
    ramp.color_ramp.elements[0].color = (0.02, 0.02, 0.022, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.55, 0.56, 0.6, 1)
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixRGB")
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], mix.inputs["Color1"])
    mix.inputs["Color2"].default_value = (0.012, 0.012, 0.014, 1) if dark else (0.5, 0.5, 0.52, 1)
    nt.links.new(mix.outputs[0], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.6
    nt.links.new(bg.outputs[0], out.inputs[0])
    c = Vector(center)
    k = size

    def light(off, energy, sx, sy, color=(1, 1, 1)):
        bpy.ops.object.light_add(type="AREA", location=c + Vector(off) * k)
        lo = bpy.context.object
        lo.data.shape = "RECTANGLE"
        lo.data.size, lo.data.size_y = sx * k, sy * k
        lo.data.energy = energy * k * k
        lo.data.color = color
        lo.rotation_euler = (c - lo.location).to_track_quat("-Z", "Y").to_euler()
        return lo

    light((0.0, 0.9, 1.3), 90, 1.6, 0.5)                    # boîte à lumière au-dessus
    light((-1.2, 1.0, 0.3), 35, 0.4, 1.2, (1.0, 0.95, 0.9))  # bande arrière gauche
    light((1.3, -0.8, 0.5), 40, 0.4, 1.2, (0.85, 0.92, 1.0))  # contre-jour droit
    light((0.2, 1.6, -0.4), 12, 1.5, 0.6)                    # débouchage bas
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"


def camera(center, direction, dist, lens=60, roll=0.0, shift=(0, 0)):
    c = Vector(center)
    d = Vector(direction).normalized()
    bpy.ops.object.camera_add(location=c + d * dist)
    cam = bpy.context.object
    cam.data.lens = lens
    cam.data.clip_start = 0.01
    cam.data.shift_x, cam.data.shift_y = shift
    q = (c - cam.location).to_track_quat("-Z", "Y")
    cam.rotation_euler = (q @ __import__("mathutils").Quaternion((0, 0, 1), roll)).to_euler()
    bpy.context.scene.camera = cam
    return cam


def render(path, res=(1920, 1080), samples=96):
    sc = bpy.context.scene
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


# ------------------------------------------------------------------ une arme
def build_weapon(key, bake=True, fast=False):
    W = importlib.import_module(key)
    reset()
    t0 = time.time()
    parts = W.build()
    objs = []
    for p in parts:
        ob = p.build()
        objs.append(ob)
        print(f"  {ob.name:28s} {kit.tri_count(ob):6d} tris  [{p.mat}]", flush=True)
    total = sum(kit.tri_count(o) for o in objs)
    print(f"{W.NAME}: {len(objs)} pièces, {total} triangles ({time.time() - t0:.1f} s)", flush=True)

    out = os.path.join(OUT, W.FOLDER)
    texdir = os.path.join(out, "textures")
    os.makedirs(texdir, exist_ok=True)
    for ob in objs:
        t = time.time()
        if bake:
            # petites pièces (gâchette, vis, levier...) : textures 512 px, sinon 1024 px
            area = sum(p.area for p in ob.data.polygons)
            small = area < 0.12
            res = 1024 if (fast or small) else 2048
            M.bake_part(ob, kit.PARTS[ob.name], texdir, res=res, final_res=res // 2)
        else:
            M.procedural(ob, kit.PARTS[ob.name])
        if bake:
            print(f"  cuit {ob.name} ({time.time() - t:.0f} s)", flush=True)

    # origine sur la poignée
    gx, gz = W.GRIP
    shift = Matrix.Translation((-gx, 0, -gz))
    for ob in objs:
        if bake:
            ob.data.transform(shift)
            ob.data.update()
        else:  # matériaux procéduraux en coordonnées « dessin » : on déplace l'objet
            ob.location = (-gx, 0, -gz)
    bpy.context.view_layer.update()
    lo, hi = bbox(objs)
    center, size = (lo + hi) / 2, hi - lo

    # hiérarchie Roblox : Model > Corps / Chargeur / Gachette / Levier + Root
    model_name = f"{W.NAME} Realiste"
    root_e = bpy.data.objects.new(model_name, None)
    bpy.context.scene.collection.objects.link(root_e)
    empties = {}
    for g, gname in kit.GROUPS.items():
        if any(o["group"] == g for o in objs):
            e = bpy.data.objects.new(gname, None)
            bpy.context.scene.collection.objects.link(e)
            e.parent = root_e
            empties[g] = e
    for ob in objs:
        ob.parent = empties[ob["group"]]
        if M.MATS[ob["mat"]]["kind"] in ("glass", "emit"):
            ob.visible_shadow = False
    rp = kit.Part("Root", "Root", "AcierNoir", bevel=0)
    rp.box(-0.1, 0.1, -0.1, 0.1, 0.1)
    root = rp.build()
    root.name = root.data.name = "Root"
    root.parent = root_e
    root.hide_render = True

    # décalage de prise en main pour le script d'installation : la poignée réaliste doit
    # tomber là où était celle de l'arme cartoon (déjà calée dans le jeu)
    ref = CARTOON[W.NAME]
    rc, hold = Vector(ref["center"]), Vector(ref["hold"])
    d = center - rc
    decal = (d.x + hold.x, d.z + hold.y, -d.y - hold.z)   # repère Roblox : X avant, Y haut, Z = -Y Blender
    attaches = {}
    for att, (piece, (ax, ay, az)) in getattr(W, "ATTACHES", {}).items():
        ob = bpy.data.objects[piece]
        plo, phi = bbox([ob])
        pc = (plo + phi) / 2
        rel = Vector((ax - gx, ay, az - gz)) - pc
        attaches[att] = {"piece": piece, "position": (rel.x, rel.z, -rel.y)}
    info = {
        "attaches": attaches,
        "name": W.NAME, "label": W.LABEL, "size": list(size), "center": list(center), "triangles": total,
        "parts": {o.name: kit.tri_count(o) for o in objs},
        "materials": {o.name: o["mat"] for o in objs},
        "groups": sorted({o["group"] for o in objs}), "decalage": decal, "length": size.x,
    }
    json.dump(info, open(os.path.join(out, "info.json"), "w"), indent=1)
    print(f"  taille {size.x:.3f} x {size.z:.3f} x {size.y:.3f} studs, décalage {tuple(round(v, 3) for v in decal)}")

    # aperçus
    L = size.x
    studio(center, L)
    samples = 24 if fast else 128
    res = (1280, 720) if fast else (1920, 1080)
    views = getattr(W, "VIEWS", None) or [
        ("apercu", (-0.35, 1.0, 0.32), 1.55, 0.0),
        ("apercu_droite", (0.45, -1.0, 0.18), 1.6, 0.0),
    ]
    for name, direction, dist, roll in views:
        cam = camera(center, direction, L * dist * 50 / 60 * (60 / 50), lens=60, roll=roll)
        render(os.path.join(out, f"{W.NAME}_{name}.png"), res, samples)
        bpy.data.objects.remove(cam)
    if hasattr(W, "CLOSEUPS"):
        for name, target, direction, dist in W.CLOSEUPS:
            tgt = Vector(target) - Vector((gx, 0, gz))
            cam = camera(tgt, direction, dist, lens=70)
            render(os.path.join(out, f"{W.NAME}_{name}.png"), res, samples)
            bpy.data.objects.remove(cam)

    for ob in list(bpy.data.objects):
        if ob.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(ob)
    if bake:
        bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, f"{W.NAME}_Realiste.blend"), compress=True)
    if os.path.exists(os.path.join(out, f"{W.NAME}_Realiste.blend1")):
        os.remove(os.path.join(out, f"{W.NAME}_Realiste.blend1"))
    if bake:
        bpy.ops.object.select_all(action="DESELECT")
        for ob in bpy.data.objects:
            ob.select_set(True)
        bpy.ops.export_scene.fbx(
            filepath=os.path.join(out, f"{W.NAME}_Realiste.fbx"),
            use_selection=True,
            object_types={"EMPTY", "MESH"},
            apply_scale_options="FBX_SCALE_UNITS",
            path_mode="COPY",
            embed_textures=True,
            mesh_smooth_type="OFF",
            use_triangles=True,
            use_tspace=True,
            add_leaf_bones=False,
        )
    print(f"{W.NAME} terminé en {time.time() - t0:.0f} s -> {out}", flush=True)
    return info


# ------------------------------------------------------------------ script d'installation Roblox
PIECES_ROBLOX = {
    # suffixe -> (matériau, transparence, couleur ou None, sans ombre)
    "Verre": ("Glass", 0.6, (0.75, 0.88, 0.95), True),
    "Lentille": ("Glass", 0.35, (0.35, 0.6, 0.8), True),
    "Reticule": ("Neon", 0, (1.0, 0.12, 0.08), True),
    "Tritium": ("Neon", 0, (0.35, 1.0, 0.45), True),
}
METAL = {"Inox", "Lame", "AcierBrut", "Laiton"}


def write_installer():
    armes, pieces = [], {}
    order = [("Phantom", "Phantom P"), ("Deagle", "Deagle P"), ("Sniper", "Sniper P"), ("Couteau", "Couteau P")]
    for name, ref in order:
        path = os.path.join(OUT, name, "info.json")
        if not os.path.exists(path):
            continue
        info = json.load(open(path))
        groups = info.get("groups", ["Body", "Magazine", "Trigger", "ChargingHandle"])
        gl = ", ".join(f"{g} = true" for g in groups)
        att = ", ".join('%s = { piece = "%s", position = Vector3.new(%.4f, %.4f, %.4f) }' % (k, v["piece"], *v["position"])
                        for k, v in info.get("attaches", {}).items())
        armes.append('\t%s = { dossier = "%s", reference = "%s", longueur = %.3f, decalage = Vector3.new(%.4f, %.4f, %.4f), '
                     'groupes = { %s }, attaches = { %s } },' % (name, name, ref, info["length"], *info["decalage"], gl, att))
        for part, mat in info.get("materials", {}).items():
            suffix = "Gachette" if part == "Trigger" else part.split("_", 1)[1]
            pieces[suffix] = mat
    lines = []
    for suffix, mat in sorted(pieces.items()):
        if suffix in PIECES_ROBLOX:
            m, tr, col, noshadow = PIECES_ROBLOX[suffix]
        else:
            m, tr, col, noshadow = ("Metal" if mat in METAL else "SmoothPlastic"), 0, None, False
        c = "Color3.new(%.2f, %.2f, %.2f)" % col if col else "nil"
        lines.append('\t%s = { materiau = Enum.Material.%s, transparence = %s, couleur = %s, sansOmbre = %s },  -- %s'
                     % (suffix, m, tr, c, "true" if noshadow else "false", mat))
    src = open(os.path.join(ROOT, "scripts", "templates", "InstallerArmesRealistes.lua"), encoding="utf-8").read()
    src = src.replace("--@@ARMES@@", "\n".join(armes)).replace("--@@PIECES@@", "\n".join(lines))
    dest = os.path.join(ROOT, "roblox", "InstallerArmesRealistes.lua")
    open(dest, "w", encoding="utf-8").write(src)
    print("INSTALLER", dest)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("weapons", nargs="+")
    ap.add_argument("--nobake", action="store_true")
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--installer", action="store_true", help="écrit seulement le script d'installation")
    a = ap.parse_args()
    if not a.installer:
        for w in a.weapons:
            build_weapon(w, bake=not a.nobake, fast=a.fast)
    write_installer()
