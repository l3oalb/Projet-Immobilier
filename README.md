# 🏠 Projet Analyse Immobilière

Système intelligent d'analyse du marché immobilier français combinant données DVF (Demandes de Valeurs Foncières), web scraping d'annonces en temps réel, et intelligence artificielle pour détecter les opportunités immobilières.

## 📋 Vue d'ensemble

Ce projet combine trois composants principaux :

1. **Pipeline ETL** : Traitement des données DVF avec PySpark pour calculer les prix médians au m² par commune
2. **Scraper intelligent** : Récupération et analyse d'annonces immobilières en temps réel avec IA
3. **Dashboard** : Visualisation interactive des tendances du marché avec Streamlit

## 🎯 Fonctionnalités

### 📊 Analyse des données DVF
- Import et traitement de fichiers DVF (transactions immobilières officielles)
- Calcul des prix médians au m² par commune et par année (2020-2024)
- Filtrage intelligent (ventes uniquement, surfaces cohérentes, prix réalistes)
- Stockage dans MongoDB pour analyse rapide

### 🔍 Scraping et détection d'opportunités
- Recherche d'annonces récentes via Google (API Serper)
- Extraction du contenu des annonces (Jina AI Reader)
- Extraction intelligente des informations (OpenAI GPT-4o-mini) :
  - Prix, surface, type de bien
  - Localisation, état du bien
- Enrichissement géographique :
  - Géocodage (API data.gouv.fr)
  - Analyse de l'environnement (OpenStreetMap) :
    - Distance aux transports en commun
    - Proximité des commerces, écoles, parcs
    - Distance aux routes principales (nuisances)
- Comparaison avec les prix DVF pour détecter les bonnes affaires

### 📈 Visualisation
- Dashboard interactif Streamlit
- Top 10 des communes avec les plus fortes hausses de prix
- Évolution historique du prix au m² par commune
- Graphiques interactifs (Plotly)

## 🛠️ Technologies

- **Python 3.11+**
- **PySpark** : Traitement distribué des données DVF
- **MongoDB** : Base de données NoSQL pour les tendances
- **Streamlit** : Interface web interactive
- **OpenAI API** : Extraction d'informations structurées
- **Jina AI Reader** : Scraping web sans blocage
- **Serper API** : Recherche Google
- **APIs externes** :
  - data.gouv.fr (géocodage)
  - OpenStreetMap/Overpass API (POI)

## 📦 Installation

### Prérequis
- Python 3.11+
- uv (gestionnaire de paquets Python moderne)
- Accès MongoDB (local ou Atlas)

### Configuration

1. **Cloner le projet**
```bash
git clone <votre-repo>
cd Projet-Immobilier
```

2. **Installer les dépendances avec uv**
```bash
uv sync
```

3. **Configuration des variables d'environnement**

Créez un fichier `.env` à la racine :
```env
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...
```

4. **Télécharger les données DVF**

Téléchargez les fichiers depuis [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/) et placez-les dans le dossier `Data/`.

## 🚀 Utilisation

### 1. Traitement des données DVF

```bash
python -m projet_immobilier.etl
```

Ce script :
- Lit tous les fichiers `.txt` du dossier `Data/`
- Calcule les prix médians au m² par commune et année
- Stocke les résultats dans MongoDB

**Note** : Vous pouvez aussi utiliser `uv run -m projet_immobilier.etl` si vous utilisez uv.

### 2. Scraping et analyse d'annonces

```bash
python main_scraper.py
```

Ce script :
- Recherche des annonces récentes (dernières 24h)
- Extrait les informations avec l'IA
- Enrichit avec les données géographiques
- Compare avec les prix DVF
- Affiche les opportunités détectées

**Exemple de sortie** :
```
🚌 Transport : 150m vers l'arrêt le plus proche
🏠 Bien : Appartement à NANTES
💰 Prix IA : 250000€ pour 65m2 (3846€/m2)
📊 Verdict : ✅ BON PRIX (Sous la médiane) (Ecart : -12.5%)
```

### 3. Dashboard de visualisation

```bash
streamlit run app.py
```

Ouvre le dashboard dans votre navigateur pour :
- Explorer les évolutions de prix par département
- Analyser les tendances par commune
- Visualiser les historiques de prix

## 📁 Structure du projet

```
Projet-Immobilier/
├── app.py                              # Dashboard Streamlit
├── main_scraper.py                     # Orchestrateur principal (point d'entrée)
├── projet_immobilier/                  # Package Python principal
│   ├── __init__.py                     # Initialisation du package
│   ├── etl.py                          # Pipeline ETL PySpark → MongoDB
│   ├── decision.py                     # Moteur de décision (opportunités)
│   ├── jina_web_scraper.py             # Scraping d'annonces
│   ├── extract_with_gen_ai.py          # Extraction IA (OpenAI)
│   ├── extract_with_regex.py           # Extraction regex (fallback)
│   ├── get_coord_API.py                # Géocodage
│   └── get_additionals_informations.py # Enrichissement environnemental
├── Data/                               # Fichiers DVF (non versionnés)
├── pyproject.toml                      # Configuration uv
├── uv.lock                             # Fichier de lock des dépendances
└── .env                                # Variables d'environnement (non versionné)
```

## 🔧 Configuration avancée

### Personnaliser les critères de filtrage (projet_immobilier/etl.py)

```python
# Ligne 29-35 : Ajustez les filtres DVF
df_filtered = df_clean.filter(
    (F.col("Nature mutation") == "Vente") &
    (F.col("Type local").isin("Maison", "Appartement")) &
    (F.col("surface_bati") > 15) &  # Surface minimale
    (F.col("valeur_fonciere") > 20000) &  # Prix minimum
    (F.col("annee").isNotNull())
)
```

### Modifier les critères d'opportunité (projet_immobilier/decision.py)

```python
# Ligne 33-40 : Ajustez les seuils
if difference <= -15:
    verdict = "🔥 EXCELLENTE AFFAIRE"
elif difference <= 0:
    verdict = "✅ BON PRIX"
elif difference <= 15:
    verdict = "⚖️ PRIX DE MARCHÉ"
else:
    verdict = "❌ TROP CHER"
```

### Paramétrer la recherche (main_scraper.py)

```python
# Ligne 8 : Modifiez la ville et la surface recherchée
ads_data = get_latest_ads_content("Nantes", "50")
```

## 🔐 Sécurité

⚠️ **Important** :
- Ne committez JAMAIS le fichier `.env`
- Utilisez des variables d'environnement pour les clés API
- Limitez les permissions MongoDB (lecture/écriture uniquement)
- Respectez les quotas des APIs (Serper, OpenAI, Overpass)

## 📊 Exemple de workflow complet

1. **Initialisation** : Traiter les données DVF historiques
```bash
python -m projet_immobilier.etl
```

2. **Monitoring quotidien** : Lancer le scraper (peut être automatisé avec cron)
```bash
python main_scraper.py
```

3. **Analyse** : Consulter le dashboard pour les tendances
```bash
streamlit run app.py
```

## 🐛 Dépannage

### Erreur MongoDB
```
⚠️ Erreur de stockage : ServerSelectionTimeoutError
```
→ Vérifiez votre `MONGO_URI` et la connexion réseau

### Timeout Jina/Serper
```
Erreur Jina : timeout
```
→ Augmentez le timeout dans `projet_immobilier/jina_web_scraper.py` ligne 47

### Erreur OpenAI
```
openai.error.RateLimitError
```
→ Vérifiez vos crédits API et respectez les limites de taux

## 🚀 Améliorations futures

- [ ] Ajouter des tests unitaires
- [ ] Créer une API REST (FastAPI)
- [ ] Système de notifications (email/Telegram)
- [ ] Support multi-régions
- [ ] Cache des résultats de géocodage
- [ ] Interface d'administration MongoDB
- [ ] Export des résultats (PDF, Excel)
- [ ] Intégration d'autres sources de données

