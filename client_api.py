import argparse
import logging
import json
import os
from typing import List

from flask import Flask, request, jsonify
from flask_cors import CORS

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
    CORS(app)
    with open(wallet_file_path, 'r') as file:
        app.wallet = json.load(file)[0]['wallet']

    #logging.basicConfig(level=logging.DEBUG)
    app.crypto_helper = CryptoHelper.instance()
    app.network_interface = ClientNetworkInterface(JsonRpcClient(), {'localhost': { '8080': {}}})
    return app

app = create_app()

@app.route('/createCase',methods=['POST'])
def createCase():
    data = request.get_json(force=True)

    case_ID = data['case_id'] if 'case_id' in data else '0'
    controller_public_key = app.wallet[data['controller']]['public_key']
    controller_private_key = app.wallet[data['controller']]['private_key']
    physician_public_key = app.wallet[data['physician']]['public_key']
    doctor_public_key = app.wallet[data['doctor']]['public_key']
    chef_public_key = app.wallet[data['chief']]['public_key']

    transaction = TransactionFactory.create_case_transaction(case_ID,controller_public_key,physician_public_key,doctor_public_key,chef_public_key)
    transaction.sign_transaction(app.crypto_helper, controller_private_key)

    try:        
        app.network_interface.sendTransaction(transaction)
        return jsonify(message='success')
    except Exception as e:
        return jsonify(message='fail', description=str(e))

@app.route('/sendAssumedDiagnosis', methods=['POST'])
def send_assumed_diagnosis():
    if request.method == 'POST':
        data = request.get_json(force=True)

        case_ID = data['case_id'] if 'case_id' in data else '0'
        physician_private_key = app.wallet[data['physician']]['private_key']
        physician_public_key = app.wallet[data['physician']]['public_key']
        doctor_public_key = app.wallet[data['doctor']]['public_key']
        workflow_transaction = data['workflow_transaction']
        previous_transaction = data['previous_transaction']
        assumed_diagnosis = data['diagnosis']
        try:
            transaction = TransactionFactory.create_assumed_diagnosis_transaction(case_ID,physician_public_key,
                                                                        doctor_public_key,
                                                                        assumed_diagnosis,
                                                                        workflow_transaction,
                                                                        previous_transaction)
            transaction.sign_transaction(app.crypto_helper, physician_private_key)
            app.network_interface.sendTransaction(transaction)
            return jsonify(message='success')
        except Exception as e:
            return jsonify(message='fail', description=str(e))

@app.route('/sendRealDiagnosis', methods=['POST'])
def send_real_diagnosis():
    if request.method == 'POST':
        data = request.get_json(force=True)

        case_ID = data['case_id'] if 'case_id' in data else '0'
        doctor_private_key = app.wallet[data['doctor']]['private_key']
        doctor_public_key = app.wallet[data['doctor']]['public_key']
        chef_public_key = app.wallet[data['chief']]['public_key']
        workflow_transaction = data['workflow_transaction']
        previous_transaction = data['previous_transaction']
        real_diagnosis = data['diagnosis']
        try:
            transaction = TransactionFactory.create_real_diagnosis_transaction(case_ID,doctor_public_key,
                                                                                    chef_public_key,
                                                                                    real_diagnosis,
                                                                                    workflow_transaction,
                                                                                    previous_transaction)
        
            transaction.sign_transaction(app.crypto_helper, doctor_private_key)
            app.network_interface.sendTransaction(transaction)
            return jsonify(message='success')
        except Exception as e:
            return jsonify(message='fail', description=str(e))

@app.route('/showAllDiagnosis', methods=['POST'])
def show_all_diagnosis():
    data = request.get_json(force=True)
    public_key = app.wallet[data['username']]['public_key']
    try:
        real_diagnosis_transactions = app.network_interface.search_transaction_from_receiver(public_key)
        diaggnosis_list = []
        for real_diagnosis_transaction in real_diagnosis_transactions:
            previous_transaction = real_diagnosis_transaction.payload['previous_transaction']
            assumed_diagnossis_transaction = app.network_interface.requestTransaction(previous_transaction)[0]
            diaggnosis = {}
            diaggnosis['real_diagnosis'] = real_diagnosis_transaction.payload['document']['real_diagnosis']
            diaggnosis['assumed_diagnosis'] = assumed_diagnossis_transaction.payload['document']['assumed_diagnosis']
            diaggnosis_list.append(diaggnosis)
        return json.dumps(diaggnosis_list)
    except Exception as e:
        return jsonify(message='fail', description=str(e))

@app.route('/checkTasks',methods=['POST'])
def checkTasks():
    data = request.get_json(force=True)
    public_key = app.wallet[data['username']]['public_key']
    try:
        transactions = TasksManeger.check_tasks(app.network_interface,public_key)
        tasks = TasksManeger.get_tasks_objects_from_task_transactions(transactions)
        return json.dumps([ob.__dict__ for ob in tasks])
    except Exception as e:
        return jsonify(message='fail', description=str(e))	

if __name__ == '__main__':
    app.run(debug=True)
