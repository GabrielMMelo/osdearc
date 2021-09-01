FROM apache/superset:latest-dev
USER root
# add support to dremio as datasource
RUN apt -y install unixodbc-dev
RUN pip install sqlalchemy_dremio
# add ODBC driver
RUN apt install -y alien 
RUN wget https://download.dremio.com/odbc-driver/1.5.3.1000_2/dremio-odbc-1.5.3.1000-2.x86_64.rpm \
  && alien -k --scripts dremio-odbc-1.5.3.1000-2.x86_64.rpm \
  && dpkg -i dremio-odbc_1.5.3.1000-1_amd64.deb
RUN cp /opt/dremio-odbc/conf/odbcinst.ini /etc/odbcinst.ini \
  && cp /opt/dremio-odbc/conf/odbc.ini /etc/odbc.ini
