import pandas as pd
from sqlalchemy import create_engine

if __name__ == "__main__":
    print("\n📦 DEBUT DE LA COUCHE DATA WAREHOUSE (Qualité & Chargement)")
    
    try:
        # 1. Lecture des données Silver
        print("Lecture du fichier hespress_clean.csv...")
        df = pd.read_csv("/opt/airflow/scripts/hespress_clean.csv")
        
        # --- TÂCHE 4.1 : QUALITÉ DES DONNÉES ---
        print("Application des règles de Qualité (Data Quality)...")
        total_avant = len(df)
        
        # Règle A : Rejeter les articles sans titre valide
        df = df[df['Titre article'] != "Titre non trouvé"]
        
        # Règle B : Rejeter les articles avec un contenu trop court (moins de 50 caractères)
        df = df[df['Contenu_Clean'].str.len() > 50]
        
        # Règle C : S'assurer qu'il n'y a pas de date manquante
        df = df[df['Date publication'] != "Date non trouvée"]
        
        total_apres = len(df)
        print(f"📊 Contrôle terminé : {total_avant - total_apres} articles corrompus rejetés.")
        
        # --- TÂCHE 4.3 : POUSSER VERS LE DATA WAREHOUSE ---
        print("\n🚀 Connexion au Data Warehouse PostgreSQL...")
        # L'URL de connexion : postgresql://user:password@host:port/database
        # 'data_warehouse' est le nom du service dans le docker-compose
        engine = create_engine('postgresql://admin_dw:password_dw@data_warehouse:5432/presse_dw')
        
        # Envoi des données analytiques complètes
        df.to_sql('articles_analytiques', engine, if_exists='replace', index=False)
        print("✅ Données insérées avec succès dans la table 'articles_analytiques' !")
        
        # Création d'une table analytique "Articles par jour" (comme demandé dans le cahier des charges)
        df_jour = df.groupby('Date publication').size().reset_index(name='Nombre_Articles')
        df_jour.to_sql('stats_articles_par_jour', engine, if_exists='replace', index=False)
        print("✅ Table agrégée 'stats_articles_par_jour' créée avec succès !")

    except Exception as e:
        print(f"❌ Erreur lors du traitement : {e}")