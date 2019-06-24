import argparse
import logging
import json
import os
from typing import List

from flask import Flask, request, jsonify

from labchain.util.cryptoHelper import CryptoHelper
from labchain.network.networking import ClientNetworkInterface, JsonRpcClient
from labchain.blockchainClient import Wallet, BlockchainClient
from labchain.documentFlowClient import DocumentFlowClient
from labchain.workflowClient import WorkflowClient
from labchain.datastructure.taskTransaction import TaskTransaction
from labchain.util.TransactionFactory import TransactionFactory
from labchain.util.TasksManeger import TasksManeger,Task


wallet_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'wallet.json'))

def create_app():
    app = Flask(__name__)

    with open(wallet_file_path, 'r') as file:
        app.wallet = json.load(file)[0]['wallet']

    #logging.basicConfig(level=logging.DEBUG)
    app.crypto_helper = CryptoHelper.instance()
    app.network_interface = ClientNetworkInterface(JsonRpcClient(), {'localhost': { '8080': {}}})
    return app

app = create_app()

@app.route('/init',methods=['POST'])
def createCase():
    data = request.get_json(force=True)

    controller_public_key = app.wallet[data['controller']]['public_key']
    controller_private_key = app.wallet[data['controller']]['private_key']
    physician_public_key = app.wallet[data['physician']]['public_key']
    doctor_public_key = app.wallet[data['doctor']]['public_key']
    chef_public_key = app.wallet[data['chef']]['public_key']

    transaction = TransactionFactory.create_case_transaction(controller_public_key,physician_public_key,doctor_public_key,chef_public_key)
    transaction.sign_transaction(app.crypto_helper, controller_private_key)

    try:
        workflow_transaction_hash = app.crypto_helper.hash(transaction.get_json_with_signature())
        app.network_interface.sendTransaction(transaction)
        return jsonify(message='success')
    except Exception as e:
        return jsonify(message='fail', description=str(e))

@app.route('/sendAssumedDiagnosis', methods=['POST'])
def send_assumed_diagnosis():
    if request.method == 'POST':
        data = request.get_json(force=True)

        physician_private_key = app.wallet[data['physician']]['private_key']
        physician_public_key = app.wallet[data['physician']]['public_key']
        doctor_public_key = app.wallet[data['doctor']]['public_key']

        assumed_diagnosis = None
        if 'diagnosis' in data:
            assumed_diagnosis = data['diagnosis']
        transaction = TransactionFactory.create_assumed_diagnosis_transaction(physician_public_key,doctor_public_key,assumed_diagnosis)
        transaction.sign_transaction(app.crypto_helper, physician_private_key)
        try:
            app.network_interface.sendTransaction(transaction)
            return jsonify(message='success')
        except Exception as e:
            return jsonify(message='fail', description=str(e))

@app.route('/doctor', methods=['POST'])
def send_real_diagnosis():
    if request.method == 'POST':
        data = request.get_json(force=True)

        doctor_private_key = app.wallet[data['doctor']]['private_key']
        doctor_public_key = app.wallet[data['doctor']]['public_key']
        chef_public_key = app.wallet[data['chef']]['public_key']

        real_diagnosis = None
        if 'diagnosis' in data:
            real_diagnosis = data['diagnosis']
        transaction = TransactionFactory.send_diagnosis(doctor_public_key, chef_public_key, None, real_diagnosis)
        transaction.sign_transaction(app.crypto_helper, doctor_private_key)

        try:
            app.network_interface.sendTransaction(transaction)
            return jsonify(message='success')
        except Exception as e:
            return jsonify(message='fail', description=str(e))

@app.route('/show-all-diagnosis', methods=['GET'])
def show_all_diagnosis():
    "GET assumed and real diagnosis, for base controller to check the performance of physicians"
    try:
        transaction_to_chef = app.network_interface.search_transaction_from_receiver(app.wallet['chef']['public_key'])
        real_diagnosis = transaction_to_chef[0].payload['document']['real_diagnosis']
        assumed_diagnosis = transaction_to_chef[0].payload['document']['assumed_diagnosis']

        return jsonify(message='success', assumed_diagnosis=assumed_diagnosis, real_diagnosis=real_diagnosis)
    except Exception as e:
        return jsonify(message='fail', description=str(e))

@app.route('/checkTasks',methods=['POST'])
def checkTasks():
    data = request.get_json(force=True)
    public_key = app.wallet[data['username']]['public_key']
    try:
        transactions = TasksManeger.check_tasks(app.network_interface,public_key)
        tasks = TasksManeger.get_tasks_objects_from_task_transactions(transactions)
        result = json.dumps([ob.__dict__ for ob in tasks])
        return result
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
