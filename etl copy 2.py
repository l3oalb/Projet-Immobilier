import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import pymongo

# Charger les variables d'environnement
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

dir_path = os.path.dirname(os.path.realpath(__file__))
java_path = os.path.join(dir_path, "java_runtime", "Contents", "Home")

os.environ["JAVA_HOME"] = java_path
os.environ["PATH"] = os.path.join(java_path, "bin") + ":" + os.environ["PATH"]

spark = SparkSession.builder \
    .appName("MonProjetImmo") \
    .getOrCreate()

def processus_etl(chemin_txt):
    # IMPORT
    df = spark.read.options(header='true', sep='|', encoding='ISO-8859-1', decimal=',').csv(chemin_txt)
    
    # NETTOYAGE ET EXTRACTION DE L'ANNÉE
    # On normalise la commune et on extrait l'année de la date de mutation
    df_clean = df.withColumn("Commune", F.upper(F.trim(F.col("Commune")))) \
                 .withColumn("valeur_fonciere", 
                             F.regexp_replace(F.col("Valeur fonciere"), ",", ".").cast("double")) \
                 .withColumn("surface_bati", 
                             F.regexp_replace(F.col("Surface reelle bati"), ",", ".").cast("double")) \
                 .withColumn("date_mutation", F.to_date(F.col("Date mutation"), "dd/MM/yyyy")) \
                 .withColumn("annee", F.year(F.col("date_mutation")))
    
    # FILTRES 
    df_filtered = df_clean.filter(
        (F.col("Nature mutation") == "Vente") &
        (F.col("Type local").isin("Maison", "Appartement")) &
        (F.col("surface_bati") > 15) &
        (F.col("valeur_fonciere") > 20000) &
        (F.col("annee").isNotNull()) # Sécurité pour les dates mal formées
    ).dropna(subset=["valeur_fonciere", "surface_bati"])

    # CALCUL ET AGRÉGATION PAR ANNÉE
    df_communes = df_filtered.withColumn("prix_m2", F.col("valeur_fonciere") / F.col("surface_bati")) \
        .filter((F.col("prix_m2") > 500) & (F.col("prix_m2") < 20000)) \
        .groupBy("Code departement", "Commune", "annee").agg(
            F.round(F.median("prix_m2"), 2).alias("prix_median"),
            F.count("valeur_fonciere").alias("nb_ventes")
        ).withColumnRenamed("Code departement", "code_dept")

    # STOCKAGE DANS MONGODB ATLAS
    try:
        if df_communes.count() > 0:
            print(f"Envoi vers MongoDB Atlas...")
            
            # Conversion en liste de dictionnaires
            data_to_insert = df_communes.toPandas().to_dict('records')
            
            # CONNEXION ATLAS
            client = pymongo.MongoClient(MONGO_URI)
            db = client["immo_db"]
            collection = db["tendances_communes"]
            
            if data_to_insert:
                # --- MODIFICATION ICI : ENVOI PAR PAQUETS ---
                taille_paquet = 500
                total_lignes = len(data_to_insert)
                
                for i in range(0, total_lignes, taille_paquet):
                    paquet = data_to_insert[i : i + taille_paquet]
                    collection.insert_many(paquet)
                    print(f"   > Paquet envoyé ({min(i + taille_paquet, total_lignes)}/{total_lignes})")
                
                print(f"✅ Succès final ! {total_lignes} lignes insérées.")
        else:
            print("⚠️ Aucune donnée à insérer pour ce fichier.")
            
    except Exception as e:
        print(f"⚠️ Erreur de stockage Atlas : {e}")

    return df_communes

# --- LANCEMENT ---
dossier = os.path.join(dir_path, "../données immobilier")

if os.path.exists(dossier):
    # Nettoyage de la base Atlas au départ
    try:
        client = pymongo.MongoClient(MONGO_URI)
        client["immo_db"]["tendances_communes"].delete_many({})
        print("🧹 Collection Atlas vidée pour nouvel import.")
    except Exception as e:
        print(f"Impossible de vider la collection : {e}")

    fichiers = [f for f in os.listdir(dossier) if f.endswith('.txt') and not f.startswith('.')]
    for nom_f in fichiers:
        chemin_complet = os.path.join(dossier, nom_f)
        processus_etl(chemin_complet).show(5)