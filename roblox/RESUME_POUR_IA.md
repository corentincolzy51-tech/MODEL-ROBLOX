# Résumé pour l'IA Roblox — état du projet skins VANTA

Tout ce qui suit est **déjà installé dans Studio**. À lire avant de toucher aux armes ou aux skins.

## 1. Ce qui existe dans le jeu

- **4 armes** : `Phantom` (AR-01), `Deagle` (DE-50), `Sniper` (SR-7), `Couteau`.
  La référence de chaque arme s'appelle `<Arme> P` (ex. `Phantom P`, dans le dossier `Base`).
- **Dossiers de rareté** sous chaque arme : `Base`, `Commun`, `Peu commun`, `Rare`, `Épique`, `Légendaire`.
- **Peu commun** (les 4 armes) : Sakura, Graffiti, Royal, Toxic, Cryo, Nebuleuse, Vortex, Arcade, Fantome.
  Ces modèles sont nommés automatiquement `<Arme> S 1`, `<Arme> S 2`… (le nom du skin est dans le dossier/attribut, pas dans le nom).
- **Test Rare / Épique / Légendaire (Phantom seulement)** :
  - `Phantom Pulse` (Rare) : environ 45 segments néon cyan parcourus par une onde de lumière ;
  - `Phantom Inferno` (Épique) : arme volcanique, lave qui pulse, braises, flammes à la bouche ;
  - `Phantom Apex` (Légendaire) : fusil à rails, faisceau d'énergie, 4 bobines, inspection F, effet d'élimination.

## 2. Structure d'un skin (identique à `Phantom P`)

- `Body_<Couleur>`, `Magazine_<Couleur>`, `Trigger`, `ChargingHandle_<Couleur>`.
- Un `<Groupe>_Contour` noir par groupe (contour cartoon). Ne pas le supprimer.
- `Root` cloné depuis la référence avec tous ses repères (`Bouche`, `Ejection`…), même position relative.
- Dossier `Sons` copié depuis la référence (noms : Tir, Equiper, ClicVide, Levier, ChargeurSort, ChargeurEntre).
- La vitre du viseur s'appelle `Body_Verre…` (en plus de `Body_Cyan` sur l'arme de base).
- Néons des skins à effets : pièces `<Groupe>_<NeonAnime>NN` (segments numérotés 01, 02…) ;
  l'index `00` = le faisceau d'Apex (`Body_ApexNoyau00`).

## 3. Attributs posés sur les skins à effets (+ tag CollectionService `EffetSkin`)

| Skin | Effet | NeonAnime | CouleurTraceur | CouleurFlamme | Autres |
|---|---|---|---|---|---|
| Pulse | `Pulse` | `CyanPulse` | 90, 230, 255 | 120, 220, 255 | — |
| Inferno | `Inferno` | `Lave` | 255, 140, 40 | 255, 110, 25 | — |
| Apex | `Apex` | `ApexNoyau` | 170, 240, 255 | 150, 230, 255 | `Inspection = true`, `EffetElimination = "Apex"` |

Les skins Peu commun n'ont aucun attribut d'effet.

## 4. Module `ReplicatedStorage › Modules › EffetsSkins` (ModuleScript, client)

Tout le code des effets est ici. Il trouve tout seul les copies taguées `EffetSkin`
(vue FPS ×1,3 et `ArmeTP_<Arme>` en main des personnages) et anime les néons à chaque image.
API :
- `AuTir(modeleArme, arme, depart, cible)` : éclat / gerbe de feu / anneau d'énergie.
- `AuRechargement(modeleArme, arme, duree)` : rallumage (Pulse), fumée (Inferno).
- `AEquipement(modeleArme, arme)` : démarrage (clignotement Apex).
- `DecalageInspection(dt, bloque) -> CFrame` : inspection touche F (seulement si attribut `Inspection`).
- `AElimination(info)` : branché automatiquement sur `Remotes.Elimination`.
Rien ne joue si `Lieu == "Lobby"` ; l'inspection est bloquée par `Vise`, `MenuOuvert`, le tir, la recharge, le changement d'arme.

## 5. Lignes ajoutées dans les scripts existants

**ArmeFPS** (toutes à l'intérieur de fonctions existantes, aucun `local` ajouté au niveau principal) :
- `tirer()` : après `tracer(...)` → `require(ReplicatedStorage.Modules.EffetsSkins).AuTir(modeleArme, arme, reperes.Bouche.WorldPosition, cible)`
- `tracer()` : couleur = `(modeleArme and modeleArme:GetAttribute("CouleurTraceur")) or Color3.fromRGB(255, 225, 140)`
- `equiper()` : flamme + `PointLight` = `CouleurFlamme` (même secours), et à la fin `...EffetsSkins).AEquipement(modeleArme, arme)`
- `activerArme(n)` : après `jouerSon("Equiper")` → `if n == 1 then ...AEquipement(modeleArme, arme) end`
- `lancerRecharge()` : au début → `...AuRechargement(modeleArme, arme, <durée>)`
- `miseAJour(dt)` : `local decalage = decalageChangement * pose * bob * ...DecalageInspection(dt, recharge or changement)`
- Vitre en visée : `nom == "Body_Cyan" or nom:match("^Body_Verre")`

**EffetsAutresJoueurs** : couleurs traceur/flamme lues sur `modeleArmeDe(perso)` + à la fin du gestionnaire `EffetTir` :
`...AuTir(modeleArmeDe(perso), perso:FindFirstChild("ArmeTP_Phantom"), boucheDe(perso), fin)`

**Combat** (serveur), `surMort` : 3 champs ajoutés au `Remotes.Elimination:FireAllClients({...})` :
`tueurId`, `position` (HumanoidRootPart du mort), `skin = tueur and tueur:GetAttribute("Skin_Phantom")`.

**Scripts modifiés** : `ArmeFPS`, `EffetsAutresJoueurs`, `Combat` + nouveau module `EffetsSkins`.

## 6. Règles à respecter

- **ArmeFPS est à la limite des 200 variables locales** : ne jamais y ajouter de `local` ou de boucle au niveau principal.
  Tout nouvel effet va dans le module `EffetsSkins` (ou dans un nouveau module).
- Ne pas renommer les pièces (`Body_*`, `_Contour`, `*_<NeonAnime>NN`), le `Root`, ses repères ni les sons :
  le module et les scripts s'appuient sur ces noms.
- Les nouveaux skins sont installés avec `InstallerSkinsPhantom.lua` (barre de commande) : il gère nom, dossier,
  taille, placement, Root, sons, attributs et tag. Ne pas les placer à la main.
- Pour l'instant `skin` = `Skin_Phantom` uniquement ; plus tard : `"Skin_" .. <arme de l'élimination>`.

## 7. À vérifier en test (en attente de retours)

- Les 3 skins rares apparaissent dans le menu K avec la bonne couleur de rareté.
- Néons animés en vue FPS **et** dans la main des autres joueurs ; traceur et flamme à la couleur du skin.
- Apex : bobines qui tournent en vue FPS (dans la main des autres elles brillent sans tourner, c'est voulu),
  F = inspection, élimination = colonne de lumière vue par tous.
- Taille des braises / particules correcte après la mise à l'échelle ×1,3.
- Rien ne joue au lobby ; pas de chute d'images sur mobile.
- Le son n'est pas prioritaire pour l'instant.
