# MODEL-ROBLOX

Modèles 3D (Blender) pour le jeu Roblox, générés par script.

## Convention des armes

- Canon vers **+X**, haut vers **+Z**, origine sur la **poignée**
- Même structure que `Phantom P` dans Roblox :

```
Phantom Sakura (Model)
├── Corps     Body_Sakura, Body_Blanc, Body_Rose, Body_Noir, Body_Verre, Body_Contour
├── Chargeur  Magazine_Sakura, Magazine_Rose, Magazine_Noir, Magazine_Contour
├── Gachette  Trigger, Trigger_Contour
├── Levier    ChargingHandle_Blanc, ChargingHandle_Rose, ChargingHandle_Contour
└── Root      repère sur la poignée
```

- Une pièce = une couleur (`*_Sakura` = texture de fleurs). `*_Contour` = contour noir
  cartoon (coque inversée, visible uniquement de l'extérieur).

| Arme | Studs (L × H × É) | Blender (m) |
|---|---|---|
| VANTA AR-01 | 3,616 × 1,343 × 0,369 | 1,096 × 0,407 × 0,112 |
| VANTA SR-7 (sniper) | 4,862 × 1,329 × 0,760 | 1,473 × 0,403 × 0,230 |
| VANTA DE-50 (deagle) | 1,250 × 0,856 × 0,660 | 0,379 × 0,259 × 0,200 |
| Couteau | 1,625 × 0,426 × 0,200 | 0,387 × 0,101 × 0,048 |

**Échelle :** les `.blend` sont en mètres (tableau ci-dessus). Les `.fbx` sont exportés
avec **1 unité = 1 stud**, à importer avec *Scale Unit = Stud*. (Un FBX Blender par
défaut est lu par Roblox comme 1 m = 100 studs : c'est ce qui donnait une arme géante.)

## Contenu

```
weapons/VANTA_AR-01/Sakura/
  Phantom_Sakura.fbx           <- à importer dans Roblox Studio
  Phantom_Sakura.blend         <- fichier Blender (textures empaquetées)
  Phantom_Sakura_preview.png   <- rendu d'aperçu
  textures/                    <- textures 1024 px + dessin source
roblox/
  InstallerPhantomSakura.lua   <- à coller dans la barre de commande après l'import
scripts/
  vanta_ar01.py                <- géométrie de l'AR-01 (pièces, couleurs, contours)
  skin_sakura.py               <- dessin de la texture Sakura
  build_ar01_sakura.py         <- construit, bake, exporte
  tools/fbx_inspect.py         <- vérifie la taille réelle (en studs) d'un FBX
```

## Import dans Roblox Studio

1. **Importer 3D** → `Phantom_Sakura.fbx`, *Scale Unit* = **Stud**.
2. Sélectionner le modèle importé, coller `roblox/InstallerPhantomSakura.lua` dans la
   **barre de commande** (Affichage > Barre de commande), Entrée. Le script :
   - range les pièces, met les couleurs, verre du viseur transparent ;
   - met l'arme à la longueur de `Phantom P` et la **superpose** à `Phantom P`
     (canon, dessus et crosse au même endroit), Root placé comme celui de `Phantom P` ;
   - centre le verre du viseur sur celui de `Phantom P` (`Body_Cyan`) pour la visée ;
   - reprend Sons / attributs / réglages / soudures de `Phantom P` ;
   - nomme le skin **Phantom S 1** (ou 2, 3… si le nom est pris) dans
     `ReplicatedStorage.Armes.Phantom`.
3. Pour recaler un skin déjà installé : le sélectionner et relancer le script (pas besoin de
   réimporter). Un skin déjà nommé « Phantom S N » garde son nom.
4. La Sortie affiche la taille de `Phantom P`, la position de son Root et l'écart avec la
   poignée du skin : utile pour ajuster le modèle.
5. Si une partie Sakura reste grise : la texture est en modération ou n'a pas été importée.
   Importer le PNG de `textures/` et le mettre en `TextureID` (ou `SurfaceAppearance.ColorMap`).

## Regénérer

```bash
pip install bpy      # Blender en module Python
python3 scripts/build_ar01_sakura.py
python3 scripts/tools/fbx_inspect.py weapons/VANTA_AR-01/Sakura/Phantom_Sakura.fbx
```
