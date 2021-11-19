FROM apache/superset:1.0.1
USER root
RUN apt-get update && \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y --no-install-recommends ./google-chrome-stable_current_amd64.deb && \
    rm -f google-chrome-stable_current_amd64.deb

RUN export CHROMEDRIVER_VERSION=$(curl --silent https://chromedriver.storage.googleapis.com/LATEST_RELEASE_94) && \
    wget -q https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/bin && \
    chmod 755 /usr/bin/chromedriver && \
    rm -f chromedriver_linux64.zip

RUN pip install --no-cache gevent psycopg2 redis
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
