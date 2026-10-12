"""Aperçus animés (GIF) des animations réalistes, vus comme dans le jeu (vue FPS).

    python3 scripts/real/preview_anim.py Phantom:Recharge Couteau:Inspection ...

Ouvre weapons/Realiste/<Arme>/<Arme>_Realiste.blend, place une caméra comme celle du jeu
(regarde vers -Z, Y en haut) et rejoue les images clés de anims.py :
  - « Arme » : décalage dans le repère caméra
  - pièces   : décalage des sous-modèles dans le repère de l'arme (X canon, Y haut, Z droite)
"""
import importlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from PIL import Image  # noqa: E402

import anims  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MODULES = {"Phantom": "rifle", "Deagle": "deagle", "Sniper": "sniper", "Couteau": "karambit"}
# position de repos de la poignée dans le repère caméra (studs) et champ de vision vertical
REST = {"Phantom": (0.55, -0.50, -1.45), "Deagle": (0.36, -0.30, -0.95),
        "Sniper": (0.55, -0.50, -1.65), "Couteau": (0.32, -0.26, -0.80)}
REST_ROT = {"Phantom": (0, 4, 0), "Deagle": (0, 4, 0), "Sniper": (0, 4, 0), "Couteau": (-6, 10, 0)}
FOV = 62

# axes de l'arme dans Blender (X canon, Y gauche, Z haut) exprimés dans le repère caméra
G0 = Matrix(((0, -1, 0, 0), (0, 0, 1, 0), (-1, 0, 0, 0), (0, 0, 0, 1)))
# repère « arme » du jeu (X canon, Y haut, Z droite) -> repère Blender de l'arme
B = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0)))


def euler_cf(r):
    rx, ry, rz = (math.radians(a) for a in r)
    return (Matrix.Rotation(rx, 3, "X") @ Matrix.Rotation(ry, 3, "Y") @ Matrix.Rotation(rz, 3, "Z"))


def ease(e, x):
    if e == "lin":
        return x
    if e == "sortie":
        return 1 - (1 - x) ** 3
    if e == "entree":
        return x ** 3
    if e == "ressort":
        c1 = 1.70158
        return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2
    return x * x * (3 - 2 * x)


def sample(keys, t):
    if t <= keys[0][0]:
        return Vector(keys[0][1]), Vector(keys[0][2])
    for a, b in zip(keys, keys[1:]):
        if t < b[0]:
            x = ease(b[3], (t - a[0]) / max(b[0] - a[0], 1e-6))
            return Vector(a[1]).lerp(Vector(b[1]), x), Vector(a[2]).lerp(Vector(b[2]), x)
    return Vector(keys[-1][1]), Vector(keys[-1][2])


def setup(weapon):
    path = os.path.join(ROOT, "weapons", "Realiste", weapon, f"{weapon}_Realiste.blend")
    bpy.ops.wm.open_mainfile(filepath=path)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 14
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = 640, 360
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    world = bpy.data.worlds.new("FPS")
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
    nt.links.new(sep.outputs[1], ramp.inputs[0])   # repère caméra : Y = haut
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.035, 0.037, 0.042, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.30, 0.33, 0.38, 1)
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.8
    nt.links.new(bg.outputs[0], out.inputs[0])
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam = bpy.context.object
    cam.data.sensor_fit = "VERTICAL"
    cam.data.angle_y = math.radians(FOV)
    cam.data.clip_start = 0.02
    sc.camera = cam

    def light(loc, energy, size, color=(1, 1, 1)):
        bpy.ops.object.light_add(type="AREA", location=loc)
        lo = bpy.context.object
        lo.data.energy, lo.data.size, lo.data.color = energy, size, color
        lo.rotation_euler = (Vector((0.4, -0.5, -1.4)) - lo.location).to_track_quat("-Z", "Y").to_euler()

    light((-1.2, 1.6, 0.6), 420, 1.6)
    light((2.0, 0.4, -0.6), 160, 1.0, (0.85, 0.92, 1.0))
    light((0.0, -1.5, -0.5), 60, 2.0)
    model = next(o for o in bpy.data.objects if o.type == "EMPTY" and o.parent is None)
    groups = {o.name: o for o in bpy.data.objects if o.type == "EMPTY" and o.parent == model}
    return model, groups


def group_center(empty):
    pts = [o.matrix_world @ v.co for o in empty.children for v in o.data.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    return (lo + hi) / 2


def render_anim(weapon, name, fps=20):
    W = importlib.import_module(MODULES[weapon])
    data = anims.ANIMS[weapon][name]
    model, groups = setup(weapon)
    gx, gz = W.GRIP
    model.matrix_world = Matrix.Identity(4)
    bpy.context.view_layer.update()
    pivots = {}
    for att, (piece, (ax, ay, az)) in getattr(W, "ATTACHES", {}).items():
        pivots[att] = Vector((ax - gx, ay, az - gz))
    centers = {g: group_center(e) for g, e in groups.items()}
    rest = Matrix.Translation(REST[weapon]) @ euler_cf(REST_ROT[weapon]).to_4x4()
    n = int(data["duree"] * fps) + 1
    pad = int(0.35 * fps)
    out = os.path.join(ROOT, "weapons", "Realiste", weapon)
    tmp = os.path.join(bpy.app.tempdir or "/tmp", f"anim_{weapon}_{name}")
    os.makedirs(tmp, exist_ok=True)
    frames = []
    for f in range(n + pad):
        t = min(f / fps, data["duree"])
        D = Matrix.Identity(4)
        if "Arme" in data:
            p, r = sample(data["Arme"], t)
            D = Matrix.Translation(p) @ euler_cf(r).to_4x4()
        model.matrix_world = rest @ D @ G0
        for g, e in groups.items():
            track = data.get(g)
            if not track:
                e.matrix_basis = Matrix.Identity(4)
                continue
            keys = track["cles"] if isinstance(track, dict) else track
            c = pivots.get(track.get("pivot")) if isinstance(track, dict) else None
            c = c if c is not None else centers[g]
            p, r = sample(keys, t)
            pb = B @ p
            Rb = (B @ euler_cf(r) @ B.transposed()).to_4x4()
            e.matrix_basis = Matrix.Translation(pb) @ Matrix.Translation(c) @ Rb @ Matrix.Translation(-c)
        path = os.path.join(tmp, f"{f:04d}.png")
        bpy.context.scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        frames.append(path)
    imgs = [Image.open(p).convert("RGB") for p in frames]
    pal = imgs[len(imgs) // 2].quantize(colors=200, method=Image.Quantize.MEDIANCUT)
    q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in imgs]
    gif = os.path.join(out, f"anim_{name}.gif")
    q[0].save(gif, save_all=True, append_images=q[1:], duration=int(1000 / fps), loop=0, optimize=True)
    print("GIF", gif, flush=True)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        w, a = arg.split(":")
        render_anim(w, a)
