# MODEL-ROBLOX

Modèles 3D (Blender) pour le jeu Roblox, générés par script.

## Convention des armes

- Canon vers **+X**, haut vers **+Z**, origine sur la **poignée**
- Pièces séparées : `Body`, `Magazine`, `Trigger`, `ChargingHandle`
- Un seul matériau par objet (une couleur, ou une texture pour les skins)

| Arme | Studs (L × H × É) | Blender (m) |
|---|---|---|
| VANTA AR-01 | 3,616 × 1,343 × 0,369 | 1,096 × 0,407 × 0,112 |
| VANTA SR-7 (sniper) | 4,862 × 1,329 × 0,760 | 1,473 × 0,403 × 0,230 |
| VANTA DE-50 (deagle) | 1,250 × 0,856 × 0,660 | 0,379 × 0,259 × 0,200 |
| Couteau | 1,625 × 0,426 × 0,200 | 0,387 × 0,101 × 0,048 |

## Contenu

```
weapons/VANTA_AR-01/Sakura/
  VANTA_AR-01_Sakura.fbx          <- à importer dans Roblox Studio (textures intégrées)
  VANTA_AR-01_Sakura.blend        <- fichier Blender (textures empaquetées)
  VANTA_AR-01_Sakura_preview.png  <- rendu d'aperçu
  textures/
    VANTA_AR-01_Sakura_Body.png       (1024², TextureID du Body)
    VANTA_AR-01_Sakura_Magazine.png   (1024², TextureID du Magazine)
    sakura_design_sideview.png        (dessin source, vue de côté)
scripts/
  vanta_ar01.py          <- géométrie de l'AR-01
  skin_sakura.py         <- dessin de la texture Sakura
  build_ar01_sakura.py   <- construit, bake, exporte
```

## Import dans Roblox Studio

1. **Avatar > 3D Importer** (ou *Import 3D*), choisir `VANTA_AR-01_Sakura.fbx`.
2. Les 4 MeshParts arrivent avec leur texture. Si une texture manque, importer le PNG
   et le mettre dans `TextureID` de la MeshPart (`Body` ou `Magazine`).
3. Mettre `Color` des MeshParts texturées en blanc pour ne pas teinter la texture.

## Regénérer

```bash
pip install bpy      # Blender en module Python
python3 scripts/build_ar01_sakura.py
```
