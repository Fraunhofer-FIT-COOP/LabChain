import unittest
from labchain.datastructure.document import Document
from labchain.datastructure.transaction import Transaction

class DocumentTestClass(unittest.TestCase):
    def setUp(self):
        self.pids = ['alex', 'bryant', 'charlie']
        self.attributes = ['1', '2', '3']
        self.values = ['a', 'b', 'c']
        self.dict_permission = {'1':{'alex':'WRITE'},'2':{'bryant':'WRITE'},'3':{'charlie':'WRITE'}}

    def test_permission_in_write(self):
        doc = Document(dict_permission=self.dict_permission, docType='initial')
        doc.write(self.pids[0], self.attributes[0], self.values[0])
        transaction1 = Transaction(
                    sender = self.pids[0], 
                    receiver = self.pids[1], 
                    payload = doc.to_json()
                    ).get_json()
        # intermediatediated holder
        transaction2 = Transaction.from_json(transaction1)
        doc = Document.from_json(transaction2.payload) # reconstruct document
        print('end')

        