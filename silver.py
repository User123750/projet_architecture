import pandas as pd
import re
import time
import boto3
from langdetect import detect

def clean_text(texte):
    if type(texte) != str: return ""
    texte = re.sub(r'<[^>]+>', '', texte) 
    texte = re.sub(r'\s+', ' ', texte)  
    return texte.strip()

def get_lang(texte):
    try: return detect(texte[:100])       
    except: return "inconnu"

print("1. Lecture du fichier brut...")
df = pd.read_csv("/opt/airflow/scripts/hespress_brut.csv")

print("2. Nettoyage et détection de langue...")
df['Contenu_Clean'] = df['Contenu'].apply(clean_text)
df['Titre_Clean'] = df['Titre article'].apply(clean_text)
df['Langue'] = df['Contenu_Clean'].apply(get_lang)

df.to_csv("/opt/airflow/scripts/hespress_clean.csv", index=False)
print(" Fichier propre sauvegardé : hespress_clean.csv")

print("3. Envoi au Data Lake (MinIO)...")
print("3. Envoi au Data Lake (MinIO)...")
s3 = boto3.client('s3', 
                  endpoint_url='http://minio:9000', 
                  aws_access_key_id='admin_projet', 
                  aws_secret_access_key='password_secure123')

nom_fichier = f"hespress_clean_{int(time.time())}.csv"

s3.upload_file("/opt/airflow/scripts/hespress_clean.csv", "silver", nom_fichier)

print(f" Fichier envoyé à MinIO sous le nom : {nom_fichier}")