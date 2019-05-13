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
        self.attribute = attribute
        self.value = value
        self.docType = docType
        self.pid_history = pid_history
        self.dict_permission = dict_permission

    def _check_permission(self, pid, attribute, action):
        """ Check the permission of a process id
        param[in] pid Process id that being check
        param[out] bool True if allow to perform the action, False if action is not permitted
        """

        if attribute in self.dict_permission:
            if pid in self.dict_permission[attribute]:
                if action is self.dict_permission[attribute][pid]:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def write(self, pid, attribute, value):
        """Write value to the given attribute
        param[in] pid Process id who write the data
        param[in] attribute Attribute that is being wrote
        param[in] value Value that being wrote to the attribute
        """
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
        """Read a certain attribute and its value
        param[out] list that has [attribute, value] 
        """
        index = self.attribute.index(attribute)
        value = self.value[index]
        return [self.attribute[index], value]

    def get_holder_history(self):
        """Get the history of pids who write to the document"""
        return self.pid_history

    def get_attribute_history(self):
        """Get the history of attribute"""
        return self.attribute

    def get_value_history(self):
        """Get the history of value"""
        return self.value

    def _to_dict(self):
        print('a')
        return {
            'attribute': self.attribute,
            'value':self.value,
            'docType':self.docType,
            'pid_history': self.pid_history,
            'dict_permission': self.dict_permission
        }

    def to_json(self):
        return json.dumps(self._to_dict())

    @staticmethod
    def _from_dict(dict_data):
        return Document(
            attribute = dict_data['attribute'],
            value = dict_data['value'],
            docType = dict_data['docType'],
            pid_history = dict_data['pid_history'],
            dict_permission=dict_data['dict_permission']
        )
    @staticmethod
    def from_json(json_data):
        dict_data = json.loads(json_data)
        return Document._from_dict(dict_data)
