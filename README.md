# Pipeline ETL : Analyse des ventes immobilières (DVF)

Ce projet a pour but de traiter les fichiers "Demandes de valeurs foncières" (Open Data) pour extraire des tendances de prix au m² par commune française.

## Architecture technique

Le pipeline est découpé en trois couches :
* **Traitement** : Utilisation de PySpark pour le nettoyage des fichiers volumineux (plusieurs centaines de Mo).
* **Stockage** : Base de données NoSQL MongoDB.
* **Restitution** : Dashboard interactif avec Streamlit.

---

## Détails de l'implémentation

### 0. Données source
Les fichiers sources sont hébergés sur data.gouv.fr sous format compressé ZIP. Bien que l'automatisation du téléchargement via l'identifiant de ressource (ex: cc8a50e4...) soit possible, la structure des URLs inclut des timestamps variables nécessitant une étape de parsing HTML pour identifier les derniers liens valides. Pour ce projet, nous avons privilégié une ingestion locale après décompression pour simplifier le travail.

### 1. Extraction et Nettoyage (Spark)
Le script `projet.py` automatise la lecture des fichiers présents dans le dossier `/Data`. Ces fichiers ne sont pas joints au dépôt Git car leur taille excède 100 Mo.

* **Gestion des types** : Conversion des valeurs foncières et des surfaces (traitement des virgules françaises via expressions régulières).
* **Filtres métier** : Exclusion des mutations autres que les "Ventes" et suppression des valeurs aberrantes (prix au m² inférieurs à 500€ ou supérieurs à 15 000€).
* **Agrégation** : Calcul de la médiane des prix et du volume de transactions par commune.

### 2. Stratégie de stockage
Les résultats agrégés sont exportés vers MongoDB. 
*Note : Pour éviter les problèmes de compatibilité des drivers JDBC/Spark sur macOS, le stockage est effectué via la bibliothèque pymongo après la phase de calcul.*

### 3. Visualisation
L'application `app.py` se connecte à la base MongoDB pour générer des graphiques. L'utilisateur peut filtrer les données par département pour visualiser le top 15 des communes les plus chères.

---

## Installation

1. **Installer les dépendances** :
   `pip install pyspark pymongo pandas streamlit plotly`

2. **Lancer le script de traitement** :
   `python projet.py`

3. **Lancer l'interface** :
   `streamlit run app.py`

---

## Contenu du dépôt

* `projet.py` : Script principal de traitement Spark.
* `app.py` : Code de l'interface Streamlit.
* `.gitignore` : Exclusion des fichiers sources volumineux.
* `Captures` : Fichiers contenant les captures d'écran du terminal, de MongoDB Compass (stockage) et de l'interface Streamlit.
