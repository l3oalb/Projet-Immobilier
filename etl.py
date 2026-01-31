from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

# 1. INITIALISATION
spark = SparkSession.builder \
    .appName("AnalyseImmobilierEvolution") \
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

    # STOCKAGE DANS MONGODB
    try:
        print(f"Envoi vers MongoDB (Année détectée : {df_communes.select('annee').first()[0] if df_communes.count() > 0 else 'N/A'})")
        data_to_insert = df_communes.toPandas().to_dict('records')
        
        client = pymongo.MongoClient(MONGO_URI)
        db = client["immo_db"]
        collection = db["tendances_communes"]
        
        if data_to_insert:
            collection.insert_many(data_to_insert)
            print(f"Données insérées.")
    except Exception as e:
        print(f"⚠️ Erreur de stockage : {e}")

    return df_communes

# --- LANCEMENT ---
dir_path = os.path.dirname(os.path.realpath(__file__))
dossier = os.path.join(dir_path, "Data")
MONGO_URI = os.getenv("MONGO_URI")

if os.path.exists(dossier):
    # Nettoyage de la base au départ pour éviter les doublons de tests
    try:
        pymongo.MongoClient(MONGO_URI)["immo_db"]["tendances_communes"].delete_many({})
        print("Collection MongoDB vidée pour nouvel import.")
    except: pass

    fichiers = [f for f in os.listdir(dossier) if f.endswith('.txt') and not f.startswith('.')]
    for nom_f in fichiers:
        chemin_complet = os.path.join(dossier, nom_f)
        processus_etl(chemin_complet).show(5)
else:
    print(f"❌ Dossier {dossier} introuvable.")