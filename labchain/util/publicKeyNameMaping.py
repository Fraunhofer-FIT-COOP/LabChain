import os
import json
import copy

class PublicKeyNamesMapping:

    @classmethod
    def replace_public_keys_with_names(cls,transaction_dict):
        wallet = PublicKeyNamesMapping.read_workflow_json()["wallet"]
        public_key_name_map = {}
        for personName, personInfo in wallet.items():
            public_key_name_map[personInfo["public_key"]] = personName
        new_transaction_dict = copy.deepcopy(transaction_dict)
        PublicKeyNamesMapping.replace_recursively(new_transaction_dict,public_key_name_map)
        return new_transaction_dict
        
    @classmethod
    def replace_recursively(cls,new_transaction_dict,public_key_name_map):
        for k, v in list(new_transaction_dict.items()):
            if v is None:
                continue
            if isinstance(v, dict):
                PublicKeyNamesMapping.replace_recursively(v,public_key_name_map)
            else:
                for public_key in public_key_name_map:
                    if public_key in v:
                        number = v.replace(public_key,"")
                        new_transaction_dict[k] = public_key_name_map[public_key] + number
                    if public_key in k:
                        number = k.replace(public_key,"")
                        new_transaction_dict[public_key_name_map[public_key]+number] = new_transaction_dict.pop(k)
                    if isinstance(v, list):
                        for i,element in enumerate(v):
                            if public_key in element:
                                number = element.replace(public_key,"")
                                v[i] = public_key_name_map[public_key] + number


    @classmethod
    def read_workflow_json(cls):
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../demo-workflow.json')), 'r') as file:
            return json.load(file)[0]

