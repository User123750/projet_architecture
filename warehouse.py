import pandas as pd
from sqlalchemy import create_engine

if __name__ == "__main__":
    print("\n DEBUT DE LA COUCHE DATA WAREHOUSE (Qualité & Chargement)")
    
    try:
        print("Lecture du fichier hespress_clean.csv...")
        df = pd.read_csv("/opt/airflow/scripts/hespress_clean.csv")

        print("Application des règles de Qualité (Data Quality)...")
        total_avant = len(df)

        df = df[df['Titre article'] != "Titre non trouvé"]

        df = df[df['Contenu_Clean'].str.len() > 50]

        df = df[df['Date publication'] != "Date non trouvée"]
        
        total_apres = len(df)
        print(f"Contrôle terminé : {total_avant - total_apres} articles corrompus rejetés.")
        
        print("\nConnexion au Data Warehouse PostgreSQL...")
        engine = create_engine('postgresql://admin_dw:password_dw@data_warehouse:5432/presse_dw')

        df.to_sql('articles_analytiques', engine, if_exists='replace', index=False)
        print("Données insérées avec succès dans la table 'articles_analytiques' !")
        
        df_jour = df.groupby('Date publication').size().reset_index(name='Nombre_Articles')
        df_jour.to_sql('stats_articles_par_jour', engine, if_exists='replace', index=False)
        print(" Table agrégée 'stats_articles_par_jour' créée avec succès !")

    except Exception as e:
        print(f" Erreur lors du traitement : {e}")