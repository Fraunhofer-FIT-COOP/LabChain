import { ec } from "elliptic";
import { Crypto } from "./Crypto";
import { Transaction } from "./Transaction";

import * as eck from "ec-key";

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

    /**
     * Returns the public key in PEM format as base64 encoded string
     * */
    public getPublicKeyPEMBase64(): string {
        let priv_key = this.keyPair.asPublicECKey().toString("pem");
        return btoa(priv_key);
    }

    public loadFromFile() {}

    generate() {
        let _ec = new ec("p256");
        let keyPair = _ec.genKeyPair();
        console.log(keyPair);
        console.log(keyPair.getPrivate());
        console.log("Public:");
        console.log(keyPair.getPublic());

        console.log("------------------");

        // ========================= LOADING THE PEM KEY =========================================
        // vertified that it provides the same x, y curve values, as the python library importing
        // the key
        let a = atob(
            "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFV3FlTCswaHRIZDZiRVpsYnlicDhvY2pKN3FnUApPWis1Q0tjcVR2OFhNdldBZ2M0c1pZYnhjR1QwTW9WaVREaGI2eW8vR3dWSEYzbWQxVlllb1lzOGR3PT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t"
        );
        console.log(a);

        let d = new eck(a, "pem");

        console.log(d);

        console.log(parseInt(d.x.toString("hex"), 16));
        console.log(parseInt(d.y.toString("hex"), 16));
        // ========================= LOADING THE PEM KEY =========================================

        // Next question:
        // How to transform this key into a elliptic key
        // ========================= TRANSFORM EC-KEY INTO ELLIPTIC KEY =========================================
        console.log(_ec.keyFromPublic(d.publicCodePoint).inspect());
        console.log(d.x.toString("hex"));
        console.log(d.y.toString("hex"));
        // how to verify the correctness? Looks good so far since the x and y values match...

        // ========================= TRANSFORM EC-KEY INTO ELLIPTIC KEY =========================================
    }
}
