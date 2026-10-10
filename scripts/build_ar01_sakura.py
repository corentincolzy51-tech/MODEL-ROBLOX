"""Construit la VANTA AR-01 + skin Sakura, bake les textures et exporte.

Usage :
    python3 scripts/build_ar01_sakura.py [dossier_de_sortie]

Sorties : .blend, .fbx (textures intégrées), textures PNG, rendu d'aperçu.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import skin_sakura  # noqa: E402
import vanta_ar01  # noqa: E402

OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "weapons", "VANTA_AR-01", "Sakura"))
TEX = os.path.join(OUT, "textures")
BAKE_RES = 2048   # bake en 2048 puis réduit en 1024 (limite Roblox) pour un rendu net
FINAL_RES = 1024
PREFIX = "VANTA_AR-01_Sakura"

FLAT = {  # couleurs unies (linéaires) des matériaux non texturés
    "Metal": (0.86, 0.86, 0.88, 1),
    "Dark": (0.012, 0.012, 0.014, 1),
    "Accent": (0.85, 0.06, 0.32, 1),
}


def flat_mat(name, color, rough=0.35, metal=0.0):
    m = bpy.data.materials.get(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    m.diffuse_color = color
    return m


def skin_mat(design_img):
    m = bpy.data.materials["Skin"]
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.4
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = design_img
    tex.extension = "EXTEND"
    uv = nt.nodes.new("ShaderNodeUVMap")
    uv.uv_map = "proj"
    nt.links.new(uv.outputs["UV"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])


def project_uvs(ob, x0, z0, xspan, zspan, z_band):
    """UV 'proj' : chaque face lit la texture de côté selon sa normale."""
    me = ob.data
    if "proj" not in me.uv_layers:
        me.uv_layers.new(name="proj")
    layer = me.uv_layers["proj"].data
    for poly in me.polygons:
        n = poly.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            if ax == 1:      # flancs : vue de côté directe
                x, z = co.x, co.z
            elif ax == 2:    # dessus/dessous : bande centrale de la texture
                x, z = co.x, z_band + co.y
            else:            # bouts (crosse, bouche)
                x, z = co.x + co.y, co.z
            layer[li].uv = ((x - x0) / xspan, (z - z0) / zspan)


def bake(ob, name):
    """Bake la couleur de tous les matériaux de l'objet dans une seule texture."""
    me = ob.data
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    if "UVMap" not in me.uv_layers:
        me.uv_layers.new(name="UVMap")
    me.uv_layers.active = me.uv_layers["UVMap"]
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    # les n-gones concaves cassent le dépliage : on triangule d'abord
    bpy.ops.mesh.quads_convert_to_tris(quad_method="BEAUTY", ngon_method="BEAUTY")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.006, scale_to_bounds=False,
                             correct_aspect=False)  # sinon Blender déforme selon la texture de design
    bpy.ops.object.mode_set(mode="OBJECT")

    img = bpy.data.images.new(name + "_bake", BAKE_RES, BAKE_RES)
    for slot in ob.material_slots:
        nt = slot.material.node_tree
        node = nt.nodes.new("ShaderNodeTexImage")
        node.image = img
        node.name = "BAKE_TARGET"
        nt.nodes.active = node
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 4
    sc.render.bake.use_pass_direct = False
    sc.render.bake.use_pass_indirect = False
    sc.render.bake.margin = 16
    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, use_clear=True)
    for slot in ob.material_slots:
        nt = slot.material.node_tree
        nt.nodes.remove(nt.nodes["BAKE_TARGET"])

    path = os.path.join(TEX, f"{name}.png")
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    from PIL import Image
    Image.open(path).resize((FINAL_RES, FINAL_RES), Image.LANCZOS).save(path)
    bpy.data.images.remove(img)
    return path


def final_material(ob, name, tex_path=None, color=None):
    """Remplace les matériaux par un seul (1 texture ou 1 couleur par objet)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.55
    if tex_path:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(tex_path)
        uv = nt.nodes.new("ShaderNodeUVMap")
        uv.uv_map = "UVMap"
        nt.links.new(uv.outputs["UV"], tex.inputs["Vector"])
        nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
    else:
        p.inputs["Base Color"].default_value = color
        m.diffuse_color = color
    ob.data.materials.clear()
    ob.data.materials.append(m)
    for poly in ob.data.polygons:
        poly.material_index = 0
    if "proj" in ob.data.uv_layers:
        ob.data.uv_layers.remove(ob.data.uv_layers["proj"])


def preview(path):
    """Rendu façon vitrine : fond sombre, vue 3/4."""
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 96
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.view_settings.view_transform = "Standard"

    world = bpy.data.worlds.new("Vitrine")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes["Background"]
    # fond : dégradé radial gris foncé visible par la caméra, éclairage doux
    lp = nt.nodes.new("ShaderNodeLightPath")
    grad = nt.nodes.new("ShaderNodeTexGradient")
    grad.gradient_type = "SPHERICAL"
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.004, 0.004, 0.004, 1)
    ramp.color_ramp.elements[1].color = (0.06, 0.06, 0.06, 1)
    win = nt.nodes.new("ShaderNodeTexCoord")
    mapn = nt.nodes.new("ShaderNodeMapping")
    mapn.inputs["Location"].default_value = (-0.5, -0.5, 0)
    mapn.inputs["Scale"].default_value = (1.0, 1.6, 1)
    nt.links.new(win.outputs["Window"], mapn.inputs["Vector"])
    nt.links.new(mapn.outputs["Vector"], grad.inputs["Vector"])
    nt.links.new(grad.outputs["Fac"], ramp.inputs["Fac"])
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.inputs["Color1"].default_value = (0.35, 0.35, 0.38, 1)
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], mix.inputs["Color2"])
    nt.links.new(mix.outputs["Color"], bg.inputs["Color"])

    def light(name, loc, energy, size):
        bpy.ops.object.light_add(type="AREA", location=loc)
        lo = bpy.context.object
        lo.name = name
        lo.data.energy = energy
        lo.data.size = size
        d = Vector((0.1, 0, -0.05)) - lo.location
        lo.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

    light("Key", (0.3, 1.4, 1.1), 28, 1.5)
    light("Fill", (1.4, 0.6, 0.2), 10, 1.5)
    light("Rim", (-0.6, -1.2, 0.9), 22, 1.0)

    # vue du flanc gauche, canon vers la gauche, comme la référence
    bpy.ops.object.camera_add(location=(-0.35, 1.9, 0.55))
    cam = bpy.context.object
    cam.data.lens = 50
    d = Vector((0.13, 0, -0.04)) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def main():
    os.makedirs(TEX, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    parts = vanta_ar01.build()

    # ---- texture de design (vue de côté) ----
    pts = [v.co for ob in parts.values() for v in ob.data.vertices]
    margin = 0.03
    x0 = min(p.x for p in pts) - margin
    x1 = max(p.x for p in pts) + margin
    z0 = min(p.z for p in pts) - margin
    z1 = max(p.z for p in pts) + margin
    xspan, zspan = x1 - x0, z1 - z0
    W = 4096
    H = int(W * zspan / xspan)
    ppm = W / xspan
    w2p = lambda x, z: ((x - x0) * ppm, (z1 - z) * ppm)
    D = vanta_ar01.design_to_world

    def rect(a, b, c, d):
        (xa, za), (xb, zb) = D(a, b), D(c, d)
        return (xa, za, xb, zb)

    zones = {
        "stock": rect(15, -75, 255, 50),
        "bouquet": rect(30, -62, 170, 18),
        "receiver": rect(262, 6, 530, 56),
        "grip": rect(296, -108, 358, -2),
        "mag": rect(448, -215, 585, 0),
        "handguard": rect(542, 8, 720, 76),
        "branch": (D(205, 14), D(522, 44)),
    }
    design = skin_sakura.generate(W, H, w2p, ppm, zones)
    design_path = os.path.join(TEX, "sakura_design_sideview.png")
    design.save(design_path)

    skin_mat(bpy.data.images.load(design_path))
    for name, col in FLAT.items():
        if name in bpy.data.materials:
            flat_mat(name, col, rough=0.2 if name == "Dark" else 0.35, metal=0.6 if name == "Dark" else 0.0)

    # la semelle du chargeur passe en rose vif comme la référence
    mag = parts["Magazine"]
    mag.data.materials.append(bpy.data.materials["Accent"])
    lowest = min(v.co.z for v in mag.data.vertices)
    for poly in mag.data.polygons:
        if all(mag.data.vertices[i].co.z < lowest + 0.022 for i in poly.vertices) and abs(poly.normal.y) < 0.99:
            poly.material_index = 1

    z_band = D(0, 30)[1]
    for key in ("Body", "Magazine"):
        project_uvs(parts[key], x0, z0, xspan, zspan, z_band)

    tex_body = bake(parts["Body"], f"{PREFIX}_Body")
    tex_mag = bake(parts["Magazine"], f"{PREFIX}_Magazine")
    final_material(parts["Body"], "Body_Sakura", tex_path=tex_body)
    final_material(parts["Magazine"], "Magazine_Sakura", tex_path=tex_mag)
    final_material(parts["Trigger"], "Trigger_White", color=FLAT["Metal"])
    final_material(parts["ChargingHandle"], "ChargingHandle_White", color=FLAT["Metal"])

    for ob in parts.values():
        for poly in ob.data.polygons:
            poly.use_smooth = False

    # ---- exports ----
    bpy.ops.object.select_all(action="DESELECT")
    for ob in parts.values():
        ob.select_set(True)
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(OUT, f"{PREFIX}.fbx"),
        use_selection=True,
        object_types={"MESH"},
        path_mode="COPY",
        embed_textures=True,
        mesh_smooth_type="FACE",
        use_triangles=True,
    )
    preview(os.path.join(OUT, f"{PREFIX}_preview.png"))
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f"{PREFIX}.blend"), compress=True)

    for ob in parts.values():
        tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
        print(f"PART {ob.name}: {tris} triangles")
    pts = [v.co for ob in parts.values() for v in ob.data.vertices]
    print("SIZE", [round(max(p[i] for p in pts) - min(p[i] for p in pts), 4) for i in range(3)])


main()
