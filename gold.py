import pandas as pd
import json
import time
import boto3
from botocore.exceptions import ClientError

if __name__ == "__main__":
    print("\n DEBUT DE LA COUCHE GOLD (Analyse et Statistiques)")
    
    try:
        print(" Lecture du fichier hespress_clean.csv...")
        df_silver = pd.read_csv("opt/airflow/scripts/hespress_clean.csv")
        
        print(" Calcul des statistiques en cours...")
        
        stats_categories = df_silver['Catégorie'].value_counts().to_dict()
        
        stats_auteurs = df_silver['Auteur'].value_counts().to_dict()
        
        stats_langues = df_silver['Langue'].value_counts().to_dict()
        
        dashboard_data = {
            "total_articles": len(df_silver),
            "repartition_categories": stats_categories,
            "top_auteurs": stats_auteurs,
            "repartition_langues": stats_langues,
            "date_generation": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        fichier_gold = "hespress_stats.json"
        with open(fichier_gold, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=4)
        print(f" Statistiques générées localement dans '{fichier_gold}' !")
        
       
        print("\n ENVOI VERS LE DATA LAKE (BUCKET GOLD)...")
        MINIO_ENDPOINT = 'http://localhost:9000' 
        MINIO_ACCESS_KEY = 'admin_projet'
        MINIO_SECRET_KEY = 'password_secure123'
        BUCKET_GOLD = 'gold'

        s3_client = boto3.client('s3',
                                 endpoint_url=MINIO_ENDPOINT,
                                 aws_access_key_id=MINIO_ACCESS_KEY,
                                 aws_secret_access_key=MINIO_SECRET_KEY)

        try:
            s3_client.head_bucket(Bucket=BUCKET_GOLD)
        except ClientError:
            s3_client.create_bucket(Bucket=BUCKET_GOLD)

       
        nom_destination = f"stats_hespress_{int(time.time())}.json"
        s3_client.upload_file(fichier_gold, BUCKET_GOLD, nom_destination)
        print(f" Fichier envoyé avec succès dans le bucket '{BUCKET_GOLD}' sous le nom '{nom_destination}' !")

    except FileNotFoundError:
        print(" Erreur : Le fichier 'hespress_clean.csv' est introuvable. Exécute la couche Silver d'abord.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")