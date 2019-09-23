# Use an official Python runtime as a parent image
FROM python:3.7-slim

RUN apt-get update && apt-get install -y gcc

# Set the working directory to /app
WORKDIR /app/LabChain

COPY labchain /app/LabChain/labchain
COPY client.py /app/LabChain/client.py
COPY node.py /app/LabChain/node.py
COPY requirements.txt /app/LabChain/requirements.txt

COPY docker/start.sh /app/LabChain/start.sh

RUN chmod +x /app/LabChain/start.sh

RUN pip install --upgrade pip

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

ENV PORT 8080
ENV PEER NONE
ENV CORS NONE
ENV BENCHMARK NONE

# Make port 8080 available to the world outside this container
EXPOSE $PORT

# Run app.py when the container launches
ENTRYPOINT ["./start.sh"]
