--[[
	Installe le skin « Phantom Sakura » (VANTA AR-01) à partir du FBX importé.

	1. Importe weapons/VANTA_AR-01/Sakura/Phantom_Sakura.fbx
	   (Accueil > Importer 3D, « Scale Unit » = Stud).
	2. Sélectionne le modèle importé dans l'Explorer.
	3. Colle tout ce script dans la barre de commande (Affichage > Barre de commande), puis Entrée.

	Le script :
	  - range les pièces comme « Phantom P » : Corps / Chargeur / Gachette / Levier + Root
	  - met les couleurs (une couleur par pièce) et le néon du viseur
	  - remet l'arme à 3,616 studs de long si l'import l'a mise à une autre taille
	  - copie depuis Phantom P : le Root (même orientation, avec ses Attachments),
	    le dossier Sons, les autres objets et les attributs, les réglages des pièces
	    et les soudures
	  - range le résultat dans ReplicatedStorage.Armes.Phantom, aligné sur Phantom P
]]

local NOM = "Phantom Sakura"
local LONGUEUR = 3.616 -- studs, sans les contours

local COULEURS = {
	Sakura = Color3.fromRGB(255, 255, 255), -- blanc pour ne pas teinter la texture
	Blanc = Color3.fromRGB(245, 241, 245),
	Rose = Color3.fromRGB(255, 92, 168),
	Noir = Color3.fromRGB(30, 26, 34),
	Lentille = Color3.fromRGB(255, 120, 200),
	Contour = Color3.fromRGB(14, 10, 16),
}
local GROUPES = { Body = "Corps", Magazine = "Chargeur", Trigger = "Gachette", ChargingHandle = "Levier" }
local NOMS_GROUPES = { Corps = true, Chargeur = true, Gachette = true, Levier = true, Root = true }

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Selection = game:GetService("Selection")

local source = Selection:Get()[1]
assert(source, "Sélectionne d'abord le modèle importé (Phantom Sakura) dans l'Explorer")

local armes = ReplicatedStorage:FindFirstChild("Armes")
local dossier = armes and armes:FindFirstChild("Phantom")
local reference = dossier and dossier:FindFirstChild("Phantom P")
local refRoot = reference and reference:FindFirstChild("Root")

local function premierMeshPart(conteneur)
	if not conteneur then
		return nil
	end
	for _, d in ipairs(conteneur:GetDescendants()) do
		if d:IsA("MeshPart") then
			return d
		end
	end
	return nil
end
local modeleRef = premierMeshPart(reference)

-- 1) récupérer les pièces importées (noms nettoyés d'éventuels suffixes)
local pieces = {}
for _, d in ipairs(source:GetDescendants()) do
	if d:IsA("BasePart") then
		local nom = d.Name:match("^[%w_]+")
		pieces[nom] = d
	end
end
local marqueur = pieces.Root
assert(marqueur, "Pièce « Root » introuvable : as-tu bien sélectionné le modèle importé ?")

-- 2) nouveau modèle avec la même structure que Phantom P
local arme = Instance.new("Model")
arme.Name = NOM
local groupes = {}
for prefixe, nomGroupe in pairs(GROUPES) do
	local g = Instance.new("Model")
	g.Name = nomGroupe
	g.Parent = arme
	groupes[prefixe] = g
end

for nom, part in pairs(pieces) do
	if nom ~= "Root" then
		local prefixe = nom:match("^(%a+)")
		local couleur = nom:match("_(%a+)$") or "Blanc"
		part.Name = nom
		part.Color = COULEURS[couleur] or COULEURS.Blanc
		part.Material = if couleur == "Lentille" then Enum.Material.Neon else Enum.Material.SmoothPlastic
		part.CastShadow = couleur ~= "Contour" and couleur ~= "Lentille"
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
end

-- 3) Root : celui de Phantom P (mêmes Attachments/réglages), posé sur la poignée
local root
if refRoot then
	root = refRoot:Clone()
	for _, d in ipairs(root:GetDescendants()) do
		if d:IsA("JointInstance") or d:IsA("WeldConstraint") then
			d:Destroy()
		end
	end
else
	root = Instance.new("Part")
	root.Size = Vector3.new(0.2, 0.2, 0.2)
	root.Transparency = 1
	root.CanCollide = false
	root.Anchored = true
end
root.Name = "Root"
local rotation = marqueur.CFrame.Rotation
if refRoot and modeleRef then
	-- même orientation du Root par rapport à l'arme que dans Phantom P
	rotation = rotation * modeleRef.CFrame.Rotation:ToObjectSpace(refRoot.CFrame.Rotation)
end
root.CFrame = CFrame.new(marqueur.Position) * rotation
root.Parent = arme
arme.PrimaryPart = root
marqueur:Destroy()

-- 4) taille : l'arme (sans contours) doit faire LONGUEUR studs
local function longueurArme()
	local mini = Vector3.new(math.huge, math.huge, math.huge)
	local maxi = -mini
	for _, p in ipairs(arme:GetDescendants()) do
		if p:IsA("BasePart") and p ~= root and not p.Name:find("Contour") then
			local h = p.Size / 2
			for _, sx in ipairs({ -1, 1 }) do
				for _, sy in ipairs({ -1, 1 }) do
					for _, sz in ipairs({ -1, 1 }) do
						local coin = p.CFrame:PointToWorldSpace(Vector3.new(h.X * sx, h.Y * sy, h.Z * sz))
						local c = root.CFrame:PointToObjectSpace(coin)
						mini = mini:Min(c)
						maxi = maxi:Max(c)
					end
				end
			end
		end
	end
	local t = maxi - mini
	return math.max(t.X, t.Y, t.Z)
end
local avant = longueurArme()
if math.abs(avant - LONGUEUR) > 0.02 then
	arme:ScaleTo(arme:GetScale() * LONGUEUR / avant)
end

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

-- 6) placement : Root de Sakura sur le Root de Phantom P
if refRoot then
	arme:PivotTo(refRoot.CFrame)
else
	arme:PivotTo(CFrame.new(source:GetPivot().Position))
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

arme.Parent = dossier or workspace
source:Destroy()
Selection:Set({ arme })
print(string.format("[Phantom Sakura] installé dans %s | longueur %.3f -> %.3f studs | soudures : %s",
	arme.Parent:GetFullName(), avant, longueurArme(), tostring(soude)))
