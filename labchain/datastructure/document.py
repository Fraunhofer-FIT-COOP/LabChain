import json

class Document:
    """Document class in workflow application
    """
    def __init__(self, attribute = [], value = [], pid_history = [], dict_permission={}, docType='initial'):
        """Constructor of document

        param[in] pid Process id of the client who sends the document
        param[in] attribute Attribute that the client want to change
        param[in] value Value that the modifying attribute 
        param[in] docType Type of the document, could only be "initial" or subsequent
        param[in] pid_history History of pid that has modify the document
        param[in] type_history History of docType 
        param[in] permission Permission of action that which pid can do what, which need to be specified if doctype is 'initial'
        """
        if docType is 'subsequent':
            assert (bool(dict_permission) == True), 'docType:subsequent should not define permission'
        
        self.attribute = attribute
        self.value = value
        self.docType = docType
        self.pid_history = pid_history
        self.dict_permission = dict_permission

    def _check_permission(self, attribute, pid, action):
        """ Check the permission of a process id
        param[in] pid Process id that being check
        param[out] bool True if allow to perform the action, False if action is not permitted
        """
        permissions = self.dict_permission[attribute]
        if permissions[pid] is action:
            return True
        else:
            return False

    def write(self, pid, attribute, value):
        permission = self._check_permission(pid, attribute, 'WRITE')
        try:
            if permission is False:
                raise Exception('Permision Denied', str(pid) + ' has no right to ' + 'WRITE')
            else:
                self.pid_history.append(pid)
                self.attribute.append(attribute)
                self.value.append(value)

        except Exception as inst:
            print(inst)
    
    def read(self, attribute, value):
        index = self.attribute.index(attribute)
        value = self.value[index]
        return [self.attribute[index], value]

    def get_holder_history(self):
        return self.pid_history

    def _to_dict(self):
        return {
            'attribute': self.attribute,
            'value':self.value,
            'docType':self.docType,
            'pid_history': self.pid_history,
            'dict_permission': self.dict_permission,
        }

    def to_json(self):
        return json.dumps(self._to_dict())

    @staticmethod
    def _from_dict(dict_data):
        return Document(
            attribute = dict_data['attribute'],
            value = dict_data['value'],
            docType = dict_data['docType'],
            pid_history = dict_data['pid_history']
        )
    @staticmethod
    def from_json(json_data):
        dict_data = json.loads(json_data)
        return Document._from_dict(dict_data)
