#!/bin/sh

cd /app/LabChain/composer/web/composer

npm install

sed -i "s/[[:space:]]*public[[:space:]]static[[:space:]]host.*/public static host = \"${HOST_NAME}\"/g" src/docker/DockerInterface.ts

npm run build

cd ../..

exec python3 composer.py
