import * as eck from "ec-key";
import { ec } from "elliptic";
import { sha256 } from "js-sha256";
import * as jsr from "jsrsasign";

export abstract class Crypto {
    public static generateKeyPair() {
        return eck.createECKey("P-256");
    }
    public static sha256(payload: string): string {
        return sha256(payload);
    }

    private static publicKeyToEllipticLibKey(key: any): any {
        let _ec = new ec("p256");
        return _ec.keyFromPublic(key.publicCodePoint);
    }

    private static privateKeyToEllipticLibKey(key: any): any {
        let _ec = new ec("p256");
        return _ec.keyFromPrivate(key.publicCodePoint);
    }

    public static sign(payload: string, private_key: any): string {
        //let ec = new eddsa("ed25519");
        //let key = ec.keyFromSecret(Crypto.privateKeyToEllipticLibKey(private_key));
        //return btoa(key.sign(payload).toHex());
        let a = atob(
            "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJHMHdhd0lCQVFRZ01nRzhXM1F2aVhZNU51R0UKMm12bUtOOElEMmFhYWRKWGpTSUYrZkFvS0tDaFJBTkNBQVJhcDR2N1NHMGQzcHNSbVZ2SnVueWh5TW51cUE4NQpuN2tJcHlwTy94Y3k5WUNCeml4bGh2RndaUFF5aFdKTU9GdnJLajhiQlVjWGVaM1ZWaDZoaXp4MwotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t"
        );

        let k = jsr.KEYUTIL.getKey(a);
        let sig = new jsr.crypto.Signature({ alg: "SHA256withDSA" });
        sig.init(k);
        return btoa(sig.signString(payload));

        //        return btoa(
        //            private_key
        //                .createSign("SHA256")
        //                .update(payload)
        //                .sign("hex")
        //        );
    }
}
