FROM nodered/node-red-docker:slim

USER root

WORKDIR /usr/local/lib/node_modules/

# Install node-red(unsafe) and node-red-dashboard
RUN npm install -g --unsafe-perm node-red
RUN npm i node-red-dashboard

# Install additional bases
RUN apk add --no-cache gcc musl-dev linux-headers

# Install python and pip
RUN apk add --no-cache python3 python3-dev py-pip

#Install Mosquitto Broker
RUN apk add --update mosquitto

RUN mkdir /labchain
WORKDIR /labchain
COPY . /labchain

# Install our requirements
RUN pip3 install -r requirements.txt

RUN chmod u+x startup.sh

EXPOSE 8080
EXPOSE 1883

CMD ["./startup.sh"]
