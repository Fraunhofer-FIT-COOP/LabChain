import { Crypto } from "./Crypto";
import { Transaction } from "./Transaction";

export class Account {
    keyPair: any;

    constructor() {
        this.keyPair = null;
    }

    /**
     * Creates a new account with new private/ public key pair
     * */
    public static createAccount(): Account {
        let ac: Account = new Account();

        ac.keyPair = Crypto.generateKeyPair();

        return ac;
    }

    /**
     * Returns the transaction signed with the private key of the current account
     * */
    public signTransaction(tx: Transaction): Transaction {
        tx.sign(this.keyPair);
        return tx;
    }

    public getPublicKey(): any {
        if (!this.keyPair) return null;

        return this.keyPair.asPublicECKey();
    }

    /**
     * Returns the public key in PEM format as base64 encoded string
     * */
    public getPublicKeyPEMBase64(): string {
        let priv_key = this.keyPair.asPublicECKey().toString("pem");
        return btoa(priv_key);
    }

    public loadFromFile() {}
}
