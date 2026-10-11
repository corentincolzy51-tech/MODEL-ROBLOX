# VANTA — fiche pour créer les skins Rare / Épique / Légendaire (test sur la VANTA AR-01 « Phantom »)

À donner à l'assistant qui écrit les effets. Tout ce qui suit décrit le jeu tel qu'il est (2026-10-11).

---

## 1. Réponses aux 3 questions

### a) Les scripts de l'arme
L'arme n'est pas un Tool Roblox : c'est un système maison, réparti en 4 scripts + 2 modules.

| Script | Type | Rôle |
|---|---|---|
| `StarterPlayerScripts › Armes › ArmeFPS` | **LocalScript** | vue 1re personne : modèle de l'arme dans la caméra, tir, recul, rechargement, visée, équipement, son |
| `StarterPlayerScripts › Armes › EffetsAutresJoueurs` | **LocalScript** | ce qu'on voit des AUTRES joueurs : flamme, traceur, son 3D de leur tir, pose des bras |
| `ServerScriptService › Combat › Combat` | **Script** (serveur) | vérifie les tirs, dégâts, éliminations, arme visible dans la main des personnages (3e personne) |
| `StarterPlayerScripts › UI › InterfacePartie` | **LocalScript** | fil des éliminations, marqueur de touche |
| `ReplicatedStorage › Modules › Skins` | **ModuleScript** | trouve le modèle du skin choisi par un joueur |
| `ReplicatedStorage › Modules › PoseArmes` | **ModuleScript** | pose des bras vue de l'extérieur |

**RemoteEvents** (`ReplicatedStorage › Remotes`) :
- `Tir` : client → serveur ;
- `EffetTir` : serveur → les autres clients ;
- `Recharge`, `AnnulerRecharge`, `ChangerArme`, `ChoisirSkin` : client → serveur ;
- `Elimination` : serveur → tous les clients ;
- `Touche` : serveur → le tireur.

### b) Les animations
**Aucune Animation Roblox.** Tout est fait par script, en déplaçant les pièces.
- L'arme FPS est un Model placé chaque image devant la caméra (`arme:PivotTo(...)`). Les sous-modèles `Gachette`, `Chargeur` et `Levier` sont déplacés aussi.
- Les animations (rechargement, lancer du couteau…) sont des tables d'images clés `{temps, valeur}` lues par `lireValeur()`. Exemples dans ArmeFPS : `animationRecharge`, `ANIM_LANCER`, `ANIM_CULASSE`.
- Les bras de la vue FPS sont 2 pièces placées par calcul sur les repères de l'arme.

👉 **L'inspection doit être faite de la même façon** : une piste de décalage (position + rotation) appliquée à l'arme pendant quelques secondes (voir § 3).

### c) Touche d'inspection
**F est libre.** Touches déjà prises :
- jeu : Z/Q/S/D ou W/A/S/D, Espace, Maj, C, R, 1, 2, clics de souris ;
- menus : T (test), B (classe), P (paramètres), K (skins).

---

## 2. Comment marche un skin (À RESPECTER)

**Rangement** : `ReplicatedStorage › Armes › Phantom ›` sous-dossiers de rareté `Base`, `Commun`, `Peu commun`, `Rare`, `Épique`, `Légendaire`. Il suffit de mettre le modèle dans `Rare` / `Épique` / `Légendaire` :
- il apparaît tout seul dans le menu Skin (touche K), avec la couleur de sa rareté ;
- le serveur l'accepte ;
- tout le monde le voit.

**Un skin = un Model qui garde la structure de `Phantom P`** :
- `Root` = Part invisible, **PrimaryPart**. Elle porte les repères (Attachments) : `MainDroite`, `MainGauche`, `Bouche` (bout du canon), `Ejection`, `Viseur`, `PivotChargeur`, `PriseChargeur`, `PivotGachette`, `PriseLevier`. Il faut les garder **aux mêmes positions** que sur `Phantom P` : les mains et la visée sont calées dessus.
- Sous-modèles **obligatoires** : `Corps`, `Chargeur`, `Gachette`, `Levier`. Le script bouge `Chargeur` (rechargement), `Gachette` et `Levier` (tir).
- Dossier `Sons` avec **ces noms exacts** : `Tir`, `Equiper`, `ClicVide`, `Levier`, `ChargeurSort`, `ChargeurEntre`. Les sons du skin sont joués automatiquement : pour des « sons complets », il suffit de changer les SoundId. Chaque son est joué avec ±5 % de hauteur au hasard.
- **Vitre du viseur** : quand on vise, la pièce `Corps › Body_Cyan` devient transparente pour voir à travers le viseur. **Si le skin n'a pas de pièce nommée `Body_Cyan` sur la vitre, le viseur reste opaque en visée.** C'est déjà le cas des skins Peu commun, dont la vitre s'appelle `Body_Verre…`.
- Toutes les pièces : Anchored, CanCollide / CanQuery / CanTouch = false, Massless.
- **Nom unique** dans le dossier `Phantom` (ex. `Phantom Pulse`, `Phantom Inferno`, `Phantom Apex`).
- **Néons faibles** : pour les pièces en matériau Neon, la luminosité de la couleur (V en HSV) est à 60 % de la valeur pleine sur tous les skins (voulu : sinon ça éblouit).

**Le modèle est copié deux fois en jeu** : tout ce qui est DANS le modèle du skin (Beam, ParticleEmitter, PointLight, Attachments en plus) est donc copié automatiquement.
1. **Vue FPS** (ArmeFPS, fonction `equiper`) : copie dans la caméra, agrandie ×1,3 (`ScaleTo`). Toutes les pièces restent Anchored et sont repositionnées chaque image.
2. **Dans la main du personnage, vue par les autres** (Combat, fonction `copieArme`) : copie agrandie ×1,2, pièces soudées. Le dossier `Sons` est retiré, les **Trail sont coupés** (`Enabled = false`), CanQuery = false.

⚠️ À vérifier : que la taille des particules et la largeur des Beams suivent bien l'agrandissement (`ScaleTo`).

**Au lobby**, l'arme est rangée : la vue FPS est enlevée et le personnage n'a rien en main. Aucun effet ne doit jouer au lobby (`joueur:GetAttribute("Lieu") == "Lobby"`).

**Le skin choisi** :
- attribut du joueur `Skin_Phantom` = nom du modèle ;
- pour obtenir le modèle : `require(ReplicatedStorage.Modules.Skins).modele(joueur, "Phantom")` ;
- pour savoir sa rareté : `Skins.rarete(modele)` → "Rare", "Épique"…

---

## 3. Où brancher chaque effet

Les numéros de ligne sont ceux d'aujourd'hui et peuvent bouger : se fier aux noms de fonction.

### ⚠️ Piège n° 1 : ArmeFPS est à la LIMITE de 200 variables locales de Roblox
Ajouter une seule `local` au niveau principal du script (hors fonction), ou une boucle `for` au niveau principal, le casse : erreur « Out of local registers ». Il ne se lance plus et l'arme disparaît.
👉 **Tout le code des effets doit être dans un ModuleScript séparé**, par exemple `ReplicatedStorage › Modules › EffetsSkins`. ArmeFPS l'appelle **à l'intérieur de ses fonctions existantes**, sans nouvelle variable globale :
```lua
require(ReplicatedStorage.Modules.EffetsSkins).AuTir(modeleArme, arme, reperes.Bouche.WorldPosition, cible)
```
(`require` met le module en cache : l'appeler à chaque tir ne coûte rien.)

### Tir — mon arme (ArmeFPS)
- `local function tirer()` : son `jouerSon("Tir")`, flamme (pièce `flamme`, couleur fixe), douille, rayon, puis `tracer(reperes.Bouche.WorldPosition, cible)`.
- `local function tracer(depart, arrivee)` : le trait de la balle, couleur **fixe** `Color3.fromRGB(255, 225, 140)`.
- La flamme est créée dans `equiper()` (`flamme = nouvellePiece(... Color3.fromRGB(255, 200, 90))`), avec une PointLight `Lumiere`.
- Variables utiles déjà disponibles : `modeleArme` (le modèle du skin dans ReplicatedStorage), `arme` (la copie dans la caméra), `reperes` (Attachments du Root de la copie), `viewmodel`, `camera`, `dossierEffets` (dossier pour les effets temporaires), `fiche` (réglages de l'arme), `armeActive` (1 = arme principale, 2 = couteau).
- 👉 Idée simple pour les couleurs : mettre des **attributs sur le modèle du skin**, par exemple `CouleurTraceur` et `CouleurFlamme` (Color3). Dans `tracer` et `tirer`, lire alors `modeleArme:GetAttribute("CouleurTraceur") or <couleur actuelle>`.

### Tir — vu par les autres (EffetsAutresJoueurs)
- `Remotes.EffetTir.OnClientEvent:Connect(function(perso, fin) ... end)` : flamme + lumière, son 3D, traceur, étincelles. Les couleurs y sont **fixes** aussi.
- `modeleArmeDe(perso)` renvoie déjà le modèle du skin de ce joueur : y lire les mêmes attributs.
- `boucheDe(perso)` donne la position du bout du canon de l'arme en main.
- Les copies en 3e personne s'appellent `ArmeTP_Phantom` dans le personnage.

### Rechargement
- Mon arme : `local function lancerRecharge()` (début). L'animation se lit dans `majFusil()`, avec des événements à des temps donnés : `"ChargeurSort"`, `"ChargeurEntre"` et `"Rempli"` (chargeur plein).
- Annulé : `annulerRecharge()` (escalade) ou `changerArme()`.
- Vu par les autres : le serveur pose l'attribut `DebutRecharge` (heure serveur) sur le **personnage** du joueur → `perso:GetAttributeChangedSignal("DebutRecharge")`.

### Équipement
- Mon arme :
  - `local function equiper(perso)` : création de la vue FPS, à l'apparition et au changement de skin ;
  - `local function activerArme(n)` : sortie de l'arme ou du couteau, avec `jouerSon("Equiper")`.
- Vu par les autres : l'attribut `ArmeActive` du personnage change (1 = VANTA, 2 = couteau, 3 = sniper, 4 = deagle, 0 = rangée).

### Élimination
- Serveur : `local function surMort(modele, humanoid)` dans Combat, puis `Remotes.Elimination:FireAllClients({ tueur = DisplayName, victime = ..., arme = ..., tete = ..., victimeId = ... })`.
- ⚠️ Le message **ne contient ni l'UserId du tueur, ni son skin, ni la position de la victime**. Pour un effet d'élimination légendaire, il faut ajouter dans `surMort` :
  - `tueurId = tueur and tueur.UserId` ;
  - `position = (modele:FindFirstChild("HumanoidRootPart") or modele.PrimaryPart).Position` ;
  - `skin = tueur and tueur:GetAttribute("Skin_Phantom")`.
- Client : `InterfacePartie` écoute déjà `Remotes.Elimination` (fil des éliminations). Un autre LocalScript peut l'écouter aussi pour jouer l'effet.

### Inspection (légendaire, touche F)
- Position de l'arme FPS : dans `miseAJour(dt)`, la ligne
  `local decalage = decalageChangement * pose * bob`
  calcule le décalage appliqué à l'arme, et `majFusil(dt, decalage, ...)` le lui applique.
  👉 Il suffit de multiplier par le décalage d'inspection : `decalage = decalage * EffetsSkins.DecalageInspection(dt)`. Ce CFrame vient d'une piste `{temps, CFrame/valeurs}` dans le module, et vaut `CFrame.new()` quand on n'inspecte pas.
- Les bras suivent l'arme tout seuls.
- À bloquer ou annuler pendant : le tir, le rechargement (variable `recharge`), le changement d'arme (`changement`), la visée (attribut joueur `Vise`), le sprint, les menus (attribut joueur `MenuOuvert`), et au lobby.
- Les touches du jeu sont réglables dans le menu Paramètres (module `Parametres`). Pour un premier test, F en dur suffit, avec `UserInputService.InputBegan` dans le module ou un petit LocalScript.

---

## 4. Ce que je conseille de faire
1. **Un ModuleScript `EffetsSkins`** (ReplicatedStorage › Modules) avec `AuTir`, `AuRechargement`, `AEquipement`, `AElimination`, `DecalageInspection`. Il lit les effets à faire dans des **attributs ou dossiers du modèle du skin**, pour que les futurs skins n'aient besoin d'aucun code.
2. Dans les scripts existants, **seulement quelques lignes d'appel**, à l'intérieur des fonctions citées plus haut.
3. Les effets permanents (Beams qui circulent, braises au repos, noyau lumineux) **directement dans le modèle du skin**. Ils seront copiés dans la vue FPS et dans la main du personnage sans code. Attention : les Trails sont coupés en 3e personne.
4. Tester d'abord le **Rare** (Pulse) : c'est celui qui demande le moins de modifications de scripts.

Scripts à lui donner si besoin : ils sont dans `workspace/fps/` (copie exacte de Studio) :
- `armes/ArmeFPS.client.lua` : gros fichier, ne donner que les fonctions citées ;
- `armes/EffetsAutresJoueurs.client.lua` ;
- `serveur/Combat.server.lua` : fonctions `surMort` et `copieArme` ;
- `modules/Skins.lua`.

## 5. Important pour la suite
Si des scripts sont modifiés dans Studio avec l'autre assistant, **note lesquels**. J'ai une copie de chaque script sur le PC et je l'envoie dans Studio quand je travaille. Sans cette info, je risque d'écraser ses changements : je relirai Studio d'abord.
