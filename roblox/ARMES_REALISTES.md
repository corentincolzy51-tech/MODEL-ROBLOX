# Armes réalistes VANTA : installation et animations

Ce sont 4 nouvelles armes de haute qualité, sans contour cartoon. Chacune est faite de pièces usinées, avec des textures PBR cuites : couleur, rugosité, métal et normales.

| Modèle Roblox | Arme | Fichier |
|---|---|---|
| `Phantom R` | fusil rapide (plateforme AR, viseur holographique) | `weapons/Realiste/Phantom/Phantom_Realiste.fbx` |
| `Deagle R` | pistolet .50 (culasse et canon en inox) | `weapons/Realiste/Deagle/Deagle_Realiste.fbx` |
| `Sniper R` | fusil de précision à verrou (châssis FDE, lunette 5-25×56) | `weapons/Realiste/Sniper/Sniper_Realiste.fbx` |
| `Couteau R` | karambit (acier satiné, plaquettes G10) | `weapons/Realiste/Couteau/Couteau_Realiste.fbx` |

Tous les FBX d'un coup : `weapons/Realiste/Armes_Realistes_FBX.zip`

## 1. Importer

1. Ouvrir **Accueil › Importer 3D** et choisir un FBX.
2. Régler **Scale Unit = Stud** et laisser l'importateur charger les textures (elles sont dans le FBX).
3. Sélectionner les modèles importés (« Phantom Realiste », « Deagle Realiste »…).
4. Coller **`roblox/InstallerArmesRealistes.lua`** dans la barre de commande, puis Entrée.

Le script range chaque arme dans `ReplicatedStorage › Armes › <Arme> › Base` sous le nom `<Arme> R`. Il garde la même structure que `<Arme> P` :

- Corps / Chargeur / Gachette / Levier ;
- le Root et tous ses repères ;
- les Sons et les attributs.

Il fait aussi ceci :

- il met l'arme à la longueur de la référence et place la poignée là où était celle de l'ancienne arme ;
- il recentre le verre du viseur sur `Body_Cyan` ;
- il ajoute au Root les repères d'animation `Anneau` (karambit) et `Verrou` (sniper).

**Textures :**

- Si l'importateur crée une **SurfaceAppearance** (PBR), le rendu est complet.
- Sinon, chaque MeshPart a déjà sa `TextureID` (couleur avec ombrage cuit). Pour le PBR complet, il faut une SurfaceAppearance par pièce avec les 4 images du dossier `textures/` : `_Couleur` = ColorMap, `_Normal` = NormalMap, `_Rugosite` = RoughnessMap, `_Metal` = MetalnessMap.

**Pièces particulières :**

| Pièce | Rôle |
|---|---|
| `Body_Verre` | vitres du viseur holographique : Glass transparent (même règle que les skins : `^Body_Verre`) |
| `Body_Reticule` | réticule rouge (anneau + point) entre les deux vitres, en Neon |
| `Body_Tritium` | points verts des organes de visée du deagle |
| `Body_Lentille` | lentilles de la lunette du sniper |
| Levier | fusil : poignée en T · deagle : culasse · sniper : verrou + poignée de culasse |
| Chargeur du deagle | contient une cartouche en laiton visible quand le chargeur sort |

## 2. Animations : module `AnimationsRealistes`

Il faut copier `roblox/AnimationsRealistes.lua` dans un nouveau **ModuleScript** `ReplicatedStorage › Modules › AnimationsRealistes`.

| Arme | Animations |
|---|---|
| Phantom | Tir, Recharge, RechargeVide (levier tiré), Equiper, Inspection |
| Deagle | Tir (culasse qui recule), Recharge, RechargeVide (culasse relâchée), Equiper, Inspection (contrôle de la chambre) |
| Sniper | Tir, **Culasse** (réarmement après chaque tir : lever, tirer, pousser, rabattre), Recharge, Equiper, Inspection |
| Couteau | Equiper (1,5 tour autour de l'anneau), Inspection (tours de lame), Attaque, Attaque2, AttaqueLourde |

Les aperçus animés sont dans `weapons/Realiste/<Arme>/anim_*.gif`.

Voici comment l'utiliser dans ArmeFPS. Tout se fait à l'intérieur des fonctions existantes, **sans nouvelle `local` au niveau principal** (limite des 200 variables).

```lua
-- démarrer (ex. lancerRecharge / activerArme / touche F) :
etat.anim = require(ReplicatedStorage.Modules.AnimationsRealistes).Jouer("Phantom", "Recharge", arme)

-- chaque image, dans miseAJour(dt), si etat.anim existe :
local decal, evenements, fini = etat.anim:Avancer(dt)
-- 1) multiplier decal dans la chaîne : decalageChangement * pose * bob * decal
-- 2) evenements : "ChargeurSort", "ChargeurEntre", "Rempli", "Levier", "LevierOuvre", "LevierFerme", "Douille"
--    -> jouerSon(...) et remplir le chargeur sur "Rempli"
-- 3) après le placement de l'arme : etat.anim:AppliquerPieces()
-- 4) if fini then etat.anim:Remettre() etat.anim = nil end
```

`etat` est une table qui existe déjà dans le script (ou un champ d'une table existante) : aucune nouvelle variable locale.

`Jouer` renvoie `nil` si l'animation n'existe pas pour l'arme. On peut donc n'activer ces animations que pour les modèles réalistes : `modeleArme:GetAttribute("Realiste")`.

**Repères :**

- La piste `Arme` est dans le même repère que la piste d'inspection d'EffetsSkins : X droite, Y haut, Z vers la caméra, angles en degrés.
- Les pièces sont dans le repère de l'arme : X vers le canon, Y haut, Z côté droit. Le module le calcule tout seul à partir des pièces.

Si une animation va dans le mauvais sens dans le jeu, il suffit d'inverser le signe dans `scripts/real/anims.py`, de relancer `python3 scripts/real/anims.py`, puis de recoller le module.

## 3. Refaire / modifier

```
python3 scripts/real/build_real.py rifle deagle sniper karambit   # modèles + textures + aperçus + FBX + installateur
python3 scripts/real/build_real.py rifle --nobake --fast          # aperçu rapide de la géométrie
python3 scripts/real/anims.py                                     # module d'animations
python3 scripts/real/preview_anim.py Phantom:Recharge             # GIF d'une animation
```

Fichiers sources :

| Fichier | Contenu |
|---|---|
| `scripts/real/kit.py` | volumes, découpes, biseaux |
| `scripts/real/materials.py` | matériaux PBR et cuisson |
| `rifle.py`, `deagle.py`, `sniper.py`, `karambit.py` | les armes |
