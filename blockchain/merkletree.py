from hashlib import sha256 as sha


class merkletree:

    def __init__(self):
        pass

    def merkle_root(self, hashes):
        """
        Recursively calls itself and calculate hash of two consecutive
        hashes till it gets one last hash

        :param hashes: hashes of all transactions
        :return:one hash of all hashes
        """
        sub_tree = []
        for i in range(0, len(hashes), 2):
            """If not the last element"""
            if i + 1 < len(hashes):
                """Concatenate the hashes and calculate their hash"""
                value = str(hashes[i]+hashes[i+1]).encode('utf-8')
                hash = sha(value).hexdigest()
            else:
                hash = hashes[i]
            sub_tree.append(hash)
        if len(sub_tree) == 1:
            return sub_tree[0]
        else:
            return self.merkle_root(sub_tree)

    def compute_merkle_root(self, txns):
        """
        Computes hash of all transactions and call merkle root

        :param txns:list of all transactions
        :return:one hash of all the transactions
        """
        for i,tx in enumerate(txns):
            txns[i] = sha(tx.encode('utf-8')).hexdigest()
        return self.merkle_root(txns)
