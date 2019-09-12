from flask import request, render_template
from flask_cors import CORS
import threading
import os
import math
import docker
from docker.types import Mount
import subprocess
import sys
import string
import random
import json
import datetime
import time
import calendar
import flask
import logging
sys.path.insert(0, '../')  # noqa
from labchain.network.networking import JsonRpcClient, NetworkInterface  # noqa
from labchain.util.cryptoHelper import CryptoHelper
from labchain.datastructure.transaction import Transaction

networkInterface = None
BENCHMARK_DATA_DIRECTORY = "./benchmark_data"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

# If 15 consecutive bloks are empty we assume that potentially
# not-mined transactions will not be mined and the benchmark will be finished
EMPTY_COUNT_THRESHOLD = 15

benchmark_data = {}

# contains the name of the currently running benchmark or an empty string, if no benchmark
# is running
currently_running_benchmark_name = ""
# stores the queue of batch benchmarks
benchmark_queue = []
lookup_thread_running = False


class BenchmarkDir:
    """ Holds the directory information where to store the benchmark data
    """

    @staticmethod
    def absolutePath(test_name=None, file_name=None):
        """ Returns the absolute path to the benchmark directory
        If test_name is not None it creates a sub folder in the benchmark directory and returns the absolute path to it
        If file_name is not None it will also append the file name
        """
        abs_path = os.path.abspath(os.environ.get("BENCHMARK_DIR", BENCHMARK_DATA_DIRECTORY))

        if test_name is not None:
            abs_path = os.path.join(abs_path, test_name)

            if not os.path.exists(abs_path):
                os.makedirs(abs_path)

        if file_name is not None:
            abs_path = os.path.join(abs_path, file_name)

        return abs_path

    @staticmethod
    def hostPath(test_name=None, file_name=None):
        """ Returns the host path to the benchmark directory. This is configurable, since in case
        the composer is running as docker container it must be possible to spawn siblings that put their
        benchmark logs into directories of the host system
        If test_name is not None it creates a sub folder in the benchmark directory and returns the relative path to it
        If file_name is not None it will also append the file name
        """
        rel_path = os.environ.get("HOST_DIR", BenchmarkDir.absolutePath())

        if test_name is not None:
            rel_path = os.path.join(rel_path, test_name)

            if not os.path.exists(rel_path):
                os.makedirs(rel_path)

        if file_name is not None:
            rel_path = os.path.join(rel_path, file_name)

        return rel_path


def spawnBenchmarkTransactions(benchmark_name):
    """ spawns the transactions of a benchmark
    """
    global benchmark_data

    benchmark = benchmark_data[benchmark_name]

    transactions_per_peer = benchmark["n_transactions_per_peer"]
    logger.info("Distribute {} transactions to {} peers, so {} per peer".format(benchmark["n_transactions"], len(benchmark["peers"]), transactions_per_peer))
    tx_count = 0

    for peer in benchmark["peers"]:
        _networkInterface = NetworkInterface(JsonRpcClient(), {os.environ.get("HOST_NAME", "localhost"): {(5000 + int(peer.split("_")[1])): {}}})
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


def setupBenchmarkNetwork(benchmark_name):
    global benchmark_data
    node_count = benchmark_data[benchmark_name]["nodecount"]

    if -1 == node_count:
        raise Exception("Invalid node count")

    # first stop all currently running instances
    stopAllDockerInstances()
    logger.info("Pruned existing network")
    logger.info("Spawn new network with {} nodes".format(node_count))
    instances = spawnNodes(node_count, benchmark_name)
    logger.info("Spawned new network")

    benchmark_data[benchmark_name]["peers"] = list(map(lambda x: x["name"], instances))


def setupBenchmark(benchmark_name):
    global benchmark_data

    if benchmark_data[benchmark_name]["nodecount"] != -1:
        setupBenchmarkNetwork(benchmark_name)

    spawnBenchmarkTransactions(benchmark_name)


def lookupThread():
    global benchmark_data
    global benchmark_queue
    global currently_running_benchmark_name
    global lookup_thread_running
    global networkInterface
    lookup_thread_running = True
    last_block_checked = -1
    empty_count = 0

    while True:
        if "" == currently_running_benchmark_name and len(benchmark_queue) > 0:
            next_benchmark_name = benchmark_queue[0]
            logger.info("Picked up new benchmark {}".format(next_benchmark_name))
            currently_running_benchmark_name = next_benchmark_name
            benchmark_queue = benchmark_queue[1:]
            setupBenchmark(next_benchmark_name)

        if "" == currently_running_benchmark_name:
            continue

        blocks = None
        try:
            blocks = networkInterface.requestBlock(None)
        except Exception as e:
            continue

        if len(blocks) > 1:
            logger.info("WARNING Multiple branch heads")

        block = blocks[0]

        if block._block_id == last_block_checked:  # block already considered
            continue

        # logger.info(str(block))

        if len(block._transactions) == 0:  # no transactions to consider
            empty_count += 1

            if empty_count == EMPTY_COUNT_THRESHOLD:
                empty_count = 0
                benchmark_data[currently_running_benchmark_name]["finished"] = True
                store_benchmark_data(benchmark_data[currently_running_benchmark_name])
                currently_running_benchmark_name = ""
            else:
                continue
        else:
            empty_count = 0

        for tx in block._transactions:
            logger.info("Check hash: {}".format(tx.transaction_hash))

            _txs = list(filter(lambda x: x["transaction_hash"] == tx.transaction_hash, benchmark_data[currently_running_benchmark_name]["watched_transactions"]))
            if len(_txs) > 0:
                logger.info("Identified transaction: {}".format(tx))
                _tx = _txs[0]
                _tx["end_time"] = time.time()
                benchmark_data[currently_running_benchmark_name]["found_transactions"].append(_tx)

                benchmark_data[currently_running_benchmark_name]["watched_transactions"].remove(_tx)

            if len(benchmark_data[currently_running_benchmark_name]["watched_transactions"]) == 0 and not benchmark_data[currently_running_benchmark_name]["finished"]:
                benchmark_data[currently_running_benchmark_name]["finished"] = True
                store_benchmark_data(benchmark_data[currently_running_benchmark_name])
                currently_running_benchmark_name = ""

        last_block_checked = block._block_id


app = flask.Flask("labchainComposer", static_folder="web/composer/build/static", template_folder="web/composer/build")
app.secret_key = "".join(
    random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
)

CORS(app, origins="*")

client = docker.from_env()

running_instances_count = 1

running_instances = {}


@app.route('/')
def main():
    return render_template('index.html')


def getDockerInstance(name):
    instances = [
        x for x in client.containers.list(all=True) if x.name == name
    ]

    if len(instances) == 0:
        return None

    return instances[0]


def getDockerInstances():
    instances = [
        x for x in client.containers.list(all=True) if x.name.startswith("labchain_") and not x.name == "labchain_network_composer"
    ]

    network_containers = {}

    if client.networks.get("labchain_network"):
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


def createInstance(instances=[], test_name=None):
    """ Starts a new instance with the given name and the port

        Return the 'name' of the given instance
    """
    global running_instances_count
    global benchmark_data

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
    envr.append("BENCHMARK=benchmark.json")

    container_benchmark_file_name = "{}.json".format(name)

    host_path = BenchmarkDir.hostPath(test_name, container_benchmark_file_name)

    if test_name is not None:
        benchmark_logs = benchmark_data[test_name].get("benchmark_logs", [])
        benchmark_logs.append(host_path)
        benchmark_data[test_name]["benchmark_logs"] = benchmark_logs

    open(BenchmarkDir.absolutePath(test_name, container_benchmark_file_name), "a").close()

    logger.info("Mount({}, {})".format("/app/LabChain/benchmark.json", host_path))

    mnt = Mount(target="/app/LabChain/benchmark.json", source=host_path, type="bind")

    container = client.containers.run(
        "labchain:latest",
        name=name,
        ports={8080: (5000 + running_instances_count)},
        network="labchain_network",
        environment=envr,
        mounts=[mnt],
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
    data_filename = data.get("benchmark_name", "testData")

    filename = BenchmarkDir.absolutePath(data_filename, "benchmark_results_{}.json".format(data_filename))

    with open(filename, "w") as f:
        f.write(json.dumps(data["found_transactions"], default=str))


@app.route("/dumpBenchmarkData", methods=["GET"])
def dump_benchmark_data():
    global benchmark_data
    global currently_running_benchmark_name

    if currently_running_benchmark_name == "":
        return "No active benchmark", 200

    store_benchmark_data(benchmark_data[currently_running_benchmark_name])

    return "dumped benchmark", 200


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

    peercount = len(data["peers"])

    if data["nodecount"] != -1:
        peercount = data["nodecount"]

    transactions_per_peer = math.ceil(float(data["n_transactions"] / peercount))
    # update number of transactions if number of transactions is not divisable by the number of peers
    data["n_transactions"] = transactions_per_peer * peercount
    data["n_transactions_per_peer"] = transactions_per_peer

    benchmark_data[benchmark_name] = data
    benchmark_queue.append(benchmark_name)

    return "Benchmark enqueued", 200


def spawnNodes(number, test_name=None):
    instances = []
    for i in range(number):
        instances.append(createInstance(instances, test_name))
        time.sleep(4)  # this is necessary, since otherwise the nodes will not connect to each other

    instances = getDockerInstances()

    if len(instances) > 0:
        global networkInterface
        networkInterface = NetworkInterface(JsonRpcClient(), {os.environ.get("HOST_NAME", "localhost"): {(5000 + running_instances_count): {}}})

        if not lookup_thread_running:
            time.sleep(3)  # wait 3 seconds
            t = threading.Thread(target=lookupThread)
            t.start()

    return instances


@app.route("/spawnNetwork", methods=["GET"])
def spawn_network():
    """ Spawns a network
    """
    number = request.args.get("number", None)

    if number is None:
        return "Specify a number", 300

    number = int(number)

    instances = spawnNodes(number)

    return json.dumps(instances), 200


def stopAllDockerInstances():
    instances = getDockerInstances()

    for instance in instances:
        stopInstance(instance["name"])
        getDockerInstance(instance["name"]).remove()


@app.route("/pruneNetwork", methods=["GET"])
def prune_network():
    """ Prune the network
    """
    stopAllDockerInstances()

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
        networkInterface = NetworkInterface(JsonRpcClient(), {os.environ.get("HOST_NAME", "localhost"): {(5000 + running_instances_count): {}}})

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

    getDockerInstance(instance["name"]).remove()

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
        logger.info("Try to pull")
        try:
            client.images.pull("labchain")
        except docker.errors.ImageNotFound as e:
            logger.info("Could not pull image")
            logger.info("Build docker image locally and tag it with 'labchain:latest'")
            logger.info("     cd ROOT/docker")
            logger.info("     docker build -t labchain:latest .")
            sys.exit()

    # initiate program
    instances = [
        x for x in client.containers.list(all=True) if x.name.startswith("labchain_") and not x.name == "labchain_network_composer"
    ]

    i = 0
    for instance in instances:
        running_instances[instance.name] = instance
        ii = int(instance.name.split("_")[1])

        if ii > i:
            i = ii

    running_instances_count = i

    logger.info("Recognized instances: {}".format(len(instances)))
    logger.info(running_instances)

    arguments = sys.argv
    _host = "0.0.0.0"
    _port = 8080

    if len(arguments) == 2:
        _host = arguments[1]
    elif len(arguments) == 3:
        _host = arguments[1]
        _port = int(arguments[2])

    logger.info("Starting server at http://{}:{}".format(_host, _port))

    if len(instances) > 0:
        networkInterface = NetworkInterface(JsonRpcClient(), {os.environ.get("HOST_NAME", "localhost"): {(5000 + running_instances_count): {}}})

    if not lookup_thread_running:
        t = threading.Thread(target=lookupThread)
        t.start()

    app.run(debug=True, threaded=True, use_reloader=True, host=_host, port=_port)
