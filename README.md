# Simulation de Vie 3D en Python (Projet Démo)

## Description

Ce projet est une démonstration simple d'une simulation de vie, codée en Python avec la bibliothèque `pygame`. Il vise à illustrer les concepts de base d'agents se déplaçant dans un environnement 2D (simulant un espace pour cette démo).

## Fonctionnalités Principales

*   Visualisation d'un environnement 2D simple.
*   Un agent, représenté par Homer Simpson, se déplaçant de manière aléatoire.
*   Chargement et redimensionnement d'une image pour l'agent depuis un dossier `assets` (hauteur définie en pixels).
*   Utilisation d'une image différente (`homer_up.gif`) lorsque l'agent est en mode "boost".
*   Fenêtre d'application gérée par `pygame`. Les images utilisées sont `homer.gif` et `homer_up.gif`.

## Prérequis Techniques

*   Python 3.8 ou supérieur.
*   Bibliothèques Python :
    *   `pygame` (pour le rendu graphique et la gestion des fenêtres).
*   Les dépendances sont listées dans `requirements.txt`.
*   Une image nommée `homer.png` dans un dossier `assets/` à la racine du projet.
*   Des images nommées `homer.gif` et `homer_up.gif` dans un dossier `assets/` à la racine du projet.

## Installation

1.  **Clonez le dépôt (si applicable) :**
    ```bash
    git clone <URL_DU_DEPOT_GIT>
    cd <NOM_DU_REPERTOIRE_DU_PROJET>
    ```

2.  **Créez et activez un environnement virtuel (recommandé) :**
    ```bash
    python -m venv venv
    ```
    Sur Windows :
    ```bash
    venv\Scripts\activate
    ```
    Sur macOS/Linux :
    ```bash
    source venv/bin/activate
    ```

3.  **Installez les dépendances :**
    Si un fichier `requirements.txt` est fourni :
    ```bash
    pip install -r requirements.txt
    ```
    Sinon, installez les bibliothèques manuellement (exemple avec pygame et numpy) :
    ```bash
    pip install pygame numpy
    ```

## Comment Lancer la Simulation

Exécutez le script principal du projet (par exemple, `main.py` ou `simulation.py`) :
```bash
python main.py
```
(Adaptez `main.py` au nom réel de votre fichier de point d'entrée).

## Commandes / Interactions

*   Décrivez ici les commandes clavier, souris ou les éléments d'interface utilisateur permettant d'interagir avec la simulation.
    *   Exemple : `Flèches directionnelles` pour déplacer la caméra.
    *   Exemple : `Espace` pour mettre en pause/reprendre la simulation.

## Structure du Projet (Exemple)

```
nom-du-projet/
├── src/ ou nom_du_projet/  # Code source de la simulation
│   ├── agent.py            # Logique des agents
│   ├── environnement.py    # Gestion de l'environnement 3D
│   ├── moteur_rendu.py     # Code pour le rendu graphique
│   └── ...
├── assets/                 # Ressources (modèles 3D, textures, sons)
├── tests/                  # Tests unitaires et d'intégration
├── main.py                 # Point d'entrée de l'application
├── requirements.txt        # Liste des dépendances Python
└── README.md               # Ce fichier
```

## Pistes d'Amélioration / Fonctionnalités Futures

*   Comportements d'agents plus complexes (IA).
*   Interactions plus riches entre agents.
*   Meilleur rendu graphique et effets visuels.
*   Sauvegarde et chargement de l'état de la simulation.

## Contribuer

Les contributions sont les bienvenues ! Si vous souhaitez contribuer, veuillez ouvrir une "issue" pour discuter des changements que vous aimeriez apporter ou soumettre une "pull request".

## Licence

Ce projet est distribué sous la licence [Nom de la Licence]. Voir le fichier `LICENSE` pour plus d'informations. (Si vous n'avez pas de licence, vous pouvez omettre cette section ou choisir une licence open source comme MIT).