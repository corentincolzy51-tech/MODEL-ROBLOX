--[[
	EffetsSkins — effets des skins Rare / Épique / Légendaire (ModuleScript)
	À placer dans : ReplicatedStorage › Modules › EffetsSkins

	Tout le code des effets est ici, pour ne pas toucher à la limite des 200 variables
	d'ArmeFPS. Les scripts existants appellent seulement (sans nouvelle variable) :
	  EffetsSkins.AuTir(modeleArme, arme, depart, cible)     -- à chaque tir
	  EffetsSkins.AuRechargement(modeleArme, arme, duree)    -- début du rechargement
	  EffetsSkins.AEquipement(modeleArme, arme)              -- arme créée / sortie
	  EffetsSkins.DecalageInspection(dt, bloque) -> CFrame   -- chaque image (inspection F)
	L'effet d'élimination se lance tout seul (écoute de Remotes.Elimination).

	Le skin décrit ses effets avec des attributs posés par le script d'installation :
	  Effet            "Pulse" | "Inferno" | "Apex"
	  NeonAnime        nom de couleur des néons animés (pièces « *_<NeonAnime> » et
	                   « *_<NeonAnime>NN » = segments / anneaux numérotés)
	  CouleurTraceur, CouleurFlamme   Color3 (lus par ArmeFPS / EffetsAutresJoueurs)
	  Inspection       true -> touche F
	  EffetElimination "Apex"
	et du tag CollectionService « EffetSkin », qui suit les copies (vue FPS, arme en main).
	Les néons ne dépassent jamais la luminosité posée par l'installation (60 %).
]]

local EffetsSkins = {}

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local CollectionService = game:GetService("CollectionService")
local UserInputService = game:GetService("UserInputService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")

local TAG = "EffetSkin"
local TOUCHE_INSPECTION = Enum.KeyCode.F
local TEX_ETINCELLE = "rbxasset://textures/particles/sparkles_main.dds"
local TEX_FUMEE = "rbxasset://textures/particles/smoke_main.dds"

local joueur = Players.LocalPlayer
local suivis = {} -- [Model] = état d'animation (copies présentes dans workspace)
local armeLocale = nil -- copie FPS du joueur local (pour l'inspection)

-- ------------------------------------------------------------------ outils
local function auLobby()
	return joueur ~= nil and joueur:GetAttribute("Lieu") == "Lobby"
end

local function echelle(modele)
	local ok, s = pcall(function()
		return modele:GetScale()
	end)
	return ok and s or 1
end

local function tween(obj, duree, props, style)
	local t = TweenService:Create(obj, TweenInfo.new(duree, style or Enum.EasingStyle.Quad, Enum.EasingDirection.Out), props)
	t:Play()
	return t
end

local function pieceEffet(props)
	local p = Instance.new("Part")
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.Material = Enum.Material.Neon
	for k, v in pairs(props) do
		p[k] = v
	end
	return p
end

-- émetteur ponctuel temporaire à une position du monde
local function rafale(position, nombre, props)
	local a = Instance.new("Attachment")
	a.WorldPosition = position
	a.Parent = workspace.Terrain
	local e = Instance.new("ParticleEmitter")
	e.Enabled = false
	for k, v in pairs(props) do
		e[k] = v
	end
	e.Parent = a
	e:Emit(nombre)
	Debris:AddItem(a, 3)
end

-- ------------------------------------------------------------------ suivi des copies
local function lireNeons(modele)
	local nomNeon = modele:GetAttribute("NeonAnime")
	local uniques, numerotes = {}, {}
	if not nomNeon then
		return uniques, numerotes
	end
	for _, p in ipairs(modele:GetDescendants()) do
		if p:IsA("BasePart") then
			local suffixe, num = p.Name:match("_(%a+)(%d*)$")
			if suffixe == nomNeon then
				local h, s, v = p.Color:ToHSV()
				local info = { part = p, h = h, s = s, v = math.max(v, 0.05) }
				if num ~= "" then
					info.index = tonumber(num)
					table.insert(numerotes, info)
				else
					table.insert(uniques, info)
				end
			end
		end
	end
	table.sort(numerotes, function(a, b)
		return a.index < b.index
	end)
	return uniques, numerotes
end

local function plusGrande(liste)
	local meilleure, taille = nil, -1
	for _, info in ipairs(liste) do
		local m = info.part.Size.Magnitude
		if m > taille then
			meilleure, taille = info.part, m
		end
	end
	return meilleure
end

local function decorer(etat)
	local effet, s = etat.effet, echelle(etat.modele)
	if effet == "Inferno" then
		local lave = plusGrande(etat.uniques)
		if lave then
			-- braises qui montent de toute la surface des fissures
			local e = Instance.new("ParticleEmitter")
			e.Name = "Braises"
			e.Texture = TEX_ETINCELLE
			e.Rate = 9
			e.Lifetime = NumberRange.new(0.6, 1.3)
			e.Speed = NumberRange.new(0.4 * s, 1.2 * s)
			e.Acceleration = Vector3.new(0, 1.5 * s, 0)
			e.SpreadAngle = Vector2.new(25, 25)
			e.EmissionDirection = Enum.NormalId.Top
			e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.07 * s), NumberSequenceKeypoint.new(1, 0) })
			e.Color = ColorSequence.new(Color3.fromRGB(255, 190, 80), Color3.fromRGB(255, 60, 10))
			e.LightEmission = 1
			e.Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.1), NumberSequenceKeypoint.new(1, 1) })
			e.Parent = lave
			local l = Instance.new("PointLight")
			l.Name = "Chaleur"
			l.Color = Color3.fromRGB(255, 110, 30)
			l.Range = 3 * s
			l.Brightness = 0.5
			l.Parent = lave
			etat.lumiere = l
		end
	elseif effet == "Apex" then
		local noyau = plusGrande(etat.uniques)
		if noyau then
			local l = Instance.new("PointLight")
			l.Name = "Noyau"
			l.Color = Color3.fromRGB(150, 240, 255)
			l.Range = 3.5 * s
			l.Brightness = 0.8
			l.Parent = noyau
			etat.lumiere = l
		end
	end
end

local function suivre(modele)
	if not modele or suivis[modele] or not modele:IsDescendantOf(workspace) then
		return suivis[modele]
	end
	local effet = modele:GetAttribute("Effet")
	if not effet then
		return nil
	end
	local uniques, numerotes = lireNeons(modele)
	local etat = {
		modele = modele,
		effet = effet,
		uniques = uniques,
		numerotes = numerotes,
		flash = -10,
		rechargeDebut = -10,
		rechargeFin = -10,
		equipement = os.clock(),
	}
	suivis[modele] = etat
	decorer(etat)
	return etat
end

-- ------------------------------------------------------------------ animation (chaque image)
local function couleur(info, facteur)
	info.part.Color = Color3.fromHSV(info.h, info.s, info.v * math.clamp(facteur, 0, 1))
end

local function animer(etat, t, dt)
	local boost = math.max(0, 1 - (t - etat.flash) / 0.18) -- éclat au tir
	local enRecharge = t < etat.rechargeFin
	local boot = math.clamp((t - etat.equipement) / 0.8, 0, 1) -- démarrage à l'équipement

	if etat.effet == "Pulse" then
		local n = #etat.numerotes
		for i, seg in ipairs(etat.numerotes) do
			local f
			if enRecharge then -- les segments se rallument un à un pendant le rechargement
				local progres = (t - etat.rechargeDebut) / math.max(0.1, etat.rechargeFin - etat.rechargeDebut)
				f = (i / n <= progres) and 0.8 or 0.12
			else
				local phase = (t * 0.9 - (i - 1) / n) % 1
				local onde = phase < 0.22 and math.sin(phase / 0.22 * math.pi) or 0
				f = 0.25 + 0.75 * math.max(onde, boost)
			end
			couleur(seg, f * (0.3 + 0.7 * boot))
		end
		for _, u in ipairs(etat.uniques) do
			couleur(u, (0.75 + 0.25 * math.sin(t * 2)) * (0.3 + 0.7 * boot))
		end
	elseif etat.effet == "Inferno" then
		for k, u in ipairs(etat.uniques) do
			local scint = 0.5 + 0.5 * math.noise(t * 2.5, k * 7.3)
			local f = 0.5 + 0.3 * (0.5 + 0.5 * math.sin(t * 2.2 + k)) + 0.2 * scint
			couleur(u, math.max(f, boost) * (0.2 + 0.8 * boot))
		end
		if etat.lumiere then
			etat.lumiere.Brightness = 0.35 + 0.25 * math.sin(t * 2.2) + boost
		end
	elseif etat.effet == "Apex" then
		local f = 0.7 + 0.3 * math.sin(t * 3)
		if boot < 1 then -- démarrage : le noyau clignote puis s'allume
			f = f * boot * (math.random() < 0.35 and 0.25 or 1)
		end
		if enRecharge then
			f = f * 0.25
		end
		f = math.max(f, boost)
		for _, u in ipairs(etat.uniques) do
			couleur(u, f)
		end
		if etat.lumiere then
			etat.lumiere.Brightness = 0.5 + 0.6 * f + boost
		end
		for i, anneau in ipairs(etat.numerotes) do
			couleur(anneau, 0.6 + 0.4 * math.max(f, boost))
			local p = anneau.part
			if p.Anchored and p.Parent then -- vue FPS : les anneaux tournent autour du canon
				local sens = (i % 2 == 0) and -1 or 1
				local vitesse = (enRecharge and 0.4 or 1.6) + 9 * boost
				p.CFrame = p.CFrame * CFrame.Angles(sens * vitesse * dt, 0, 0)
			end
		end
	end
end

-- ------------------------------------------------------------------ inspection (F)
-- piste : { temps, position (studs), rotation (degrés) } appliquée au décalage de l'arme
local PISTE_INSPECTION = {
	{ 0.0, Vector3.new(0, 0, 0), Vector3.new(0, 0, 0) },
	{ 0.35, Vector3.new(0.05, 0.08, -0.05), Vector3.new(10, -35, -15) },
	{ 1.2, Vector3.new(0.05, 0.1, -0.05), Vector3.new(14, -45, -20) },
	{ 1.6, Vector3.new(-0.02, 0.06, 0), Vector3.new(-6, 30, 20) },
	{ 2.4, Vector3.new(-0.02, 0.06, 0), Vector3.new(-8, 38, 25) },
	{ 3.0, Vector3.new(0, 0, 0), Vector3.new(0, 0, 0) },
}
local inspection = { actif = false, t = 0 }

local function lisse(x)
	return x * x * (3 - 2 * x)
end

local function bloqueInspection()
	if not joueur then
		return true
	end
	return auLobby() or joueur:GetAttribute("Vise") == true or joueur:GetAttribute("MenuOuvert") == true
end

function EffetsSkins.DecalageInspection(dt, bloque)
	if not inspection.actif then
		return CFrame.new()
	end
	if bloque or bloqueInspection() or not armeLocale or not armeLocale.Parent then
		inspection.actif = false
		return CFrame.new()
	end
	inspection.t += dt
	local t = inspection.t
	local derniere = PISTE_INSPECTION[#PISTE_INSPECTION]
	if t >= derniere[1] then
		inspection.actif = false
		return CFrame.new()
	end
	for i = 1, #PISTE_INSPECTION - 1 do
		local a, b = PISTE_INSPECTION[i], PISTE_INSPECTION[i + 1]
		if t >= a[1] and t < b[1] then
			local k = lisse((t - a[1]) / (b[1] - a[1]))
			local pos = a[2]:Lerp(b[2], k)
			local rot = a[3]:Lerp(b[3], k)
			return CFrame.new(pos) * CFrame.Angles(math.rad(rot.X), math.rad(rot.Y), math.rad(rot.Z))
		end
	end
	return CFrame.new()
end

-- ------------------------------------------------------------------ appels depuis l'arme
function EffetsSkins.AEquipement(modeleArme, arme)
	inspection.actif = false
	if arme then
		armeLocale = arme
		local etat = suivre(arme)
		if etat then
			etat.equipement = os.clock()
		end
	end
end

function EffetsSkins.AuTir(modeleArme, arme, depart, cible)
	inspection.actif = false
	local source = arme or modeleArme
	if not source then
		return
	end
	local etat = arme and suivre(arme)
	if etat then
		etat.flash = os.clock()
	end
	local effet = source:GetAttribute("Effet")
	if not effet or not depart then
		return
	end
	local s = arme and echelle(arme) or 1
	if effet == "Inferno" then
		rafale(depart, 8, {
			Texture = TEX_ETINCELLE,
			Lifetime = NumberRange.new(0.2, 0.5),
			Speed = NumberRange.new(4, 9),
			SpreadAngle = Vector2.new(35, 35),
			Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.12 * s), NumberSequenceKeypoint.new(1, 0) }),
			Color = ColorSequence.new(Color3.fromRGB(255, 200, 90), Color3.fromRGB(255, 70, 10)),
			LightEmission = 1,
			Drag = 4,
		})
	elseif effet == "Apex" then
		-- petit anneau d'énergie à la bouche du canon
		local direction = cible and (cible - depart).Unit or Vector3.new(0, 0, -1)
		local anneau = pieceEffet({
			Shape = Enum.PartType.Cylinder,
			Size = Vector3.new(0.05, 0.3 * s, 0.3 * s),
			Color = Color3.fromRGB(110, 190, 210),
			Transparency = 0.2,
			CFrame = CFrame.lookAt(depart, depart + direction) * CFrame.Angles(0, math.rad(90), 0),
		})
		anneau.Parent = workspace.Terrain
		tween(anneau, 0.15, { Size = Vector3.new(0.02, 0.9 * s, 0.9 * s), Transparency = 1 })
		Debris:AddItem(anneau, 0.2)
	end
end

function EffetsSkins.AuRechargement(modeleArme, arme, duree)
	inspection.actif = false
	local etat = arme and suivre(arme)
	if not etat then
		return
	end
	local t = os.clock()
	etat.rechargeDebut = t
	etat.rechargeFin = t + (duree or 2)
	if etat.effet == "Inferno" then
		local root = arme.PrimaryPart
		local ejection = root and root:FindFirstChild("Ejection")
		if ejection then
			rafale(ejection.WorldPosition, 6, {
				Texture = TEX_FUMEE,
				Lifetime = NumberRange.new(0.6, 1.1),
				Speed = NumberRange.new(0.5, 1.5),
				SpreadAngle = Vector2.new(30, 30),
				Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.2), NumberSequenceKeypoint.new(1, 0.8) }),
				Color = ColorSequence.new(Color3.fromRGB(70, 60, 55)),
				Transparency = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.5), NumberSequenceKeypoint.new(1, 1) }),
				Acceleration = Vector3.new(0, 1.5, 0),
			})
		end
	end
end

-- ------------------------------------------------------------------ élimination (légendaire)
local function effetEliminationApex(position)
	local dossier = Instance.new("Folder")
	dossier.Name = "EffetElimination"
	dossier.Parent = workspace
	Debris:AddItem(dossier, 2)
	local cyan, or_ = Color3.fromRGB(90, 145, 155), Color3.fromRGB(140, 105, 30)

	-- colonne de lumière
	local colonne = pieceEffet({
		Shape = Enum.PartType.Cylinder,
		Size = Vector3.new(14, 1.4, 1.4),
		Color = cyan,
		Transparency = 0.15,
		CFrame = CFrame.new(position + Vector3.new(0, 5, 0)) * CFrame.Angles(0, 0, math.rad(90)),
	})
	colonne.Parent = dossier
	local lumiere = Instance.new("PointLight")
	lumiere.Color = Color3.fromRGB(150, 240, 255)
	lumiere.Range = 16
	lumiere.Brightness = 3
	lumiere.Parent = colonne
	tween(colonne, 0.7, { Size = Vector3.new(14, 0.05, 0.05), Transparency = 1 })
	tween(lumiere, 0.7, { Brightness = 0 })

	-- onde au sol
	local onde = pieceEffet({
		Shape = Enum.PartType.Cylinder,
		Size = Vector3.new(0.15, 1, 1),
		Color = or_,
		Transparency = 0.1,
		CFrame = CFrame.new(position - Vector3.new(0, 2.6, 0)) * CFrame.Angles(0, 0, math.rad(90)),
	})
	onde.Parent = dossier
	tween(onde, 0.6, { Size = Vector3.new(0.05, 16, 16), Transparency = 1 })

	-- éclats qui partent dans toutes les directions
	for i = 1, 16 do
		local dir = Vector3.new(math.random() - 0.5, math.random() * 0.8 + 0.2, math.random() - 0.5).Unit
		local eclat = pieceEffet({
			Size = Vector3.new(0.35, 0.35, 0.35),
			Color = (i % 3 == 0) and or_ or cyan,
			CFrame = CFrame.new(position) * CFrame.Angles(math.random() * 6, math.random() * 6, math.random() * 6),
		})
		eclat.Parent = dossier
		local arrivee = CFrame.new(position + dir * (3 + math.random() * 4))
			* CFrame.Angles(math.random() * 12, math.random() * 12, math.random() * 12)
		tween(eclat, 0.8, { CFrame = arrivee, Size = Vector3.new(0.02, 0.02, 0.02), Transparency = 1 })
	end

	-- poussière d'étincelles
	rafale(position, 40, {
		Texture = TEX_ETINCELLE,
		Lifetime = NumberRange.new(0.5, 1.0),
		Speed = NumberRange.new(6, 14),
		SpreadAngle = Vector2.new(180, 180),
		Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.4), NumberSequenceKeypoint.new(1, 0) }),
		Color = ColorSequence.new(Color3.fromRGB(170, 240, 255), Color3.fromRGB(255, 210, 120)),
		LightEmission = 1,
		Drag = 3,
	})
end

local EFFETS_ELIMINATION = { Apex = effetEliminationApex }

-- info = message de Remotes.Elimination ; il faut les champs ajoutés côté serveur :
-- position (Vector3) et skin (nom du modèle du skin du tueur)
function EffetsSkins.AElimination(info)
	if type(info) ~= "table" or not info.position or not info.skin or auLobby() then
		return
	end
	local armes = ReplicatedStorage:FindFirstChild("Armes")
	local modele = armes and armes:FindFirstChild(info.skin, true)
	local nomEffet = modele and modele:GetAttribute("EffetElimination")
	local effet = nomEffet and EFFETS_ELIMINATION[nomEffet]
	if effet then
		effet(info.position)
	end
end

-- ------------------------------------------------------------------ démarrage (client)
if RunService:IsClient() then
	local function surTag(instance)
		if instance:IsA("Model") then
			task.defer(suivre, instance) -- laisser la copie se placer avant de la lire
		end
	end
	CollectionService:GetInstanceAddedSignal(TAG):Connect(surTag)
	for _, instance in ipairs(CollectionService:GetTagged(TAG)) do
		surTag(instance)
	end

	RunService.RenderStepped:Connect(function(dt)
		local t = os.clock()
		for modele, etat in pairs(suivis) do
			if not modele.Parent or not modele:IsDescendantOf(workspace) then
				suivis[modele] = nil
			else
				animer(etat, t, dt)
			end
		end
	end)

	UserInputService.InputBegan:Connect(function(entree, traite)
		if traite or entree.KeyCode ~= TOUCHE_INSPECTION then
			return
		end
		if armeLocale and armeLocale.Parent and armeLocale:GetAttribute("Inspection") and not bloqueInspection() then
			inspection.actif = true
			inspection.t = 0
		end
	end)

	local remotes = ReplicatedStorage:WaitForChild("Remotes", 10)
	local elimination = remotes and remotes:FindFirstChild("Elimination")
	if elimination then
		elimination.OnClientEvent:Connect(EffetsSkins.AElimination)
	end
end

return EffetsSkins
