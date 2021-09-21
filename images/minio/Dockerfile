FROM raspbian/stretch:latest

WORKDIR /home/pi/
RUN apt update
RUN apt upgrade -y
RUN wget https://dl.minio.io/server/minio/release/linux-arm/minio && \
    wget https://dl.minio.io/client/mc/release/linux-arm/mc && \
    sudo chmod +x /home/pi/minio && \
    sudo chmod +x /home/pi/mc && \
    sudo ln -s /home/pi/minio /usr/bin/minio