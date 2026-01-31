# 🏠 ImmoAlert GenAI-MLOps 🚀
> Système intelligent d'alerte immobilière basé sur l'extraction LLM et l'analyse comparative DVF.

## 📌 Présentation du Projet
Ce projet vise à automatiser la détection de "pépites" immobilières (biens sous-évalués) en combinant le webscraping, l'intelligence artificielle générative et l'ingénierie de données.

Le système surveille les sites d'annonces, extrait précisément les caractéristiques des biens via un **LLM**, et compare en temps réel le prix affiché avec les données historiques des ventes notariales (**DVF - Demande de Valeur Foncière**).

### 🔄 Flux de données (Pipeline)
1. **Ingestion :** Scraping asynchrone des plateformes (Leboncoin, ParuVendu).
2. **Extraction (GenAI) :** Transformation du texte brut non structuré en données JSON précises (prix, m², travaux, DPE).
3. **Analyse :** Comparaison géographique et temporelle avec les bases de données d'État (Etalab/DVF).
4. **Alerte :** Envoi d'une notification email si le prix au $m^2$ est inférieur de $X \%$ à la moyenne du secteur.

---

## 🛠 Stack Technique

### **Intelligence Artificielle & Data**
* **LLM :** Langchain, API OpenAI.
* **Data Validation :** `Pydantic` / `Instructor` pour garantir la structure des données extraites.
* **Database :** `MongoDB`

### **MLOps & Engineering**
* **Orchestration :** `Dagster` ou `Prefect` pour gérer la fréquence des runs et les retries.
* **Scraping :** `Playwright` (gestion du JS) + `ScrapingBee` (gestion des proxies).
* **Versioning :** `DVC` (Data Version Control) pour le suivi des bases DVF.
* **Monitoring :** `Evidently AI` pour détecter les dérives de prix sur le marché.

### **Environnement**
* **Langage :** Python 3.10+
* **Conteneurisation :** Docker & Docker Compose

---

## 🏗 Architecture du Système

| Composant | Technologie | Rôle |
| :--- | :--- | :--- |
| **Scraper** | Playwright | Récupération du HTML brut. |
| **Parser AI** | Instructor + LLM | Extraction : "Bel appart" → `{surface: 50, prix: 150000}`. |
| **Data Engine** | Pandas / SQL | Calcul de l'écart type par rapport aux données DVF. |
| **Alerting** | SMTP / Resend | Envoi de l'email avec lien direct vers l'annonce. |

---

## 🌍 Enrichissement Géographique

### **Géocodage** (`get_coord_API.py`)
Conversion d'adresses en coordonnées GPS via l'API de la Géoplateforme (IGN). Permet de localiser précisément chaque bien pour l'analyse spatiale.

### **Analyse Environnementale** (`transport.py`)
Enrichissement des biens avec des indicateurs de qualité de vie via OpenStreetMap :
- Distance aux transports (bus, métro) et gares
- Proximité des commerces et écoles
- Présence de parcs et espaces verts
- Exposition aux routes majeures (nuisances)

Ces données permettent d'affiner l'analyse de valeur en intégrant la qualité de l'emplacement.


