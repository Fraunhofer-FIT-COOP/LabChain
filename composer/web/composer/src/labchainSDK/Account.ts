import { Crypto, KeyObject } from "./Crypto";
import { Transaction } from "./Transaction";

export class Account {
    keyPair: KeyObject;

    /**
     * Creates a new account with new private/ public key pair
     * @param pem The PEM string from which the key can be extracted
     * */
    constructor(pem?: string) {
        if (pem) {
            this.keyPair = Crypto.keyFromPEM(pem);
        } else {
            this.keyPair = Crypto.generateKeyPair();
        }
    }

    /**
     * Creates a new account with new private/ public key pair
     * @param pem The PEM string from which the key can be extracted
     * @return Account Newly created account
     * */
    public static createAccount(pem?: string): Account {
        let ac: Account = new Account();

        if (pem) {
            ac.keyPair = Crypto.keyFromPEM(pem);
        } else {
            ac.keyPair = Crypto.generateKeyPair();
        }

        return ac;
    }

    /**
     * Returns the transaction signed with the private key of the current account
     * @param tx Transaction to sign
     * @return Signed transaction
     * */
    public signTransaction(tx: Transaction): Transaction {
        tx.sign(this.keyPair);
        return tx;
    }

    /**
     * @return public key
     * */
    public getPublicKey(): KeyObject {
        return this.keyPair.asPublicECKey();
    }

    /**
     * @return public key in PEM format as base64 encoded string
     * */
    public getPublicKeyPEMBase64(): string {
        let priv_key = this.getPublicKey().toString("pem");
        return btoa(priv_key);
    }
}
