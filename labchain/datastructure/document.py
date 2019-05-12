import json

class Document:
    def __init__(self, holder, attribute, value, docType, holder_history = [], type_history=[]):
        # Contructor of document class, a document class exist in the workflow
        self.attribute = attribute
        self.value = value
        self.docType = docType
        self.holder = holder
        self.holder_history = holder_history

    def get_holder_history(self):
        return self.holder_history
    
    def add_to_holder_list(self, new_holder):
        self.holder_history.append(new_holder)

    def _to_dict(self):
        return {
            'holder':self.holder,
            'attribute': self.attribute,
            'value':self.value,
            'docType':self.docType,
            'holder_history': self.holder_history
        }

    def to_json(self):
        return json.dumps(self._to_dict())

    @staticmethod
    def _from_dict(dict_data):
        return Document(
            holder = dict_data['holder'],
            attribute = dict_data['attribute'],
            value = dict_data['value'],
            docType = dict_data['docType'],
            holder_history = dict_data['holder_history']
        )
    @staticmethod
    def from_json(json_data):
        dict_data = json.loads(json_data)
        return Document._from_dict(dict_data)
