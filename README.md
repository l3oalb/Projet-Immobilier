Pipeline ETL : Analyse des ventes immobilières (DVF)
Ce projet a pour but de traiter les fichiers "Demandes de valeurs foncières" (Open Data) pour extraire des tendances de prix au m² par commune.

Architecture technique
Le pipeline est découpé en trois couches :
Traitement : Utilisation de PySpark pour le nettoyage des fichiers volumineux (plusieurs centaines de Mo).
Stockage : Base de données NoSQL MongoDB.
Restitutin : Dashboard interactif avec Streamlit.

Détails de l'implémentation
1. Extraction et Nettoyage (Spark)
Le script projet.py automatise la lecture des fichiers présents dans le dossier /Data (pas joints au git car trop lourds >100 Mo).
Gestion des types : Conversion des valeurs foncières et des surfaces (gestion des virgules françaises via regex).
Filtres métier : Exclusion des mutations autres que les "Ventes" et suppression des valeurs aberrantes (prix au m² inférieurs à 500€ ou supérieurs à 15 000€).
Agrégation : Calcul de la médiane des prix et du volume de transactions par commune.

2. Stratégie de stockage
Les résultats agrégés sont exportés vers MongoDB. Note : Pour éviter les problèmes de compatibilité des drivers JDBC/Spark sur macOS, le stockage est effectué via la bibliothèque pymongo après la phase de calcul.

3. Visualisation
L'application app.py se connecte à la base MongoDB pour générer des graphiques. L'utilisateur peut filtrer les données par département pour visualiser le top 15 des communes les plus chères.

Installation
Installer les dépendances : pip install pyspark pymongo pandas streamlit plotly
Lancer le script de traitement : python projet.py
Lancer l'interface : streamlit run app.py

Contenu du dépôt
projet.py : Script principal de traitement Spark.
app.py : Code de l'interface Streamlit.
.gitignore : Exclusion des fichiers sources volumineux.
Captures/ : Captures d'écran du terminal et de MongoDB Compass validant le stockage + interface streamlit.
