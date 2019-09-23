# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Set the working directory to /app
WORKDIR /app

RUN apt-get update && apt-get install -y git gcc npm

RUN pip install --upgrade pip

RUN git clone "https://github.com/putschli/LabChain.git"

WORKDIR /app/LabChain

RUN git checkout network-composer

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

WORKDIR /app/LabChain/composer

ADD start.sh ./start.sh

RUN chmod +x start.sh

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

RUN pip3 install json-rpc

ENV LABCHAIN_DOCKER_NAME labchain:latest
ENV HOST_NAME localhost
ENV PORT 8080

ENTRYPOINT ["./start.sh"]
