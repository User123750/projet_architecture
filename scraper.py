import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import boto3
from botocore.exceptions import ClientError

def scraper_article_hespress(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200: 
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')

        # -- Extraction des métadonnées --
        try: 
            titre = soup.find('h1').text.strip()
        except: 
            titre = "Titre non trouvé"
            
        try: 
            auteur = soup.find(class_='author').text.strip()
        except: 
            auteur = "Hespress"
            
        try: 
            date_pub = soup.find(class_='date-post').text.strip()
        except: 
            date_pub = "Date non trouvée"
            
        try: 
            categorie = soup.find(class_='cat').text.strip()
        except: 
            categorie = "Infos"

        # -- Nettoyage du Contenu --
        try:
            article_body = soup.find('div', class_='article-content')
            if article_body:
                paragraphes = article_body.find_all('p')
                contenu = " ".join([p.text.strip() for p in paragraphes if len(p.text.strip()) > 30])
            else:
                paragraphes = soup.find_all('p')
                contenu = " ".join([p.text.strip() for p in paragraphes if len(p.text.strip()) > 30])
        except:
            contenu = "Contenu non trouvé"

        return {
            'Titre article': titre, 
            'Auteur': auteur, 
            'Date publication': date_pub, 
            'Catégorie': categorie, 
            'Contenu': contenu, 
            'Source': 'Hespress', 
            'Url': url
        }
    except Exception as e:
        print(f"Erreur sur l'URL {url} : {e}")
        return None

def get_liens_hespress(url_accueil):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url_accueil, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        liens_articles = []
        for a in soup.find_all('a', href=True):
            lien = a['href']
            if "hespress.com" in lien and ".html" in lien:
                liens_articles.append(lien)
        return list(set(liens_articles))[:20] 
    except:
        return []


if __name__ == "__main__":
    print("\n🚀 DEBUT DU SCRAPING : HESPRESS (Version Nettoyée)")
    url_hespress = "https://fr.hespress.com"
    
    liens = get_liens_hespress(url_hespress)
    print(f"   => {len(liens)} articles uniques trouvés.\n")
    
    articles_data = []
    for index, lien in enumerate(liens):
        print(f"   [{index+1}/{len(liens)}] Scraping : {lien}")
        donnees = scraper_article_hespress(lien)
        if donnees:
            articles_data.append(donnees)
        
        # Pause pour ne pas bloquer le serveur
        time.sleep(1)
        
    # --- ETAPE 1 : SAUVEGARDE LOCALE D'ABORD ---
    if articles_data:
        df = pd.DataFrame(articles_data)
        # On sauvegarde le fichier CSV dans notre PC d'abord
        df.to_csv("hespress_brut.csv", index=False, encoding='utf-8-sig')
        print(f"\n✅ Terminé ! {len(articles_data)} articles enregistrés dans le fichier 'hespress_brut.csv'")
        
        # --- ETAPE 2 : ENVOI VERS LE DATA LAKE (MINIO) ENSUITE ---
        print("\n🚀 ENVOI VERS LE DATA LAKE (MINIO)...")
        MINIO_ENDPOINT = 'http://localhost:9000' 
        MINIO_ACCESS_KEY = 'admin_projet'
        MINIO_SECRET_KEY = 'password_secure123'
        BUCKET_NAME = 'bronze'

        # Le "facteur" (client s3) qui va livrer notre fichier
        s3_client = boto3.client('s3',
                                 endpoint_url=MINIO_ENDPOINT,
                                 aws_access_key_id=MINIO_ACCESS_KEY,
                                 aws_secret_access_key=MINIO_SECRET_KEY)

        try:
            # On vérifie si la boîte (bucket) existe, sinon on la crée
            try:
                s3_client.head_bucket(Bucket=BUCKET_NAME)
            except ClientError:
                s3_client.create_bucket(Bucket=BUCKET_NAME)

            # On crée un nom unique avec le temps actuel pour ne pas écraser les anciens fichiers
            nom_fichier_destination = f"hespress_{int(time.time())}.csv" 
            
            # On envoie le fichier "hespress_brut.csv" qu'on vient de créer vers MinIO
            s3_client.upload_file("hespress_brut.csv", BUCKET_NAME, nom_fichier_destination)
            print(f" Fichier envoyé avec succès dans le bucket '{BUCKET_NAME}' sous le nom '{nom_fichier_destination}' !")
            
        except Exception as e:
            print(f" Erreur lors de l'envoi vers MinIO : {e}")
            
    else:
        print("\n Aucun article n'a pu être récupéré.")