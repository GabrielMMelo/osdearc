from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
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
    'scripts-test',
    default_args=default_args,
    schedule_interval='0 */4 * * *',
    description=''
)

t1 = SparkSubmitOperator(
    task_id='1-test-scripts',
    conn_id='spark_local',
    application='/opt/airflow/spark/scripts/pyspark/test-scripts.py',
    #total_executor_cores=4,
    #packages="io.delta:delta-core_2.12:0.7.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0",
    #executor_cores=2,
    #executor_memory='5g',
    #driver_memory='5g',
    name='test-scripts',
    execution_timeout=timedelta(minutes=10),
    dag=dag
)

t1
