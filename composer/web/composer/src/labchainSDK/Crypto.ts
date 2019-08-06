import * as eck from "ec-key";
import { sha256 } from "js-sha256";

export abstract class Crypto {
    /**
     * Creates a public private keypair
     */
    public static generateKeyPair() {
        return eck.createECKey("P-256");
    }

    /**
     * Computes the SHA256 has of the given string
     */
    public static sha256(payload: string): string {
        return sha256(payload);
    }

    /**
     * Returns the key of the given pem
     * */
    public static keyFromPEM(pem: any): any {
        return new eck(pem);
    }

    /**
     * Signs the message with the given private key
     */
    public static sign(payload: string, private_key: any): string {
        return private_key
            .createSign("SHA256")
            .update(payload) // double hash!!!
            .sign("base64");
    }

    /**
     * Verifies the signature
     */
    public static verify(payload: string, public_key: any, signature: any) {
        return public_key
            .createVerify("SHA256")
            .update(payload)
            .verify(signature, "base64");
    }
}
