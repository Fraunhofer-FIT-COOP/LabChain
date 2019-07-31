# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Set the working directory to /app
WORKDIR /app

RUN apt-get update && apt-get install -y git gcc

RUN git clone "https://github.com/putschli/LabChain.git"

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip

WORKDIR /app/LabChain

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

ENV PORT 8080
ENV PEER NONE

# Make port 8080 available to the world outside this container
EXPOSE $PORT

# Run app.py when the container launches
CMD ["python3", "./node.py", "--port", "8080", "--very-verbose", "--peer-discovery"]
