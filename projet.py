from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType

# Objectif : Source (CSV) -> PySpark (Nettoyage) -> HDFS/Mongo (Stockage) -> Streamlit (Visualisation).

# 1. INITIALISATION (Obligatoire pour PySpark)
spark = SparkSession.builder \
    .appName("AnalyseImmobilier") \
    .config("spark.mongodb.output.uri", "mongodb://127.0.0.1/immo_db.tendances") \
    .getOrCreate()

def processus_etl(chemin_csv):
    # 2. IMPORT (5 points)
    # On utilise Spark pour lire le fichier avec le séparateur '|'
    df = spark.read.options(header='true', sep='|', inferSchema='true').csv("ton_fichier.txt")

    # 3. NETTOYAGE & TRANSFORMATION (Organisation de la donnée)
    # On caste les types pour les calculs
    df_clean = df.withColumn("Valeur fonciere", F.col("Valeur fonciere").cast("double")) \
                 .withColumn("Surface reelle bati", F.col("Surface reelle bati").cast("double")) \
                 .withColumn("Date mutation", F.to_date(F.col("Date mutation"), "dd/MM/yyyy"))

    # Filtres métier (comme dans ton code Pandas)
    df_filtered = df_clean.filter(
        (F.col("Nature mutation") == "Vente") &
        (F.col("Type local").isin("Maison", "Appartement")) &
        (F.col("Surface reelle bati") > 9) &
        (F.col("Valeur fonciere") > 1000)
    ).dropna(subset=["Valeur fonciere", "Surface reelle bati"])

    # 4. CALCUL DES KPIS (Table Gold / Tendances)
    # Calcul du prix au m2
    df_final = df_filtered.withColumn("prix_m2", F.col("Valeur fonciere") / F.col("Surface reelle bati"))
    
    # Filtre des aberrations
    df_final = df_final.filter((F.col("prix_m2") > 500) & (F.col("prix_m2") < 15000))

    # Agrégation par Commune (pour tes tendances)
    df_communes = df_final.groupBy("Code departement", "Commune").agg(
        F.median("prix_m2").alias("prix_median"),
        F.count("Valeur fonciere").alias("nb_ventes")
    )

    # 5. STOCKAGE (2 points facultatifs)
    # Sauvegarde sur HDFS au format Parquet (plus performant que CSV)
    df_communes.write.mode("overwrite").parquet("hdfs:///user/data/immo_final")
    
    # OU Sauvegarde vers MongoDB
    # df_communes.write.format("mongodb").mode("append").save()

    return df_communes

# Lancement
processus_etl("ValeursFoncieres-2020-S2.txt").show()