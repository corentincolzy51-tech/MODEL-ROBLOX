# Intégration des skins Rare / Épique / Légendaire — VANTA AR-01 (test)

Fiche pour l'IA qui modifie les scripts dans Roblox Studio. Elle répond au briefing
`BRIEFING_SKINS_RARES.md`. Les 3 skins de test sont :

| Skin | Rareté | Dossier | Effet |
|---|---|---|---|
| `Phantom Pulse` | Rare | `Armes › Phantom › Rare` | 16 segments néon parcourus par une onde de lumière ; éclat au tir ; les segments se rallument un à un pendant le rechargement |
| `Phantom Inferno` | Épique | `Armes › Phantom › Épique` | fissures de lave qui pulsent et scintillent, braises qui montent, lueur orange ; gerbe d'étincelles au tir ; fumée au rechargement |
| `Phantom Apex` | Légendaire | `Armes › Phantom › Légendaire` | noyau d'énergie qui pulse (démarrage en clignotant à l'équipement), 3 anneaux hexagonaux qui tournent autour du canon (plus vite au tir) ; anneau d'énergie à la bouche ; **inspection (F)** ; **effet d'élimination** (colonne de lumière, onde au sol, éclats) |

---

## 1. Fichiers à mettre dans Studio

1. **`roblox/EffetsSkins.lua`** → nouveau **ModuleScript** `ReplicatedStorage › Modules › EffetsSkins`.
   Tout le code des effets est dedans (rien à ajouter au niveau principal d'ArmeFPS).
2. **Les 3 FBX** (`weapons/VANTA_AR-01/Skins_AR-01_RareEpiqueLegendaire_FBX.zip`) : importer
   (Scale Unit = Stud), sélectionner les 3 modèles, coller **`roblox/InstallerSkinsPhantom.lua`**
   dans la barre de commande. Le script d'installation :
   - range chaque skin dans le dossier de sa rareté et le nomme `Phantom Pulse` / `Phantom Inferno` / `Phantom Apex` ;
   - reprend le Root de `Phantom P` (cherché aussi dans les sous-dossiers, ex. `Base`) avec tous ses repères ;
   - pose les attributs : `Effet`, `NeonAnime`, `CouleurTraceur`, `CouleurFlamme` (+ `Inspection` et
     `EffetElimination` pour Apex) et le tag CollectionService **`EffetSkin`** ;
   - met les néons à 60 % de luminosité.

Le module repère tout seul les copies du skin (vue FPS dans la caméra, arme `ArmeTP_Phantom` en main
des personnages) grâce au tag `EffetSkin`, qui est copié avec le modèle. Il anime les néons chaque
image et ajoute les braises/lumières sur chaque copie : **aucun code** n'est nécessaire pour les
effets permanents, y compris vus par les autres joueurs.

---

## 2. Lignes à ajouter dans les scripts existants

Toutes les lignes sont **à l'intérieur de fonctions existantes** et ne créent **aucune nouvelle
variable `local` au niveau principal** d'ArmeFPS (limite des 200 registres). Remplacer
`ReplicatedStorage` par le nom déjà utilisé dans le script si besoin.

### ArmeFPS (LocalScript)

**a) `local function tirer()`** — juste après l'appel à `tracer(reperes.Bouche.WorldPosition, cible)` :
```lua
require(ReplicatedStorage.Modules.EffetsSkins).AuTir(modeleArme, arme, reperes.Bouche.WorldPosition, cible)
```

**b) `local function tracer(depart, arrivee)`** — remplacer la couleur fixe `Color3.fromRGB(255, 225, 140)` par :
```lua
(modeleArme and modeleArme:GetAttribute("CouleurTraceur")) or Color3.fromRGB(255, 225, 140)
```

**c) `local function equiper(perso)`**
- couleur de la flamme (`nouvellePiece(... Color3.fromRGB(255, 200, 90))`) et de sa `PointLight` `Lumiere` :
```lua
(modeleArme and modeleArme:GetAttribute("CouleurFlamme")) or Color3.fromRGB(255, 200, 90)
```
- à la fin de la fonction, une fois `arme` créée :
```lua
require(ReplicatedStorage.Modules.EffetsSkins).AEquipement(modeleArme, arme)
```

**d) `local function activerArme(n)`** — juste après `jouerSon("Equiper")` :
```lua
if n == 1 then require(ReplicatedStorage.Modules.EffetsSkins).AEquipement(modeleArme, arme) end
```

**e) `local function lancerRecharge()`** — au début (3e argument = durée de l'animation de
rechargement en secondes, par ex. le temps de la dernière image clé de `animationRecharge`) :
```lua
require(ReplicatedStorage.Modules.EffetsSkins).AuRechargement(modeleArme, arme, animationRecharge[#animationRecharge][1])
```
(si la table n'a pas cette forme, mettre directement la durée, ex. `2.2`).

**f) `miseAJour(dt)`** — modifier la ligne existante (pas de nouvelle variable) :
```lua
local decalage = decalageChangement * pose * bob * require(ReplicatedStorage.Modules.EffetsSkins).DecalageInspection(dt, recharge or changement)
```
La touche **F** est gérée par le module. L'inspection ne démarre que si le skin a l'attribut
`Inspection` ; elle s'arrête au tir, au rechargement, au changement d'arme, en visée (`Vise`),
dans les menus (`MenuOuvert`) et au lobby (`Lieu == "Lobby"`). Si le sprint a sa propre variable,
l'ajouter dans le 2e argument : `recharge or changement or sprint`.

### EffetsAutresJoueurs (LocalScript)

Dans `Remotes.EffetTir.OnClientEvent:Connect(function(perso, fin) ... end)` :
- couleurs du traceur et de la flamme : lire `modeleArmeDe(perso):GetAttribute("CouleurTraceur")` /
  `("CouleurFlamme")` avec la couleur actuelle en secours (comme dans ArmeFPS) ;
- éclat des néons de l'arme vue en main, à la fin du gestionnaire :
```lua
require(ReplicatedStorage.Modules.EffetsSkins).AuTir(modeleArmeDe(perso), perso:FindFirstChild("ArmeTP_Phantom"), boucheDe(perso), fin)
```
- (facultatif) rechargement vu par les autres, là où `DebutRecharge` est écouté :
```lua
require(ReplicatedStorage.Modules.EffetsSkins).AuRechargement(nil, perso:FindFirstChild("ArmeTP_Phantom"), 2.2)
```

### Combat (Script serveur) — pour l'effet d'élimination

Dans `local function surMort(modele, humanoid)`, ajouter ces 3 champs dans la table envoyée par
`Remotes.Elimination:FireAllClients({...})` :
```lua
tueurId = tueur and tueur.UserId,
position = (modele:FindFirstChild("HumanoidRootPart") or modele.PrimaryPart).Position,
skin = tueur and tueur:GetAttribute("Skin_Phantom"),
```
(pour l'instant seulement la Phantom ; plus tard : `"Skin_" .. <arme de l'élimination>`).
Le module écoute `Remotes.Elimination` lui-même et joue l'effet si le skin du tueur a l'attribut
`EffetElimination` ; le fil des éliminations d'InterfacePartie ne change pas.

### Vitre du viseur (bug déjà noté)

Là où la vitre devient transparente en visée (`Body_Cyan`), accepter aussi les vitres des skins :
```lua
nom == "Body_Cyan" or nom:match("^Body_Verre")
```

---

## 3. À vérifier pendant le test

- [ ] Les 3 skins apparaissent dans le menu K avec la bonne couleur de rareté.
- [ ] Pulse : l'onde parcourt les segments vers le canon ; éclat au tir ; rallumage pendant le rechargement.
- [ ] Inferno : la lave pulse, les braises montent (vue FPS et arme en main d'un autre joueur), étincelles au tir.
- [ ] Apex : le noyau clignote puis s'allume à l'équipement ; les anneaux tournent en vue FPS (dans la main
      des autres ils sont soudés : ils brillent sans tourner, c'est voulu) ; F lance l'inspection ;
      une élimination déclenche la colonne de lumière chez tous les joueurs.
- [ ] Traceur et flamme ont la couleur du skin (aussi vus par les autres).
- [ ] Rien ne joue au lobby. Pas de perte d'images sur mobile.
- [ ] Taille des braises correcte en vue FPS (copie ×1,3) : le module multiplie leur taille par
      `GetScale()` de la copie.

**Scripts modifiés** (à noter pour la synchronisation PC ↔ Studio) : `ArmeFPS`, `EffetsAutresJoueurs`,
`Combat`, + le nouveau module `EffetsSkins`.

---

## 4. Prompt pour l'IA du son (sons complets des 3 skins)

```
Jeu Roblox FPS, arme VANTA AR-01. Trois nouveaux skins ont un dossier « Sons » avec ces noms exacts :
Tir, Equiper, ClicVide, Levier, ChargeurSort, ChargeurEntre. Garde ces noms, change seulement le SoundId
et les réglages. Le jeu joue chaque son avec ±5 % de hauteur au hasard : ne rajoute pas de variation.
Sons courts et lisibles en combat, volume proche des sons d'origine.

1. Phantom Pulse (Rare) — électro / synthwave : Tir = coup sec + « bwip » synthétique pulsé ;
   Equiper = petit arpège électronique montant ; Levier = clic électronique ; ChargeurSort / ChargeurEntre
   = glissement métallique + bip de charge ; ClicVide = petit bip grave.
2. Phantom Inferno (Épique) — feu / magma : Tir = détonation grave + souffle de flamme court ;
   Equiper = allumage de brasier (« fwoosh ») ; Levier = métal chaud qui claque ; ChargeurSort = grésillement
   de braises ; ChargeurEntre = clang lourd + sifflement de vapeur ; ClicVide = braise qui crépite.
3. Phantom Apex (Légendaire) — haute technologie / énergie : Tir = détonation nette + « zing » d'énergie
   cristallin ; Equiper = démarrage de réacteur (montée en fréquence + verrouillage) ; Levier = servomoteur
   bref ; ChargeurSort = décompression pneumatique ; ChargeurEntre = verrouillage magnétique + bourdonnement
   qui remonte ; ClicVide = bip d'erreur doux.
Donne la liste : skin -> son -> SoundId -> réglages.
```
