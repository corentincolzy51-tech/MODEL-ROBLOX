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
	Phantom = {
		Tir = {
			duree = 0.140,
			evenements = {  },
			Arme = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.030, V(0.000, 0.010, 0.090), V(3.5, 0.6, 0.8), "sortie"},
				{0.140, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Gachette = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.020, V(-0.012, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{0.100, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
		Recharge = {
			duree = 2.250,
			evenements = { {0.420, "ChargeurSort"}, {1.180, "ChargeurEntre"}, {1.300, "Rempli"} },
			Arme = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.300, V(0.050, -0.120, 0.050), V(-6.0, 14.0, -24.0), "doux"},
				{0.450, V(0.050, -0.100, 0.050), V(-4.0, 14.0, -26.0), "sortie"},
				{1.050, V(0.030, -0.150, 0.040), V(-8.0, 12.0, -22.0), "doux"},
				{1.180, V(0.030, -0.090, 0.040), V(-4.0, 12.0, -19.0), "sortie"},
				{1.320, V(0.030, -0.120, 0.040), V(-6.0, 12.0, -21.0), "doux"},
				{1.750, V(0.000, -0.020, 0.000), V(2.0, 2.0, 4.0), "doux"},
				{2.250, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Chargeur = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.400, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.440, V(0.000, -0.060, 0.000), V(0.0, 0.0, 0.0), "entree"},
				{0.800, V(0.100, -1.700, 0.120), V(0.0, 0.0, 28.0), "entree"},
				{0.801, V(0.000, -1.500, 0.300), V(0.0, 0.0, -10.0), "lin"},
				{1.050, V(0.000, -0.220, 0.000), V(0.0, 0.0, -6.0), "sortie"},
				{1.180, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{2.250, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
		RechargeVide = {
			duree = 2.750,
			evenements = { {0.420, "ChargeurSort"}, {1.180, "ChargeurEntre"}, {1.840, "Levier"}, {1.900, "Rempli"} },
			Arme = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.300, V(0.050, -0.120, 0.050), V(-6.0, 14.0, -24.0), "doux"},
				{0.450, V(0.050, -0.100, 0.050), V(-4.0, 14.0, -26.0), "sortie"},
				{1.050, V(0.030, -0.150, 0.040), V(-8.0, 12.0, -22.0), "doux"},
				{1.180, V(0.030, -0.090, 0.040), V(-4.0, 12.0, -19.0), "sortie"},
				{1.320, V(0.030, -0.120, 0.040), V(-6.0, 12.0, -21.0), "doux"},
				{1.550, V(0.020, -0.060, 0.080), V(6.0, -6.0, 10.0), "doux"},
				{1.800, V(0.020, -0.050, 0.130), V(8.0, -6.0, 12.0), "doux"},
				{1.900, V(0.020, -0.020, 0.080), V(3.0, -4.0, 6.0), "sortie"},
				{2.750, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Chargeur = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.400, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.440, V(0.000, -0.060, 0.000), V(0.0, 0.0, 0.0), "entree"},
				{0.800, V(0.100, -1.700, 0.120), V(0.0, 0.0, 28.0), "entree"},
				{0.801, V(0.000, -1.500, 0.300), V(0.0, 0.0, -10.0), "lin"},
				{1.050, V(0.000, -0.220, 0.000), V(0.0, 0.0, -6.0), "sortie"},
				{1.180, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{2.750, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Levier = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{1.550, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{1.760, V(-0.300, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{1.840, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{2.750, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
		Equiper = {
			duree = 0.600,
			evenements = { {0.450, "Levier"} },
			Arme = { cles = {
				{0.000, V(0.250, -0.900, 0.200), V(-55.0, 25.0, 35.0), "doux"},
				{0.360, V(0.000, 0.020, 0.000), V(3.0, -2.0, -3.0), "sortie"},
				{0.600, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Levier = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.320, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.410, V(-0.140, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.450, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{0.600, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
		Inspection = {
			duree = 4.200,
			evenements = { {2.750, "Levier"}, {2.950, "Levier"} },
			Arme = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.550, V(-0.150, 0.050, 0.100), V(8.0, -38.0, 22.0), "doux"},
				{1.600, V(-0.170, 0.060, 0.100), V(10.0, -42.0, 27.0), "doux"},
				{2.250, V(-0.050, 0.000, 0.050), V(-5.0, 25.0, -70.0), "doux"},
				{3.100, V(-0.060, 0.010, 0.060), V(-6.0, 28.0, -75.0), "doux"},
				{3.550, V(0.000, -0.030, 0.000), V(4.0, 0.0, -8.0), "doux"},
				{4.200, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Levier = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{2.600, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{2.780, V(-0.120, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{2.920, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{2.960, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{4.200, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
	},
	Deagle = {
		Tir = {
			duree = 0.160,
			evenements = {  },
			Arme = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.030, V(0.000, 0.030, 0.120), V(14.0, 1.0, 2.0), "sortie"},
				{0.160, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Levier = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.025, V(-0.170, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{0.090, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "entree"},
			} },
			Gachette = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.020, V(-0.010, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{0.100, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
		Recharge = {
			duree = 1.900,
			evenements = { {0.350, "ChargeurSort"}, {1.000, "ChargeurEntre"}, {1.100, "Rempli"} },
			Arme = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.250, V(0.000, -0.080, 0.050), V(10.0, 12.0, -30.0), "doux"},
				{0.400, V(0.000, -0.060, 0.050), V(8.0, 12.0, -32.0), "sortie"},
				{0.950, V(0.000, -0.100, 0.050), V(12.0, 10.0, -28.0), "doux"},
				{1.020, V(0.000, -0.060, 0.050), V(9.0, 10.0, -26.0), "sortie"},
				{1.400, V(0.000, 0.000, 0.000), V(-3.0, 0.0, 4.0), "doux"},
				{1.900, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Chargeur = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.330, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.370, V(0.000, -0.050, 0.000), V(0.0, 0.0, 0.0), "entree"},
				{0.650, V(0.000, -1.300, 0.100), V(0.0, 0.0, 15.0), "entree"},
				{0.651, V(0.000, -1.200, 0.200), V(0.0, 0.0, 0.0), "lin"},
				{0.900, V(0.000, -0.150, 0.000), V(0.0, 0.0, -8.0), "sortie"},
				{1.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{1.900, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
		RechargeVide = {
			duree = 2.200,
			evenements = { {0.350, "ChargeurSort"}, {1.000, "ChargeurEntre"}, {1.460, "Levier"}, {1.500, "Rempli"} },
			Arme = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.250, V(0.000, -0.080, 0.050), V(10.0, 12.0, -30.0), "doux"},
				{0.400, V(0.000, -0.060, 0.050), V(8.0, 12.0, -32.0), "sortie"},
				{0.950, V(0.000, -0.100, 0.050), V(12.0, 10.0, -28.0), "doux"},
				{1.020, V(0.000, -0.060, 0.050), V(9.0, 10.0, -26.0), "sortie"},
				{1.250, V(0.000, -0.040, 0.060), V(6.0, -8.0, 12.0), "doux"},
				{1.420, V(0.000, -0.030, 0.100), V(8.0, -8.0, 14.0), "doux"},
				{1.480, V(0.000, 0.000, 0.050), V(2.0, -4.0, 6.0), "sortie"},
				{2.200, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Chargeur = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.330, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.370, V(0.000, -0.050, 0.000), V(0.0, 0.0, 0.0), "entree"},
				{0.650, V(0.000, -1.300, 0.100), V(0.0, 0.0, 15.0), "entree"},
				{0.651, V(0.000, -1.200, 0.200), V(0.0, 0.0, 0.0), "lin"},
				{0.900, V(0.000, -0.150, 0.000), V(0.0, 0.0, -8.0), "sortie"},
				{1.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{2.200, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Levier = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{1.250, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{1.400, V(-0.170, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{1.460, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{2.200, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
		Equiper = {
			duree = 0.500,
			evenements = {  },
			Arme = { cles = {
				{0.000, V(0.200, -0.700, 0.100), V(-50.0, 20.0, 30.0), "doux"},
				{0.320, V(0.000, 0.015, 0.000), V(2.0, -1.0, -2.0), "sortie"},
				{0.500, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
		Inspection = {
			duree = 4.000,
			evenements = { {2.500, "Levier"}, {2.900, "Levier"} },
			Arme = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.500, V(-0.100, 0.050, 0.050), V(5.0, -30.0, 40.0), "doux"},
				{1.400, V(-0.100, 0.050, 0.050), V(5.0, -35.0, 45.0), "doux"},
				{2.000, V(-0.080, 0.040, 0.050), V(-5.0, 30.0, -60.0), "doux"},
				{2.900, V(-0.080, 0.040, 0.050), V(-5.0, 32.0, -62.0), "doux"},
				{3.400, V(0.000, -0.020, 0.000), V(2.0, 0.0, 0.0), "doux"},
				{4.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Levier = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{2.300, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{2.500, V(-0.090, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{2.800, V(-0.090, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{2.900, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{4.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
	},
	Sniper = {
		Tir = {
			duree = 0.200,
			evenements = {  },
			Arme = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.040, V(0.000, 0.060, 0.220), V(9.0, 1.5, 3.0), "sortie"},
				{0.200, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Gachette = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.020, V(-0.012, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{0.120, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
		Culasse = {
			duree = 1.050,
			evenements = { {0.300, "LevierOuvre"}, {0.550, "Douille"}, {0.920, "LevierFerme"} },
			Arme = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.120, V(0.020, -0.030, 0.030), V(2.0, 4.0, -12.0), "doux"},
				{0.500, V(0.020, -0.050, 0.050), V(3.0, 4.0, -14.0), "doux"},
				{0.900, V(0.010, -0.020, 0.020), V(1.0, 2.0, -6.0), "doux"},
				{1.050, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Levier = { pivot = "Verrou", cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.150, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.300, V(0.000, 0.000, 0.000), V(-58.0, 0.0, 0.0), "doux"},
				{0.550, V(-0.420, 0.000, 0.000), V(-58.0, 0.0, 0.0), "doux"},
				{0.800, V(0.000, 0.000, 0.000), V(-58.0, 0.0, 0.0), "doux"},
				{0.920, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{1.050, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
		Recharge = {
			duree = 3.000,
			evenements = { {0.320, "LevierOuvre"}, {0.950, "ChargeurSort"}, {1.750, "ChargeurEntre"}, {1.800, "Rempli"}, {2.450, "LevierFerme"} },
			Arme = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.250, V(0.020, -0.050, 0.040), V(3.0, 6.0, -14.0), "doux"},
				{0.800, V(0.040, -0.120, 0.050), V(-4.0, 12.0, -22.0), "doux"},
				{1.000, V(0.040, -0.100, 0.050), V(-3.0, 12.0, -24.0), "sortie"},
				{1.650, V(0.040, -0.140, 0.050), V(-6.0, 10.0, -20.0), "doux"},
				{1.780, V(0.040, -0.090, 0.050), V(-3.0, 10.0, -18.0), "sortie"},
				{2.150, V(0.020, -0.050, 0.040), V(3.0, 6.0, -14.0), "doux"},
				{2.500, V(0.010, -0.020, 0.020), V(1.0, 2.0, -5.0), "doux"},
				{3.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Chargeur = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.920, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.960, V(0.000, -0.060, 0.000), V(0.0, 0.0, 0.0), "entree"},
				{1.300, V(0.100, -1.700, 0.100), V(0.0, 0.0, 20.0), "entree"},
				{1.301, V(0.000, -1.500, 0.300), V(0.0, 0.0, 0.0), "lin"},
				{1.620, V(0.000, -0.200, 0.000), V(0.0, 0.0, -5.0), "sortie"},
				{1.750, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{3.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Levier = { pivot = "Verrou", cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.180, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.320, V(0.000, 0.000, 0.000), V(-58.0, 0.0, 0.0), "doux"},
				{0.550, V(-0.420, 0.000, 0.000), V(-58.0, 0.0, 0.0), "doux"},
				{2.150, V(-0.420, 0.000, 0.000), V(-58.0, 0.0, 0.0), "doux"},
				{2.350, V(0.000, 0.000, 0.000), V(-58.0, 0.0, 0.0), "doux"},
				{2.450, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{3.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
		Equiper = {
			duree = 0.750,
			evenements = {  },
			Arme = { cles = {
				{0.000, V(0.300, -1.000, 0.300), V(-50.0, 25.0, 35.0), "doux"},
				{0.500, V(0.000, 0.020, 0.000), V(2.0, -2.0, -2.0), "sortie"},
				{0.750, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
		Inspection = {
			duree = 4.500,
			evenements = { {2.600, "LevierOuvre"}, {3.200, "LevierFerme"} },
			Arme = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.600, V(-0.200, 0.050, 0.150), V(6.0, -32.0, 20.0), "doux"},
				{1.700, V(-0.220, 0.060, 0.150), V(8.0, -36.0, 24.0), "doux"},
				{2.300, V(-0.050, 0.000, 0.100), V(-3.0, 22.0, -55.0), "doux"},
				{3.400, V(-0.060, 0.010, 0.100), V(-4.0, 25.0, -58.0), "doux"},
				{3.900, V(0.000, -0.030, 0.000), V(3.0, 0.0, -6.0), "doux"},
				{4.500, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Levier = { pivot = "Verrou", cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{2.450, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{2.600, V(0.000, 0.000, 0.000), V(-58.0, 0.0, 0.0), "doux"},
				{2.850, V(-0.300, 0.000, 0.000), V(-58.0, 0.0, 0.0), "doux"},
				{3.050, V(0.000, 0.000, 0.000), V(-58.0, 0.0, 0.0), "doux"},
				{3.200, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "sortie"},
				{4.500, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
	},
	Couteau = {
		Equiper = {
			duree = 0.950,
			evenements = {  },
			Arme = { cles = {
				{0.000, V(0.120, -0.600, 0.100), V(-30.0, 10.0, 20.0), "doux"},
				{0.350, V(0.000, 0.020, 0.000), V(2.0, 0.0, 0.0), "sortie"},
				{0.950, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Corps = { pivot = "Anneau", cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 540.0), "doux"},
				{0.750, V(0.000, 0.000, 0.000), V(0.0, 0.0, -8.0), "sortie"},
				{0.950, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
		Inspection = {
			duree = 4.600,
			evenements = {  },
			Arme = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.500, V(-0.120, 0.100, 0.120), V(10.0, -35.0, 30.0), "doux"},
				{1.300, V(-0.130, 0.110, 0.120), V(12.0, -38.0, 32.0), "doux"},
				{2.400, V(-0.100, 0.100, 0.120), V(8.0, -30.0, 26.0), "doux"},
				{3.000, V(-0.060, 0.060, 0.100), V(-6.0, 30.0, -65.0), "doux"},
				{3.800, V(-0.060, 0.060, 0.100), V(-8.0, 32.0, -68.0), "doux"},
				{4.600, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Corps = { pivot = "Anneau", cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{1.300, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{2.200, V(0.000, 0.000, 0.000), V(0.0, 0.0, -720.0), "doux"},
				{2.400, V(0.000, 0.000, 0.000), V(0.0, 0.0, -725.0), "doux"},
				{3.600, V(0.000, 0.000, 0.000), V(0.0, 0.0, -725.0), "doux"},
				{4.200, V(0.000, 0.000, 0.000), V(0.0, 0.0, -1080.0), "doux"},
				{4.600, V(0.000, 0.000, 0.000), V(0.0, 0.0, -1080.0), "doux"},
			} },
		},
		Attaque = {
			duree = 0.450,
			evenements = {  },
			Arme = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.080, V(0.150, 0.050, 0.050), V(10.0, -25.0, -20.0), "sortie"},
				{0.220, V(-0.350, -0.120, -0.150), V(-15.0, 45.0, 40.0), "sortie"},
				{0.450, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
		Attaque2 = {
			duree = 0.500,
			evenements = {  },
			Arme = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.090, V(-0.120, 0.080, 0.050), V(12.0, 30.0, 25.0), "sortie"},
				{0.240, V(0.300, -0.150, -0.120), V(-20.0, -40.0, -35.0), "sortie"},
				{0.500, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
		},
		AttaqueLourde = {
			duree = 0.850,
			evenements = {  },
			Arme = { cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.180, V(0.050, 0.050, 0.250), V(15.0, -10.0, -10.0), "doux"},
				{0.340, V(-0.050, -0.020, -0.550), V(-8.0, 5.0, 5.0), "sortie"},
				{0.850, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
			} },
			Corps = { pivot = "Anneau", cles = {
				{0.000, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.100, V(0.000, 0.000, 0.000), V(0.0, 0.0, 0.0), "doux"},
				{0.300, V(0.000, 0.000, 0.000), V(0.0, 0.0, 360.0), "sortie"},
				{0.850, V(0.000, 0.000, 0.000), V(0.0, 0.0, 360.0), "doux"},
			} },
		},
	},
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
