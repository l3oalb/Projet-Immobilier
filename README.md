# Pipeline ETL : Analyse des tendances et évolutions immobilières (DVF)

Ce projet traite les fichiers "Demandes de valeurs foncières" (Open Data) pour analyser l'évolution du marché immobilier entre 2020 et 2024. Le pipeline permet d'identifier les communes ayant les plus fortes croissances de prix au m².

## Architecture technique

Le pipeline repose sur une architecture découplée :
* **Traitement** : PySpark pour le nettoyage massif et l'agrégation temporelle (calcul des médianes par année/commune).
* **Stockage** : MongoDB pour la persistance des données structurées en séries temporelles.
* **Restitution** : Dashboard Streamlit interactif pour le calcul d'évolution (2020-2024).

---

## Détails de l'implémentation

### 0. Stratégie d'ingestion et limites de l'automatisation
L'automatisation du téléchargement des données via les URL de `data.gouv.fr` n'a pas été retenue pour ce projet. L'analyse a révélé que les liens directs vers les archives ZIP (hébergées sur `[data.gouv.fr](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres)`) intègrent des jetons temporels variables (timestamps) dans leur structure. 

Cette architecture rend l'ingestion par script instable sans l'implémentation d'un module de web scraping complexe pour identifier dynamiquement les derniers liens valides. Nous avons donc opté pour une ingestion locale : les fichiers sont décompressés dans le répertoire `/Data` avant d'être pris en charge par le moteur PySpark.

### 1. Extraction et Agrégation temporelle (Spark)
Le script `projet.py` traite les fichiers sources présents dans le dossier `/Data`. Ils n'ont pas été joints au git car trop volumineux.

* **Normalisation** : Transformation des noms de communes (majuscules/trim) pour garantir la fusion correcte des données multi-sources.
* **Analyse temporelle** : Extraction de l'année à partir des dates de mutation pour permettre la comparaison inter-annuelle.
* **Filtres de fiabilité** : Exclusion des dépendances (surfaces < 15m²) et des prix non représentatifs (< 500€/m² ou > 15 000€/m²) pour assurer la pertinence des médianes.

### 2. Stratégie de stockage
Les résultats sont injectés dans MongoDB via la bibliothèque `pymongo`. Chaque document en base représente l'état d'une commune pour une année donnée (ex: Commune, Code Département, Année, Prix Médian, Volume de ventes). Cette structure facilite les requêtes de comparaison et d'historique.

### 3. Visualisation et Analyse d'évolution
L'application `app.py` propose deux niveaux d'analyse :
* **Palmarès des hausses** : Calcul dynamique du pourcentage d'évolution entre 2020 et 2024 par département. 
* **Courbes de tendance** : Visualisation de l'historique complet d'une ville sélectionnée pour observer la trajectoire des prix sur 5 ans.

---

## Installation et Utilisation

1. **Installation des dépendances** :
   `pip install pyspark pymongo pandas streamlit plotly`

2. **Phase de traitement (ETL)** :
   `python3 projet.py`
   *(Nettoie la base de données et importe les fichiers du dossier /Data)*

3. **Lancement du Dashboard** :
   `streamlit run app.py`

---

## Contenu du dépôt

* `projet.py` : Script ETL Spark (Nettoyage, Agrégation, Ingestion).
* `app.py` : Dashboard Streamlit (Calcul d'évolution et Visualisation).
* `.gitignore` : Exclusion des fichiers sources volumineux.
* `Captures .png` : Fichiers contenant les preuves de succès du pipeline (Terminal, MongoDB Compass et Dashboard streamlit).
