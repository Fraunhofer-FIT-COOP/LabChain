import client
from flask import Flask
from flask_restful import Api, Resource


app = Flask(__name__)
api = Api(app)

class ClientAPI(Resource):
    def get(self):
        return "test response"

api.add_resource(ClientAPI, '/')




if __name__ == '__main__':
    clientObj=client.create_document_flow_client_instance()
    clientObj.demo()
    app.run(debug=True)
