from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'scripts')))

from data_generator import load_data_to_dwh

# Налаштування DAG
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

DBT_PROJECT_DIR = '/mnt/c/Users/pilga/cinema-dwh/cinema_dbt'
DBT_PROFILES_DIR = '/mnt/c/Users/pilga/cinema-dwh/cinema_dbt'

with DAG(
    'cinema_elt_pipeline',
    default_args=default_args,
    description='Конвеєр завантаження, трансформації та тестування даних онлайн-кінотеатру',
    schedule='@daily',
    catchup=False
) as dag:

    # Таск 1: Видобуток та завантаження сирих даних у PostgreSQL
    extract_load_task = PythonOperator(
        task_id='extract_and_load_raw_data',
        python_callable=load_data_to_dwh
    )

    # Таск 2: Запуск SQL-трансформацій dbt для побудови схеми «Зірка»
    dbt_run_task = BashOperator(
        task_id='dbt_run_transformations',
        bash_command=f'dbt run --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}'
    )

    # Таск 3: Запуск перевірок якості даних dbt test
    dbt_test_task = BashOperator(
        task_id='dbt_test_data_quality',
        bash_command=f'dbt test --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}'
    )

    # Чітка послідовність виконання
    extract_load_task >> dbt_run_task >> dbt_test_task