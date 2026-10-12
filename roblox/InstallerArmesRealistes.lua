--[[
	Installe les armes RÉALISTES VANTA à partir des FBX importés :
	Phantom_Realiste.fbx (fusil), Deagle_Realiste.fbx, Sniper_Realiste.fbx, Couteau_Realiste.fbx (karambit).

	1. Accueil > Importer 3D, choisir le(s) FBX, « Scale Unit » = Stud.
	   (laisser l'importateur charger les textures : elles sont dans le FBX)
	2. Sélectionner les modèles importés dans l'Explorer (Ctrl + clic).
	3. Coller tout ce script dans la barre de commande (Affichage > Barre de commande), Entrée.

	Pour chaque modèle, le script :
	  - range les pièces comme la référence « <Arme> P » : Corps / Chargeur / Gachette / Levier + Root
	  - garde les textures (TextureID / SurfaceAppearance), règle matériau, verre et points lumineux
	  - met l'arme à la longueur de la référence, superposée à elle, avec la poignée là où
	    était celle de l'ancienne arme (décalage calculé par scripts/real/build_real.py)
	  - recentre le verre du viseur sur celui de la référence (Body_Cyan) pour la visée
	  - copie depuis la référence : Root et ses repères, Sons, attributs, réglages des pièces, soudures
	  - la nomme « <Arme> R » et la range dans Armes.<Arme>.Base (sinon Armes.<Arme>)

	Fichier généré par scripts/real/build_real.py : ne pas modifier les tables à la main.
]]

-- arme : dossier, référence, longueur (studs), décalage de prise en main (studs, repère de
-- l'arme : X avant, Y haut, Z côté), groupes
local ARMES = {
	Phantom = { dossier = "Phantom", reference = "Phantom P", longueur = 3.616, decalage = Vector3.new(0.0050, 0.0015, -0.0000), groupes = { Body = true, ChargingHandle = true, Magazine = true, Trigger = true }, attaches = {  } },
	Deagle = { dossier = "Deagle", reference = "Deagle P", longueur = 1.310, decalage = Vector3.new(0.0328, -0.0128, -0.0015), groupes = { Body = true, ChargingHandle = true, Magazine = true, Trigger = true }, attaches = {  } },
	Sniper = { dossier = "Sniper", reference = "Sniper P", longueur = 4.862, decalage = Vector3.new(0.0050, 0.0177, 0.0125), groupes = { Body = true, ChargingHandle = true, Magazine = true, Trigger = true }, attaches = { Verrou = { piece = "ChargingHandle_Culasse", position = Vector3.new(0.0000, 0.0188, -0.1154) } } },
	Couteau = { dossier = "Couteau", reference = "Couteau P", longueur = 1.587, decalage = Vector3.new(0.0215, -0.1407, -0.0000), groupes = { Body = true }, attaches = { Anneau = { piece = "Body_Lame", position = Vector3.new(-0.6687, 0.1477, -0.0000) } } },
}
-- suffixe de pièce -> matériau Roblox, transparence, couleur (nil = blanc : la texture fait tout)
local PIECES = {
	Acier = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- AcierNoir
	Bas = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- AnodiseNoir
	Bipied = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- CerakoteNoir
	Boitier = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- AcierNoir
	Boule = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- PolymereNoir
	Canon = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- AcierNoir
	Carcasse = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- CerakoteNoir
	Cartouche = { materiau = Enum.Material.Metal, transparence = 0, couleur = nil, sansOmbre = false },  -- Laiton
	Chargeur = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- AcierNoir
	Chassis = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- CerakoteFDE
	Colliers = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- AcierNoir
	Crosse = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- CerakoteFDE
	Culasse = { materiau = Enum.Material.Metal, transparence = 0, couleur = nil, sansOmbre = false },  -- AcierBrut
	Gachette = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- AcierNoir
	Garde = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- AnodiseNoir
	Guidon = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- AcierNoir
	Lame = { materiau = Enum.Material.Metal, transparence = 0, couleur = nil, sansOmbre = false },  -- Lame
	Lentille = { materiau = Enum.Material.Glass, transparence = 0.35, couleur = Color3.new(0.35, 0.60, 0.80), sansOmbre = true },  -- VerreLunette
	Levier = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- AnodiseNoir
	Lunette = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- AnodiseNoir
	Manche = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- G10
	Optique = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- CerakoteNoir
	Plaquettes = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- Caoutchouc
	Poignee = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- PolymereNoir
	Polymere = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- PolymereNoir
	Reticule = { materiau = Enum.Material.Neon, transparence = 0, couleur = Color3.new(1.00, 0.12, 0.08), sansOmbre = true },  -- Tritium
	Talon = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- Caoutchouc
	Tritium = { materiau = Enum.Material.Neon, transparence = 0, couleur = Color3.new(0.35, 1.00, 0.45), sansOmbre = true },  -- Tritium
	Tube = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- AnodiseNoir
	Verre = { materiau = Enum.Material.Glass, transparence = 0.6, couleur = Color3.new(0.75, 0.88, 0.95), sansOmbre = true },  -- Verre
	Verrou = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- AcierNoir
	Vis = { materiau = Enum.Material.SmoothPlastic, transparence = 0, couleur = nil, sansOmbre = false },  -- AcierNoir
}
local NOMS_GROUPES = { Corps = true, Chargeur = true, Gachette = true, Levier = true, Root = true }
local GROUPES = { Body = "Corps", Magazine = "Chargeur", Trigger = "Gachette", ChargingHandle = "Levier" }
local LUMINOSITE_NEON = 0.6

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Selection = game:GetService("Selection")
local dossierArmes = ReplicatedStorage:FindFirstChild("Armes")

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
					local c = repere:PointToObjectSpace(p.CFrame:PointToWorldSpace(Vector3.new(h.X * sx, h.Y * sy, h.Z * sz)))
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

-- Repère de l'arme (même calcul que le script des skins) : X = canon, Y = haut, centre de la boîte.
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

local function armeDe(modele)
	local mot = modele.Name:match("^(%a+)")
	return mot and ARMES[mot] and mot or nil
end

local function estRealiste(modele)
	if modele:GetAttribute("Realiste") then
		return true
	end
	if modele.Name:match("Realiste") or modele.Name:match("^%a+ R%s?%d*$") then
		return true
	end
	return false
end

local infos = {}
local function infoArme(cle)
	if infos[cle] then
		return infos[cle]
	end
	local def = ARMES[cle]
	local dossier = dossierArmes and dossierArmes:FindFirstChild(def.dossier)
	local reference = dossier and dossier:FindFirstChild(def.reference, true)
	local info = {
		def = def,
		dossier = dossier,
		reference = reference,
		refRoot = reference and reference:FindFirstChild("Root"),
		modeleRef = premierMeshPart(reference),
	}
	if reference then
		info.refRepere, info.refTaille = repereArme(reference)
		print(string.format("[Réaliste] %s : référence = %s", cle, reference:GetFullName()))
	else
		warn(string.format("[Réaliste] %s : « %s » introuvable dans Armes.%s (placement approximatif)", cle, def.reference, def.dossier))
	end
	infos[cle] = info
	return info
end

local function deplacer(arme, root, monde)
	for _, p in ipairs(arme:GetDescendants()) do
		if p:IsA("BasePart") and p ~= root then
			p.CFrame = p.CFrame + monde
		end
	end
end

local function installer(source)
	local cle = armeDe(source)
	local I = infoArme(cle)
	local reference, refRoot, modeleRef = I.reference, I.refRoot, I.modeleRef
	local refRepere, refTaille = I.refRepere, I.refTaille

	-- 1) pièces
	local pieces = {}
	for _, d in ipairs(source:GetDescendants()) do
		if d:IsA("BasePart") then
			local nom = d.Name:match("^[%w_]+")
			if nom == "Root" then
				d:Destroy()
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

	-- 2) structure Corps / Chargeur / Gachette / Levier
	local arme = Instance.new("Model")
	local groupes = {}
	for prefixe, nomGroupe in pairs(GROUPES) do
		if I.def.groupes[prefixe] then
			local g = Instance.new("Model")
			g.Name = nomGroupe
			g.Parent = arme
			groupes[prefixe] = g
		end
	end
	for nom, part in pairs(pieces) do
		local prefixe = nom:match("^(%a+)")
		local suffixe = if nom == "Trigger" then "Gachette" else (nom:match("_(%a+)$") or "")
		if not groupes[prefixe] then
			prefixe = "Body"
		end
		part.Name = nom
		local def = PIECES[suffixe]
		if def then
			part.Material = def.materiau
			part.Transparency = def.transparence or 0
			if def.couleur then
				local c = def.couleur
				if def.materiau == Enum.Material.Neon then
					local h, s, v = c:ToHSV()
					c = Color3.fromHSV(h, s, v * LUMINOSITE_NEON)
				end
				part.Color = c
				if part:IsA("MeshPart") then
					part.TextureID = ""
				end
			else
				part.Color = Color3.new(1, 1, 1)
			end
			part.CastShadow = not def.sansOmbre
		else
			part.Material = Enum.Material.SmoothPlastic
			part.Color = Color3.new(1, 1, 1)
		end
		if modeleRef then
			part.Anchored = modeleRef.Anchored
			part.CanCollide = modeleRef.CanCollide
			part.CanTouch = modeleRef.CanTouch
			part.CanQuery = modeleRef.CanQuery
			part.Massless = modeleRef.Massless
		else
			part.Anchored, part.CanCollide, part.CanTouch, part.CanQuery, part.Massless = true, false, false, false, true
		end
		part.Parent = groupes[prefixe] or arme
	end

	-- 3) longueur de la référence
	local monRepere, maTaille = repereArme(arme)
	local longueurAvant = maTaille.X
	local cible = if refTaille then refTaille.X else I.def.longueur
	local echelle = cible / maTaille.X
	if math.abs(echelle - 1) > 0.002 then
		arme.WorldPivot = monRepere
		arme:ScaleTo(arme:GetScale() * echelle)
		monRepere, maTaille = repereArme(arme)
	end

	-- 4) Root : même position relative que dans la référence
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
		root.CFrame = monRepere
	end
	root.Name = "Root"
	root.Parent = arme
	arme.PrimaryPart = root

	-- 5) Sons, scripts, valeurs... + attributs de la référence
	if reference then
		for _, enfant in ipairs(reference:GetChildren()) do
			if not NOMS_GROUPES[enfant.Name] and not enfant:IsA("BasePart") then
				enfant:Clone().Parent = arme
			end
		end
		for k, v in pairs(reference:GetAttributes()) do
			arme:SetAttribute(k, v)
		end
	end
	arme:SetAttribute("Realiste", true)

	-- 6) superposition sur la référence
	if refRoot then
		arme:PivotTo(refRoot.CFrame)
	else
		arme:PivotTo(CFrame.new(source:GetPivot().Position))
	end
	local repere = if refRepere then refRepere else root.CFrame

	-- 6 bis) poignée au même endroit que celle de l'ancienne arme (le Root ne bouge pas)
	local decalage = I.def.decalage * echelle
	if decalage.Magnitude > 0 then
		deplacer(arme, root, repere:VectorToWorldSpace(decalage))
	end

	-- 6 ter) visée : verre du viseur à la hauteur / au centre de Body_Cyan de la référence
	local decalageVerre = Vector3.zero
	local refVerre = reference and reference:FindFirstChild("Body_Cyan", true)
	local monVerre = trouverVerre(arme)
	if refVerre and monVerre and refVerre:IsA("BasePart") then
		local d = repere:PointToObjectSpace(refVerre.Position) - repere:PointToObjectSpace(monVerre.Position)
		decalageVerre = Vector3.new(0, d.Y, d.Z)
		deplacer(arme, root, repere:VectorToWorldSpace(decalageVerre))
	end

	-- 6 quater) repères des animations (Attachments du Root) : anneau du karambit, axe du verrou
	for nomAtt, def in pairs(I.def.attaches or {}) do
		local piece = arme:FindFirstChild(def.piece, true)
		if piece and piece:IsA("BasePart") then
			local att = root:FindFirstChild(nomAtt) or Instance.new("Attachment")
			att.Name = nomAtt
			att.Parent = root
			att.WorldPosition = piece.CFrame:PointToWorldSpace(def.position * echelle)
		end
	end

	-- 7) soudures si la référence en a
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

	-- 8) nom et rangement
	local destination = (I.dossier and (I.dossier:FindFirstChild("Base") or I.dossier)) or workspace
	local base = cle .. " R"
	local nom = base
	local n = 2
	local function pris(x)
		local t = (I.dossier or destination):FindFirstChild(x, true)
		return t ~= nil and t ~= source
	end
	if not (source.Name:match("^" .. base .. "%s?%d*$") and I.dossier and source:IsDescendantOf(I.dossier)) then
		while pris(nom) do
			nom = base .. " " .. n
			n += 1
		end
	else
		nom = source.Name
	end
	arme.Name = nom
	arme.Parent = destination
	source:Destroy()
	print(string.format("[Réaliste] %s installé dans %s | longueur %.3f -> %.3f | décalage (%.3f, %.3f, %.3f) | verre (%.3f, %.3f)%s",
		nom, destination:GetFullName(), longueurAvant, maTaille.X, decalage.X, decalage.Y, decalage.Z,
		decalageVerre.Y, decalageVerre.Z, if monVerre and not refVerre then " -- Body_Cyan introuvable" else ""))
	return arme
end

local selection = {}
for _, m in ipairs(Selection:Get()) do
	if m:IsA("Model") then
		local cle = armeDe(m)
		if cle and estRealiste(m) and infoArme(cle).reference ~= m then
			table.insert(selection, m)
		else
			warn("[Réaliste] ignoré : " .. m:GetFullName() .. " (attendu : « Phantom Realiste », « Deagle Realiste »...)")
		end
	end
end
assert(#selection > 0, "Sélectionne les modèles importés (Phantom Realiste, Deagle Realiste, Sniper Realiste, Couteau Realiste)")
local faits = {}
for _, m in ipairs(selection) do
	table.insert(faits, installer(m))
end
Selection:Set(faits)
print(string.format("[Réaliste] %d arme(s) installée(s)", #faits))
