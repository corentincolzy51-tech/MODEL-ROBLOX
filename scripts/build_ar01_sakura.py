"""VANTA AR-01 + skin Sakura -> FBX prêt pour Roblox (structure « Phantom P »).

Usage :
    python3 scripts/build_ar01_sakura.py [dossier_de_sortie]

Sorties :
    Phantom_Sakura.fbx   valeurs du fichier en studs (Scale Unit = Stud à l'import)
    Phantom_Sakura.blend en mètres (1,096 m de long), textures empaquetées
    textures/*.png       textures 1024 px des parties Sakura
    Phantom_Sakura_preview.png
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import skin_sakura  # noqa: E402
import vanta_ar01 as V  # noqa: E402

OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "weapons", "VANTA_AR-01", "Sakura"))
TEX = os.path.join(OUT, "textures")
MODEL = "Phantom Sakura"
FILE = "Phantom_Sakura"
BAKE_RES, FINAL_RES = 2048, 1024

# couleurs sRGB 0-255 (les mêmes que dans le script Roblox)
COLORS = {
    "Sakura": (255, 255, 255),
    "Blanc": (245, 241, 245),
    "Rose": (255, 92, 168),
    "Noir": (30, 26, 34),
    "Lentille": (255, 120, 200),
    "Contour": (14, 10, 16),
}


def lin(c):
    f = lambda v: (v / 255) ** 2.2
    return (f(c[0]), f(c[1]), f(c[2]), 1.0)


def color_key(name):
    return "Blanc" if name == "Trigger" else name.split("_")[-1]


# ------------------------------------------------------------- texture Sakura
def project_uvs(ob, x0, z0, xspan, zspan, z_band):
    """UV 'proj' : chaque face lit le dessin de côté selon sa normale."""
    me = ob.data
    layer = me.uv_layers.new(name="proj").data
    for poly in me.polygons:
        ax = max(range(3), key=lambda i: abs(poly.normal[i]))
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            if ax == 1:
                x, z = co.x, co.z
            elif ax == 2:
                x, z = co.x, z_band + co.y
            else:
                x, z = co.x + co.y, co.z
            layer[li].uv = ((x - x0) / xspan, (z - z0) / zspan)


def bake_sakura(ob, design_img, out_name):
    me = ob.data
    m = bpy.data.materials.new("bake_src")
    m.use_nodes = True
    nt = m.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = design_img
    tex.extension = "EXTEND"
    uvn = nt.nodes.new("ShaderNodeUVMap")
    uvn.uv_map = "proj"
    nt.links.new(uvn.outputs["UV"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    me.materials.clear()
    me.materials.append(m)

    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    uv = me.uv_layers.new(name="UVMap")
    me.uv_layers.active = uv
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    # n-gones concaves -> triangles, sinon le dépliage casse
    bpy.ops.mesh.quads_convert_to_tris(quad_method="BEAUTY", ngon_method="BEAUTY")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.006,
                             scale_to_bounds=False, correct_aspect=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    img = bpy.data.images.new(out_name, BAKE_RES, BAKE_RES)
    target = nt.nodes.new("ShaderNodeTexImage")
    target.image = img
    nt.nodes.active = target
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 4
    sc.render.bake.margin = 16
    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, use_clear=True)
    path = os.path.join(TEX, out_name + ".png")
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    from PIL import Image
    Image.open(path).resize((FINAL_RES, FINAL_RES), Image.LANCZOS).save(path)
    bpy.data.images.remove(img)
    me.uv_layers.remove(me.uv_layers["proj"])
    me.materials.clear()
    bpy.data.materials.remove(m)
    return path


# --------------------------------------------------------------- matériaux
def assign_material(ob, tex_path=None):
    key = color_key(ob.name)
    m = bpy.data.materials.new(ob.name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.55
    c = lin(COLORS[key])
    m.diffuse_color = c
    if tex_path:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(tex_path)
        nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
    else:
        p.inputs["Base Color"].default_value = c
    if key == "Lentille":
        p.inputs["Emission Color"].default_value = c
        p.inputs["Emission Strength"].default_value = 4.0
    if key == "Contour":
        # aperçu Blender uniquement : la coque n'est visible que de l'intérieur
        # (dans Roblox les MeshParts sont à simple face, ça marche tout seul)
        m.use_backface_culling = True
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = c
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(geo.outputs["Backfacing"], mix.inputs["Fac"])
        nt.links.new(em.outputs["Emission"], mix.inputs[1])
        nt.links.new(tr.outputs["BSDF"], mix.inputs[2])
        nt.links.new(mix.outputs["Shader"], nt.nodes["Material Output"].inputs["Surface"])
    ob.data.materials.clear()
    ob.data.materials.append(m)
    for poly in ob.data.polygons:
        poly.use_smooth = False


# ------------------------------------------------------------------ aperçu
def preview(path, root):
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
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.inputs["Color1"].default_value = (0.35, 0.35, 0.38, 1)
    mix.inputs["Color2"].default_value = (0.025, 0.025, 0.03, 1)
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
    nt.links.new(mix.outputs["Color"], nt.nodes["Background"].inputs["Color"])

    def light(loc, energy, size):
        bpy.ops.object.light_add(type="AREA", location=loc)
        lo = bpy.context.object
        lo.data.energy, lo.data.size = energy, size
        lo.rotation_euler = (Vector((0.15, 0, 0)) - lo.location).to_track_quat("-Z", "Y").to_euler()

    light((0.3, 1.4, 1.1), 28, 1.5)
    light((1.4, 0.6, 0.2), 10, 1.5)
    light((-0.6, -1.2, 0.9), 22, 1.0)
    bpy.ops.object.camera_add(location=(-0.25, 1.95, 0.5))
    cam = bpy.context.object
    cam.data.lens = 50
    cam.rotation_euler = (Vector((0.16, 0, 0.0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def main():
    os.makedirs(TEX, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    objs = V.build()

    # ---- dessin Sakura (vue de côté, coordonnées monde)
    pts = [v.co for n, ob in objs.items() if n != "Root" for v in ob.data.vertices]
    margin = 0.03
    x0, x1 = min(p.x for p in pts) - margin, max(p.x for p in pts) + margin
    z0, z1 = min(p.z for p in pts) - margin, max(p.z for p in pts) + margin
    xspan, zspan = x1 - x0, z1 - z0
    W = 4096
    H = int(W * zspan / xspan)
    ppm = W / xspan
    w2p = lambda x, z: ((x - x0) * ppm, (z1 - z) * ppm)
    D = V.design_to_world

    def rect(a, b, c, d):
        (xa, za), (xb, zb) = D(a, b), D(c, d)
        return (xa, za, xb, zb)

    zones = {
        "stock": rect(0.05, 0.50, 0.70, 1.04),
        "bouquet": rect(0.10, 0.56, 0.52, 0.98),
        "receiver": rect(1.04, 0.64, 2.02, 1.06),
        "grip": rect(1.00, 0.18, 1.34, 0.62),
        "mag": rect(1.55, 0.12, 1.92, 0.58),
        "handguard": rect(2.02, 0.74, 2.95, 1.05),
        "branch": (D(0.55, 0.80), D(2.85, 0.96)),
    }
    design = skin_sakura.generate(W, H, w2p, ppm, zones)
    design_path = os.path.join(TEX, "sakura_design_sideview.png")
    design.save(design_path)
    design_img = bpy.data.images.load(design_path)

    z_band = D(0, 0.90)[1]
    tex = {}
    for name in ("Body_Sakura", "Magazine_Sakura"):
        project_uvs(objs[name], x0, z0, xspan, zspan, z_band)
        tex[name] = bake_sakura(objs[name], design_img, f"{FILE}_{name}")

    objs.update(V.add_contours(objs))
    for name, ob in objs.items():
        if name != "Root":
            assign_material(ob, tex.get(name))
    objs["Root"].hide_render = True
    for name, ob in objs.items():
        if name.endswith("_Contour"):  # le contour ne doit pas faire d'ombre dans l'aperçu
            ob.visible_shadow = ob.visible_diffuse = ob.visible_glossy = ob.visible_transmission = False
    root = V.organize(objs, MODEL)

    preview(os.path.join(OUT, f"{FILE}_preview.png"), root)
    for ob in bpy.data.objects:
        if ob.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(ob)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f"{FILE}.blend"), compress=True)

    # ---- export : géométrie convertie en studs (1 unité du fichier = 1 stud)
    to_studs = Matrix.Scale(1 / V.STUD, 4)
    for ob in objs.values():
        ob.data.transform(to_studs)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in bpy.data.objects:
        ob.select_set(True)
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(OUT, f"{FILE}.fbx"),
        use_selection=True,
        object_types={"EMPTY", "MESH"},
        apply_scale_options="FBX_SCALE_UNITS",
        path_mode="COPY",
        embed_textures=True,
        mesh_smooth_type="FACE",
        use_triangles=True,
        add_leaf_bones=False,
    )

    for name, ob in sorted(objs.items()):
        tris = len(ob.data.polygons)
        print(f"PART {name:24s} {tris:5d} triangles")


main()
