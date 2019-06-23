import argparse
import logging
import json
import os

from flask import Flask
from flask import request


from labchain.util.cryptoHelper import CryptoHelper
from labchain.network.networking import ClientNetworkInterface, JsonRpcClient
from labchain.blockchainClient import Wallet, BlockchainClient
from labchain.documentFlowClient import DocumentFlowClient
from labchain.workflowClient import WorkflowClient
from labchain.util.TransactionFactory import TransactionFactory

CONFIG_DIRECTORY = os.path.join(os.path.expanduser("~"), '.labchain')
WALLET_FILE_PATH = os.path.join(CONFIG_DIRECTORY, 'wallet.csv')


demo_workflow_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'labchain/demo-workflow.json'))

def create_app():
    app = Flask(__name__)
    def create_config_directory():
        os.makedirs(CONFIG_DIRECTORY, exist_ok=True)

    def read_workflow_json():
        with open(demo_workflow_file_path, 'r') as file:
            app.workflow_json = json.load(file)[0]

    logging.basicConfig(level=logging.DEBUG)

    create_config_directory()
    read_workflow_json()

    if os.path.exists(WALLET_FILE_PATH):
        file_mode = 'r+'
    else:
        file_mode = 'w+'
    with open(WALLET_FILE_PATH, file_mode) as open_wallet_file:
        app.crypto_helper = CryptoHelper.instance()
        app.network_interface = ClientNetworkInterface(JsonRpcClient(), {'localhost': { '8080': {}}})
        return app

app = create_app()

@app.route('/createCase',methods=['POST'])
def createCase():
    data = request.get_json(force=True)

    wallet = app.workflow_json["wallet"]
    
    controller_public_key = wallet[data['controller']]['public_key']
    controller_private_key = wallet[data['controller']]['private_key']
    physician_public_key = wallet[data['physician']]['public_key']
    doctor_public_key = wallet[data['doctor']]['public_key']
    chef_public_key = wallet[data['chef']]['public_key']
    
    transaction = TransactionFactory.create_case_transaction(controller_public_key,physician_public_key,doctor_public_key,chef_public_key)
    transaction.sign_transaction(app.crypto_helper, controller_private_key)
    
    try:
        app.network_interface.sendTransaction(transaction)
        return 'Success'
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
