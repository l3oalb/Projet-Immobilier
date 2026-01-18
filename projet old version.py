from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType

# Objectif : Source (txt) -> PySpark (Nettoyage) -> HDFS/Mongo (Stockage) -> Streamlit (Visualisation).

# 1. INITIALISATION (Corrigée pour MongoDB)
spark = SparkSession.builder \
    .appName("AnalyseImmobilier") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .config("spark.mongodb.read.connection.uri", "mongodb://127.0.0.1:27017/immo_db.tendances_communes") \
    .config("spark.mongodb.write.connection.uri", "mongodb://127.0.0.1:27017/immo_db.tendances_communes") \
    .getOrCreate()
    #.config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.1.1") \
    #.config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.4.0") \

def processus_etl(chemin_txt):
    # IMPORT : Ajout du decimal=',' pour les prix français
    df = spark.read.options(header='true', sep='|', encoding='ISO-8859-1', decimal=',').csv(chemin_txt)
    
    # Traçabilité
    df = df.withColumn("source_file", F.element_at(F.split(F.input_file_name(), "/"), -1))

    # NETTOYAGE : On garde des noms propres dès le début
    # On remplace la virgule par un point AVANT de caster en double
    df_clean = df.withColumn("valeur_fonciere", 
                             F.regexp_replace(F.col("Valeur fonciere"), ",", ".").cast("double")) \
                 .withColumn("surface_bati", 
                             F.regexp_replace(F.col("Surface reelle bati"), ",", ".").cast("double")) \
                 .withColumn("date_mutation", F.to_date(F.col("Date mutation"), "dd/MM/yyyy"))
    
    # Filtres
    df_filtered = df_clean.filter(
        (F.col("Nature mutation") == "Vente") &
        (F.col("Type local").isin("Maison", "Appartement")) &
        (F.col("surface_bati") > 9) &
        (F.col("valeur_fonciere") > 1000)
    ).dropna(subset=["valeur_fonciere", "surface_bati"])

    # Calcul et Agrégation
    df_communes = df_filtered.withColumn("prix_m2", F.col("valeur_fonciere") / F.col("surface_bati")) \
        .filter((F.col("prix_m2") > 500) & (F.col("prix_m2") < 15000)) \
        .groupBy("Code departement", "Commune", "source_file").agg(
            F.round(F.median("prix_m2"), 2).alias("prix_median"),
            F.count("valeur_fonciere").alias("nb_ventes")
        ).withColumnRenamed("Code departement", "code_dept")

    # STOCKAGE : Plus simple car configuré dans la SparkSession
    print(f"📥 Stockage de {chemin_txt} dans MongoDB...")
    df_communes.write.format("mongodb").mode("append").save()

    return df_communes

# Lancement
import os

# On récupère le chemin absolu du dossier "Data"
dir_path = os.path.dirname(os.path.realpath(__file__))
dossier = os.path.join(dir_path, "Data") 

print(f"Le script cherche ici : {dossier}")

if os.path.exists(dossier):
    fichiers = [f for f in os.listdir(dossier) if f.endswith('.txt') and not f.startswith('.')]
    print(f"📂 Fichiers trouvés : {fichiers}")

    for nom_f in fichiers:
        chemin_complet = os.path.join(dossier, nom_f)
        print(f"🚀 Début du traitement Spark pour : {nom_f}")
        
        # On appelle l'ETL
        resultat = processus_etl(chemin_complet)
        
        # On force l'affichage du tableau
        print(f"Résumé des données pour {nom_f} :")
        resultat.show(10)
else:
    print(f"ERREUR : Le dossier {dossier} est introuvable !")