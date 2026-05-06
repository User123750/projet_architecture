from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# 1. Les paramètres par défaut
default_args = {
    'owner': 'rihab',
    'depends_on_past': False,
    'start_date': datetime(2026, 5, 5), 
    'retries': 1, 
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    'pipeline_hespress_medallion',
    default_args=default_args,
    description='Mon premier pipeline de donnees: Bronze -> Silver -> Gold',
    schedule_interval='@daily', 
    catchup=False,
    tags=['projet_hespress'],
) as dag:

    tache_bronze = BashOperator(
        task_id='ingestion_bronze',
        bash_command='cd /opt/airflow/scripts && python scraper.py'
    )

    tache_silver = BashOperator(
        task_id='nettoyage_silver',
        bash_command='cd /opt/airflow/scripts && python silver.py' 
    )

    tache_gold = BashOperator(
        task_id='analyse_gold',
        bash_command='cd /opt/airflow/scripts && python gold.py'
    )

    tache_bronze >> tache_silver >> tache_gold