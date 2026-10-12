"""Mesure les armes cartoon (gabarit calé dans le jeu) : centre de la boîte englobante par
rapport à la poignée, en studs. Sert à placer les armes réalistes au même endroit dans la main."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import bpy  # noqa: E402

import weapon_kit as K  # noqa: E402

out = {}
for mod, key in (("vanta_ar01", "Phantom"), ("vanta_de50", "Deagle"), ("vanta_sr7", "Sniper"), ("couteau", "Couteau")):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    W = __import__(mod).WEAPON
    objs = W.build()
    pts = [v.co / K.STUD for (g, r), ob in objs.items() if g != "Root" for v in ob.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    out[key] = {"center": [(a + b) / 2 for a, b in zip(lo, hi)], "size": [b - a for a, b in zip(lo, hi)],
                "hold": list(W.hold_offset)}
    print(key, out[key])
json.dump(out, open(os.path.join(os.path.dirname(__file__), "cartoon_ref.json"), "w"), indent=1)
