import { Crypto } from "./Crypto";

export class Transaction {
    sender: string = "";
    receiver: string = "";
    payload: string = "";
    signature: string = "";

    constructor(sender: string, receiver: string, payload: string) {
        this.sender = sender;
        this.receiver = receiver;
        this.payload = payload;
    }

    private toBCRepresentation(): string {
        let _payload: string = this.payload + this.receiver + this.sender;

        return _payload;
    }

    sign(privatekey: any) {
        this.signature = Crypto.sign(this.toBCRepresentation(), privatekey);
    }

    validate(publickey: any): Boolean {
        if (typeof publickey === "string" || publickey instanceof String) {
            publickey = Crypto.keyFromPEM(publickey);
        }

        return Crypto.verify(this.toBCRepresentation(), publickey, this.signature);
    }
}
