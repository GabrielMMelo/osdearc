from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago


default_args = {
    'owner': 'gabrielmelocomp',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': True,
    'start_date': days_ago(2),
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    'clean_scheduler_log',
    default_args=default_args,
    schedule_interval='0 */12 * * *',
    description='Clean scheduler logs older than 15 days. Keep the logs dry and save precious space on raspberry'
)


t1 = BashOperator(
    task_id='cleaner',
    bash_command='find /usr/local/airflow/logs/scheduler/ -type f -mtime +15 -delete',
    dag=dag
)

t1
