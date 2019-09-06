from flask import request
from flask_cors import CORS
import threading
import os
import math
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
from labchain.util.cryptoHelper import CryptoHelper
from labchain.datastructure.transaction import Transaction

networkInterface = None
BENCHMARK_DATA_DIRECTORY = "./benchmark_data"

benchmark_data = {}

# contains the name of the currently running benchmark or an empty string, if no benchmark
# is running
currently_running_benchmark_name = ""
# stores the queue of batch benchmarks
benchmark_queue = []
lookup_thread_running = False


# spawns the transactions of a benchmark
def spawnBenchmarkTransactions(benchmark_name):
    global benchmark_data

    benchmark = benchmark_data[benchmark_name]

    transactions_per_peer = benchmark["n_transactions_per_peer"]
    print("Distribute {} transactions to {} peers, so {} per peer".format(benchmark["n_transactions"], len(benchmark["peers"]), transactions_per_peer))
    tx_count = 0

    for peer in benchmark["peers"]:
        _networkInterface = NetworkInterface(JsonRpcClient(), {"localhost": {(5000 + int(peer.split("_")[1])): {}}})
        crypto_helper = CryptoHelper.instance()
        sender_pr_key, sender_pub_key = crypto_helper.generate_key_pair()
        recv_pr_key, recv_pub_key = crypto_helper.generate_key_pair()

        for i in range(transactions_per_peer):
            payload = "Example Transaction Payload #" + str(tx_count)
            tx_count += 1
            new_transaction = Transaction(str(sender_pub_key), str(recv_pub_key), payload)
            new_transaction.sign_transaction(crypto_helper, sender_pr_key)
            transaction_hash = crypto_helper.hash(new_transaction.get_json())

            benchmark["watched_transactions"].append({"transaction_hash": transaction_hash, "start_time": time.time()})

            _networkInterface.sendTransaction(new_transaction)


def lookupThread():
    global benchmark_data
    global benchmark_queue
    global currently_running_benchmark_name
    global lookup_thread_running
    global networkInterface
    lookup_thread_running = True
    last_block_checked = -1
    while True:
        if "" == currently_running_benchmark_name and len(benchmark_queue) > 0:
            next_benchmark_name = benchmark_queue[0]
            print("Picked up new benchmark {}".format(next_benchmark_name))
            currently_running_benchmark_name = next_benchmark_name
            benchmark_queue = benchmark_queue[1:]
            spawnBenchmarkTransactions(next_benchmark_name)

        if "" == currently_running_benchmark_name:
            continue

        blocks = None
        try:
            blocks = networkInterface.requestBlock(None)
        except Exception as e:
            continue

        if len(blocks) > 1:
            print("WARNING Multiple branch heads")

        block = blocks[0]

        if block._block_id == last_block_checked:  # block already considered
            continue

        # print(str(block))

        if len(block._transactions) == 0:  # no transactions to consider
            continue

        for tx in block._transactions:
            print("Check hash: {}".format(tx.transaction_hash))

            _txs = list(filter(lambda x: x["transaction_hash"] == tx.transaction_hash, benchmark_data[currently_running_benchmark_name]["watched_transactions"]))
            if len(_txs) > 0:
                print("Identified transaction: {}".format(tx))
                _tx = _txs[0]
                _tx["end_time"] = time.time()
                benchmark_data[currently_running_benchmark_name]["found_transactions"].append(_tx)

                benchmark_data[currently_running_benchmark_name]["watched_transactions"].remove(_tx)

            if len(benchmark_data[currently_running_benchmark_name]["watched_transactions"]) == 0 and not benchmark_data[currently_running_benchmark_name]["finished"]:
                benchmark_data[currently_running_benchmark_name]["finished"] = True
                store_benchmark_data(benchmark_data[currently_running_benchmark_name])
                currently_running_benchmark_name = ""

        last_block_checked = block._block_id


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
    data_filename = data.get("benchmark_name", "")

    if data_filename is None:
        data_filename = "testData"

    filename = "{}/{}_{}.json".format(BENCHMARK_DATA_DIRECTORY, data_filename, str(datetime.datetime.now()).replace(" ", "_"))

    with open(filename, "w") as f:
        f.write(json.dumps(data["found_transactions"], default=str))


@app.route("/benchmarkStatus", methods=["GET"])
def get_benchmark_status():
    global benchmark_data
    global currently_running_benchmark_name

    if "" == currently_running_benchmark_name:
        return {"name": "", "found_txs": 0, "remaining_txs": 0, "total_txs": 0}

    data = {"name": currently_running_benchmark_name, "found_txs": len(benchmark_data[currently_running_benchmark_name]["found_transactions"]), "remaining_txs": len(benchmark_data[currently_running_benchmark_name]["watched_transactions"]), "total_txs": benchmark_data[currently_running_benchmark_name]["n_transactions"]}

    return json.dumps(data), 200


@app.route("/benchmarkQueue")
def get_benchmark_queue():
    global benchmark_queue
    global currently_running_benchmark_name
    qu = []

    if "" != currently_running_benchmark_name:
        qu.append(currently_running_benchmark_name)

    qu.extend(benchmark_queue)
    return json.dumps(qu), 200


@app.route("/benchmarkFiles", methods=["GET"])
def get_benchmarkFiles():
    files = [x[0] for x in sorted([(fn, os.stat(os.path.join(BENCHMARK_DATA_DIRECTORY, fn))) for fn in os.listdir(BENCHMARK_DATA_DIRECTORY)], key=lambda x: x[1].st_ctime)]
    files.reverse()
    return json.dumps(files), 200


@app.route("/benchmarkSimple", methods=["POST"])
def benchmark_simple():
    """ Enqueues a benchmark simple, what means it sends the number of transctions 'n'
    to the peers 'p' provided as parameters in the call.

    The parameter is a JSON of the form:
    { benchmark_name: "", n_transactions : <number>, peers : [] }

    The peer list contains the names of the targetted peers.

    The composer will watch the blocks in the blockchain to determine when a transaction got mined.
    """
    data = json.loads(request.data.decode('utf-8'))

    global benchmark_data
    global benchmark_queue

    benchmark_name = data.get("benchmark_name", None)

    if benchmark_name is None:
        return "Please specify a benchmark name", 300

    if benchmark_name in benchmark_data:
        return "Benchmark exists", 300

    data["watched_transactions"] = []
    data["found_transactions"] = []
    data["finished"] = False

    transactions_per_peer = math.ceil(float(data["n_transactions"] / len(data["peers"])))
    # update number of transactions if number of transactions is not divisable by the number of peers
    data["n_transactions"] = transactions_per_peer * len(data["peers"])
    data["n_transactions_per_peer"] = transactions_per_peer

    benchmark_data[benchmark_name] = data
    benchmark_queue.append(benchmark_name)

    return "Benchmark enqueued", 200


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

    if len(instances) > 0:
        global networkInterface
        networkInterface = NetworkInterface(JsonRpcClient(), {"localhost": {(5000 + running_instances_count): {}}})

        time.sleep(3)  # wait 3 seconds
        t = threading.Thread(target=lookupThread)
        t.start()

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

    if len(instances) > 0 and not lookup_thread_running:
        global networkInterface
        networkInterface = NetworkInterface(JsonRpcClient(), {"localhost": {(5000 + running_instances_count): {}}})

        time.sleep(3)  # wait 3 seconds
        t = threading.Thread(target=lookupThread)
        t.start()

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

    if len(instances) > 0 and not lookup_thread_running:
        networkInterface = NetworkInterface(JsonRpcClient(), {"localhost": {(5000 + running_instances_count): {}}})
        t = threading.Thread(target=lookupThread)
        t.start()

    app.run(debug=True, host=_host, port=_port)
