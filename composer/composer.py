import flask
import json
import random
import string
import sys
import subprocess
import docker
import os

from flask_cors import CORS
from flask import request

app = flask.Flask("labchainComposer", static_folder="./web/")
app.secret_key = "".join(
    random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
)

CORS(app, origins="*")

client = docker.from_env()

running_instances_count = 1

running_instances = {}


def getDockerInstances():
    instances = client.containers.list(all=True)
    return [
        {
            "id": x.id,
            "name": x.name,
            "status": x.status,
            "port": list(x.attrs["HostConfig"]["PortBindings"].keys()),
        }
        for x in instances
    ]


def getDockerImages():
    images = client.images.list()
    return images


def startInstance(name):
    """ Starts an existing instance
    """
    container = running_instances.get(name, "None")

    if container is None:
        return False

    container.start()

    return True


def createInstance():
    """ Starts a new instance with the given name and the port
    """
    global running_instances_count

    try:
        client.networks.get("labchain_network")
    except docker.errors.NotFound:
        client.networks.create("labchain_network", "bridge")

    running_instances_count += 1

    name = "labchain_{}".format(running_instances_count)

    container = client.containers.run(
        "labchain:latest",
        name=name,
        ports={8080: (5000 + running_instances_count)},
        network="labchain_network",
        detach=True,
    )

    running_instances[name] = container


def stopInstance(name):
    container = running_instances.get(name, "None")

    if container is None:
        return False

    container.stop()

    return True


@app.route("/spawnNetwork", methods=["GET"])
def spawn_network():
    """ Spawns a network
    """
    number = request.args.get("number", None)

    if number is None:
        return "Specify a number", 300

    for i in range(int(number)):
        createInstance()

    instances = getDockerInstances()
    return json.dumps(instances), 200


@app.route("/pruneNetwork", methods=["GET"])
def prune_network():
    """ Prune the network
    """
    instances = getDockerInstances()

    for instance in instances:
        stopInstance(instance["name"])
        os.system("docker rm " + str(instance["name"]))

    return json.dumps([]), 200


@app.route("/getInstances", methods=["GET"])
def get_instances():
    """ Returns the docker instances
    """
    instances = getDockerInstances()
    return json.dumps(instances), 200


@app.route("/deleteInstance", methods=["GET"])
def delete_instance():
    """ Deletes the instance with the given name
    """
    name = request.args.get("name", None)

    if name is None:
        return "Specify a name", 404

    os.system("docker rm " + str(name))

    instances = getDockerInstances()
    return json.dumps(instances), 200


@app.route("/startInstance", methods=["GET"])
def start_instance():
    """ Starts an existing docker instance or creates a new one
    """
    name = request.args.get("name", None)

    if name is None:
        createInstance()
    else:
        if not startInstance(name):
            return "No such instance", 300

    instances = getDockerInstances()
    return json.dumps(instances), 200


@app.route("/stopInstance", methods=["GET"])
def stop_instance():
    """ Stops an existing docker instance
    """
    name = request.args.get("name", None)

    if name is None:
        return "Specify name", 300

    if not stopInstance(name):
        return "Cannot find instance", 300

    instances = getDockerInstances()
    return json.dumps(instances), 200


def hasContainer():
    images = [x.tags for x in getDockerImages()]

    return ["labchain:latest"] in images


if "__main__" == __name__:

    # check if labchain container is available
    if not hasContainer():
        print("Try to pull")
        try:
            client.images.pull("labchain")
        except docker.errors.ImageNotFound as e:
            print("Could not pull image")
            print("Build docker image locally and tag it with 'labchain:latest'")
            print("     cd ROOT/docker")
            print("     docker build -t labchain:latest .")
            sys.exit()

    # initiate program
    instances = [
        x for x in client.containers.list(all=True) if x.name.startswith("labchain_")
    ]

    i = 0
    for instance in instances:
        running_instances[instance.name] = instance
        ii = int(instance.name.split("_")[1])

        if ii > i:
            i = ii

    running_instances_count = i

    print("Recognized instances: {}".format(running_instances_count + 1))
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

    app.run(debug=True, host=_host, port=_port)
