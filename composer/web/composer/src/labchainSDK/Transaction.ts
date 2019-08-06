import { Crypto } from "./Crypto";
import * as eck from "ec-key";

export class Transaction {
    sender: string = "";
    receiver: string = "";
    payload: string = "";
    signature: string = "";
    //    signature: string;
    constructor(sender: string, receiver: string, payload: string) {
        this.sender = sender;
        this.receiver = receiver;
        this.payload = payload;
    }

    hash(): string {
        // evaluated -> equal to the node implementation
        let _payload: string = this.payload + this.receiver + this.sender;

        return Crypto.sha256(_payload);
    }

    sign(privatekey: any) {
        this.signature = '{"payload": "' + Crypto.sha256(this.payload) + '", "receiver": "' + this.receiver + ', "sender": "' + this.sender + '"}';
        let payload = {
            payload: "pblople",
            receiver: "auelpueeb",
            sender:
                "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFV3FlTCswaHRIZDZiRVpsYnlicDhvY2pKN3FnUApPWis1Q0tjcVR2OFhNdldBZ2M0c1pZYnhjR1QwTW9WaVREaGI2eW8vR3dWSEYzbWQxVlllb1lzOGR3PT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t"
        };

        payload = {
            receiver: "abce",
            payload: "ueuivevbp",
            sender:
                "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFV3FlTCswaHRIZDZiRVpsYnlicDhvY2pKN3FnUApPWis1Q0tjcVR2OFhNdldBZ2M0c1pZYnhjR1QwTW9WaVREaGI2eW8vR3dWSEYzbWQxVlllb1lzOGR3PT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t"
        };

        let tx: Transaction = new Transaction(payload.sender, payload.receiver, payload.payload);

        let a = atob(
            "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFV3FlTCswaHRIZDZiRVpsYnlicDhvY2pKN3FnUApPWis1Q0tjcVR2OFhNdldBZ2M0c1pZYnhjR1QwTW9WaVREaGI2eW8vR3dWSEYzbWQxVlllb1lzOGR3PT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t"
        );
        a = atob(
            "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJHMHdhd0lCQVFRZ01nRzhXM1F2aVhZNU51R0UKMm12bUtOOElEMmFhYWRKWGpTSUYrZkFvS0tDaFJBTkNBQVJhcDR2N1NHMGQzcHNSbVZ2SnVueWh5TW51cUE4NQpuN2tJcHlwTy94Y3k5WUNCeml4bGh2RndaUFF5aFdKTU9GdnJLajhiQlVjWGVaM1ZWaDZoaXp4MwotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t"
        );
        console.log(a);

        let d = new eck(a, "pem");

        console.log("Hashed payload:");
        console.log(tx.hash());

        console.log(Crypto.sign(tx.hash(), d));
        // Target Signature:
        // BnYqJ0HRuNIk0CoIPpR6+Ujik6BQU8Payi65V9Sh5l5XCEudOUW48udhQ6gQKoRr5l7NcXrFjaeswzYxODXxjQ==
    }
}
