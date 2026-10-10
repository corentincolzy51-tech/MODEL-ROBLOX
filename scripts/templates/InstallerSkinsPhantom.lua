--[[
	Installe un ou plusieurs skins de la VANTA AR-01 à partir des FBX importés.

	1. Importe les fichiers Phantom_<Skin>.fbx (Accueil > Importer 3D, « Scale Unit » = Stud).
	   -> ou sélectionne des skins déjà installés pour les recaler.
	2. Sélectionne TOUS ces modèles dans l'Explorer (Ctrl + clic).
	   (les modèles qui ne sont pas des skins, comme Phantom P, sont ignorés)
	3. Colle tout le script dans la barre de commande (Affichage > Barre de commande), puis Entrée.

	Pour chaque modèle, le script :
	  - range les pièces comme « Phantom P » : Corps / Chargeur / Gachette / Levier + Root
	  - met les couleurs (une couleur par pièce), le néon et le verre transparent du viseur
	  - met l'arme à la même longueur que Phantom P et la superpose à Phantom P
	    (canon, dessus et crosse au même endroit), Root placé comme celui de Phantom P
	  - centre le verre du viseur sur celui de Phantom P (Body_Cyan) pour la visée
	  - copie depuis Phantom P : Sons, autres objets, attributs, réglages des pièces, soudures
	  - le nomme « Phantom S 1 », 2, 3... (premier numéro libre, dans l'ordre du catalogue)
	    (un skin déjà nommé « Phantom S N » que l'on recale garde son nom)

	Fichier généré par scripts/build_skins.py : ne pas modifier les tables à la main.
]]

local PREFIXE_NOM = "Phantom S " -- les skins s'appellent Phantom S 1, Phantom S 2, ...
local LONGUEUR = 3.616 -- studs, utilisé seulement si Phantom P est introuvable
-- poignée dans le repère de l'arme (X vers le canon, Y vers le haut, origine au centre
-- de la boîte englobante), pour une arme de 3,616 studs
local POIGNEE = Vector3.new(-0.638, -0.2515, 0)

-- nom de couleur -> { couleur, néon }
local COULEURS = {
--@@COULEURS@@
}
-- skins connus (ordre du catalogue) : nom de la texture -> couleur de la gâchette
local SKINS = {
--@@SKINS@@
}
local SKINS_ORDRE = { --@@ORDRE@@ }
local GROUPES = { Body = "Corps", Magazine = "Chargeur", Trigger = "Gachette", ChargingHandle = "Levier" }
local NOMS_GROUPES = { Corps = true, Chargeur = true, Gachette = true, Levier = true, Root = true }

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Selection = game:GetService("Selection")

local armes = ReplicatedStorage:FindFirstChild("Armes")
local dossier = armes and armes:FindFirstChild("Phantom")
local reference = dossier and dossier:FindFirstChild("Phantom P")
local refRoot = reference and reference:FindFirstChild("Root")

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
	if chargeur and (chargeur - centre):Dot(haut) > 0 then
		haut = -haut
	end
	local gachette = centreDe(modele:FindFirstChild("Gachette"))
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
		if d:IsA("BasePart") and d.Name:match("^Body_Verre") then
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

local modeleRef = premierMeshPart(reference)
local refRepere, refTaille
if reference then
	refRepere, refTaille = repereArme(reference)
end
local parent = dossier or workspace

-- ------------------------------------------------------------------ un skin
local function installer(source)
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
		local couleur = nom:match("_(%a+)$") or gachette
		local def = COULEURS[couleur]
		local verre = couleur:match("^Verre") ~= nil
		part.Name = nom
		if SKINS[couleur] then
			part.Color = Color3.new(1, 1, 1) -- pièce texturée : ne pas teinter
		elseif def then
			part.Color = def[1]
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
		root.CFrame = monRepere * CFrame.new(POIGNEE * maTaille.X / 3.616)
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

	-- 8) nom automatique : Phantom S 1, 2, 3... (le premier libre)
	local nom = source.Name
	if not (source.Parent == parent and nom:match("^" .. PREFIXE_NOM .. "%d+$")) then
		local n = 1
		while parent:FindFirstChild(PREFIXE_NOM .. n) do
			n += 1
		end
		nom = PREFIXE_NOM .. n
	end
	arme.Name = nom
	arme.Parent = parent
	source:Destroy()

	print(string.format("[Skin] %s = %s | longueur %.3f -> %.3f studs | verre recentré (%.3f, %.3f)%s | soudures : %s",
		nom, skin or "?", longueurAvant, maTaille.X, decalageVerre.Y, decalageVerre.Z,
		if refVerre then "" else " -- Body_Cyan introuvable", tostring(soude)))
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
		if m == reference or not skinDe(m) then
			warn("[Skin] ignoré (ce n'est pas un skin connu) : " .. m:GetFullName())
		else
			table.insert(selection, m)
		end
	end
end
assert(#selection > 0, "Aucun skin à installer : sélectionne les modèles importés (Phantom <Skin>) dans l'Explorer")
-- les skins déjà nommés « Phantom S N » d'abord (ils gardent leur numéro), puis l'ordre du catalogue
table.sort(selection, function(a, b)
	local ka = if a.Parent == parent and a.Name:match("^" .. PREFIXE_NOM .. "%d+$") then 0 else 1
	local kb = if b.Parent == parent and b.Name:match("^" .. PREFIXE_NOM .. "%d+$") then 0 else 1
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
print(string.format("[Skin] %d skin(s) installé(s) dans %s", #faits, parent:GetFullName()))
