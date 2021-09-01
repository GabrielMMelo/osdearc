ARG DOCKER_GROUP_ID
FROM apache/airflow:2.0.1-python3.7
ARG DOCKER_GROUP_ID
USER root
RUN apt update && apt install -y default-jdk  apt-transport-https ca-certificates curl gnupg2 software-properties-common
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
RUN apt update
RUN groupadd -g $DOCKER_GROUP_ID docker \
  && curl -sSL https://get.docker.com/ | sh \
  && apt-get -q autoremove \
  && apt-get -q clean -y \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*.bin 
RUN usermod -aG docker airflow
USER airflow
RUN pip install --user apache-airflow-providers-apache-spark==1.0.3
