from datetime import datetime, timedelta

from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.utils.dates import days_ago

minio_conn = BaseHook.get_connection("minio")

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
    'pyspark-test',
    default_args=default_args,
    schedule_interval='0 */4 * * *',
    description='',
    catchup=False
)

# spark-submit --packages "org.apache.hadoop:hadoop-aws:3.2.0,com.amazonaws:aws-java-sdk-bundle:.11.980,org.apache.httpcomponents:httpclient:4.5.3,joda-time:joda-time:2.9.9,io.delta:delta-core_2.12:1.0.0" --conf "spark.hadoop.fs.s3a.access.key=admin"  --conf "spark.hadoop.fs.s3a.secret.key=q8Lyl30TwfiOsr7qzeim" --conf "spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem" --conf "spark.hadoop.fs.s3a.endpoint=http://rpi.home.net:9000" --conf "spark.hadoop.fs.s3a.path.style.access=true" --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" --conf "log4j.logger.org.apache.spark.storage.BlockManager=TRACE" -v pyspark/test-pyspark.py
t1 = SparkSubmitOperator(
    task_id='1-test-pyspark',
    conn_id='spark_standalone',
    application='/opt/airflow/spark/scripts/pyspark/test-pyspark.py',
    packages="org.apache.hadoop:hadoop-aws:3.2.0,com.amazonaws:aws-java-sdk-bundle:.11.980,org.apache.httpcomponents:httpclient:4.5.3,joda-time:joda-time:2.9.9,io.delta:delta-core_2.12:1.0.0",
    conf={
        #"spark.deploy.defaultCores": "2",
        #"spark.deploy.maxExecutorRetries": "2",
        "spark.worker.cleanup.enabled": "true",
        "spark.hadoop.fs.s3a.access.key": minio_conn.login,
        "spark.hadoop.fs.s3a.secret.key": minio_conn.password,
        "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
        "spark.hadoop.fs.s3a.endpoint": "http{}://{}:{}".format("", minio_conn.host, minio_conn.port),
        "spark.hadoop.fs.s3a.path.style.access": "true",
        "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
        "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog"
    },
    total_executor_cores=4,
    num_executors=2,
    executor_cores=2,
    executor_memory='512m',
    driver_memory='512m',
    name='test-pyspark',
    execution_timeout=timedelta(minutes=10),
    dag=dag
)

t1
