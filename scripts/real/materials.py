"""Matériaux PBR procéduraux (Cycles) et cuisson en textures pour Roblox.

Chaque pièce reçoit un matériau procédural (couleur, usure des arêtes, saleté dans les creux,
grain, texture granuleuse, moletage, gravures), puis il est cuit en 4 images :
    <pièce>_Couleur.png   (couleur + occlusion)       -> TextureID / ColorMap
    <pièce>_Rugosite.png                              -> RoughnessMap
    <pièce>_Metal.png                                 -> MetalnessMap
    <pièce>_Normal.png    (espace tangent, OpenGL)    -> NormalMap
"""
import math
import os

import bpy
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

FONTS = {
    "sans": "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "sans_r": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "cond": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
    "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
}

# kind : coated (peinture/anodisation sur métal), metal (métal nu), poly (polymère),
#        rubber (caoutchouc), glass
# bump : grain | brushed | stipple | rubber | g10 | cast | none
MATS = {
    "AnodiseNoir": dict(kind="coated", color=(0.030, 0.031, 0.034), metal=0.85, rough=0.40,
                        wear=(0.20, 0.20, 0.21), wear_amt=0.45, bump="grain", bump_s=0.25),
    "CerakoteNoir": dict(kind="coated", color=(0.024, 0.024, 0.026), metal=0.0, rough=0.66,
                         wear=(0.30, 0.30, 0.31), wear_amt=0.45, bump="grain", bump_s=0.35),
    "CerakoteFDE": dict(kind="coated", color=(0.27, 0.19, 0.11), metal=0.0, rough=0.62,
                        wear=(0.42, 0.42, 0.43), wear_amt=0.50, bump="grain", bump_s=0.35),
    "CerakoteGris": dict(kind="coated", color=(0.13, 0.135, 0.14), metal=0.0, rough=0.58,
                         wear=(0.45, 0.45, 0.47), wear_amt=0.45, bump="grain", bump_s=0.35),
    "PolymereNoir": dict(kind="poly", color=(0.016, 0.016, 0.017), metal=0.0, rough=0.74,
                         wear=(0.07, 0.07, 0.075), wear_amt=0.6, bump="grain", bump_s=0.25),
    "PolymereFDE": dict(kind="poly", color=(0.30, 0.23, 0.15), metal=0.0, rough=0.66,
                        wear=(0.40, 0.32, 0.22), wear_amt=0.6, bump="grain", bump_s=0.25),
    "Caoutchouc": dict(kind="rubber", color=(0.018, 0.018, 0.019), metal=0.0, rough=0.86,
                       wear=(0.04, 0.04, 0.04), wear_amt=0.3, bump="rubber", bump_s=0.5),
    "AcierNoir": dict(kind="coated", color=(0.045, 0.046, 0.05), metal=0.75, rough=0.45,
                      wear=(0.55, 0.55, 0.57), wear_amt=0.6, bump="grain", bump_s=0.2),
    "AcierBrut": dict(kind="metal", color=(0.42, 0.42, 0.43), metal=1.0, rough=0.38,
                      wear=(0.62, 0.62, 0.63), wear_amt=0.5, bump="brushed", bump_s=0.25),
    "Inox": dict(kind="metal", color=(0.60, 0.60, 0.59), metal=1.0, rough=0.24,
                 wear=(0.72, 0.72, 0.71), wear_amt=0.4, bump="brushed", bump_s=0.2),
    "Lame": dict(kind="metal", color=(0.58, 0.585, 0.59), metal=1.0, rough=0.30,
                 wear=(0.75, 0.75, 0.76), wear_amt=0.3, bump="stonewash", bump_s=0.3),
    "LameNoire": dict(kind="coated", color=(0.05, 0.05, 0.055), metal=0.8, rough=0.36,
                      wear=(0.62, 0.62, 0.63), wear_amt=0.7, bump="stonewash", bump_s=0.3),
    "G10": dict(kind="poly", color=(0.022, 0.024, 0.022), metal=0.0, rough=0.70,
                wear=(0.10, 0.11, 0.10), wear_amt=0.5, bump="g10", bump_s=0.8),
    "Laiton": dict(kind="metal", color=(0.72, 0.52, 0.24), metal=1.0, rough=0.32,
                   wear=(0.85, 0.66, 0.36), wear_amt=0.4, bump="brushed", bump_s=0.15),
    "Tritium": dict(kind="emit", color=(0.35, 1.0, 0.45), metal=0.0, rough=0.3),
    "Verre": dict(kind="glass", color=(0.55, 0.75, 0.85)),
    "VerreLunette": dict(kind="glass", color=(0.25, 0.55, 0.75)),
}


# ------------------------------------------------------------------ outils de nœuds
class G:
    def __init__(self, mat):
        self.nt = mat.node_tree
        self.n = self.nt.nodes
        self.l = self.nt.links

    def node(self, kind, **props):
        nd = self.n.new(kind)
        for k, v in props.items():
            if k.startswith("in_"):
                key = k[3:].replace("_", " ")
                nd.inputs[key].default_value = v
            else:
                setattr(nd, k, v)
        return nd

    def link(self, a, b):
        self.l.new(a, b)
        return b

    def math(self, op, a, b=None, clamp=False):
        nd = self.node("ShaderNodeMath", operation=op, use_clamp=clamp)
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                nd.inputs[i].default_value = v
            else:
                self.link(v, nd.inputs[i])
        return nd.outputs[0]

    def mix(self, fac, a, b):
        nd = self.node("ShaderNodeMix", data_type="RGBA", blend_type="MIX")
        for sock, v in ((nd.inputs[0], fac), (nd.inputs[6], a), (nd.inputs[7], b)):
            if isinstance(v, (tuple, list)):
                sock.default_value = (*v, 1.0) if len(v) == 3 else v
            elif isinstance(v, (int, float)):
                sock.default_value = v
            else:
                self.link(v, sock)
        return nd.outputs[2]

    def lerp(self, fac, a, b):
        """a + (b - a) * fac (valeurs ou sorties de nœuds)."""
        d = b - a if isinstance(a, (int, float)) and isinstance(b, (int, float)) else self.math("SUBTRACT", b, a)
        return self.math("ADD", self.math("MULTIPLY", fac, d), a)

    def maprange(self, v, a, b, c=0.0, d=1.0, smooth=False):
        nd = self.node("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP" if smooth else "LINEAR", clamp=True)
        self.link(v, nd.inputs["Value"])
        nd.inputs["From Min"].default_value = a
        nd.inputs["From Max"].default_value = b
        nd.inputs["To Min"].default_value = c
        nd.inputs["To Max"].default_value = d
        return nd.outputs["Result"]

    def noise(self, vec, scale, detail=4.0, rough=0.5, dims="3D", w=None):
        nd = self.node("ShaderNodeTexNoise", noise_dimensions=dims)
        self.link(vec, nd.inputs["Vector"])
        nd.inputs["Scale"].default_value = scale
        nd.inputs["Detail"].default_value = detail
        nd.inputs["Roughness"].default_value = rough
        return nd.outputs["Fac"]

    def voronoi(self, vec, scale, feature="F1", out="Distance", rand=1.0):
        nd = self.node("ShaderNodeTexVoronoi", feature=feature)
        self.link(vec, nd.inputs["Vector"])
        nd.inputs["Scale"].default_value = scale
        nd.inputs["Randomness"].default_value = rand
        return nd.outputs[out]

    def scale_vec(self, vec, s):
        nd = self.node("ShaderNodeVectorMath", operation="MULTIPLY")
        self.link(vec, nd.inputs[0])
        nd.inputs[1].default_value = s
        return nd.outputs[0]

    def sep(self, vec):
        nd = self.node("ShaderNodeSeparateXYZ")
        self.link(vec, nd.inputs[0])
        return nd.outputs


# ------------------------------------------------------------------ gravures
def engraving_images(ob, part, px_per_stud=900):
    """Une image de masque par côté (+Y, -Y), projetée en (X, Z) sur la boîte de la pièce."""
    if not part or not part.engravings:
        return None
    xs = [v.co.x for v in ob.data.vertices]
    zs = [v.co.z for v in ob.data.vertices]
    x0, x1, z0, z1 = min(xs) - 0.01, max(xs) + 0.01, min(zs) - 0.01, max(zs) + 0.01
    W = max(64, int((x1 - x0) * px_per_stud))
    H = max(64, int((z1 - z0) * px_per_stud))
    imgs = {}
    for side in (1, -1):
        im = Image.new("L", (W, H), 0)
        for text, x, z, h, s, font, bold, depth in part.engravings:
            if s != side:
                continue
            fpath = FONTS.get(font, FONTS["sans"])
            hp = max(6, int(h * px_per_stud))
            f = ImageFont.truetype(fpath, int(hp * 1.32))
            bb = f.getbbox(text)
            tw, th = bb[2] - bb[0] + 4, bb[3] - bb[1] + 4
            block = Image.new("L", (tw, th), 0)
            ImageDraw.Draw(block).text((2 - bb[0], 2 - bb[1]), text, fill=int(255 * depth), font=f)
            if side == 1:  # vu de +Y : +X va vers la gauche, x = bord gauche vu par l'observateur
                block = ImageOps.mirror(block)
                px = int((x - x0) * px_per_stud) - tw
            else:
                px = int((x - x0) * px_per_stud)
            pz = H - int((z - z0) * px_per_stud) - th
            im.paste(block, (px, pz), block)
        if im.getbbox():
            imgs[side] = im
    if not imgs:
        return None
    return (x0, x1, z0, z1), imgs


def _engraving_mask(g, coord, ob, part):
    data = engraving_images(ob, part)
    if not data:
        return None
    (x0, x1, z0, z1), imgs = data
    xyz = g.sep(coord)
    u = g.math("DIVIDE", g.math("SUBTRACT", xyz[0], x0), x1 - x0)
    v = g.math("DIVIDE", g.math("SUBTRACT", xyz[2], z0), z1 - z0)
    comb = g.node("ShaderNodeCombineXYZ")
    g.link(u, comb.inputs[0])
    g.link(v, comb.inputs[1])
    geo = g.node("ShaderNodeNewGeometry")
    ny = g.sep(geo.outputs["True Normal"])[1]
    total = None
    for side, im in imgs.items():
        path = os.path.join(bpy.app.tempdir or "/tmp", f"grav_{ob.name}_{side}.png")
        im.save(path)
        bimg = bpy.data.images.load(path)
        bimg.colorspace_settings.name = "Non-Color"
        tex = g.node("ShaderNodeTexImage", image=bimg, extension="CLIP", interpolation="Cubic")
        g.link(comb.outputs[0], tex.inputs["Vector"])
        facing = g.maprange(ny, 0.55, 0.8) if side == 1 else g.maprange(ny, -0.55, -0.8)
        m = g.math("MULTIPLY", tex.outputs["Color"], facing)
        total = m if total is None else g.math("MAXIMUM", total, m)
    return total


# ------------------------------------------------------------------ matériau procédural
def procedural(ob, part, mask_image=None):
    spec = MATS[ob["mat"]]
    mat = bpy.data.materials.new(f"M_{ob.name}")
    mat.use_nodes = True
    g = G(mat)
    for nd in list(g.n):
        g.n.remove(nd)
    out = g.node("ShaderNodeOutputMaterial")
    bsdf = g.node("ShaderNodeBsdfPrincipled")
    g.link(bsdf.outputs[0], out.inputs["Surface"])
    kind = spec["kind"]
    if kind == "glass":
        bsdf.inputs["Base Color"].default_value = (*spec["color"], 1)
        bsdf.inputs["Roughness"].default_value = 0.02
        bsdf.inputs["Transmission Weight"].default_value = 1.0
        bsdf.inputs["IOR"].default_value = 1.5
        ob.data.materials.append(mat)
        return mat, {}
    if kind == "emit":
        bsdf.inputs["Base Color"].default_value = (*spec["color"], 1)
        bsdf.inputs["Emission Color"].default_value = (*spec["color"], 1)
        bsdf.inputs["Emission Strength"].default_value = 3.0
        ob.data.materials.append(mat)
        return mat, {}

    tc = g.node("ShaderNodeTexCoord")
    co = tc.outputs["Object"]
    seed = (hash(ob.name) % 97) * 0.731
    cos = g.node("ShaderNodeVectorMath", operation="ADD")
    g.link(co, cos.inputs[0])
    cos.inputs[1].default_value = (seed, seed * 0.37, seed * 0.61)
    co = cos.outputs[0]

    # masques : arêtes (usure) et creux (saleté)
    if mask_image is None:
        bev = g.node("ShaderNodeBevel", samples=8)
        bev.inputs["Radius"].default_value = 0.012
        geo = g.node("ShaderNodeNewGeometry")
        dot = g.node("ShaderNodeVectorMath", operation="DOT_PRODUCT")
        g.link(bev.outputs[0], dot.inputs[0])
        g.link(geo.outputs["Normal"], dot.inputs[1])
        edge = g.maprange(g.math("SUBTRACT", 1.0, dot.outputs["Value"]), 0.004, 0.05)
        ao = g.node("ShaderNodeAmbientOcclusion", samples=16)
        ao.inputs["Distance"].default_value = 0.12
        cav = g.math("SUBTRACT", 1.0, ao.outputs["AO"])
    else:
        uv = g.node("ShaderNodeUVMap", uv_map="UVMap")
        mt = g.node("ShaderNodeTexImage", image=mask_image, interpolation="Linear")
        g.link(uv.outputs[0], mt.inputs["Vector"])
        rgb = g.node("ShaderNodeSeparateColor")
        g.link(mt.outputs["Color"], rgb.inputs[0])
        edge, cav = rgb.outputs[0], rgb.outputs[1]
    mask_out = (edge, cav)

    # usure : arêtes cassées par un bruit
    brk = g.noise(co, 9.0, 6.0, 0.62)
    brk2 = g.noise(co, 38.0, 3.0, 0.5)
    wear_fac = g.math("MULTIPLY", edge, g.maprange(g.math("ADD", brk, g.math("MULTIPLY", brk2, 0.35)), 0.62, 0.88))
    wear = g.maprange(wear_fac, 0.30 * (1.3 - spec.get("wear_amt", 0.5)), 0.75, smooth=True)
    wear = g.math("MULTIPLY", wear, 0.7)
    if kind in ("poly", "rubber"):
        wear = g.math("MULTIPLY", wear, 0.7)

    # couleur de base avec variations douces
    var = g.noise(co, 2.2, 5.0, 0.55)
    var2 = g.noise(co, 14.0, 4.0, 0.6)
    vv = g.maprange(g.math("ADD", var, g.math("MULTIPLY", var2, 0.4)), 0.35, 1.05, 0.88, 1.12)
    base = g.mix(0.0, spec["color"], spec["color"])
    tint = g.node("ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
    tint.inputs[0].default_value = 1.0
    g.link(base, tint.inputs[6])
    cvv = g.node("ShaderNodeCombineColor")
    for i in range(3):
        g.link(vv, cvv.inputs[i])
    g.link(cvv.outputs[0], tint.inputs[7])
    color = tint.outputs[2]

    rough = g.math("ADD", spec["rough"], g.math("MULTIPLY", g.math("SUBTRACT", var2, 0.5), 0.12))
    metal = spec["metal"]

    # traces / taches (empreintes, huile) sur le métal
    if kind in ("coated", "metal"):
        smudge = g.maprange(g.noise(co, 4.5, 3.0, 0.5), 0.5, 0.75)
        rough = g.math("ADD", rough, g.math("MULTIPLY", smudge, 0.10 if kind == "metal" else -0.08))

    # zones granuleuses / moletées
    height = None
    if part and part.stipple:
        xyz = g.sep(tc.outputs["Object"])
        zone = None
        for x0, z0, x1, z1 in part.stipple:
            zx = g.math("MULTIPLY", g.math("GREATER_THAN", xyz[0], x0), g.math("LESS_THAN", xyz[0], x1))
            zz = g.math("MULTIPLY", g.math("GREATER_THAN", xyz[2], z0), g.math("LESS_THAN", xyz[2], z1))
            z = g.math("MULTIPLY", zx, zz)
            zone = z if zone is None else g.math("MAXIMUM", zone, z)
        st = g.voronoi(co, 140.0, "SMOOTH_F1", "Distance")
        st = g.maprange(st, 0.0, 0.5, 1.0, 0.0)
        height = g.math("MULTIPLY", g.math("MULTIPLY", st, zone), 0.9)
        rough = g.math("ADD", rough, g.math("MULTIPLY", zone, 0.12))
    if part and part.knurl:
        xyz = g.sep(tc.outputs["Object"])
        zone = None
        for x0, z0, x1, z1 in part.knurl:
            zx = g.math("MULTIPLY", g.math("GREATER_THAN", xyz[0], x0), g.math("LESS_THAN", xyz[0], x1))
            zz = g.math("MULTIPLY", g.math("GREATER_THAN", xyz[2], z0), g.math("LESS_THAN", xyz[2], z1))
            z = g.math("MULTIPLY", zx, zz)
            zone = z if zone is None else g.math("MAXIMUM", zone, z)
        k = 2 * math.pi * 55
        a = g.math("SINE", g.math("MULTIPLY", g.math("ADD", xyz[0], xyz[2]), k))
        b = g.math("SINE", g.math("MULTIPLY", g.math("SUBTRACT", xyz[0], xyz[2]), k))
        kn = g.math("MULTIPLY", g.math("MINIMUM", g.math("ABSOLUTE", a), g.math("ABSOLUTE", b)), zone)
        height = kn if height is None else g.math("MAXIMUM", height, kn)

    # micro-relief du matériau
    bump_kind = spec.get("bump", "none")
    micro = None
    if bump_kind == "grain":
        micro = g.math("MULTIPLY", g.noise(co, 90.0, 2.0, 0.5), 0.35)
    elif bump_kind == "brushed":
        stretched = g.node("ShaderNodeMapping")
        g.link(co, stretched.inputs["Vector"])
        stretched.inputs["Scale"].default_value = (0.6, 60.0, 60.0)
        micro = g.math("MULTIPLY", g.noise(stretched.outputs[0], 5.0, 6.0, 0.7), 0.5)
        rough = g.math("ADD", rough, g.math("MULTIPLY", g.math("SUBTRACT", micro, 0.25), 0.25))
    elif bump_kind == "stonewash":
        sw = g.voronoi(co, 150.0, "F1", "Distance")
        micro = g.math("MULTIPLY", g.maprange(sw, 0.0, 0.3, 1.0, 0.0), 0.25)
        rough = g.math("ADD", rough, g.math("MULTIPLY", g.noise(co, 30.0, 4.0, 0.6), 0.12))
    elif bump_kind == "rubber":
        micro = g.math("MULTIPLY", g.voronoi(co, 160.0, "SMOOTH_F1", "Distance"), 0.8)
    elif bump_kind == "g10":
        n1 = g.noise(co, 25.0, 8.0, 0.75)
        micro = g.math("MULTIPLY", g.maprange(n1, 0.45, 0.62), 0.9)
        color = g.mix(g.math("MULTIPLY", g.maprange(n1, 0.45, 0.6), 0.35), color, (0.05, 0.055, 0.05))
    if micro is not None:
        micro = g.math("MULTIPLY", micro, spec.get("bump_s", 0.3))
        height = micro if height is None else g.math("ADD", height, micro)

    # gravures
    grav = _engraving_mask(g, tc.outputs["Object"], ob, part)

    # assemblage
    wear_rgb = spec.get("wear", spec["color"])
    color = g.mix(wear, color, wear_rgb)
    rough = g.lerp(wear, rough, 0.28 if kind in ("coated", "metal") else spec["rough"] - 0.15)
    if kind == "coated":
        metal = g.lerp(wear, metal, 1.0)
    # saleté dans les creux
    dirt = g.math("MULTIPLY", g.maprange(cav, 0.08, 0.7), g.maprange(g.noise(co, 6.0, 4.0, 0.6), 0.35, 0.7, 0.55, 1.0))
    color = g.mix(g.math("MULTIPLY", dirt, 0.55), color, (0.012, 0.011, 0.010))
    rough = g.lerp(g.math("MULTIPLY", dirt, 0.6), rough, 0.85)
    if grav is not None:
        fill = (0.085, 0.085, 0.09) if kind in ("coated", "poly") else (0.10, 0.10, 0.10)
        color = g.mix(g.math("MULTIPLY", grav, 0.75), color, fill)
        rough = g.lerp(grav, rough, 0.75)
        if kind == "coated":
            metal = g.lerp(grav, metal, 0.2)
        gh = g.math("MULTIPLY", grav, -1.0)
        height = gh if height is None else g.math("ADD", height, gh)

    # AO multipliée dans la couleur cuite (pour les vues sans SurfaceAppearance)
    ao_mul = g.maprange(cav, 0.0, 0.8, 1.0, 0.55)
    color_ao = g.node("ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
    color_ao.inputs[0].default_value = 1.0
    g.link(color, color_ao.inputs[6])
    cao = g.node("ShaderNodeCombineColor")
    for i in range(3):
        g.link(ao_mul, cao.inputs[i])
    g.link(cao.outputs[0], color_ao.inputs[7])

    if isinstance(rough, float):
        bsdf.inputs["Roughness"].default_value = rough
    else:
        g.link(g.math("MAXIMUM", g.math("MINIMUM", rough, 1.0), 0.05), bsdf.inputs["Roughness"])
    if isinstance(metal, (int, float)):
        bsdf.inputs["Metallic"].default_value = metal
    else:
        g.link(metal, bsdf.inputs["Metallic"])
    g.link(color_ao.outputs[2], bsdf.inputs["Base Color"])
    if height is not None:
        bump = g.node("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 1.0
        bump.inputs["Distance"].default_value = 0.0025
        g.link(height, bump.inputs["Height"])
        g.link(bump.outputs[0], bsdf.inputs["Normal"])
    if kind in ("poly", "rubber"):  # aperçu seulement : reflet atténué des plastiques
        bsdf.inputs["Specular IOR Level"].default_value = 0.3
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    return mat, {"edge": mask_out[0], "cav": mask_out[1], "bsdf": bsdf, "out": out, "g": g}


# ------------------------------------------------------------------ cuisson
def uv_unwrap(ob):
    me = ob.data
    while me.uv_layers:
        me.uv_layers.remove(me.uv_layers[0])
    me.uv_layers.new(name="UVMap")
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.004,
                             area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.pack_islands(margin=0.004, rotate=True, shape_method="CONCAVE")
    bpy.ops.object.mode_set(mode="OBJECT")


def _bake_to(ob, mat, name, socket, colorspace, res, samples, kind="EMIT"):
    g = G(mat)
    img = bpy.data.images.new(name, res, res, alpha=False, float_buffer=False)
    img.colorspace_settings.name = colorspace
    tex = g.node("ShaderNodeTexImage", image=img)
    g.n.active = tex
    out = next(n for n in g.n if n.type == "OUTPUT_MATERIAL")
    old = out.inputs["Surface"].links[0].from_socket
    em = None
    if kind == "EMIT":
        em = g.node("ShaderNodeEmission")
        if isinstance(socket, (int, float)):
            em.inputs["Color"].default_value = (socket, socket, socket, 1)
        else:
            g.link(socket, em.inputs["Color"])
        g.link(em.outputs[0], out.inputs["Surface"])
    sc = bpy.context.scene
    sc.cycles.samples = samples
    sc.render.bake.margin = max(4, res // 128)
    sc.render.bake.use_clear = True
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    if kind == "EMIT":
        bpy.ops.object.bake(type="EMIT")
    else:
        sc.render.bake.normal_space = "TANGENT"
        bpy.ops.object.bake(type="NORMAL")
    if em:
        g.n.remove(em)
        g.link(old, out.inputs["Surface"])
    g.n.remove(tex)
    return img


def _save(img, path, final_res):
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    Image.open(path).convert("RGB").resize((final_res, final_res), Image.LANCZOS).save(path, optimize=True)


def bake_part(ob, part, outdir, res=2048, final_res=1024):
    """Cuit le matériau procédural de ob en 4 textures, puis lui met le matériau final."""
    outdir = os.path.abspath(outdir)
    os.makedirs(outdir, exist_ok=True)
    spec = MATS[ob["mat"]]
    if spec["kind"] in ("glass", "emit"):
        procedural(ob, part)
        return {}
    uv_unwrap(ob)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    # 1) masques (arêtes, creux) : bruités -> beaucoup d'échantillons
    mat, s = procedural(ob, part)
    comb = s["g"].node("ShaderNodeCombineColor")
    s["g"].link(s["edge"], comb.inputs[0])
    s["g"].link(s["cav"], comb.inputs[1])
    mask = _bake_to(ob, mat, f"{ob.name}_mask", comb.outputs[0], "Non-Color", res // 2, 24)
    mask.pack()
    bpy.data.materials.remove(mat)
    # 2) couleur / rugosité / métal / normales à partir des masques cuits
    mat, s = procedural(ob, part, mask_image=mask)
    bsdf = s["bsdf"]
    paths = {}

    def socket_of(name):
        sock = bsdf.inputs[name]
        return sock.links[0].from_socket if sock.links else sock.default_value

    for key, sock_name, cs in (("Couleur", "Base Color", "sRGB"), ("Rugosite", "Roughness", "Non-Color"),
                               ("Metal", "Metallic", "Non-Color")):
        src = socket_of(sock_name)
        if isinstance(src, (int, float)) or (hasattr(src, "__len__") and not hasattr(src, "node")):
            v = src if isinstance(src, (int, float)) else src[0]
            img = bpy.data.images.new(f"{ob.name}_{key}", 8, 8)
            img.colorspace_settings.name = cs
            img.pixels = [v, v, v, 1.0] * 64
            path = os.path.join(outdir, f"{ob.name}_{key}.png")
            img.filepath_raw = path
            img.file_format = "PNG"
            img.save()
            Image.open(path).convert("RGB").resize((64, 64)).save(path)
        else:
            img = _bake_to(ob, mat, f"{ob.name}_{key}", src, cs, res, 1)
            path = os.path.join(outdir, f"{ob.name}_{key}.png")
            _save(img, path, final_res)
        bpy.data.images.remove(img)
        paths[key] = path
    img = _bake_to(ob, mat, f"{ob.name}_Normal", None, "Non-Color", res, 2, kind="NORMAL")
    paths["Normal"] = os.path.join(outdir, f"{ob.name}_Normal.png")
    _save(img, paths["Normal"], final_res)
    bpy.data.images.remove(img)
    bpy.data.materials.remove(mat)
    bpy.data.images.remove(mask)
    final_material(ob, paths)
    return paths


def final_material(ob, paths):
    mat = bpy.data.materials.new(f"M_{ob.name}")
    mat.use_nodes = True
    g = G(mat)
    bsdf = next(n for n in g.n if n.type == "BSDF_PRINCIPLED")
    uv = g.node("ShaderNodeUVMap", uv_map="UVMap")

    def tex(path, cs):
        im = bpy.data.images.load(path)
        im.colorspace_settings.name = cs
        t = g.node("ShaderNodeTexImage", image=im)
        g.link(uv.outputs[0], t.inputs["Vector"])
        return t

    g.link(tex(paths["Couleur"], "sRGB").outputs["Color"], bsdf.inputs["Base Color"])
    g.link(tex(paths["Rugosite"], "Non-Color").outputs["Color"], bsdf.inputs["Roughness"])
    g.link(tex(paths["Metal"], "Non-Color").outputs["Color"], bsdf.inputs["Metallic"])
    nm = g.node("ShaderNodeNormalMap")
    g.link(tex(paths["Normal"], "Non-Color").outputs["Color"], nm.inputs["Color"])
    g.link(nm.outputs[0], bsdf.inputs["Normal"])
    if MATS[ob["mat"]]["kind"] in ("poly", "rubber"):
        bsdf.inputs["Specular IOR Level"].default_value = 0.3
    ob.data.materials.clear()
    ob.data.materials.append(mat)
