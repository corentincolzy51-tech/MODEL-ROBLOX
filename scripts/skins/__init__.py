"""Catalogue des skins de la VANTA AR-01.

Chaque skin donne :
  - name     : nom ASCII (pièces Body_<name> / Magazine_<name>, fichier Phantom_<name>.fbx)
  - palette  : rôle -> nom de couleur (voir vanta_ar01.pieces)
  - paint    : fonction(ctx) -> image PIL de la texture vue de côté
Les couleurs nommées sont dans COLORS (reprises telles quelles par le script Roblox).
"""
from . import arcade, cryo, fantome, graffiti, nebuleuse, royal, sakura, toxic, vortex

# nom -> (r, g, b, neon)
COLORS = {
    "Contour": (14, 10, 16, False),
    "Noir": (30, 26, 34, False),
    "Blanc": (245, 241, 245, False),
    "Rose": (255, 92, 168, False),
    "RoseVif": (255, 45, 165, False),
    "Jaune": (255, 214, 40, False),
    "Or": (232, 178, 52, False),
    "Rouge": (205, 28, 42, False),
    "GrisFonce": (58, 54, 60, False),
    "Gris": (118, 118, 124, False),
    "GrisClair": (184, 184, 190, False),
    "Argent": (196, 206, 218, False),
    "VertAcide": (160, 255, 30, True),
    "VertSombre": (38, 84, 30, False),
    "BleuGlace": (105, 205, 255, True),
    "BleuNuit": (22, 38, 78, False),
    "Bleu": (58, 82, 230, False),
    "Violet": (104, 58, 186, False),
    "NoirViolet": (24, 14, 40, False),
    "VioletNeon": (165, 75, 255, True),
    "CyanNeon": (50, 225, 255, True),
    "MagentaNeon": (255, 40, 205, True),
    # lentilles de lunette (néon, opaques)
    "LentilleRose": (255, 120, 200, True),
    "LentilleViolet": (175, 100, 255, True),
    "LentilleRouge": (255, 60, 60, True),
    "LentilleVert": (150, 255, 80, True),
    "LentilleBleu": (110, 210, 255, True),
    "LentilleMagenta": (255, 70, 220, True),
    "LentilleBlanc": (235, 235, 245, True),
    # verres du viseur (transparents)
    "Verre": (255, 170, 215, False),
    "VerreViolet": (185, 120, 255, False),
    "VerreRouge": (255, 70, 70, False),
    "VerreVert": (150, 255, 90, False),
    "VerreBleu": (120, 205, 255, False),
    "VerreMagenta": (255, 95, 225, False),
    "VerreBlanc": (232, 232, 242, False),
}

SKINS = [m.SKIN for m in (sakura, graffiti, royal, toxic, cryo, nebuleuse, vortex, arcade, fantome)]
BY_NAME = {s["name"].lower(): s for s in SKINS}
