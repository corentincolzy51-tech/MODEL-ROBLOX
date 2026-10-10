"""Construit les skins de la VANTA AR-01 -> FBX prêts pour Roblox (structure « Phantom P »).

Usage :
    python3 scripts/build_skins.py                         # AR-01, tous les skins
    python3 scripts/build_skins.py --weapon de50 Sakura    # deagle, skin Sakura
    python3 scripts/build_skins.py --weapon sr7 Royal Toxic
    python3 scripts/build_skins.py --installer             # régénère seulement le script Roblox
Armes : ar01 (Phantom), de50 (Deagle), sr7 (Sniper), couteau (Couteau).

Sorties (weapons/<Arme>/<Skin>/) :
    <Préfixe>_<Skin>.fbx    1 unité = 1 stud (Scale Unit = Stud à l'import)
    <Préfixe>_<Skin>.blend  en mètres, textures empaquetées
    textures/*.png          textures 1024 px + dessin source vue de côté
    <Préfixe>_<Skin>_preview.png
Et aussi :
    roblox/InstallerSkinsPhantom.lua   script à coller dans la barre de commande (toutes les armes)
    weapons/<Arme>/Skins_<Arme>_FBX.zip et weapons/<Arme>/galerie.png
"""
import math
import os
import sys
import zipfile

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import couteau  # noqa: E402
import skins  # noqa: E402
import vanta_ar01  # noqa: E402
import vanta_de50  # noqa: E402
import vanta_sr7  # noqa: E402
import weapon_kit as K  # noqa: E402
from skins.common import Ctx  # noqa: E402

WEAPONS = {m.WEAPON.key: m.WEAPON for m in (vanta_ar01, vanta_de50, vanta_sr7, couteau)}
BAKE_RES, FINAL_RES = 2048, 1024
# skins déjà installés dans le jeu, à ne pas remettre dans le zip
ZIP_EXCLUDE = {"ar01": {"Sakura"}}


def weapon_dir(W):
    return os.path.join(ROOT, "weapons", W.folder)


def lin(c):
    f = lambda v: (v / 255) ** 2.2
    return (f(c[0]), f(c[1]), f(c[2]), 1.0)


# ------------------------------------------------------------- texture du skin
def project_uvs(ob, x0, z0, xspan, zspan, z_band):
    """UV 'proj' : chaque face lit le dessin de côté selon sa normale.

    Le dessin fait deux largeurs : [flanc droit + dessus | flanc gauche (textes en miroir)].
    """
    me = ob.data
    layer = me.uv_layers.new(name="proj").data
    for poly in me.polygons:
        ax = max(range(3), key=lambda i: abs(poly.normal[i]))
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            half = 0.0
            if ax == 1:
                x, z = co.x, co.z
                if poly.normal.y > 0:  # flanc gauche : moitié droite du dessin (textes en miroir)
                    half = 0.5
            elif ax == 2:
                x, z = co.x, z_band + co.y
            else:
                x, z = co.x + co.y, co.z
            layer[li].uv = (half + 0.5 * (x - x0) / xspan, (z - z0) / zspan)


def bake(ob, design_img, path):
    """Dépliage propre + bake du dessin projeté dans une texture unique."""
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

    img = bpy.data.images.new(os.path.basename(path), BAKE_RES, BAKE_RES)
    target = nt.nodes.new("ShaderNodeTexImage")
    target.image = img
    nt.nodes.active = target
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 4
    sc.render.bake.margin = 16
    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, use_clear=True)
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    from PIL import Image
    Image.open(path).resize((FINAL_RES, FINAL_RES), Image.LANCZOS).save(path)
    bpy.data.images.remove(img)
    me.uv_layers.remove(me.uv_layers["proj"])
    me.materials.clear()
    bpy.data.materials.remove(m)


# --------------------------------------------------------------- matériaux
def assign_material(ob, skin, tex_path=None):
    name = ob.name
    key = skin["palette"]["Gachette"] if name == "Trigger" else name.split("_")[-1]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.55
    if tex_path:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(tex_path)
        nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
        m.diffuse_color = (1, 1, 1, 1)
    else:
        r, g, b, neon = skins.COLORS[key]
        c = lin((r, g, b))
        p.inputs["Base Color"].default_value = c
        m.diffuse_color = c
        if neon:
            p.inputs["Emission Color"].default_value = c
            p.inputs["Emission Strength"].default_value = 2.5
        if key.startswith("Verre"):  # verre teinté (Transparency réglée par le script Roblox)
            p.inputs["Alpha"].default_value = 0.22
        if key == "Contour":
            # aperçu Blender : la coque n'est visible que de l'intérieur
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
def preview(path, W, center):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 64
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = 1600, 900
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

    # tout est mis à l'échelle de l'arme (cadrage réglé sur l'AR-01 ; les armes
    # compactes comme le deagle sont cadrées sur leur hauteur)
    k = max(W.target[0], 2.7 * W.target[2]) / 3.626
    c = Vector(center)

    def light(off, energy, size):
        bpy.ops.object.light_add(type="AREA", location=c + Vector(off) * k)
        lo = bpy.context.object
        lo.data.energy, lo.data.size = energy * k * k, size * k
        lo.rotation_euler = (c - lo.location).to_track_quat("-Z", "Y").to_euler()

    light((0.1, 1.4, 1.1), 28, 1.5)
    light((1.2, 0.6, 0.2), 10, 1.5)
    light((-0.8, -1.2, 0.9), 22, 1.0)
    bpy.ops.object.camera_add(location=c + Vector((-0.41, 1.95, 0.5)) * k)
    cam = bpy.context.object
    cam.data.lens = 50
    cam.data.clip_start = 0.01
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    for ob in list(bpy.data.objects):
        if ob.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(ob)


# ------------------------------------------------------------------ un skin
def build_skin(W, skin):
    name = skin["name"]
    out = os.path.join(weapon_dir(W), name)
    tex_dir = os.path.join(out, "textures")
    os.makedirs(tex_dir, exist_ok=True)
    file = f"{W.file_prefix}_{name}"
    bpy.ops.wm.read_factory_settings(use_empty=True)
    objs = W.build()

    # dessin vue de côté (coordonnées monde)
    pts = [v.co for (g, r), ob in objs.items() if g != "Root" for v in ob.data.vertices]
    margin = 0.03
    x0, x1 = min(p.x for p in pts) - margin, max(p.x for p in pts) + margin
    z0, z1 = min(p.z for p in pts) - margin, max(p.z for p in pts) + margin
    xspan, zspan = x1 - x0, z1 - z0
    Wpx = 4096
    H = int(Wpx * zspan / xspan)
    ppm = Wpx / xspan
    w2p = lambda x, z: ((x - x0) * ppm, (z1 - z) * ppm)
    from PIL import Image
    halves = []
    for mirror in (False, True):
        ctx = Ctx(Wpx, H, w2p, ppm, W.design_to_world, K.STUD * W.scale.x, seed=11)
        ctx.mirror_text = mirror
        ctx.zones = {k: v for k, v in W.zones.items() if k not in ("branch", "top_band_z")}
        ctx.zones["branch"] = W.zones["branch"]
        ctx.emblem = W.emblem
        ctx.flower_scale = W.flower_scale
        halves.append(skin["paint"](ctx))
    design = Image.new("RGB", (2 * Wpx, H))
    design.paste(halves[0], (0, 0))
    design.paste(halves[1], (Wpx, 0))
    design_path = os.path.join(tex_dir, f"{name.lower()}_design_sideview.png")
    design.save(design_path)
    design_img = bpy.data.images.load(design_path)

    z_band = W.design_to_world(0, W.zones["top_band_z"])[1]
    tex = {}
    for group in W.groups:
        ob = objs.get((group, "Motif"))
        if ob is None:
            continue
        project_uvs(ob, x0, z0, xspan, zspan, z_band)
        path = os.path.join(tex_dir, f"{file}_{group}_{name}.png")
        bake(ob, design_img, path)
        tex[f"{group}_{name}"] = path

    contours = W.add_contours(objs)
    palette = dict(skin["palette"], Motif=name)
    final = W.assemble(objs, contours, palette, f"{W.file_prefix} {name}")
    for oname, ob in final.items():
        if oname != "Root":
            assign_material(ob, skin, tex.get(oname))
    final["Root"].hide_render = True
    for oname, ob in final.items():
        key = oname.split("_")[-1]
        if key == "Contour" or key.startswith("Verre") or key.startswith("Lentille"):  # pas d'ombre dans l'aperçu
            ob.visible_shadow = ob.visible_diffuse = ob.visible_glossy = ob.visible_transmission = False

    center = ((x0 + x1) / 2, 0.0, (z0 + z1) / 2)
    preview(os.path.join(out, f"{file}_preview.png"), W, center)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, f"{file}.blend"), compress=True)
    blend1 = os.path.join(out, f"{file}.blend1")
    if os.path.exists(blend1):
        os.remove(blend1)

    # export : géométrie convertie en studs (1 unité du fichier = 1 stud)
    to_studs = Matrix.Scale(1 / K.STUD, 4)
    for ob in final.values():
        ob.data.transform(to_studs)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in bpy.data.objects:
        ob.select_set(True)
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(out, f"{file}.fbx"),
        use_selection=True,
        object_types={"EMPTY", "MESH"},
        apply_scale_options="FBX_SCALE_UNITS",
        path_mode="COPY",
        embed_textures=True,
        mesh_smooth_type="FACE",
        use_triangles=True,
        add_leaf_bones=False,
    )
    tris = sum(len(ob.data.polygons) for ob in final.values())
    print(f"SKIN {name:10s} {len(final):2d} pièces, {tris} triangles -> {file}.fbx", flush=True)


# ------------------------------------------------------------------ script Roblox
def write_installer():
    tpl = open(os.path.join(HERE, "templates", "InstallerSkinsPhantom.lua"), encoding="utf-8").read()
    lines = []
    for name, (r, g, b, neon) in skins.COLORS.items():
        lines.append(f"\t{name} = {{ Color3.fromRGB({r}, {g}, {b}), {'true' if neon else 'false'} }},")
    skin_lines = [f"\t{s['name']} = {{ Gachette = \"{s['palette']['Gachette']}\" }}," for s in skins.SKINS]
    ordre = ", ".join(f'"{s["name"]}"' for s in skins.SKINS)
    arme_lines = []
    for W in WEAPONS.values():
        groups = ", ".join(f'{k} = "{v}"' for k, v in W.groups.items())
        arme_lines.append(f'\t{W.file_prefix} = {{ dossier = "{W.file_prefix}", reference = "{W.file_prefix} P", '
                          f'longueur = {W.target[0]}, groupes = {{ {groups} }} }},')
    tpl = tpl.replace("--@@COULEURS@@", "\n".join(lines)).replace("--@@SKINS@@", "\n".join(skin_lines))
    tpl = tpl.replace("--@@ORDRE@@", ordre).replace("--@@ARMES@@", "\n".join(arme_lines))
    path = os.path.join(ROOT, "roblox", "InstallerSkinsPhantom.lua")
    with open(path, "w", encoding="utf-8") as f:
        f.write(tpl)
    print("INSTALLER", path)


def write_zip_and_gallery(W):
    from PIL import Image, ImageDraw, ImageFont
    wd = weapon_dir(W)
    tag = W.folder.replace("VANTA_", "")
    zpath = os.path.join(wd, f"Skins_{tag}_FBX.zip")
    tiles = []
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for s in skins.SKINS:
            fbx = os.path.join(wd, s["name"], f"{W.file_prefix}_{s['name']}.fbx")
            if os.path.exists(fbx) and s["name"] not in ZIP_EXCLUDE.get(W.key, ()):
                z.write(fbx, os.path.basename(fbx))
            prev = os.path.join(wd, s["name"], f"{W.file_prefix}_{s['name']}_preview.png")
            if os.path.exists(prev):
                tiles.append((s["name"], Image.open(prev).convert("RGB")))
    print("ZIP", zpath)
    if not tiles:
        return
    tw, th = 800, 450
    cols = min(3, len(tiles))
    rows = math.ceil(len(tiles) / cols)
    g = Image.new("RGB", (tw * cols, th * rows), (12, 12, 15))
    f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", 40)
    for i, (name, im) in enumerate(tiles):
        im = im.resize((tw, th), Image.LANCZOS).crop((0, 0, tw, th))
        x, y = (i % cols) * tw, (i // cols) * th
        g.paste(im, (x, y))
        ImageDraw.Draw(g).text((x + 24, y + 18), name.upper(), font=f, fill=(255, 255, 255))
    g.save(os.path.join(wd, "galerie.png"))
    print("GALERIE", os.path.join(wd, "galerie.png"))


def main():
    argv = sys.argv[1:]
    key = "ar01"
    if "--weapon" in argv:
        i = argv.index("--weapon")
        key = argv[i + 1]
        del argv[i:i + 2]
    W = WEAPONS[key]
    args = [a for a in argv if not a.startswith("--")]
    if "--installer" not in argv:
        todo = [skins.BY_NAME[a.lower()] for a in args] if args else skins.SKINS
        for s in todo:
            build_skin(W, s)
        write_zip_and_gallery(W)
    write_installer()


main()
