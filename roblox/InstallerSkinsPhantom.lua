--[[
	Installe un ou plusieurs skins d'armes VANTA à partir des FBX importés
	(AR-01 « Phantom », DE-50 « Deagle », SR-7 « Sniper », « Couteau »).

	1. Importe les fichiers <Arme>_<Skin>.fbx (Accueil > Importer 3D, « Scale Unit » = Stud).
	   -> ou sélectionne des skins déjà installés pour les recaler.
	2. Sélectionne TOUS ces modèles dans l'Explorer (Ctrl + clic).
	   (les modèles qui ne sont pas des skins, comme Phantom P, sont ignorés)
	3. Colle tout le script dans la barre de commande (Affichage > Barre de commande), puis Entrée.

	L'arme est reconnue par le début du nom du modèle (« Deagle Sakura », « Phantom S 3 »...).
	Elle est rangée dans ReplicatedStorage.Armes.<Arme>, à côté de son modèle de référence
	(« <Arme> P », sinon le premier modèle du dossier qui a un « Corps » et n'est pas un skin).

	Pour chaque modèle, le script :
	  - range les pièces comme la référence : Corps / Chargeur / Gachette / Levier + Root
	  - met les couleurs (une couleur par pièce), le néon et le verre transparent du viseur
	  - met l'arme à la même longueur que la référence et la superpose à elle
	    (même boîte englobante), Root placé comme celui de la référence
	  - centre le verre du viseur / de la lunette sur celui de la référence (Body_Cyan)
	  - copie depuis la référence : Sons, autres objets, attributs, réglages des pièces, soudures
	  - le range dans le dossier de sa rareté (Armes.<Arme>.Peu commun / Rare / Épique /
	    Légendaire, s'il existe) ; un Peu commun s'appelle « <Arme> S N » (premier numéro
	    libre), les autres « <Arme> <Skin> » (ex. « Phantom Pulse »)
	  - skins à effets : pose les attributs (Effet, NeonAnime, CouleurTraceur, CouleurFlamme,
	    Inspection, EffetElimination) et le tag « EffetSkin » lus par le module EffetsSkins
	  - néons à 60 % de luminosité (règle du jeu)

	Fichier généré par scripts/build_skins.py : ne pas modifier les tables à la main.
]]

-- armes : premier mot du nom du modèle -> dossier, référence, longueur (studs),
-- décalage de prise en main (studs, repère de l'arme), groupes
local ARMES = {
	Phantom = { dossier = "Phantom", reference = "Phantom P", longueur = 3.616, decalage = Vector3.new(0.0, 0.0, 0.0), groupes = { Body = "Corps", Magazine = "Chargeur", Trigger = "Gachette", ChargingHandle = "Levier" } },
	Deagle = { dossier = "Deagle", reference = "Deagle P", longueur = 1.25, decalage = Vector3.new(0.0, 0.0, 0.0), groupes = { Body = "Corps", Magazine = "Chargeur", Trigger = "Gachette", ChargingHandle = "Levier" } },
	Sniper = { dossier = "Sniper", reference = "Sniper P", longueur = 4.862, decalage = Vector3.new(0.0, 0.0, 0.0), groupes = { Body = "Corps", Magazine = "Chargeur", Trigger = "Gachette", ChargingHandle = "Levier" } },
	Couteau = { dossier = "Couteau", reference = "Couteau P", longueur = 1.625, decalage = Vector3.new(0.2, 0.0, 0.0), groupes = { Body = "Corps" } },
}

-- nom de couleur -> { couleur, néon }
local COULEURS = {
	Contour = { Color3.fromRGB(14, 10, 16), false },
	Noir = { Color3.fromRGB(30, 26, 34), false },
	Blanc = { Color3.fromRGB(245, 241, 245), false },
	Rose = { Color3.fromRGB(255, 92, 168), false },
	RoseVif = { Color3.fromRGB(255, 45, 165), false },
	Jaune = { Color3.fromRGB(255, 214, 40), false },
	Or = { Color3.fromRGB(232, 178, 52), false },
	Rouge = { Color3.fromRGB(205, 28, 42), false },
	GrisFonce = { Color3.fromRGB(58, 54, 60), false },
	Gris = { Color3.fromRGB(118, 118, 124), false },
	GrisClair = { Color3.fromRGB(184, 184, 190), false },
	Argent = { Color3.fromRGB(196, 206, 218), false },
	VertAcide = { Color3.fromRGB(160, 255, 30), true },
	VertSombre = { Color3.fromRGB(38, 84, 30), false },
	BleuGlace = { Color3.fromRGB(105, 205, 255), true },
	BleuNuit = { Color3.fromRGB(22, 38, 78), false },
	Bleu = { Color3.fromRGB(58, 82, 230), false },
	Violet = { Color3.fromRGB(104, 58, 186), false },
	NoirViolet = { Color3.fromRGB(24, 14, 40), false },
	VioletNeon = { Color3.fromRGB(165, 75, 255), true },
	CyanNeon = { Color3.fromRGB(50, 225, 255), true },
	MagentaNeon = { Color3.fromRGB(255, 40, 205), true },
	Carbone = { Color3.fromRGB(34, 37, 44), false },
	CyanPulse = { Color3.fromRGB(0, 225, 255), true },
	Lave = { Color3.fromRGB(255, 110, 20), true },
	OrangeBrule = { Color3.fromRGB(170, 60, 20), false },
	Graphite = { Color3.fromRGB(42, 44, 50), false },
	ApexNoyau = { Color3.fromRGB(150, 240, 255), true },
	VerreOrange = { Color3.fromRGB(255, 150, 60), false },
	LentilleOrange = { Color3.fromRGB(255, 130, 40), true },
	LentilleRose = { Color3.fromRGB(255, 120, 200), true },
	LentilleViolet = { Color3.fromRGB(175, 100, 255), true },
	LentilleRouge = { Color3.fromRGB(255, 60, 60), true },
	LentilleVert = { Color3.fromRGB(150, 255, 80), true },
	LentilleBleu = { Color3.fromRGB(110, 210, 255), true },
	LentilleMagenta = { Color3.fromRGB(255, 70, 220), true },
	LentilleBlanc = { Color3.fromRGB(235, 235, 245), true },
	Verre = { Color3.fromRGB(255, 170, 215), false },
	VerreViolet = { Color3.fromRGB(185, 120, 255), false },
	VerreRouge = { Color3.fromRGB(255, 70, 70), false },
	VerreVert = { Color3.fromRGB(150, 255, 90), false },
	VerreBleu = { Color3.fromRGB(120, 205, 255), false },
	VerreMagenta = { Color3.fromRGB(255, 95, 225), false },
	VerreBlanc = { Color3.fromRGB(232, 232, 242), false },
}
-- skins connus (ordre du catalogue) : nom de la texture -> couleur de la gâchette, rareté,
-- attributs posés sur le modèle (effets animés)
local SKINS = {
	Sakura = { Gachette = "Blanc", Rarete = "Peu commun", Attributs = {  } },
	Graffiti = { Gachette = "Jaune", Rarete = "Peu commun", Attributs = {  } },
	Royal = { Gachette = "Or", Rarete = "Peu commun", Attributs = {  } },
	Toxic = { Gachette = "VertAcide", Rarete = "Peu commun", Attributs = {  } },
	Cryo = { Gachette = "Blanc", Rarete = "Peu commun", Attributs = {  } },
	Nebuleuse = { Gachette = "CyanNeon", Rarete = "Peu commun", Attributs = {  } },
	Vortex = { Gachette = "Rouge", Rarete = "Peu commun", Attributs = {  } },
	Arcade = { Gachette = "CyanNeon", Rarete = "Peu commun", Attributs = {  } },
	Fantome = { Gachette = "GrisClair", Rarete = "Peu commun", Attributs = {  } },
	Pulse = { Gachette = "CyanPulse", Rarete = "Rare", Attributs = { Effet = "Pulse", NeonAnime = "CyanPulse", CouleurTraceur = Color3.fromRGB(90, 230, 255), CouleurFlamme = Color3.fromRGB(120, 220, 255) } },
	Inferno = { Gachette = "Lave", Rarete = "Épique", Attributs = { Effet = "Inferno", NeonAnime = "Lave", CouleurTraceur = Color3.fromRGB(255, 140, 40), CouleurFlamme = Color3.fromRGB(255, 110, 25) } },
	Apex = { Gachette = "Or", Rarete = "Légendaire", Attributs = { Effet = "Apex", NeonAnime = "ApexNoyau", CouleurTraceur = Color3.fromRGB(170, 240, 255), CouleurFlamme = Color3.fromRGB(150, 230, 255), Inspection = true, EffetElimination = "Apex" } },
}
local SKINS_ORDRE = { "Sakura", "Graffiti", "Royal", "Toxic", "Cryo", "Nebuleuse", "Vortex", "Arcade", "Fantome", "Pulse", "Inferno", "Apex" }
local NOMS_GROUPES = { Corps = true, Chargeur = true, Gachette = true, Levier = true, Root = true }

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Selection = game:GetService("Selection")
local CollectionService = game:GetService("CollectionService")
local LUMINOSITE_NEON = 0.6 -- les néons du jeu sont à 60 % de luminosité
local dossierArmes = ReplicatedStorage:FindFirstChild("Armes")

-- ------------------------------------------------------------------ outils
local function estMesure(p)
	return p:IsA("BasePart") and p.Name ~= "Root" and not p.Name:find("Contour")
end

local function bornes(parts, repere)
	local mini = Vector3.new(math.huge, math.huge, math.huge)
	local maxi = -mini
	for _, p in ipairs(parts) do
		local h = p.Size / 2
		for _, sx in ipairs({ -1, 1 }) do
			for _, sy in ipairs({ -1, 1 }) do
				for _, sz in ipairs({ -1, 1 }) do
					local coin = p.CFrame:PointToWorldSpace(Vector3.new(h.X * sx, h.Y * sy, h.Z * sz))
					local c = repere:PointToObjectSpace(coin)
					mini = mini:Min(c)
					maxi = maxi:Max(c)
				end
			end
		end
	end
	return mini, maxi
end

local function piecesDe(conteneur)
	local parts = {}
	if conteneur then
		for _, d in ipairs(conteneur:GetDescendants()) do
			if estMesure(d) then
				table.insert(parts, d)
			end
		end
	end
	return parts
end

local function centreDe(conteneur)
	local parts = piecesDe(conteneur)
	if #parts == 0 then
		return nil
	end
	local mini, maxi = bornes(parts, CFrame.new())
	return (mini + maxi) / 2
end

-- Repère de l'arme : X vers le canon, Y vers le haut, origine au centre de la boîte
-- englobante (sans contours ni Root). Le canon est l'axe le plus long ; le chargeur
-- est en bas ; la gâchette est en arrière du centre.
local function repereArme(modele)
	local parts = piecesDe(modele)
	assert(#parts > 0, "Aucune pièce trouvée dans " .. modele:GetFullName())
	local base = parts[1].CFrame.Rotation
	local mini, maxi = bornes(parts, base)
	local taille = maxi - mini
	local centre = base:PointToWorldSpace((mini + maxi) / 2)
	local axes = {
		{ v = base.XVector, s = taille.X },
		{ v = base.YVector, s = taille.Y },
		{ v = base.ZVector, s = taille.Z },
	}
	table.sort(axes, function(a, b)
		return a.s > b.s
	end)
	local avant, haut = axes[1].v, axes[2].v
	local chargeur = centreDe(modele:FindFirstChild("Chargeur"))
	local gachette = centreDe(modele:FindFirstChild("Gachette"))
	if not chargeur and not gachette then
		-- arme sans chargeur ni gâchette (couteau) : convention d'export Blender
		-- (X vers l'avant, Z Blender = Y Roblox vers le haut)
		return CFrame.fromMatrix(centre, base.XVector, base.YVector), Vector3.new(taille.X, taille.Y, taille.Z)
	end
	if chargeur and (chargeur - centre):Dot(haut) > 0 then
		haut = -haut
	end
	if gachette and (gachette - centre):Dot(avant) > 0 then
		avant = -avant
	end
	return CFrame.fromMatrix(centre, avant, haut), Vector3.new(axes[1].s, axes[2].s, axes[3].s)
end

local function premierMeshPart(conteneur)
	for _, p in ipairs(piecesDe(conteneur)) do
		if p:IsA("MeshPart") then
			return p
		end
	end
	return nil
end

local function trouverVerre(conteneur)
	for _, d in ipairs(conteneur:GetDescendants()) do
		if d:IsA("BasePart") and (d.Name:match("^Body_Verre") or d.Name:match("^Body_Lentille")) then
			return d
		end
	end
	return nil
end

-- nom du skin d'un modèle = suffixe de sa pièce texturée (Body_<Skin>)
local function skinDe(modele)
	for _, d in ipairs(modele:GetDescendants()) do
		if d:IsA("BasePart") then
			local suffixe = d.Name:match("^Body_(%a+)$")
			if suffixe and SKINS[suffixe] then
				return suffixe
			end
		end
	end
	return nil
end

-- arme d'un modèle : premier mot de son nom (« Deagle Sakura », « Phantom S 3 »)
local function armeDe(modele)
	local mot = modele.Name:match("^(%a+)")
	return mot and ARMES[mot] and mot or nil
end

-- infos de référence par arme (calculées une fois)
local infos = {}
local function infoArme(cle)
	if infos[cle] then
		return infos[cle]
	end
	local def = ARMES[cle]
	local dossier = dossierArmes and dossierArmes:FindFirstChild(def.dossier)
	local prefixe = cle .. " S "
	local reference = dossier and dossier:FindFirstChild(def.reference, true)
	if dossier and not reference then
		-- pas de « <Arme> P » : premier modèle du dossier qui ressemble à l'arme d'origine
		for _, m in ipairs(dossier:GetDescendants()) do
			if m:IsA("Model") and m:FindFirstChild("Corps") and not m.Name:find("faire")
				and not m.Name:match("^" .. prefixe .. "%d+$") and not skinDe(m) then
				reference = m
				break
			end
		end
	end
	local info = {
		def = def,
		dossier = dossier,
		parent = dossier or workspace,
		prefixe = prefixe,
		reference = reference,
		refRoot = reference and reference:FindFirstChild("Root"),
		modeleRef = premierMeshPart(reference),
	}
	if reference then
		info.refRepere, info.refTaille = repereArme(reference)
		print(string.format("[Skin] %s : référence = %s", cle, reference:GetFullName()))
	else
		warn(string.format("[Skin] %s : aucune référence trouvée dans Armes.%s (placement approximatif)", cle, def.dossier))
	end
	infos[cle] = info
	return info
end

-- ------------------------------------------------------------------ un skin
local function installer(source)
	local cle = armeDe(source)
	local I = infoArme(cle)
	local reference, refRoot, modeleRef = I.reference, I.refRoot, I.modeleRef
	local refRepere, refTaille, parent = I.refRepere, I.refTaille, I.parent
	local PREFIXE_NOM, LONGUEUR, GROUPES = I.prefixe, I.def.longueur, I.def.groupes
	local skin = skinDe(source)
	local gachette = skin and SKINS[skin].Gachette or "Blanc"

	-- 1) récupérer les pièces (import FBX ou skin déjà installé)
	local pieces = {}
	for _, d in ipairs(source:GetDescendants()) do
		if d:IsA("BasePart") then
			local nom = d.Name:match("^[%w_]+")
			if nom == "Root" then
				d:Destroy() -- recréé plus bas à partir de celui de Phantom P
			else
				for _, j in ipairs(d:GetChildren()) do
					if j:IsA("JointInstance") or j:IsA("WeldConstraint") then
						j:Destroy()
					end
				end
				pieces[nom] = d
			end
		end
	end

	-- 2) nouveau modèle avec la même structure que Phantom P
	local arme = Instance.new("Model")
	local groupes = {}
	for prefixe, nomGroupe in pairs(GROUPES) do
		local g = Instance.new("Model")
		g.Name = nomGroupe
		g.Parent = arme
		groupes[prefixe] = g
	end

	for nom, part in pairs(pieces) do
		local prefixe = nom:match("^(%a+)")
		local couleur = nom:match("_(%a+)%d*$") or gachette
		local def = COULEURS[couleur]
		local verre = couleur:match("^Verre") ~= nil
		if prefixe and not GROUPES[prefixe] then
			prefixe = "Body" -- pièce d'un groupe que cette arme n'a pas : rangée dans Corps
		end
		part.Name = nom
		if SKINS[couleur] then
			part.Color = Color3.new(1, 1, 1) -- pièce texturée : ne pas teinter
		elseif def then
			part.Color = def[1]
			if def[2] then -- néon : luminosité réduite
				local h, s, v = def[1]:ToHSV()
				part.Color = Color3.fromHSV(h, s, v * LUMINOSITE_NEON)
			end
		end
		part.Material = if def and def[2] then Enum.Material.Neon else Enum.Material.SmoothPlastic
		part.Transparency = if verre then 0.75 else 0
		part.CastShadow = couleur ~= "Contour" and not verre and not (def and def[2])
		if modeleRef then
			part.Anchored = modeleRef.Anchored
			part.CanCollide = modeleRef.CanCollide
			part.CanTouch = modeleRef.CanTouch
			part.CanQuery = modeleRef.CanQuery
			part.Massless = modeleRef.Massless
		else
			part.Anchored = true
			part.CanCollide = false
			part.CanTouch = false
			part.CanQuery = false
			part.Massless = true
		end
		part.Parent = groupes[prefixe] or arme
	end

	-- 3) même longueur que Phantom P
	local monRepere, maTaille = repereArme(arme)
	local longueurAvant = maTaille.X
	local cible = if refTaille then refTaille.X else LONGUEUR
	if math.abs(cible / maTaille.X - 1) > 0.002 then
		arme.WorldPivot = monRepere
		arme:ScaleTo(arme:GetScale() * cible / maTaille.X)
		monRepere, maTaille = repereArme(arme)
	end

	-- 4) Root : même position/orientation relative que dans Phantom P
	local root
	if refRoot then
		root = refRoot:Clone()
		for _, d in ipairs(root:GetDescendants()) do
			if d:IsA("JointInstance") or d:IsA("WeldConstraint") then
				d:Destroy()
			end
		end
		root.CFrame = monRepere * refRepere:ToObjectSpace(refRoot.CFrame)
	else
		root = Instance.new("Part")
		root.Size = Vector3.new(0.2, 0.2, 0.2)
		root.Transparency = 1
		root.CanCollide = false
		root.Anchored = true
		root.CFrame = monRepere -- au centre de l'arme, faute de référence
	end
	root.Name = "Root"
	root.Parent = arme
	arme.PrimaryPart = root

	-- 5) tout ce qui n'est pas une pièce dans Phantom P (Sons, scripts, valeurs...) + attributs
	if reference then
		for _, enfant in ipairs(reference:GetChildren()) do
			if not NOMS_GROUPES[enfant.Name] and not enfant:IsA("BasePart") then
				enfant:Clone().Parent = arme
			end
		end
		for cle, valeur in pairs(reference:GetAttributes()) do
			arme:SetAttribute(cle, valeur)
		end
	end

	-- 6) placement : superposé à Phantom P
	if refRoot then
		arme:PivotTo(refRoot.CFrame)
	else
		arme:PivotTo(CFrame.new(source:GetPivot().Position))
	end

	-- 6 bis) visée : le verre du skin au même endroit (hauteur/côté) que celui de Phantom P,
	-- par rapport au Root. On déplace les pièces, pas le Root.
	local decalageVerre = Vector3.zero
	local refVerre = reference and reference:FindFirstChild("Body_Cyan", true)
	local monVerre = trouverVerre(arme)
	if refVerre and monVerre and refVerre:IsA("BasePart") then
		local d = refRepere:PointToObjectSpace(refVerre.Position) - refRepere:PointToObjectSpace(monVerre.Position)
		decalageVerre = Vector3.new(0, d.Y, d.Z)
		local monde = refRepere:VectorToWorldSpace(decalageVerre)
		for _, p in ipairs(arme:GetDescendants()) do
			if p:IsA("BasePart") and p ~= root then
				p.CFrame = p.CFrame + monde
			end
		end
	end

	-- 6 ter) décalage propre à l'arme (ex. couteau avancé pour voir le manche), dans le
	-- repère de l'arme : X vers l'avant, Y vers le haut, Z sur le côté. Le Root ne bouge pas.
	local decalage = I.def.decalage or Vector3.zero
	if decalage.Magnitude > 0 then
		local repere = if refRepere then refRepere else root.CFrame
		local monde = repere:VectorToWorldSpace(decalage)
		for _, p in ipairs(arme:GetDescendants()) do
			if p:IsA("BasePart") and p ~= root then
				p.CFrame = p.CFrame + monde
			end
		end
	end

	-- 7) soudures sur le Root si Phantom P en utilise
	local soude = false
	if reference then
		for _, d in ipairs(reference:GetDescendants()) do
			if d:IsA("WeldConstraint") or d:IsA("JointInstance") then
				soude = true
				break
			end
		end
	end
	if soude then
		for _, p in ipairs(arme:GetDescendants()) do
			if p:IsA("BasePart") and p ~= root then
				local w = Instance.new("WeldConstraint")
				w.Part0 = root
				w.Part1 = p
				w.Parent = p
			end
		end
	end

	-- 8) attributs des skins à effets (lus par le module EffetsSkins) + tag
	local infoSkin = skin and SKINS[skin]
	if infoSkin and infoSkin.Attributs then
		for cle, valeur in pairs(infoSkin.Attributs) do
			arme:SetAttribute(cle, valeur)
		end
		if infoSkin.Attributs.Effet then
			CollectionService:AddTag(arme, "EffetSkin")
		end
	end

	-- 9) rangement dans le dossier de la rareté + nom unique dans tout le dossier de l'arme
	local rarete = infoSkin and infoSkin.Rarete or "Peu commun"
	local destination = (I.dossier and I.dossier:FindFirstChild(rarete)) or parent
	local function pris(n)
		local trouve = (I.dossier or parent):FindFirstChild(n, true)
		return trouve ~= nil and trouve ~= source
	end
	local nom = source.Name
	local garde = (I.dossier and source:IsDescendantOf(I.dossier))
		and (nom:match("^" .. PREFIXE_NOM .. "%d+$") or (skin and nom == cle .. " " .. skin))
	if not garde then
		if rarete == "Peu commun" then
			local n = 1
			while pris(PREFIXE_NOM .. n) do
				n += 1
			end
			nom = PREFIXE_NOM .. n
		else
			nom = cle .. " " .. (skin or "Skin")
			local n = 2
			while pris(nom) do
				nom = cle .. " " .. (skin or "Skin") .. " " .. n
				n += 1
			end
		end
	end
	arme.Name = nom
	arme.Parent = destination
	source:Destroy()

	print(string.format("[Skin] %s = %s %s (%s, dans %s) | longueur %.3f -> %.3f studs | verre recentré (%.3f, %.3f)%s | soudures : %s",
		nom, cle, skin or "?", rarete, destination:GetFullName(), longueurAvant, maTaille.X, decalageVerre.Y, decalageVerre.Z,
		if not monVerre then " (pas de verre)" elseif refVerre then "" else " -- Body_Cyan introuvable",
		tostring(soude)))
	return arme
end

-- ------------------------------------------------------------------ tous les modèles sélectionnés
local ordre = {}
for i, nom in ipairs(SKINS_ORDRE) do
	ordre[nom] = i
end
local selection = {}
for _, m in ipairs(Selection:Get()) do
	if m:IsA("Model") then
		-- sécurité : on ne touche qu'aux skins connus (pièce Body_<Skin>), jamais à Phantom P,
		-- aux « Phantom A faire » ou à une autre arme sélectionnée par erreur
		local cle = armeDe(m)
		local estReference = cle and infoArme(cle).reference == m
		if estReference or not skinDe(m) or not cle then
			warn("[Skin] ignoré (ce n'est pas un skin connu) : " .. m:GetFullName())
		else
			table.insert(selection, m)
		end
	end
end
assert(#selection > 0, "Aucun skin à installer : sélectionne les modèles importés (Phantom <Skin>) dans l'Explorer")
-- les skins déjà nommés « Phantom S N » d'abord (ils gardent leur numéro), puis l'ordre du catalogue
local function dejaNomme(m)
	local I = infoArme(armeDe(m))
	return I.dossier ~= nil and m:IsDescendantOf(I.dossier) and m.Name:match("^" .. I.prefixe .. "%d+$") ~= nil
end
table.sort(selection, function(a, b)
	local ka = if dejaNomme(a) then 0 else 1
	local kb = if dejaNomme(b) then 0 else 1
	if ka ~= kb then
		return ka < kb
	end
	return (ordre[skinDe(a) or ""] or 99) < (ordre[skinDe(b) or ""] or 99)
end)
local faits = {}
for _, m in ipairs(selection) do
	table.insert(faits, installer(m))
end
Selection:Set(faits)
print(string.format("[Skin] %d skin(s) installé(s)", #faits))
