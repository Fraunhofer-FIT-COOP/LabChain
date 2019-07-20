import flask
import json
import random
import string
import sys
import subprocess
import docker

from flask_cors import CORS
from flask import request

app = flask.Flask("labchainComposer", static_folder = "./web/")
app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

CORS(app, origins = "*")

client = docker.from_env()

running_instances_count = 1

running_instances = {}

def getDockerInstances():
    instances = client.containers.list()
    return [{"id" : x.id, "name" : x.name, "status" : x.status, "port" : list(x.attrs["HostConfig"]["PortBindings"].keys())} for x in instances]

def getDockerImages():
    images = client.images.list()
    return images

def startInstance():
    """ Starts a new instance with the given name and the port
    """

    name = "labchain_{}".format(running_instances_count)

    container = client.containers.run( \
            "labchain:latest", \
            name = name, \
            ports = {(5000 + running_instances_count) : 8080},
            detach=True)

    running_instances[name] = container

    running_instances_count += 1

def stopInstance(name):
    container = running_instances.get(name, "None")

    if container is None:
        return

    container.stop()

@app.route('/getInstances', methods=["GET"])
def get_instances():
    """ Returns the docker instances
    """
    instances = getDockerInstances()
    return json.dumps(instances), 200

@app.route('/startInstance', methods=["GET"])
def start_instance():
    """ Starts an existing docker instance or creates a new one
    """
    startInstance()

    instances = getDockerInstances()
    return json.dumps(instances), 200

@app.route('/stopInstance', methods=["GET"])
def stop_instance():
    """ Stops an existing docker instance
    """
    name = request.args.get('name', None)

    if name is None:
        return "Specify name", 300

    stopInstance(name)

    instances = getDockerInstances()
    return json.dumps(instances), 200

def hasContainer():
    images = [ x.tags for x in getDockerImages()]

    return ["labchain:latest"] in images

if '__main__' == __name__:

    # check if labchain container is available
    if not hasContainer():
        print("Try to pull")
        client.images.pull("labchain")
        if not hasContainer():
            print("Docker image not found - please execute 'docker pull labchain:latest'")
            sys.exit()

    # initiate program
    instances = [x for x in client.containers.list() if x.name.startswith("labchain_")]

    i = 0
    for instance in instances:
        running_instances[instance.name] = instance
        ii = int(instance.name.split("_")[1])

        if ii > i:
            i = ii

    running_instances_count = i

    print("Recognized instances: {}".format(running_instances_count))
    print(running_instances)

    arguments = sys.argv
    _host = "127.0.0.1"
    _port = 80

    if len(arguments) == 2:
        _host = arguments[1]
    elif len(arguments) == 3:
        _host = arguments[1]
        _port = int(arguments[2])

    print("Starting server at http://{}:{}".format(_host, _port))

    app.run(debug = True, host = _host, port = _port)
