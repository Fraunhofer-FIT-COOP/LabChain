import json
import unittest
import some_txn_verify_package

from labchain.blockchain import BlockChain
from mock.consensus import Consensus
from mock.txPool import TxPool


    def sign_transaction(self):
        """
        Sign transaction with private key
        """
        private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')


    def validate_transaction(self):

    # Check transaction validity; throw an error if an invalid transaction was found.
        WALLET_KEYS = ["foo", "1", "2", "3", "4", "5"]

        for wk in WALLET_KEYS:
        wallet = BIP32Node.from_master_secret(secp256k1_generator, wk.encode("utf8"))
        text = wallet.wallet_key(as_private=True)
        self.assertEqual(is_private_bip32_valid(text))
        self.assertEqual(is_public_bip32_valid(text))
        a = text[:-1] + chr(ord(text[-1]) + 1)
        self.assertEqual(is_private_bip32_valid(a))
        self.assertEqual(is_public_bip32_valid(a))
        text = wallet.wallet_key(as_private=False)
        self.assertEqual(is_private_bip32_valid(text))
        self.assertEqual(is_public_bip32_valid(text))
        a = text[:-1] + chr(ord(text[-1]) + 1)
        self.assertEqual(is_private_bip32_valid(a))
        self.assertEqual(is_public_bip32_valid(a))

        self.assertEqual(status, True)

if __name__ == '__main__':
    unittest.main()

