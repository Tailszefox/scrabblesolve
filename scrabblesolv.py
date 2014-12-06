#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os.path
import time

# Classe Arbre utilisée pour le dictionnaire
from binaire import Arbre

# Module colorama utilisé pour l'affichage de la grille
from colorama import init
from colorama import Fore, Back, Style

###
# Classe Lettre : représente une lettre (ou un groupe de lettres) dans la grille
###

class Lettre(object):
	
	"""
	Constructeur
	
	lettre : lettre ou groupe de lettres
	x : emplacement horizontal de la première lettre du groupe
	y : emplacement vertical de la première lettre du groupe
	horizontal : True si un mot peut être rajouté à l'horizontale en utilisant 'lettre', False pour la verticale
	maxGauche : position maximale que peut avoir 'lettre' à partir de la gauche dans un nouveau mot
	maxDroite : position maximale que peut avoir 'lettre' à partir de la droite dans un nouveau mot
	longueur : longueur maximale du mot comprenant 'lettre' pouvant être inséré
	valeur : valeur actuelle de 'lettre'
	"""
	def __init__(self, lettre, x, y, horizontal, maxGauche, maxDroite, longueur, valeur):
		# Les jokers sont représentés en interne par un point
		lettre = lettre.replace('#', '.')
		
		self.lettre = lettre
		self.x = x
		self.y = y
		self.horizontal = horizontal
		self.maxGauche = maxGauche
		self.maxDroite = maxDroite
		self.longueur = longueur
		self.valeur = valeur

	# Comparaison de deux instances pour classement
	def __cmp__(self, other):
		# Les groupes d'une lettre sont classés différemment
		if(len(self.getLettre()) == 1 and len(other.getLettre()) == 1):
			return (other.getValeur() - self.getValeur())
		return (self.getValeur() - other.getValeur())
		
	# Getters
	def getLettre(self):
		return self.lettre
		
	def getLongueur(self):
		return self.longueur
	
	def getMaxGauche(self):
		return self.maxGauche
		
	def getMaxDroite(self):
		return self.maxDroite
		
	def getValeur(self):
		return self.valeur

###
# Classe Grille: contient la grille de Scrabble
###

class Grille(object):
	
	# Construit une grille chargée depuis un fichier
	def __init__(self, chemin):
		
		self.grille = []			# Matrice représentant la grille
		self.vide = True		# True si la grille est vide (aucune lettre)
		self.places = []		# Contiendra les lettres nouvellement placées sur la grille
		
		fichierGrille = open(chemin)
		
		i = 0
		total = 0
		
		ligne = []
		self.grille.append(ligne)
		
		# Pour chaque lettre du fichier
		for e in fichierGrille:
			lettre = e.strip()
			# Création d'une nouvelle ligne dans la matrice toutes les 15 cases
			if i == 15:
				i = 0
				ligne = []
				self.grille.append(ligne)
				
			i += 1
			total += 1
			ligne.append(lettre)
			
			# Il s'agit d'une lettre, la grille n'est donc pas vide
			if(lettre != '.' and not lettre.isdigit()):
				self.vide = False
		
		# Pas assez de cases, le fichier est invalide
		if(total < 225):
			sys.exit("Le fichier " + chemin + " n'est pas un fichier de grille valide.") 
		
		fichierGrille.close()
	
	# Renvoie vrai si la grille est vide
	def grilleEstVide(self):
		return self.vide
	
	# Affichage de la grille
	def afficher(self):
		
		# Initialisation de l'affichage
		init()
		
		# Codes couleurs et styles
		gras = Style.BRIGHT
		nouvelle = Back.RED
		rouge = Fore.RED
		magenta = Fore.MAGENTA
		bleu = Fore.BLUE
		cyan = Fore.CYAN
		reset = Style.RESET_ALL
		
		for x in range(0, 15):
			for y in range(0, 15):
				
				# Si la case actuelle est vide
				if(self.estVide(x, y)):
					if(self.grille[x][y] == '2'):
						print cyan + self.grille[x][y].upper() + reset,
					elif(self.grille[x][y] == '3'):
						print bleu + self.grille[x][y].upper() + reset,
					elif(self.grille[x][y] == '4'):
						print magenta + self.grille[x][y].upper() + reset,
					elif(self.grille[x][y] == '5'):
						print rouge + self.grille[x][y].upper() + reset,
					else:
						print self.grille[x][y].upper(),
				else:
					# Si la lettre vient d'être placée, on la met en valeur
					if((x, y) in self.places):
						print gras + nouvelle + self.grille[x][y].upper() + reset,
					else:
						print gras + self.grille[x][y].upper() + reset,
			
			# Retour à la ligne après affichage de chaque ligne
			print ""
			
	# Mise à jour de la grille dans le fichier
	def update(self, chemin):
		fichier = open(chemin, 'w')
		
		for x in self.grille:
			for y in x:
				fichier.write(y.upper() + "\n")
			
		fichier.close()
	
	# Renvoie Vrai si une case est vide
	def estVide(self, x, y):
		# On considère les cases non-existantes comme vides
		if(x < 0 or x >= 15 or y < 0 or y >= 15):
			return True
			
		if(self.grille[x][y] == '.' or self.grille[x][y].isdigit()):
			return True
			
		return False
	
	# Renvoie une liste de Lettres disponibles pour réutilisation
	def disponibles(self, valeurs):
		disponibles = []
		motHorizontal = ""
		motHorizontalX = 0
		motHorizontalY = 0
		
		motVertical = ""
		motVerticalX = 0
		motVerticalY = 0
		
		# Parcours de la grille
		for x in range(0, 15):
			for y in range(0, 15):
				if(not self.estVide(x, y)):
					
					motHorizontal += self.grille[x][y]
					motHorizontalX = x
					motHorizontalY = y
					
					# Il ne doit rien y avoir dans les diagonales de la lettre pour qu'elle soit considérée comme réutilisable
					if(self.estVide(x + 1, y + 1) and self.estVide(x + 1, y - 1) and self.estVide(x - 1, y + 1) and self.estVide(x - 1, y - 1)):
						
						# La lettre ne doit pas être entourée dans une des deux dimensions pour être réutilisable
						if (self.estVide(x + 1, y) and self.estVide(x - 1, y)) or (self.estVide(x, y + 1) and self.estVide(x, y -1)):
						
							# La lettre peut-elle être réutilisée pour former un mot à la verticale ou à l'horizontal ?
							if(self.estVide(x, y-1) and self.estVide(x, y+1)):
								horizontal = True
							else:
								horizontal = False
							
							# maxGauche : À partir de la gauche, position maximale de la lettre
							# maxDroite : À partir de la droite, position maximale de la lettre
							maxGauche = self.calculerEspace(x, y, horizontal, -1)
							maxDroite = self.calculerEspace(x, y, horizontal, 1)
							
							# Calcul de la longueur maximale que peut avoir le mot formé à partir de la lettre
							if(maxGauche == 0):
								longueur = maxDroite
								
							elif(maxDroite == 0):
								longueur = maxGauche
							
							else:
								longueur = (maxGauche - 1) + (maxDroite - 1) + 1
							
							# On rajoute la lettre dans notre liste de lettres réutilisables
							lettreDisponible = Lettre(self.grille[x][y], x, y, horizontal, maxGauche, maxDroite, longueur, calculerPoints(self.grille[x][y], valeurs))
							disponibles.append(lettreDisponible)
				
				# On considère aussi les mots, que l'on peut compléter à l'horizontal
				elif(motHorizontal != ""):
					# Si le mot fait plus d'une lettre (sans quoi il s'agit d'une lettre isolée qui a déjà été ajoutée)
					if(len(motHorizontal) > 1):
						motHorizontalY = motHorizontalY - len(motHorizontal) + 1
						
						maxGauche = self.calculerEspace(motHorizontalX, motHorizontalY, True, -1, len(motHorizontal))
						maxDroite = self.calculerEspace(motHorizontalX, motHorizontalY, True, 1, len(motHorizontal))
						
						if(maxGauche == 0):
							longueur = maxDroite
								
						elif(maxDroite == 0):
							longueur = maxGauche
							
						else:
							longueur = (maxGauche - 1) + (maxDroite - 1) + 1
						
						lettreDisponible = Lettre(motHorizontal, motHorizontalX, motHorizontalY, True, maxGauche, maxDroite, longueur, calculerPoints(motHorizontal, valeurs))
						disponibles.append(lettreDisponible)
						
					motHorizontal = ""
				
			# On s'occupe du mot horizontal actuel avant de passer à la ligne suivante
			if(motHorizontal != ""):
				if(len(motHorizontal) > 1):
					motHorizontalY = motHorizontalY - len(motHorizontal) + 1
				
					maxGauche = self.calculerEspace(motHorizontalX, motHorizontalY, True, -1, len(motHorizontal))
					maxDroite = self.calculerEspace(motHorizontalX, motHorizontalY, True, 1, len(motHorizontal))
				
					if(maxGauche == 0):
						longueur = maxDroite
					
					elif(maxDroite == 0):
						longueur = maxGauche
						
					else:
						longueur = (maxGauche - 1) + (maxDroite - 1) + 1
						
					lettreDisponible = Lettre(motHorizontal, motHorizontalX, motHorizontalY, True, maxGauche, maxDroite, longueur, calculerPoints(motHorizontal, valeurs))
					disponibles.append(lettreDisponible)
					
				motHorizontal = ""
		
		# Parcours de la grille verticalement pour les mots à la verticale
		for y in range(0, 15):
			for x in range(0, 15):
				if(not self.estVide(x, y)):
					motVertical += self.grille[x][y]
					motVerticalX = x
					motVerticalY = y
					
				elif(motVertical != ""):
					if(len(motVertical) > 1):
						motVerticalX = motVerticalX - len(motVertical) + 1
						
						maxGauche = self.calculerEspace(motVerticalX, motVerticalY, False, -1, len(motVertical))
						maxDroite = self.calculerEspace(motVerticalX, motVerticalY, False, 1, len(motVertical))
						
						if(maxGauche == 0):
							longueur = maxDroite
							
						elif(maxDroite == 0):
							longueur = maxGauche
								
						else:
							longueur = (maxGauche - 1) + (maxDroite - 1) + 1
								
						lettreDisponible = Lettre(motVertical, motVerticalX, motVerticalY, False, maxGauche, maxDroite, longueur, calculerPoints(motVertical, valeurs))
						disponibles.append(lettreDisponible)
						
					motVertical = ""
			
			# On s'occupe du mot vertical actuel avant de passer à la colonne suivante
			
			if(motVertical != ""):
				if(len(motVertical) > 1):
					motVerticalX = motVerticalX - len(motVertical) + 1
					
					maxGauche = self.calculerEspace(motVerticalX, motVerticalY, False, -1, len(motVertical))
					maxDroite = self.calculerEspace(motVerticalX, motVerticalY, False, 1, len(motVertical))
					
					if(maxGauche == 0):
						longueur = maxDroite
						
					elif(maxDroite == 0):
						longueur = maxGauche
							
					else:
						longueur = (maxGauche - 1) + (maxDroite - 1) + 1
							
					lettreDisponible = Lettre(motVertical, motVerticalX, motVerticalY, False, maxGauche, maxDroite, longueur, calculerPoints(motVertical, valeurs))
					disponibles.append(lettreDisponible)
					
				motVertical = ""
					
		return disponibles
	
	
	# Calcule l'espace disponible pour rajouter des lettres dans le sens donné à partir d'une case
	# x, y : coordonnées de la case de départ
	# horizontal : True si la recherche doit se faire à l'horizontale, False pour la verticale
	# sens : -1, gauche ou haut ; 1, droite ou bas (selon la valeur de 'horizontal')
	# longueurMot : longueur du mot déjà en place (x et y représentent la première lettre de ce mot)
	
	def calculerEspace(self, x, y, horizontal, sens, longueurMot = 1):
		
		espace = 0
		
		# Mot à placer à l'horizontale
		if(horizontal):
			if(sens == 1):
				y += longueurMot
			else:
				y -= 1
				
			# Une lettre peut être placée tant que la case actuelle est vide,
			# et que les cases situées en haut et en bas sont également vides
			while(y >= 0 and y < 15 and self.estVide(x, y) and self.estVide(x - 1, y) and self.estVide(x + 1, y)):
				espace += 1
				y += sens
			
			if(y == -1 or y == 15):
				return espace + 1
			else:
				return espace
		
		# Mot à placer à la verticale
		if(sens == 1):
			x += longueurMot
		else:
			x -= 1
		
		# Même méthode que pour un mot à l'horizontal,
		# mais avec une recherche de cases vides à gauche et à droite
		while(x >= 0 and x < 15 and self.estVide(x, y) and self.estVide(x, y - 1) and self.estVide(x, y + 1)):
			espace += 1
			x += sens
			
		if(x == -1 or x == 15):
			return espace + 1
		else:
			return espace
		
	
	"""
	Place le mot donné sur la grille, et retourne le nombre de points gagnés
	
	mot : Mot à placer (sous la forme d'un tableau comportant le vrai mot et le mot comportant un joker si besoin)
	points : valeur des jetons
	tirage : tirage actuel afin de pouvoir en retirer les lettres placées
	options : liste des options actives
	ligne, colonne : coordonnées où placer la première lettre du mot
	horizontal : True si le mot est à placer à l'horizontale, False s'il est à placer à la verticale
	"""
	
	def placer(self, motSet, points, tirage, options, ligne = 7, colonne = 7, horizontal = True):
		total = 0
		motDouble = 0
		motTriple = 0
		affichagePoints = ""
		longueurTirageInitial = len(tirage)

		vraiMot = motSet[0]
		motTirage = motSet[1]
		
		# Construction de la chaine affichée quand l'option -points est activée
		affichagePoints += "Le mot " + motTirage.replace('.', '#')

		if(vraiMot != motTirage):
			affichagePoints += " (" + vraiMot +  ")"

		affichagePoints += " rapporte "
		
		# Pour chaque lettre du mot à ajouter
		i = 0

		while i < len(motTirage):
			l = motTirage[i];

			# Calcul du total des points rapportés par le mot
			affichagePoints +=  "("+ l +" vaut "+ str(points[l]) +") "
			
			# Application de multiplicateur lettre
			if(self.grille[ligne][colonne] == '2'):
				valeur = points[l] * 2
				affichagePoints += "(" + l + " lettre compte double soit " + str(valeur) + ") "
			elif(self.grille[ligne][colonne] == '3'):
				valeur = points[l] * 3
				affichagePoints += "(" + l + " lettre compte triple soit "+ str(valeur) +") "
			else:
				# Détection des multiplicateurs mot
				if(self.grille[ligne][colonne] == '4'):
					motDouble += 1
					
				elif(self.grille[ligne][colonne] == '5'):
					motTriple += 1
					
				valeur = points[l]
			total += valeur
			
			# Placement de la lettre dans la grille, si la case est vide
			if(self.estVide(ligne, colonne)):
				self.places.append((ligne, colonne))
				tirage.remove(l)
				# S'il s'agissait d'un joker, on pose la vrai elettre
				if(l == "."):
					self.grille[ligne][colonne] = vraiMot[i]
				else:
					self.grille[ligne][colonne] = l

			if(horizontal):
				colonne += 1
			else:
				ligne += 1

			i += 1
		
		affichagePoints += "(soit "+ str(total) + ") "
		
		# Application des multiplicateurs mot
		if(motDouble > 0):
			total *= 2 * motDouble
			affichagePoints += "(" + str(motDouble) +  " mot compte double) "
		if(motTriple > 0):
			total *= 3 * motTriple
			affichagePoints += "(" + str(motTriple) +  " mot compte triple) "
		
		# Si on a utilisé les 7 lettres de son tirage, on gagne un bonus
		if(len(tirage) == 0 and longueurTirageInitial == 7):
			affichagePoints += "(bonus de 50 points) "
			total += 50
		
		affichagePoints += str(total) + " points."
		
		if(options['points']):
			print affichagePoints
			
		return total

###
# Classe Tirage : liste des lettres tirées par le joueur
###

class Tirage(object):
	# Création d'une instance à partir d'un fichier
	def __init__(self, chemin):
		fichierTirage = open(chemin)
		self.tirage = []
		
		# Pour chaque lettre du tirage
		for t in fichierTirage:
			t = t.strip()
			
			# Les jokers sont représentés en interne par un point
			if t == '#' :
				t = '.'
				
			# Ignorer les lignes vides
			if(t):
				self.tirage.append(t)
		
		fichierTirage.close()
		
		if(len(self.tirage) == 0 or len(self.tirage) > 7):
			sys.exit("Le fichier " + chemin + " n'est pas un fichier de tirage valide.")
		
	# Mise à jour du fichier
	def update(self, chemin):
		fichier = open(chemin, 'w')
		
		for l in self.tirage:
			fichier.write(l + "\n")
			
		fichier.close()

#######################

# Charge la valeur des jetons
def chargerPoints():
	try:
		fichierPoints = open('./properties')
	except:
		sys.exit("Impossible de charger le fichier properties.")
		
	# Tableau associatif : points['A'] contient le nombre de points rapportés par la lettre A, etc.
	points = {}
	
	# 'A' en ASCII
	lettre = 65
	
	# Parcours du fichier en ajoutant dans le tableau la valeur de chaque lettre
	for p in fichierPoints:
		points[chr(lettre)] = int(p.strip())
		lettre += 1
	
	# Valeur du joker
	points['.'] = 0
	points['#'] = 0
	
	fichierPoints.close()
	return points

"""
Cherche les mots existants à partir du tirage

tL : partie gauche (qui sera recherchée), liste de lettres ou de groupes de lettres
q : partie droite (qui sera utilisée récursivement pour completer la partie gauche)
obligatoire : Objet Lettre, contenant une chaine qui doit se trouver dans tL pour que le mot soit valide (correspond à la chaine vide pour une grille vide)
tEntiere : partie gauche entière (représente le mot complet actuellement recherché)
suivants : nœuds de l'arbre binaire à partir desquels lancer la recherche
dico : dictionnaire dans lequel rechercher
points : correspondance lettres/points
resultat : liste des mots valides trouvés, avec les points qu'ils rapportent
"""

def rechercherNoTime(tL, q, obligatoire, tEntiere, suivants, dico, points, resultat):
	
	# Chaine formée à partir de la liste tL
	t = ''.join(tL)
	
	# Chaine formée à partir de tEntiere
	cEntiere = ''.join(tEntiere)
	
	longueur = len(tEntiere)
	
	# 'obligatoire' fait partie de 'tEntiere'
	try:
		posGauche =  tEntiere.index(obligatoire.getLettre()) + 1
		posDroite = longueur - posGauche + 1
		
	# 'obligatoire' ne fait pas partie de 'tEntiere'
	except:
		posGauche = 0
		posDroite = 0
	
	# Le mot actuel ne respecte pas les conditions imposées par l'objet Lettre 'obligatoire'
	# (le mot est trop long pour être placé, par exemple)
	# Il est dans ce cas inutile de continuer la recherche à partir d'ici
	if(longueur > obligatoire.getLongueur() or posGauche > obligatoire.getMaxGauche() or posDroite > obligatoire.getMaxDroite() or 
		(len(obligatoire.getLettre()) > 2 and posGauche > 1 and posDroite > 1)):
		return

	# Si le mot recherché comporte au moins deux lettres (le dictionnaire ne contient pas de mots de une lettre)
	if(len(tEntiere) > 1):
		# Recherche du mot dans le dico si obligatoire en fait partie
		if(obligatoire.getLettre() in tEntiere or obligatoire.getLettre() == ""):
			
			# rechercher renvoie deux valeurs
			# estMot : nœud correspondant à un mot valide, False sinon
			# suivants : nœuds à partir desquels il est possible de continuer la recherche
			estMot, suivants = dico.rechercher(t, suivants)
			
			# Le mot est dans le dictionnaire, on l'ajoute à resultat, avec comme indice les points qu'il rapporte
			if(estMot is not False):
				rapporte = calculerPoints(cEntiere, points)
				resultat[rapporte] = [estMot.motComplet, cEntiere]
				
		# Même si obligatoire n'est pas dans tEntiere, on fait la recherche pour savoir s'il est utile de continuer
		else:
			estMot, suivants = dico.rechercher(t, suivants)
			
	# S'il reste des lettres dans q, et qu'il existe des mots commençant par (ayant pour préfixe) tEntiere
	if(len(q) > 0 and (suivants or len(tEntiere) < 2)):
		testes = []
		
		# Chaque élément de q est rajouté comme nouvel élément de tEntiere pour former un nouveau mot à rechercher
		for i in range(0, len(q)):
			
			# Effectue une copie par valeur (et non par adresse)
			ntE = tEntiere[:]
			ntE.append(q[i])
			
			# La nouvelle tête ne se compose que d'un élément
			nt = q[i]
			
			# Le nouveau q est formé en enlevant la lettre qu'on vient d'ajouter dans ntE
			nq = q[:i] + q[(i + 1):]
			
			# Si tEntiere < 2, on n'a pas fait la recherche, il faut donc que nt soit le mot entier
			if(len(tEntiere) < 2):
				nt = ntE
				
			# Évite de rechercher deux fois un même mot (si par exemple le tirage comporte plusieurs fois la même lettre)
			if(nt not in testes):
				testes.append(nt)
				rechercherNoTime(nt, nq, obligatoire, ntE, suivants, dico, points, resultat)

# Fonction identique à rechercherNoTime mais arrêtant la recherche après 'limite' secondes
# Cette fonction a été créée afin de ne pas avoir à calculer constamment le temps passé si aucune limite n'a été imposée
def rechercherTime(tL, q, obligatoire, tEntiere, suivants, dico, points, resultat, limite, debut):
	
	# Temps imparti dépassé, on arrête la recherche
	if((time.time() - debut) > limite):
		return
	
	# Chaine formée à partir de la liste tL
	t = ''.join(tL)
	
	# Chaine formée à partir de tEntiere
	cEntiere = ''.join(tEntiere)
	
	longueur = len(tEntiere)
	
	# 'obligatoire' fait partie de 'tEntiere'
	try:
		posGauche =  tEntiere.index(obligatoire.getLettre()) + 1
		posDroite = longueur - posGauche + 1
		
	# 'obligatoire' ne fait pas partie de 'tEntiere'
	except:
		posGauche = 0
		posDroite = 0
	
	# Le mot actuel ne respecte pas les conditions imposées par l'objet Lettre 'obligatoire'
	if(longueur > obligatoire.getLongueur() or posGauche > obligatoire.getMaxGauche() or posDroite > obligatoire.getMaxDroite() or 
		(len(obligatoire.getLettre()) > 2 and posGauche > 1 and posDroite > 1)):
		return

	
	if(len(tEntiere) > 1):
		# Recherche du mot dans le dico si obligatoire en fait partie
		if(obligatoire.getLettre() in tEntiere or obligatoire.getLettre() == ""):
			
			# rechercher renvoie deux valeurs
			# estMot : nœud correspondant à un mot valide, False sinon
			# suivants : nœuds à partir desquels il est possible de continuer la recherche
			estMot, suivants = dico.rechercher(t, suivants)
			
			# Le mot est dans le dictionnaire, on l'ajoute à resultat, avec comme indice les points qu'il rapportera
			if(estMot is not False):
				rapporte = calculerPoints(cEntiere, points)
				resultat[rapporte] = [estMot.motComplet, cEntiere]
				
		# Même si obligatoire n'est pas dans tEntiere, on fait la recherche pour savoir s'il est utile de continuer
		else:
			estMot, suivants = dico.rechercher(t, suivants)
			
	# S'il reste des lettres dans q, et qu'il existe des mots commençant par (ayant pour préfixe) tEntiere
	if(len(q) > 0 and (suivants or len(tEntiere) < 2)):
		testes = []
		
		# Chaque élément de q est rajouté comme nouvel élément de tEntiere pour former un nouveau mot à rechercher
		for i in range(0, len(q)):
			
			# Effectue une copie par valeur (et non par adresse)
			ntE = tEntiere[:]
			ntE.append(q[i])
			
			# La nouvelle tête ne se compose que d'un élément
			nt = q[i]
			
			# Le nouveau q est formé en enlevant la lettre qu'on vient d'ajouter dans ntE
			nq = q[:i] + q[(i + 1):]
			
			# Si tEntiere < 2, on n'a pas fait la recherche, il faut donc que nt soit le mot entier
			if(len(tEntiere) < 2):
				nt = ntE
				
			# Évite de rechercher deux fois un même mot
			if(nt not in testes):
				testes.append(nt)
				rechercherTime(nt, nq, obligatoire, ntE, suivants, dico, points, resultat, limite, debut)

# Renvoie le total de points rapportés par un mot
def calculerPoints(mot, points):
	total = 0
	for l in mot:
		total += points[l]
	
	return total

# Renvoie le mot rapportant le plus de points, et le nombre de points rapportés par celui-ci
def maximum(resultat):
	pointsMax = sorted(resultat.keys())[-1]
	return pointsMax, resultat[pointsMax]

# Prépare un mot afin de le placer sur la grille
def preparerPlacer(mot, lettre, grille, points, tirage, options):
	
	# Cas de la grille vide : pas de préparation nécessaire
	if(lettre is None):
		grille.placer(mot, points, tirage, options)
		return
	
	# Espace nécessaire à gauche (ou en haut) de la lettre pour placer le nouveau mot	
	besoinG = mot[0].find(lettre.getLettre())
	
	# Si mot placé à l'horizontale
	if(lettre.horizontal):
		grille.placer(mot, points, tirage, options, ligne = lettre.x , colonne = lettre.y  - besoinG, horizontal = lettre.horizontal)
	# Si mot placé à la verticale
	else:
		grille.placer(mot, points, tirage, options, ligne = lettre.x - besoinG , colonne = lettre.y, horizontal = lettre.horizontal)

#######################

# Fonction principale

def main():
	# Initialisation des options
	options = {}
	options['points'] = False
	options['print'] = False
	options['update'] = False
	options['time'] = False
	options['limit'] = False
	
	cheminGrille = ""
	cheminTirage = ""
	
	# Pas assez d'arguments
	if(len(sys.argv) <= 2):
		sys.exit("Usage : " + sys.argv[0] + " [options] grille lettres")
		
	# Activation des options demandées
	i = 1
	while(i < len(sys.argv) and sys.argv[i][0] == '-'):
		if(sys.argv[i] == '-points'):
			options['points'] = True
			
		elif(sys.argv[i] == '-print'):
			options['print'] = True
			
		elif(sys.argv[i] == '-update'):
			options['update'] = True
			
		elif(sys.argv[i] == '-time'):
			options['time'] = True
		
		elif(sys.argv[i] == '-limit'):
			try:
				options['limit'] = float(sys.argv[i + 1].replace(',', '.'))
			except:
				sys.exit('L\'option -limit doit être suivie d\'un temps en seconde')
				
			if(options['limit'] <= 0):
					sys.exit('La limite de recherche doit être un temps strictement positif')
			i += 1
		
		else:
			sys.exit("Option " + sys.argv[i] + " inconnue.")
			
		i += 1
		
	if(len(sys.argv) > (i + 2)):
		sys.exit("Trop d'arguments.")
	
	# Pas assez d'arguments (que des options)
	if(len(sys.argv) < (i + 2)):
		sys.exit("Usage : " + sys.argv[0] + " [options] grille lettres")
		
	cheminGrille = sys.argv[i]
	cheminTirage = sys.argv[i + 1]
	
	if not os.path.exists(cheminGrille):
		sys.exit("Le fichier " + cheminGrille + " n'existe pas.")
		
	if not os.path.exists(cheminTirage):
		sys.exit("Le fichier " + cheminTirage + " n'existe pas.")
	
	# Chargement de la grille, du tirage, des points et du dictionnaire
	g = Grille(cheminGrille)
	tirage = Tirage(cheminTirage)
	points = chargerPoints()
	
	if(options['time']):
		print "Temps de chargement du dictionnaire :",
		sys.stdout.flush()
		debut = time.time()
	
	dico = Arbre('./dico')
	
	# Calcul et affichage du temps de chargement du dico si demandé
	if(options['time']):
		print round(time.time() - debut, 5), "secondes."
		print "Temps de recherche :",
		sys.stdout.flush()
		debut = time.time()
	
	motPoints = {}
	resultat = {}
	
	# Grille vide : on utilise un objet Lettre vide
	if(g.grilleEstVide()):
		# On utilise une fonction différente selon que le temps de recherche est limité ou non
		if(options['limit']):
			rechercherTime([], tirage.tirage, Lettre("", 7, 7, False, 8, 8, 8, 0), [], [], dico, points, resultat, options['limit'], debut)
		else:
			rechercherNoTime([], tirage.tirage, Lettre("", 7, 7, False, 8, 8, 8, 0), [], [], dico, points, resultat)
			
		# Des mots ont été trouvés
		if(len(resultat) > 0):
			pointsMax, motsMax = maximum(resultat)
			motPoints[pointsMax] = [motsMax, None]	
			
	# Grille remplie : on établit la liste des lettres pouvant être réutilisées
	else:
		disponibles = g.disponibles(points)
		disponibles.sort()
		
		# Pour chacune des lettres pouvant être réutilisées, on fait une recherche avec notre tirage
		for lettreDisponible in disponibles:
			resultat = {}
			if(options['limit']):
				rechercherTime([], [lettreDisponible.getLettre()] + tirage.tirage, lettreDisponible, [], [], dico, points, resultat, options['limit'], debut)
			else:
				rechercherNoTime([], [lettreDisponible.getLettre()] + tirage.tirage, lettreDisponible, [], [], dico, points, resultat)
			
			# Si on a trouvé des mots, on garde celui qui rapporte le plus (pour cet objet Lettre)
			if(len(resultat) > 0):
				pointsMax, motsMax = maximum(resultat)
				motPoints[pointsMax] = [motsMax, lettreDisponible]
	
	if(options['time']):
		print round(time.time() - debut, 5), "secondes."
	
	# Si on a trouvé des mots à placer, on prend celui qui rapporte le plus parmi ceux qui rapportent le plus
	if(len(motPoints) > 0):
		rapporte, mot = maximum(motPoints)
		preparerPlacer(mot[0], mot[1], g, points, tirage.tirage, options)
		
	# Aucun mot trouvé, abandon
	else:
		print "Je passe."
	
	if(options['print']):
		g.afficher()

	if(options['update']):
		tirage.update(cheminTirage)
		g.update(cheminGrille)

# Appel de la fonction principale
main()
