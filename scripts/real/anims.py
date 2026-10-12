"""Animations des armes réalistes (images clés), inspirées des gestes réels.

Une seule source pour :
  - le ModuleScript Roblox roblox/AnimationsRealistes.lua (généré par write_lua())
  - les aperçus animés rendus dans Blender (preview_anim.py)

Conventions (les mêmes que la piste d'inspection du module EffetsSkins) :
  Arme      décalage de l'arme dans la vue FPS, repère caméra : X droite, Y haut, Z vers la caméra
            (studs) ; rotations en degrés, appliquées comme CFrame.Angles(rx, ry, rz)
            (rx > 0 : canon vers le haut, ry > 0 : canon vers la gauche, rz > 0 : bascule à gauche)
  pièces    Chargeur / Levier / Gachette / Corps : décalage du sous-modèle par rapport à sa place
            au repos, dans le repère de l'arme : X vers le canon, Y haut, Z côté droit.
            « pivot » = nom d'un Attachment du Root autour duquel tourner (Anneau du karambit,
            Verrou du sniper) ; sinon le centre du sous-modèle.
Chaque image clé : (temps, (x, y, z), (rx, ry, rz), lissage) ; le lissage s'applique au trajet
qui ARRIVE sur l'image clé : "lin", "doux", "sortie" (rapide puis freine), "entree", "ressort".
Les angles sont interpolés numériquement : 720° = deux tours complets.
"""
import os

Z = (0, 0, 0)


def k(t, p=Z, r=Z, e="doux"):
    return (t, p, r, e)


# ---------------------------------------------------------------- fusil (Phantom)
_AR_RELOAD_ARME = [
    k(0.0), k(0.30, (0.05, -0.12, 0.05), (-6, 14, -24)), k(0.45, (0.05, -0.10, 0.05), (-4, 14, -26), "sortie"),
    k(1.05, (0.03, -0.15, 0.04), (-8, 12, -22)), k(1.18, (0.03, -0.09, 0.04), (-4, 12, -19), "sortie"),
    k(1.32, (0.03, -0.12, 0.04), (-6, 12, -21)),
]
_AR_RELOAD_MAG = [
    k(0.0), k(0.40), k(0.44, (0, -0.06, 0), Z, "entree"), k(0.80, (0.10, -1.7, 0.12), (0, 0, 28), "entree"),
    k(0.801, (0.0, -1.5, 0.30), (0, 0, -10), "lin"), k(1.05, (0.0, -0.22, 0.0), (0, 0, -6), "sortie"),
    k(1.18, Z, Z, "sortie"),
]
ANIMS = {
    "Phantom": {
        "Tir": {"duree": 0.14, "Arme": [k(0.0), k(0.03, (0, 0.01, 0.09), (3.5, 0.6, 0.8), "sortie"), k(0.14)],
                "Gachette": [k(0.0), k(0.02, (-0.012, 0, 0), Z, "sortie"), k(0.10)]},
        "Recharge": {
            "duree": 2.25, "evenements": [(0.42, "ChargeurSort"), (1.18, "ChargeurEntre"), (1.30, "Rempli")],
            "Arme": _AR_RELOAD_ARME + [k(1.75, (0, -0.02, 0), (2, 2, 4)), k(2.25)],
            "Chargeur": _AR_RELOAD_MAG + [k(2.25)],
        },
        "RechargeVide": {
            "duree": 2.75,
            "evenements": [(0.42, "ChargeurSort"), (1.18, "ChargeurEntre"), (1.84, "Levier"), (1.90, "Rempli")],
            "Arme": _AR_RELOAD_ARME + [k(1.55, (0.02, -0.06, 0.08), (6, -6, 10)), k(1.80, (0.02, -0.05, 0.13), (8, -6, 12)),
                                       k(1.90, (0.02, -0.02, 0.08), (3, -4, 6), "sortie"), k(2.75)],
            "Chargeur": _AR_RELOAD_MAG + [k(2.75)],
            "Levier": [k(0.0), k(1.55), k(1.76, (-0.30, 0, 0)), k(1.84, Z, Z, "sortie"), k(2.75)],
        },
        "Equiper": {
            "duree": 0.6, "evenements": [(0.45, "Levier")],
            "Arme": [k(0.0, (0.25, -0.9, 0.2), (-55, 25, 35)), k(0.36, (0, 0.02, 0), (3, -2, -3), "sortie"),
                     k(0.60, Z, Z, "doux")],
            "Levier": [k(0.0), k(0.32), k(0.41, (-0.14, 0, 0)), k(0.45, Z, Z, "sortie"), k(0.6)],
        },
        "Inspection": {
            "duree": 4.2, "evenements": [(2.75, "Levier"), (2.95, "Levier")],
            "Arme": [k(0.0), k(0.55, (-0.15, 0.05, 0.10), (8, -38, 22)), k(1.6, (-0.17, 0.06, 0.10), (10, -42, 27)),
                     k(2.25, (-0.05, 0.0, 0.05), (-5, 25, -70)), k(3.1, (-0.06, 0.01, 0.06), (-6, 28, -75)),
                     k(3.55, (0, -0.03, 0), (4, 0, -8)), k(4.2)],
            "Levier": [k(0.0), k(2.6), k(2.78, (-0.12, 0, 0)), k(2.92), k(2.96, Z, Z, "sortie"), k(4.2)],
        },
    },
    # ------------------------------------------------------------ pistolet (Deagle)
    "Deagle": {
        "Tir": {"duree": 0.16, "Arme": [k(0.0), k(0.03, (0, 0.03, 0.12), (14, 1, 2), "sortie"), k(0.16)],
                "Levier": [k(0.0), k(0.025, (-0.17, 0, 0), Z, "sortie"), k(0.09, Z, Z, "entree")],
                "Gachette": [k(0.0), k(0.02, (-0.01, 0, 0), Z, "sortie"), k(0.10)]},
        "Recharge": {
            "duree": 1.9, "evenements": [(0.35, "ChargeurSort"), (1.0, "ChargeurEntre"), (1.1, "Rempli")],
            "Arme": [k(0.0), k(0.25, (0, -0.08, 0.05), (10, 12, -30)), k(0.40, (0, -0.06, 0.05), (8, 12, -32), "sortie"),
                     k(0.95, (0, -0.10, 0.05), (12, 10, -28)), k(1.02, (0, -0.06, 0.05), (9, 10, -26), "sortie"),
                     k(1.4, Z, (-3, 0, 4)), k(1.9)],
            "Chargeur": [k(0.0), k(0.33), k(0.37, (0, -0.05, 0), Z, "entree"), k(0.65, (0, -1.3, 0.1), (0, 0, 15), "entree"),
                         k(0.651, (0, -1.2, 0.2), Z, "lin"), k(0.90, (0, -0.15, 0), (0, 0, -8), "sortie"),
                         k(1.0, Z, Z, "sortie"), k(1.9)],
        },
        "RechargeVide": {
            "duree": 2.2, "evenements": [(0.35, "ChargeurSort"), (1.0, "ChargeurEntre"), (1.46, "Levier"), (1.5, "Rempli")],
            "Arme": [k(0.0), k(0.25, (0, -0.08, 0.05), (10, 12, -30)), k(0.40, (0, -0.06, 0.05), (8, 12, -32), "sortie"),
                     k(0.95, (0, -0.10, 0.05), (12, 10, -28)), k(1.02, (0, -0.06, 0.05), (9, 10, -26), "sortie"),
                     k(1.25, (0, -0.04, 0.06), (6, -8, 12)), k(1.42, (0, -0.03, 0.10), (8, -8, 14)),
                     k(1.48, (0, 0.0, 0.05), (2, -4, 6), "sortie"), k(2.2)],
            "Chargeur": [k(0.0), k(0.33), k(0.37, (0, -0.05, 0), Z, "entree"), k(0.65, (0, -1.3, 0.1), (0, 0, 15), "entree"),
                         k(0.651, (0, -1.2, 0.2), Z, "lin"), k(0.90, (0, -0.15, 0), (0, 0, -8), "sortie"),
                         k(1.0, Z, Z, "sortie"), k(2.2)],
            "Levier": [k(0.0), k(1.25), k(1.40, (-0.17, 0, 0)), k(1.46, Z, Z, "sortie"), k(2.2)],
        },
        "Equiper": {
            "duree": 0.5,
            "Arme": [k(0.0, (0.2, -0.7, 0.1), (-50, 20, 30)), k(0.32, (0, 0.015, 0), (2, -1, -2), "sortie"), k(0.5)],
        },
        "Inspection": {
            "duree": 4.0, "evenements": [(2.5, "Levier"), (2.9, "Levier")],
            "Arme": [k(0.0), k(0.5, (-0.10, 0.05, 0.05), (5, -30, 40)), k(1.4, (-0.10, 0.05, 0.05), (5, -35, 45)),
                     k(2.0, (-0.08, 0.04, 0.05), (-5, 30, -60)), k(2.9, (-0.08, 0.04, 0.05), (-5, 32, -62)),
                     k(3.4, (0, -0.02, 0), (2, 0, 0)), k(4.0)],
            "Levier": [k(0.0), k(2.3), k(2.5, (-0.09, 0, 0)), k(2.8, (-0.09, 0, 0)), k(2.9, Z, Z, "sortie"), k(4.0)],
        },
    },
    # ------------------------------------------------------------ fusil à verrou (Sniper)
    "Sniper": {
        "Tir": {"duree": 0.20, "Arme": [k(0.0), k(0.04, (0, 0.06, 0.22), (9, 1.5, 3), "sortie"), k(0.20)],
                "Gachette": [k(0.0), k(0.02, (-0.012, 0, 0), Z, "sortie"), k(0.12)]},
        "Culasse": {  # réarmement après chaque tir
            "duree": 1.05, "evenements": [(0.30, "LevierOuvre"), (0.55, "Douille"), (0.92, "LevierFerme")],
            "Arme": [k(0.0), k(0.12, (0.02, -0.03, 0.03), (2, 4, -12)), k(0.5, (0.02, -0.05, 0.05), (3, 4, -14)),
                     k(0.9, (0.01, -0.02, 0.02), (1, 2, -6)), k(1.05)],
            "Levier": {"pivot": "Verrou", "cles": [
                k(0.0), k(0.15), k(0.30, Z, (-58, 0, 0)), k(0.55, (-0.42, 0, 0), (-58, 0, 0)),
                k(0.80, Z, (-58, 0, 0)), k(0.92, Z, Z, "sortie"), k(1.05)]},
        },
        "Recharge": {
            "duree": 3.0,
            "evenements": [(0.32, "LevierOuvre"), (0.95, "ChargeurSort"), (1.75, "ChargeurEntre"), (1.8, "Rempli"),
                           (2.45, "LevierFerme")],
            "Arme": [k(0.0), k(0.25, (0.02, -0.05, 0.04), (3, 6, -14)), k(0.8, (0.04, -0.12, 0.05), (-4, 12, -22)),
                     k(1.0, (0.04, -0.10, 0.05), (-3, 12, -24), "sortie"), k(1.65, (0.04, -0.14, 0.05), (-6, 10, -20)),
                     k(1.78, (0.04, -0.09, 0.05), (-3, 10, -18), "sortie"), k(2.15, (0.02, -0.05, 0.04), (3, 6, -14)),
                     k(2.5, (0.01, -0.02, 0.02), (1, 2, -5)), k(3.0)],
            "Levier": {"pivot": "Verrou", "cles": [
                k(0.0), k(0.18), k(0.32, Z, (-58, 0, 0)), k(0.55, (-0.42, 0, 0), (-58, 0, 0)),
                k(2.15, (-0.42, 0, 0), (-58, 0, 0)), k(2.35, Z, (-58, 0, 0)), k(2.45, Z, Z, "sortie"), k(3.0)]},
            "Chargeur": [k(0.0), k(0.92), k(0.96, (0, -0.06, 0), Z, "entree"), k(1.3, (0.1, -1.7, 0.1), (0, 0, 20), "entree"),
                         k(1.301, (0, -1.5, 0.3), Z, "lin"), k(1.62, (0, -0.2, 0), (0, 0, -5), "sortie"),
                         k(1.75, Z, Z, "sortie"), k(3.0)],
        },
        "Equiper": {
            "duree": 0.75,
            "Arme": [k(0.0, (0.3, -1.0, 0.3), (-50, 25, 35)), k(0.5, (0, 0.02, 0), (2, -2, -2), "sortie"), k(0.75)],
        },
        "Inspection": {
            "duree": 4.5, "evenements": [(2.6, "LevierOuvre"), (3.2, "LevierFerme")],
            "Arme": [k(0.0), k(0.6, (-0.20, 0.05, 0.15), (6, -32, 20)), k(1.7, (-0.22, 0.06, 0.15), (8, -36, 24)),
                     k(2.3, (-0.05, 0.0, 0.10), (-3, 22, -55)), k(3.4, (-0.06, 0.01, 0.10), (-4, 25, -58)),
                     k(3.9, (0, -0.03, 0), (3, 0, -6)), k(4.5)],
            "Levier": {"pivot": "Verrou", "cles": [
                k(0.0), k(2.45), k(2.6, Z, (-58, 0, 0)), k(2.85, (-0.3, 0, 0), (-58, 0, 0)), k(3.05, Z, (-58, 0, 0)),
                k(3.2, Z, Z, "sortie"), k(4.5)]},
        },
    },
    # ------------------------------------------------------------ karambit (Couteau)
    "Couteau": {
        "Equiper": {  # sort de la poche en tournant 1,5 tour autour de l'index (anneau)
            "duree": 0.95,
            "Arme": [k(0.0, (0.12, -0.6, 0.1), (-30, 10, 20)), k(0.35, (0, 0.02, 0), (2, 0, 0), "sortie"), k(0.95)],
            "Corps": {"pivot": "Anneau", "cles": [k(0.0, Z, (0, 0, 540)), k(0.75, Z, (0, 0, -8), "sortie"),
                                                  k(0.95, Z, Z, "doux")]},
        },
        "Inspection": {
            "duree": 4.6,
            "Arme": [k(0.0), k(0.5, (-0.12, 0.10, 0.12), (10, -35, 30)), k(1.3, (-0.13, 0.11, 0.12), (12, -38, 32)),
                     k(2.4, (-0.10, 0.10, 0.12), (8, -30, 26)), k(3.0, (-0.06, 0.06, 0.10), (-6, 30, -65)),
                     k(3.8, (-0.06, 0.06, 0.10), (-8, 32, -68)), k(4.6)],
            "Corps": {"pivot": "Anneau", "cles": [k(0.0), k(1.3), k(2.2, Z, (0, 0, -720), "doux"), k(2.4, Z, (0, 0, -725)),
                                                  k(3.6, Z, (0, 0, -725)), k(4.2, Z, (0, 0, -1080), "doux"), k(4.6, Z, (0, 0, -1080))]},
        },
        "Attaque": {
            "duree": 0.45,
            "Arme": [k(0.0), k(0.08, (0.15, 0.05, 0.05), (10, -25, -20), "sortie"),
                     k(0.22, (-0.35, -0.12, -0.15), (-15, 45, 40), "sortie"), k(0.45)],
        },
        "Attaque2": {
            "duree": 0.5,
            "Arme": [k(0.0), k(0.09, (-0.12, 0.08, 0.05), (12, 30, 25), "sortie"),
                     k(0.24, (0.30, -0.15, -0.12), (-20, -40, -35), "sortie"), k(0.5)],
        },
        "AttaqueLourde": {  # coup d'estoc avec tour de lame
            "duree": 0.85,
            "Arme": [k(0.0), k(0.18, (0.05, 0.05, 0.25), (15, -10, -10)), k(0.34, (-0.05, -0.02, -0.55), (-8, 5, 5), "sortie"),
                     k(0.85)],
            "Corps": {"pivot": "Anneau", "cles": [k(0.0), k(0.10), k(0.30, Z, (0, 0, 360), "sortie"), k(0.85, Z, (0, 0, 360))]},
        },
    },
}


# ---------------------------------------------------------------- génération Lua
def _lua_key(key):
    t, p, r, e = key
    return "{%.3f, V(%.3f, %.3f, %.3f), V(%.1f, %.1f, %.1f), \"%s\"}" % (t, *p, *r, e)


def _lua_track(track, indent):
    if isinstance(track, dict):
        inner = (",\n" + indent + "\t").join(_lua_key(c) for c in track["cles"])
        return "{ pivot = \"%s\", cles = {\n%s\t%s,\n%s} }" % (track["pivot"], indent, inner, indent)
    inner = (",\n" + indent + "\t").join(_lua_key(c) for c in track)
    return "{ cles = {\n%s\t%s,\n%s} }" % (indent, inner, indent)


def lua_table():
    out = []
    for weapon, anims in ANIMS.items():
        out.append("\t%s = {" % weapon)
        for name, a in anims.items():
            out.append("\t\t%s = {" % name)
            out.append("\t\t\tduree = %.3f," % a["duree"])
            ev = ", ".join("{%.3f, \"%s\"}" % e for e in a.get("evenements", []))
            out.append("\t\t\tevenements = { %s }," % ev)
            for tr in ("Arme", "Chargeur", "Levier", "Gachette", "Corps"):
                if tr in a:
                    out.append("\t\t\t%s = %s," % (tr, _lua_track(a[tr], "\t\t\t")))
            out.append("\t\t},")
        out.append("\t},")
    return "\n".join(out)


def write_lua(template, dest):
    src = open(template, encoding="utf-8").read()
    open(dest, "w", encoding="utf-8").write(src.replace("--@@ANIMS@@", lua_table()))


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, "..", ".."))
    write_lua(os.path.join(root, "scripts", "templates", "AnimationsRealistes.lua"),
              os.path.join(root, "roblox", "AnimationsRealistes.lua"))
    print("roblox/AnimationsRealistes.lua écrit")
