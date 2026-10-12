--[[
	AnimationsRealistes (ModuleScript) — ReplicatedStorage › Modules › AnimationsRealistes

	Animations par images clés des armes réalistes (« <Arme> R ») : rechargement, rechargement
	à vide, équipement, inspection, tir, réarmement du sniper, attaques et tours du karambit.
	Aucune Animation Roblox : comme le reste du jeu, tout est fait en déplaçant l'arme et ses
	sous-modèles (Chargeur, Levier, Gachette, Corps).

	Utilisation (à l'intérieur des fonctions existantes d'ArmeFPS, sans nouvelle variable
	locale au niveau principal) :

		-- démarrer (ex. dans lancerRecharge) ; renvoie nil si l'animation n'existe pas pour cette arme
		lectureAnim = require(ReplicatedStorage.Modules.AnimationsRealistes).Jouer("Phantom", "Recharge", arme)

		-- chaque image (ex. dans miseAJour) :
		local decal, evenements, fini = lectureAnim:Avancer(dt)
		-- decal : CFrame à multiplier dans la chaîne du décalage de l'arme
		--         (local decalage = decalageChangement * pose * bob * decal)
		-- evenements : noms passés pendant cette image : "ChargeurSort", "ChargeurEntre", "Rempli",
		--              "Levier", "LevierOuvre", "LevierFerme", "Douille" -> jouer les sons, remplir le chargeur...
		lectureAnim:AppliquerPieces()   -- après le placement de l'arme : bouge Chargeur / Levier / Gachette / Corps
		if fini then lectureAnim:Remettre() lectureAnim = nil end

	Animations : Phantom, Deagle, Sniper -> Tir, Recharge, RechargeVide (pas le sniper), Equiper,
	Inspection, Culasse (sniper : réarmement après chaque tir) ; Couteau -> Equiper, Inspection,
	Attaque, Attaque2, AttaqueLourde.

	Repères : voir scripts/real/anims.py (source des tables ci-dessous, ne pas modifier à la main).
	  - Arme : repère caméra (X droite, Y haut, Z vers la caméra), degrés.
	  - pièces : repère de l'arme (X vers le canon, Y haut, Z côté droit), calculé à partir des pièces.
	  - pivot « Anneau » (karambit) / « Verrou » (sniper) : Attachments du Root posés par le script
	    d'installation des armes réalistes.
]]

local V = Vector3.new
local ANIMS = {
--@@ANIMS@@
}

local A = {}
local GROUPES = { "Chargeur", "Levier", "Gachette", "Corps" }

local function lissage(e, x)
	if e == "lin" then
		return x
	elseif e == "sortie" then
		return 1 - (1 - x) ^ 3
	elseif e == "entree" then
		return x ^ 3
	elseif e == "ressort" then
		local c1 = 1.70158
		return 1 + (c1 + 1) * (x - 1) ^ 3 + c1 * (x - 1) ^ 2
	end
	return x * x * (3 - 2 * x)
end

local function echantillon(cles, t)
	if t <= cles[1][1] then
		return cles[1][2], cles[1][3]
	end
	for i = 1, #cles - 1 do
		local a, b = cles[i], cles[i + 1]
		if t < b[1] then
			local x = lissage(b[4], (t - a[1]) / math.max(b[1] - a[1], 1e-6))
			return a[2]:Lerp(b[2], x), a[3]:Lerp(b[3], x)
		end
	end
	local d = cles[#cles]
	return d[2], d[3]
end

local function versCFrame(p, r)
	return CFrame.new(p) * CFrame.Angles(math.rad(r.X), math.rad(r.Y), math.rad(r.Z))
end

-- repère de l'arme à partir de ses pièces (comme le script d'installation)
local function repereArme(modele)
	local parts = {}
	for _, d in ipairs(modele:GetDescendants()) do
		if d:IsA("BasePart") and d.Name ~= "Root" then
			table.insert(parts, d)
		end
	end
	if #parts == 0 then
		return nil
	end
	local base = parts[1].CFrame.Rotation
	local mini, maxi = V(math.huge, math.huge, math.huge), V(-math.huge, -math.huge, -math.huge)
	local function centre(g)
		if not g then
			return nil
		end
		local s, n = V(), 0
		for _, d in ipairs(g:GetDescendants()) do
			if d:IsA("BasePart") then
				s += d.Position
				n += 1
			end
		end
		return if n > 0 then s / n else nil
	end
	for _, p in ipairs(parts) do
		local h = p.Size / 2
		for _, sx in ipairs({ -1, 1 }) do
			for _, sy in ipairs({ -1, 1 }) do
				for _, sz in ipairs({ -1, 1 }) do
					local c = base:PointToObjectSpace(p.CFrame:PointToWorldSpace(V(h.X * sx, h.Y * sy, h.Z * sz)))
					mini = mini:Min(c)
					maxi = maxi:Max(c)
				end
			end
		end
	end
	local taille = maxi - mini
	local milieu = base:PointToWorldSpace((mini + maxi) / 2)
	local axes = { { v = base.XVector, s = taille.X }, { v = base.YVector, s = taille.Y }, { v = base.ZVector, s = taille.Z } }
	table.sort(axes, function(a, b)
		return a.s > b.s
	end)
	local avant, haut = axes[1].v, axes[2].v
	local chargeur, gachette = centre(modele:FindFirstChild("Chargeur")), centre(modele:FindFirstChild("Gachette"))
	if not chargeur and not gachette then
		return CFrame.fromMatrix(milieu, base.XVector, base.YVector)
	end
	if chargeur and (chargeur - milieu):Dot(haut) > 0 then
		haut = -haut
	end
	if gachette and (gachette - milieu):Dot(avant) > 0 then
		avant = -avant
	end
	return CFrame.fromMatrix(milieu, avant, haut)
end

-- ------------------------------------------------------------------ lecture
local Lecture = {}
Lecture.__index = Lecture

function A.Existe(arme, nom)
	return ANIMS[arme] ~= nil and ANIMS[arme][nom] ~= nil
end

function A.Duree(arme, nom)
	local d = ANIMS[arme] and ANIMS[arme][nom]
	return d and d.duree or 0
end

-- arme : "Phantom" / "Deagle" / "Sniper" / "Couteau" ; modele : la copie FPS (facultatif)
function A.Jouer(arme, nom, modele)
	local d = ANIMS[arme] and ANIMS[arme][nom]
	if not d then
		return nil
	end
	return setmetatable({ d = d, t = 0, modele = modele, repos = nil }, Lecture)
end

function Lecture:Avancer(dt)
	local t0 = self.t
	self.t = math.min(self.t + dt, self.d.duree)
	local ev = {}
	for _, e in ipairs(self.d.evenements) do
		if e[1] > t0 and e[1] <= self.t then
			table.insert(ev, e[2])
		end
	end
	local cf = CFrame.new()
	if self.d.Arme then
		cf = versCFrame(echantillon(self.d.Arme.cles, self.t))
	end
	return cf, ev, self.t >= self.d.duree
end

function Lecture:_preparer(modele)
	local root = modele.PrimaryPart or modele:FindFirstChild("Root")
	if not root then
		return false
	end
	local repere = repereArme(modele)
	if not repere then
		return false
	end
	self.root = root
	self.repereRel = root.CFrame:ToObjectSpace(repere)
	self.repos = {}
	for _, nomG in ipairs(GROUPES) do
		local g = modele:FindFirstChild(nomG)
		if g and self.d[nomG] then
			self.repos[nomG] = { g = g, rel = root.CFrame:ToObjectSpace(g:GetPivot()) }
		end
	end
	return true
end

-- Bouge les sous-modèles selon l'animation (à appeler après le placement de l'arme dans l'image)
function Lecture:AppliquerPieces(modele)
	modele = modele or self.modele
	if not modele or not modele.Parent then
		return
	end
	if not self.repos and not self:_preparer(modele) then
		return
	end
	local root = self.root
	local repere = root.CFrame * self.repereRel
	for nomG, info in pairs(self.repos) do
		local piste = self.d[nomG]
		local p, r = echantillon(piste.cles, self.t)
		local reposMonde = root.CFrame * info.rel
		local centre
		local att = piste.pivot and root:FindFirstChild(piste.pivot, true)
		if att and att:IsA("Attachment") then
			centre = repere:PointToObjectSpace(att.WorldPosition)
		else
			centre = repere:PointToObjectSpace(reposMonde.Position)
		end
		local m = CFrame.new(p) * CFrame.new(centre) * CFrame.Angles(math.rad(r.X), math.rad(r.Y), math.rad(r.Z))
			* CFrame.new(-centre)
		info.g:PivotTo(repere * m * repere:ToObjectSpace(reposMonde))
	end
end

-- Remet les sous-modèles à leur place (fin ou annulation de l'animation)
function Lecture:Remettre()
	if not self.repos or not self.root or not self.root.Parent then
		return
	end
	for _, info in pairs(self.repos) do
		info.g:PivotTo(self.root.CFrame * info.rel)
	end
end

return A
