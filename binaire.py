#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import sys

# Nœud de l'arbre contenant une lettre
class Noeud(object):
	
	"""
	Constructeur
	
	lettre : lettre stockée dans le nœud
	mot : True si le chemin représente un mot du dictionnaire, False sinon
	fd : lettre située au même niveau et après dans l'ordre alphabétique
	fm : lettre située au niveau suivant
	"""
	def __init__(self, lettre = None, motComplet = None):
		
		self._lettre = None
		self._mot = False
		self._motComplet = None
		
		self._fd = None
		self._fm = None
		
		self.lettre = lettre
		self.motComplet = motComplet
	
	#Getters et setters
	
	def setLettre(self, lettre):
		self._lettre = lettre
		
	def getLettre(self):
		return self._lettre
		
	def setFd(self, fd):
		self._fd = fd
		
	def getFd(self):
		return self._fd
		
	def setFm(self, fm):
		self._fm = fm
	
	def getFm(self):
		return self._fm
	
	def setMot(self, mot):
		self._mot = mot
	
	def getMot(self):
		return self._mot

	def setMotComplet(self, motComplet):
		self._motComplet = motComplet

	def getMotComplet(self):
		return self._motComplet
		
	lettre = property(getLettre, setLettre)
	estMot = property(getMot, setMot)
	motComplet = property(getMotComplet, setMotComplet)
	fd = property(getFd, setFd)
	fm = property(getFm, setFm)
		
#Arbre binaire
class Arbre(object):
	
	""" 
	Constructeur
	
	racine : nœud racine de l'arbre
	fichier : fichier du dictionnaire
	hash : tableau de hashage correspondant aux nœuds
	"""
	
	def __init__(self, fichier = None):
		self._racine = None
		self._fichier = None
		self._hash = None
		
		self.charger(fichier)
	
	#Getters et setters
	
	def getFichier(self):
		return self._fichier
		
	def setFichier(self, fichier):
		self._fichier = fichier
		
	def getRacine(self):
		return self._racine
		
	def setRacine(self, racine):
		self._racine = racine
	
	def setHash(self, h):
		self._hash = h
		
	def getHash(self):
		return self._hash

	fichier = property(getFichier, setFichier)
	racine = property(getRacine, setRacine)
	hash = property(getHash, setHash)
	
	""" Chargement d'un fichier de dictionnaire """
		
	def charger(self, fichier):
		
		if not os.path.exists(fichier):
			sys.exit('Le dictionnaire ' + fichier + ' n\'existe pas.')
			
		self.hash = {}
		self.fichier = fichier
		self.racine = self.chargerMots()
		
	def chargerMots(self):
		racine = None
		
		#Pour chaque mot du dictionnaire
		for mot in open(self.fichier):
			
			#Suppression du \n
			mot = mot[:-1]
			noeud = None
			i = 1
			
			#On cherche le préfixe du mot le plus grand existant déjà dans la table de hashage
			motDecoupe = mot[0:-i]
			while(motDecoupe and not noeud):
				try:
					noeud = self.hash[motDecoupe]
				except:
					#Le préfixe n'existe pas, on enlève une lettre au préfixe et on réessaye
					i += 1
					motDecoupe = mot[0:-i]
			
			#Aucun préfixe n'existe, on ajoute le mot en entier
			if(not motDecoupe):
				racine = self.inserer(racine, mot, "")
			#On a trouvé un préfixe, on démarre l'ajout à partir du noeud du préfixe, en ajoutant la partie du mot qui n'existe pas encore
			else:
				noeud.fm = self.inserer(noeud.fm, mot[-i:], motDecoupe)
			
		return racine
	
	""" 
	Insertion d'un nœud 
	noeud : noeud à partir duquel démarrer l'ajout
	mot : mot à ajouter (si 'noeud' n'est pas la racine, il ne s'agit pas d'un mot entier)
	chemin : chaine représentant le chemin parcouru pour arriver à 'noeud' (vide si noeud est la racine) 
	"""
	
	def inserer(self, noeud, mot, chemin):
		
		#Le noeud n'existe pas, on le crée et on l'ajoute dans la table de hashage
		if noeud is None:
			chemin += mot[0]
			noeud = Noeud(mot[0], chemin)
			self.hash[chemin] = noeud
			
		#On est sur le noeud correspondant à la lettre actuelle
		if (mot[0] == noeud.lettre):
			#On a ajouté le mot en entier, estMot devient vrai
			if (len(mot) == 1):
				noeud.estMot = True
			#On ajoute la suite du mot
			else:
				noeud.fm = self.inserer(noeud.fm, mot[1:], chemin)
		
		#On n'est pas sur le noeud correspondant à la lettre actuelle, on continue l'insertion à droite
		else:
			noeud.fd = self.inserer(noeud.fd, mot, chemin)
		
		return noeud
		
	""" Recherche d'un mot dans l'arbre """
	
	def rechercher(self, mot, noeuds = None):
		
		estMot = False
		suivants = []
		
		#Si aucun noeud de départ n'est précisé, on démarre de la racine
		if(not noeuds):
			noeuds = [self.racine]
			
		#Pour chacun des noeuds à partir desquels lancer la recherche
		for noeud in noeuds:
			estMotActuel, suivant = self.rechercherMot(noeud, mot)
			
			#Si on trouve au moins un mot, estMot devient le nœud actuel comportant le mot complet
			if(estMotActuel is not False):
				estMot = estMotActuel
				
			#On complète la liste des noeuds à partir desquels continuer la recherche (avec mot comme préfixe)
			suivants += suivant
			
		return estMot, suivants
		
	def rechercherMot(self, noeudA, mot):
		
		estMotM = False
		estMotD = False
		
		suivantM = []
		suivantD = []
		
		#Si le noeud existe
		if(noeudA):
			
			lettre = noeudA.lettre
			estMot = noeudA.estMot
			
			fmA = noeudA.fm
			fdA = noeudA.fd
					
			#Si le noeud correspond à la lettre actuelle (ou qu'il s'agit d'un joker)
			if (mot[0] == '.' or mot[0] == lettre):
				#On a trouvé le noeud correspond au mot
				if(len(mot) == 1):
					#Ce noeud à un fils, on le garde pour démarrer la recherche dessus plus tard
					if(fmA):
						suivantM.append(fmA)
					#Le chemin parcouru correspond à un mot du dictionnaire
					if(estMot):
						estMotM = noeudA
				#On continue la recherche du mot avec la lettre suivante si on n'est pas à la fin
				else:
					if(fmA):
						estMotM, suivantM = self.rechercherMot(fmA, mot[1:])
					
			#Si le noeud ne correspond pas à la lettre actuelle (ou qu'il s'agit d'un joker), on continue la recherche à droite
			if (mot[0] == '.' or mot[0] > lettre):
				if(fdA):
					estMotD, suivantD = self.rechercherMot(fdA, mot)
				
		#On fusionne les deux listes de noeuds (utile uniquement quand mot[0] est un joker)
		suivant = suivantM + suivantD
			
		#Si on a trouvé un mot à droite ou au milieu (ou les deux), on récupère le noeud correspondant à ce mot
		if(estMotM):
			estMot = estMotM
		elif(estMotD):
			estMot = estMotD
		else:
			estMot = False
		
		return estMot, suivant

