# Projet POO - Blue Prince

Une implémentation simplifiée du jeu Blue Prince, réalisée dans le cadre d'un projet de Programmation Orientée Objet (POO).

Ce jeu permet au joueur d'être dans la peau d'un d'explorateur de manoir qui construit pièce par pièce, gère ses ressources (pas, clés, gemmes) et tente d'atteindre l'Antichambre en partant de la chambre d'entrée.


## 📋 Prérequis
Avant de commencer, assurez-vous d'avoir Python 3.10 (ou une version plus récente) installé sur votre machine.

## 🚀 Installation
Suivez ces étapes pour installer et préparer le projet :
1. Créé un nouveau dossier par exemple nommé toto 
2. Ouvrez un terminal et accéder au dossier toto avec la commande :

>cd toto


3. Puis clonez ce dépôt sur votre machine locale :

> git clone https://github.com/Faresous/PROJETPOO

4. Accéder au dossier du projet :

>cd PROJETPOO

5. Créer un environnement virtuel est une bonne pratique pour isoler les dépendances de votre projet 

# Pour Windows
> python -m venv venv
.\venv\Scripts\activate

5. Installez Pygame (la seule dépendance) en utilisant le fichier requirements.txt :

> pip install -r requirements.txt

# ▶️ Lancer le jeu

Une fois l'installation terminée, vous pouvez lancer le jeu en exécutant le fichier interface.py :

>python interface.py

Le jeu se lancera en mode plein écran.

# ⌨️ Contrôles
## Menu Principal :

Flèches Haut/Bas : Naviguer.

Espace / Entrée : Valider.

## En Jeu :

**ZQSD / Flèches**: Sélectionner une direction de déplacement.

**Espace / Entrée** : Confirmer le déplacement dans la direction choisie.

**U** : Ouvre le menu "Actions" (pour Manger, Ouvrir un coffre, Creuser, etc.).

**Échap** : Retourner au menu principal.

## Écran de droite :

**Flèches Gauche/Droite** : Choisir une salle du tirage au sort aléatoire.

**Espace / Entrée** : Valider le choix de la salle.

**R** : Relancer le tirage aléatoire (coûte 1 dé dans le jeu).

## Remarque : **l'Utilisation de la souris est impossible seul le clavier fonctionne**.