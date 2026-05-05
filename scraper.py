import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json  


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
