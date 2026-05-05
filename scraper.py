import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json  
import boto3 
from botocore.exceptions import ClientError 

def scraper_article_hespress(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.content, 'html.parser')

        try: titre = soup.find('h1').text.strip()
        except: titre = "Titre non trouvé"
        try: auteur = soup.find(class_='author').text.strip()
        except: auteur = "Hespress"
        try: date_pub = soup.find(class_='date-post').text.strip()
        except: date_pub = "Date non trouvée"
        try: categorie = soup.find(class_='cat').text.strip()
        except: categorie = "Politique / À définir"
        try:
            paragraphes = soup.find_all('p')
            contenu = " ".join([p.text.strip() for p in paragraphes])
        except: contenu = "Contenu non trouvé"

        return {'Titre article': titre, 'Auteur': auteur, 'Date publication': date_pub, 'Catégorie': categorie, 'Contenu': contenu, 'Source': 'Hespress', 'Url': url}
    except Exception as e:
        print(f"Erreur Hespress {url} : {e}")
        return None

def get_liens_hespress(url_accueil):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url_accueil, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    liens_articles = []
    for a in soup.find_all('a', href=True):
        lien = a['href']
        if "hespress.com" in lien and ".html" in lien:
            liens_articles.append(lien)
    return list(set(liens_articles))[:20] 

 
if __name__ == "__main__":

    print("\n DEBUT DU SCRAPING : HESPRESS")
    url_hespress = "https://fr.hespress.com"
    liens_hespress = get_liens_hespress(url_hespress)
    print(f"   => {len(liens_hespress)} articles trouvés pour le test.\n")
    
    articles_hespress = []
    for lien in liens_hespress:
        print(f"   - Scraping de : {lien}")
        donnees = scraper_article_hespress(lien)
        if donnees: articles_hespress.append(donnees)
        time.sleep(1)
        
    pd.DataFrame(articles_hespress).to_csv("hespress_brut.csv", index=False, encoding='utf-8-sig')
    print(" Fichier hespress_brut.csv est créé avec succès !")
    print("\n ENVOI VERS LE DATA LAKE (MINIO)...")
    
    
    MINIO_ENDPOINT = 'http://localhost:9000' 
    MINIO_ACCESS_KEY = 'admin_projet'
    MINIO_SECRET_KEY = 'password_secure123'
    BUCKET_NAME = 'bronze'

    s3_client = boto3.client('s3',
                             endpoint_url=MINIO_ENDPOINT,
                             aws_access_key_id=MINIO_ACCESS_KEY,
                             aws_secret_access_key=MINIO_SECRET_KEY)

    try:
        try:
            s3_client.head_bucket(Bucket=BUCKET_NAME)
        except ClientError:
            s3_client.create_bucket(Bucket=BUCKET_NAME)

        nom_fichier_destination = f"hespress_{int(time.time())}.csv" # Ajoute un timestamp pour ne pas écraser les anciens
        s3_client.upload_file("hespress_brut.csv", BUCKET_NAME, nom_fichier_destination)
        print(f"  Fichier envoyé avec succès dans le bucket '{BUCKET_NAME}' sous le nom '{nom_fichier_destination}' !")
        
    except Exception as e:
        print(f"  Erreur lors de l'envoi vers MinIO : {e}")