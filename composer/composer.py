import flask
import datetime
import json
import random
import string
import sys
import subprocess
import docker
import os
import threading

from flask_cors import CORS
from flask import request


class BCClient:
    def getBlock(self):
        return []


bcclient = BCClient()


def lookupThread():
    while True:
        blocks = bcclient.getBlock()

        for block in blocks:
            for tx in block.transactions:
                _txs = filter(lambda x: x["transaction_hash"])
                if len(_txs) > 0:
                    _tx = _txs[0]
                    _tx["end_date"] = datetime.datetime.now()

                    watched_transactions.remove(_tx)


watched_transactions = []

app = flask.Flask("labchainComposer", static_folder="./web/")
app.secret_key = "".join(
    random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
)

CORS(app, origins="*")

client = docker.from_env()

running_instances_count = 1

running_instances = {}


def getDockerInstances():
    instances = [
        x for x in client.containers.list(all=True) if x.name.startswith("labchain_")
    ]
    network_containers = client.networks.get("labchain_network").attrs["Containers"]

    return [
        {
            "id": x.id,
            "name": x.name,
            "status": x.status,
            "mac": network_containers.get(x.id, {"MacAddress": ""})["MacAddress"],
            "ipv4": network_containers.get(x.id, {"IPv4Address": ""})["IPv4Address"],
            "ipv6": network_containers.get(x.id, {"IPv6Address": ""})["IPv6Address"],
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


def createInstance(instances=[]):
    """ Starts a new instance with the given name and the port

        Return the 'name' of the given instance
    """
    global running_instances_count

    try:
        client.networks.get("labchain_network")
    except docker.errors.NotFound:
        client.networks.create("labchain_network", "bridge")

    running_instances_count += 1

    name = "labchain_{}".format(running_instances_count)

    envr = []

    if len(instances) > 0:
        envr = ["PEER=" + " ".join([str(x) + ":8080" for x in instances])]

    envr.append("CORS=\"*\"")

    container = client.containers.run(
        "labchain:latest",
        name=name,
        ports={8080: (5000 + running_instances_count)},
        network="labchain_network",
        environment=envr,
        detach=True,
    )

    running_instances[name] = container

    return name


def stopInstance(name):
    container = running_instances.get(name, "None")

    if container is None:
        return False

    container.stop()

    return True


def store_benchmark_data(data):
    """ Stores the data into a file locally
    """
    filename = "./testData_{}.json".format(str(datetime.datetime.now()).replace(" ", "_"))

    with open(filename, "w") as f:
        f.write(data)


@app.route("/watchTransactions", methods=["POST"])
def watch_transactions():
    """ Watches the given transactions to determine when those got mined
    """
    txs = json.loads(request.data)

    for tx in txs:
        watched_transactions.append(tx)

    return "Added transactions", 200


@app.route("/spawnNetwork", methods=["GET"])
def spawn_network():
    """ Spawns a network
    """
    number = request.args.get("number", None)

    if number is None:
        return "Specify a number", 300

    number = int(number)

    instances = []
    for i in range(number):
        instances.append(createInstance(instances))

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

    print("Recognized instances: {}".format(len(instances)))
    print(running_instances)

    arguments = sys.argv
    _host = "127.0.0.1"
    _port = 8080

    if len(arguments) == 2:
        _host = arguments[1]
    elif len(arguments) == 3:
        _host = arguments[1]
        _port = int(arguments[2])

    print("Starting server at http://{}:{}".format(_host, _port))

    t = threading.Thread(target=lookupThread)
    t.start()

    app.run(debug=True, host=_host, port=_port)
