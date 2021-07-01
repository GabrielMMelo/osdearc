FROM apache/airflow:2.0.1-python3.7
USER root
RUN apt update && apt install -y default-jdk 
USER airflow
RUN pip install --user apache-airflow-providers-apache-spark==1.0.3
