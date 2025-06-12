#!/bin/bash

# Script pour installer les dépendances et lancer la simulation

# S'assurer que le script est exécuté depuis le répertoire du projet
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "Création de l'environnement virtuel..."
python3 -m venv venv

echo "Activation de l'environnement virtuel..."
source venv/bin/activate

echo "Installation des dépendances..."
pip install -r requirements.txt

echo "Lancement de la simulation..."
python main.py

echo "Simulation terminée. Désactivation de l'environnement virtuel..."
deactivate