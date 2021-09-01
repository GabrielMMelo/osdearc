FROM openjdk:8-jdk as run

#MAINTAINER Dremio

#LABEL org.label-schema.name='dremio/dremio-oss'
#LABEL org.label-schema.description='Dremio OSS.'

ARG DOWNLOAD_URL=https://download.dremio.com/community-server/4.9.0-202010170313000159-4a37757a/dremio-community-4.9.0-202010170313000159-4a37757a.tar.gz
#ARG DOWNLOAD_URL=https://download.dremio.com/community-server/dremio-community-LATEST.tar.gz

RUN \
  mkdir -p /opt/dremio \
  && mkdir -p /var/lib/dremio \
  && mkdir -p /var/run/dremio \
  && mkdir -p /var/log/dremio \
  && mkdir -p /opt/dremio/data \
  \
  && groupadd --system dremio \
  && useradd --base-dir /var/lib/dremio --system --gid dremio dremio \
  && chown -R dremio:dremio /opt/dremio/data \
  && chown -R dremio:dremio /var/run/dremio \
  && chown -R dremio:dremio /var/log/dremio \
  && chown -R dremio:dremio /var/lib/dremio \
  && wget -q "${DOWNLOAD_URL}" -O dremio.tar.gz \
  && tar vxfz dremio.tar.gz -C /opt/dremio --strip-components=1 \
  && rm -rf dremio.tar.gz \
#  && apt update \
#  && apt install -y alien \
#  && wget https://download.dremio.com/odbc-driver/1.5.3.1000_2/dremio-odbc-1.5.3.1000-2.x86_64.rpm \
#  && alien -k dremio-odbc.rpm \
#  && dpkg -i dremio-odbc_1.5.3.1000-1_amd64.deb
#  && rpm2cpio dremio-odbc-1.5.3.1000-2.x86_64.rpm | cpio -idmv \
#  && cp /opt/dremio-odbc/conf/odbcinst.ini /etc/odbcinst.ini \
#  && cp /opt/dremio-odbc/conf/odbc.ini /etc/odbc.ini


EXPOSE 9047/tcp
EXPOSE 31010/tcp
EXPOSE 32010/tcp
EXPOSE 45678/tcp

USER dremio
WORKDIR /opt/dremio
ENV DREMIO_HOME /opt/dremio
ENV DREMIO_PID_DIR /var/run/dremio
ENV DREMIO_GC_LOGS_ENABLED="no"
ENV DREMIO_LOG_DIR="/var/log/dremio"
ENV SERVER_GC_OPTS="-XX:+PrintGCDetails -XX:+PrintGCDateStamps"

#COPY certs/CAs/rootCA.pem /opt/dremio/certs/CAs/rootCA.pem
#USER root
#RUN /usr/local/openjdk-8/bin/keytool -import -v -noprompt -trustcacerts -alias minio -file /opt/dremio/certs/CAs/rootCA.pem -keystore cacerts -keypass minio1 -storepass minio1 
#USER dremio
