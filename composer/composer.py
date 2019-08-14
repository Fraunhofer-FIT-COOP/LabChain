from flask import request
from flask_cors import CORS
import threading
import os
import docker
import subprocess
import sys
import string
import random
import json
import datetime
import time
import calendar
import flask
sys.path.insert(0, '../')  # noqa
from labchain.network.networking import JsonRpcClient, NetworkInterface  # noqa


networkInterface = None

watched_transactions = []

BENCHMARK_DATA_DIRECTORY = "./benchmark_data"

benchmark_data = []


def lookupThread():
    global benchmark_data
    last_block_checked = -1
    while True:
        blocks = networkInterface.requestBlock(None)

        if len(blocks) > 1:
            print("WARNING Multiplebranch heads")

        block = blocks[0]

        if block._block_id == last_block_checked:
            continue

        print(str(block))

        for tx in block._transactions:
            print("Check hash: {}".format(tx.transaction_hash))
            _txs = list(filter(lambda x: x["transaction_hash"] == tx.transaction_hash, watched_transactions))
            if len(_txs) > 0:
                print("Identified transaction: {}".format(tx))
                _tx = _txs[0]
                _tx["end_time"] = calendar.timegm(time.gmtime())
                benchmark_data.append(_tx)

                watched_transactions.remove(_tx)
                print("Watched transactions now #{}".format(len(watched_transactions)))

        last_block_checked = block._block_id

        if len(watched_transactions) == 0 and len(benchmark_data) > 0:
            store_benchmark_data(benchmark_data)
            benchmark_data = []


app = flask.Flask("labchainComposer", static_folder="./web/")
app.secret_key = "".join(
    random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
)

CORS(app, origins="*")

client = docker.from_env()

running_instances_count = 1

running_instances = {}

data_filename = None


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
    global data_filename

    if data_filename is None:
        data_filename = "testData"

    filename = "{}/{}_{}.json".format(BENCHMARK_DATA_DIRECTORY, data_filename, str(datetime.datetime.now()).replace(" ", "_"))

    with open(filename, "w") as f:
        f.write(json.dumps(data, default=str))


@app.route("/dumpBenchmarkData", methods=["GET"])
def dump_benchmark_data():
    store_benchmark_data(benchmark_data)
    return "done", 200


@app.route("/watchTransactions", methods=["POST"])
def set_watch_transactions():
    """ Watches the given transactions to determine when those got mined
    """
    data = json.loads(request.data.decode('utf-8'))

    print("Watch transactions: {}".format(data))

    global data_filename
    data_filename = data["filename"]

    print("Received {} transactions to watch".format(len(data["transactions"])))

    for tx in data["transactions"]:
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


@app.route("/benchmarkStatus", methods=["GET"])
def get_benchmark_status():
    return json.dumps({"found_txs": len(benchmark_data), "remaining_txs": len(watched_transactions)}), 200


@app.route("/benchmarkFiles", methods=["GET"])
def get_benchmarkFiles():
    return json.dumps(os.listdir(BENCHMARK_DATA_DIRECTORY)), 200


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

    if not os.path.exists(BENCHMARK_DATA_DIRECTORY):
        os.makedirs(BENCHMARK_DATA_DIRECTORY)

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

    if len(instances) > 0:
        networkInterface = NetworkInterface(JsonRpcClient(), {"localhost": {(5000 + running_instances_count): {}}})
        t = threading.Thread(target=lookupThread)
        t.start()

    app.run(debug=True, host=_host, port=_port)
