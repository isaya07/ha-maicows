# Guide de Développement - Maico WS VMC Integration

Ce document explique comment utiliser ce dépôt pour continuer le développement de l'intégration **Maico WS VMC** (`maicows`).

## Prérequis

- [Visual Studio Code](https://code.visualstudio.com/)
- Portman ou Docker (pour utiliser les Dev Containers, recommandé)

## Structure du Projet

- **`custom_components/maicows/`** : C'est ici que se trouve tout le code source de votre intégration.
  - `manifest.json` : Définit les métadonnées de l'intégration (version, dépendances, etc.).
  - `__init__.py` : Point d'entrée de l'intégration.
  - `sensor.py`, `binary_sensor.py`, etc. : Définitions des entités.
  - `maico_ws_api.py` : Votre API pour communiquer avec la VMC.
- **`scripts/`** : Scripts utilitaires pour le développement.
  - `develop` : Script principal pour lancer Home Assistant.
- **`.devcontainer.json`** : Configuration pour l'environnement de développement Docker.

## Environnement de Développement

Ce projet est configuré pour être utilisé avec les **Dev Containers** de VS Code. Cela configure automatiquement Python, Home Assistant et toutes les dépendances nécessaires.

1. Ouvrez le dossier du projet dans VS Code.
2. Une notification devrait apparaître vous proposant de rouvrir dans le conteneur ("Reopen in Container"). Si ce n'est pas le cas, appuyez sur `F1` et cherchez **Dev Containers: Reopen in Container**.
3. Attendez l'initialisation du conteneur (installation des dépendances, etc.).

## Lancer Home Assistant

Pour tester vos modifications, vous pouvez lancer une instance de Home Assistant directement depuis ce projet.

1. Ouvrez un terminal dans VS Code (**Terminal > New Terminal**).
2. Lancez la commande suivante :
   ```bash
   scripts/develop
   ```
3. Ce script va :
   - Créer un dossier `config/` s'il n'existe pas.
   - Configurer Home Assistant pour charger votre intégration depuis `custom_components/`.
   - Lancer Home Assistant.

4. Accédez à Home Assistant via votre navigateur à l'adresse : [http://localhost:8123](http://localhost:8123).
5. Lors du premier lancement, vous devrez peut-être passer l'écran de configuration initiale (création d'un compte admin).

## Ajouter/Modifier des Fonctionnalités

1. **Code** : Modifiez les fichiers `.py` dans `custom_components/maicows/`.
2. **Redémarrage** : Une fois vos modifications effectuées, arrêtez le script `develop` (Ctrl+C) et relancez-le pour que Home Assistant prenne en compte les changements.
   - *Note : Certaines modifications (comme le changement de code dans les méthodes `update`) ne nécessitent parfois pas un redémarrage complet si vous utilisez le rechargement YAML, mais pour une intégration personnalisée en développement, le redémarrage est le plus sûr.*

## Tests

Ce projet contient une suite de tests unitaires utilisant `pytest`.

### Prérequis des tests

Les dépendances de test sont listées dans `requirements_test.txt`. Elles sont installées automatiquement dans le Dev Container ou vous pouvez les installer manuellement :

```bash
pip install -r requirements_test.txt
```

### Lancer les tests

Pour exécuter tous les tests unitaires :

```bash
pytest
```

Pour exécuter un fichier de test spécifique :

```bash
pytest tests/test_maico_ws_api.py
```

## Débogage

- Les logs de Home Assistant s'affichent directement dans le terminal où vous avez lancé `scripts/develop`.
- Vous pouvez ajouter des logs dans votre code avec `_LOGGER.debug(...)` ou `_LOGGER.info(...)`. Assurez-vous que le niveau de log est configuré correctement dans `config/configuration.yaml` si vos logs n'apparaissent pas (le script `develop` lance HA avec le flag `--debug` par défaut, ce qui aide).
