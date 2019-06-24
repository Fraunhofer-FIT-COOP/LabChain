import client
import os
import json

from labchain.util.cryptoHelper import CryptoHelper
from labchain.network.networking import ClientNetworkInterface, JsonRpcClient
from labchain.blockchainClient import Wallet, BlockchainClient
from labchain.workflowClient import WorkflowClient
from labchain.util.TransactionFactory import TransactionFactory
from labchain.datastructure.taskTransaction import TaskTransaction
from labchain.datastructure.transaction import Transaction

from flask import Flask, redirect, url_for, request, jsonify
from flask_restful import Api, Resource


app = Flask(__name__)
api = Api(app)

"""Assume all webclients will connect to the same node"""

CONFIG_DIRECTORY = os.path.join(os.path.expanduser("~"), '.labchain')
WALLET_FILE_PATH = os.path.join(CONFIG_DIRECTORY, 'wallet.csv')

def create_config_directory():
    os.makedirs(CONFIG_DIRECTORY, exist_ok=True)

create_config_directory()

if os.path.exists(WALLET_FILE_PATH):
    file_mode = 'r+'
else:
    file_mode = 'w+'
with open(WALLET_FILE_PATH, file_mode) as open_wallet_file:
    crypto_helper = CryptoHelper.instance()
    network_interface = ClientNetworkInterface(JsonRpcClient(), {'localhost': {'8080': {}}})

tx_JSON_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'labchain/EFL.json'))

with open(tx_JSON_file_path, 'r') as file:
        workflow_json = json.load(file)[0]

@app.route('/init', methods=['POST'])
def initialCase():
    transaction = TransactionFactory.create_transcation(workflow_json["workflow"])
    for k,v in  workflow_json["wallet"].items():
        if v["public_key"] == transaction.sender:
            transaction.sign_transaction(crypto_helper,  v["private_key"])
    print(crypto_helper.hash(transaction.get_json()))
    network_interface.sendTransaction(transaction)
    try:
        network_interface.sendTransaction(transaction)
        return jsonify(message='success')
    except:
        return jsonify(message='fail')

@app.route('/physician', methods=['GET', 'POST'])
def physician():
    if request.method == 'GET':
        """GET real diagnosis"""
        "TODO:methods to check sent transaction, and get real diagnosis"
        try:
            "methods here"
            return jsonify(message='success', assumed_diagnosis='heart_attack', real_diagnosis='not_a_heart_attack')
        except:
            return jsonify(message='fail')
    if request.method == 'POST':
        """POST assumed diagnosis
        parameter: diagnosis: string
        response: message: string (success or fail)"""
        req_data = request.get_json()
        assumed_diagnosis = None
        if 'diagnosis' in req_data:
            assumed_diagnosis = req_data['diagnosis']
        transaction_json = workflow_json['task1']
        transaction_json['payload']['document']['assumed_diagnosis'] = assumed_diagnosis
        transaction = TransactionFactory.create_transcation(transaction_json)
        for k,v in  workflow_json["wallet"].items():
            if v["public_key"] == transaction.sender:
                transaction.sign_transaction(crypto_helper,  v["private_key"])
        print(crypto_helper.hash(transaction.get_json()))
        try:
            network_interface.sendTransaction(transaction)
            return jsonify(message='success')
        except:
            return jsonify(message='fail')

@app.route('/doctor', methods=['POST'])
def send_real_diagnosis():
    if request.method == 'POST':
        "POST real diagnosis"
        req_data = request.get_json()
        real_diagnosis = None
        if 'diagnosis' in req_data:
            real_diagnosis = req_data['diagnosis']
        transaction_json = workflow_json['task2']
        transaction_json['payload']['document']['real_diagnosis'] = real_diagnosis
        transaction = TransactionFactory.create_transcation(transaction_json)
        for k,v in  workflow_json["wallet"].items():
            if v["public_key"] == transaction.sender:
                transaction.sign_transaction(crypto_helper,  v["private_key"])
        print(crypto_helper.hash(transaction.get_json()))
        try:
            network_interface.sendTransaction(transaction)
            return jsonify(message='success')
        except:
            return jsonify(message='fail')

@app.route('/show-all-diagnosis', methods=['GET'])
def show_all_diagnosis():
    "GET assumed and real diagnosis, for base controller to check the performance of physicians"
    "TODO: methods to get the transaction task2"
    try:
        "methods here"
        return jsonify(message='success', assumed_diagnosis='heart_attack', real_diagnosis='not_a_heart_attack')
    except:
        return jsonify(message='fail')

@app.route('/send-tx', methods=['POST'])
def send_normal_transaction():
    """POST normal transaction, with hardcoded receiver and payload from JSON sent with POST request
    parameter: payload: string
    response: message: string (success or fail)
    """
    req_data = request.get_json()
    payload = None
    if 'payload' in req_data:
        payload = req_data['payload']

    private_key = workflow_json['wallet']['Admin']['private_key']
    public_key = workflow_json['wallet']['Admin']['public_key']

    new_transaction = Transaction(str(public_key), str('some receiver'), str(payload))
    new_transaction.sign_transaction(crypto_helper, private_key)
    transaction_hash = crypto_helper.hash(new_transaction.get_json())

    try:
        network_interface.sendTransaction(new_transaction)
        return jsonify(message='success', transaction_hash=transaction_hash, payload=payload)
    except:
        return jsonify(message='fail')

if __name__ == '__main__':
    app.run(debug=True)
