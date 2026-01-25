# Maico VMC Card

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Carte Lovelace personnalisée pour l'intégration [Maico WS VMC](https://github.com/isaya07/ha-maicows).

![Maico VMC Card Preview](docs/preview.png)

## ✨ Fonctionnalités

- 🔄 **Auto-découverte** des entités Maico
- 🌡️ **4 températures** affichées (air ext, rejeté, extrait, insufflé)
- 📊 **Rendement** calculé automatiquement
- 💧 **Humidité** et mode ventilateur
- 🎛️ **Contrôles** intégrés (haut/bas/menu)
- 🎨 **Design moderne** adapté au thème HA
- ⚙️ **Configuration minimale**

## 📥 Installation

### HACS (Recommandé)

1. Ouvrir HACS
2. Aller dans "Frontend"
3. Cliquer sur les 3 points → "Custom repositories"
4. Ajouter `https://github.com/isaya07/ha-maicows-card` (catégorie: Lovelace)
5. Installer "Maico VMC Card"
6. Redémarrer Home Assistant

[![Ouvre votre instance Home Assistant et ajoute un dépôt dans la boutique communautaire Home Assistant.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=isaya07&repository=ha-maicows-card&category=lovelace)

### Manuel

1. Télécharger `ha-maicows-card.js` depuis les [releases](https://github.com/isaya07/ha-maicows-card/releases)
2. Copier dans `/config/www/`
3. Ajouter la ressource dans Lovelace:

```yaml
resources:
  - url: /local/ha-maicows-card.js
    type: module
```

## 🚀 Utilisation

### Configuration minimale

```yaml
type: custom:maico-vmc-card
```

C'est tout ! La carte détecte automatiquement vos entités Maico.

### Configuration complète

```yaml
type: custom:maico-vmc-card
name: VMC Maison
show_efficiency: true
show_humidity: true
show_fan_mode: true
show_graph: true
graph_hours: 24
climate_entity: climate.maico_ws_climat  # Optionnel, auto-détecté
```

## ⚙️ Options

| Option | Type | Défaut | Description |
|--------|------|--------|-------------|
| `name` | string | `VMC` | Nom affiché sur la carte |
| `show_efficiency` | boolean | `true` | Afficher le rendement |
| `show_humidity` | boolean | `true` | Afficher l'humidité |
| `show_fan_mode` | boolean | `true` | Afficher le mode ventilateur |
| `show_graph` | boolean | `true` | Afficher le graphique d'arrière-plan |
| `graph_hours` | number | `24` | Nombre d'heures pour le graphique |
| `graph_color` | string | `accent-color` | Couleur de la courbe et du dégradé |
| `climate_entity` | string | auto | Entité climate (auto-détectée si non spécifiée) |

## 🎨 Thématisation

La carte utilise les variables CSS de Home Assistant :
- `--primary-color` : Couleur des accents
- `--info-color` : Couleur des flèches d'air
- `--card-background-color` : Fond de l'échangeur

## 📋 Prérequis

- Home Assistant 2023.1+
- Intégration [Maico WS VMC](https://github.com/isaya07/ha-maicows) installée

## 🐛 Support

[Ouvrir une issue](https://github.com/isaya07/ha-maicows-card/issues)

## 📄 Licence

MIT
