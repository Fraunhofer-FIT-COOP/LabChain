import { Crypto, KeyObject } from "./Crypto";
import { Account } from "./Account";

/**
 * Represents a transaction in the blockchain
 * */
export class Transaction {
    sender: Account;
    receiver: Account | string = "";
    payload: string = "";
    signature: string = "";

    /**
     * @param sender The public key of the sender must be provided as <Account>
     * @param receiver The public key of the receiver can be provided either as <Account> or as string in PEM format
     * @param payload The payload of the transaction as string
     * */
    constructor(sender: Account, receiver: Account | string, payload: string) {
        this.sender = sender;
        this.receiver = receiver;
        this.payload = payload;
    }

    /**
     * Private function that describes the structure of the data that is hashed, when
     * we hasing a transaction
     * */
    private toBCRepresentation(): string {
        let _payload: string = this.payload;

        if (this.receiver instanceof Account) {
            _payload += (this.receiver as Account).getPublicKeyPEMBase64();
        } else {
            _payload += this.receiver;
        }

        _payload += this.sender.getPublicKeyPEMBase64();

        return _payload;
    }

    /**
     * Sign the transaction with the private key
     * @param privatekey Can be the key in PEM format, as KeyObject or as <Account>
     * */
    sign(privatekey: KeyObject | string | Account) {
        if (privatekey instanceof Account) {
            privatekey = (privatekey as Account).keyPair;
        } else if (typeof privatekey === "string" || privatekey instanceof String) {
            privatekey = Crypto.keyFromPEM(privatekey);
        }

        this.signature = Crypto.sign(this.toBCRepresentation(), privatekey);
    }

    /**
     * Verify the transaction with the public key
     * @param publickey Can be the key in PEM format, as KeyObject or as <Account>
     * @param _signature Provide the signature as string. If no signature is given it uses the transaction signature field. If no signature is available it throws an error.
     * */
    verify(publickey: Account | KeyObject | string, _signature?: string): Boolean {
        if (publickey instanceof Account) {
            publickey = (publickey as Account).getPublicKey();
        } else if (typeof publickey === "string" || publickey instanceof String) {
            publickey = Crypto.keyFromPEM(publickey);
        }

        if (_signature) this.signature = _signature;

        if (!this.signature || "" === this.signature) {
            throw Error("Transaction has no signature");
        }

        return Crypto.verify(this.toBCRepresentation(), publickey, this.signature);
    }

    /**
     * @returns a transmittable representation of the transaction
     * */
    toTransmittableString(): any {
        let ret: any = { sender: this.sender.getPublicKeyPEMBase64(), signature: this.signature, payload: this.payload };

        if (this.receiver instanceof Account) {
            ret.receiver = (this.receiver as Account).getPublicKeyPEMBase64();
        } else {
            ret.receiver = this.receiver;
        }

        return ret;
    }
}
