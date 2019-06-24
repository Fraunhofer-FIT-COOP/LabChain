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


wallet_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'wallet.json'))

def create_app():
    app = Flask(__name__)

    with open(wallet_file_path, 'r') as file:
        app.wallet = json.load(file)[0]['wallet']

    logging.basicConfig(level=logging.DEBUG)
    app.crypto_helper = CryptoHelper.instance()
    app.network_interface = ClientNetworkInterface(JsonRpcClient(), {'localhost': { '8080': {}}})
    return app

app = create_app()

@app.route('/createCase',methods=['POST'])
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
        app.network_interface.sendTransaction(transaction)
        return 'Success'
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
