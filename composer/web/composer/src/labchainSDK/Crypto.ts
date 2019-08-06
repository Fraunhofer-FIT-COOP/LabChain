import * as eck from "ec-key";
import { sha256 } from "js-sha256";

/**
 * Mock class because i am to lazy to type the ec-key package TODO!
 * */
export abstract class KeyObject {
    abstract createSign(_type: string): any;
    abstract createVerify(_type: string): any;
    abstract asPublicECKey(): KeyObject;

    abstract toString(_type: string): string;
}

export abstract class Crypto {
    /**
     * Creates a public private keypair using the P-256 curve
     */
    public static generateKeyPair(): KeyObject {
        return eck.createECKey("P-256");
    }

    /**
     * Computes the SHA256 has of the given string
     * @param payload Provided as string
     * @return Returns the hash
     */
    public static sha256(payload: string): string {
        return sha256(payload);
    }

    /**
     * Transforms a PEM given key into a <KeyObject>
     * @param pem String PEM
     * @return <KeyObject>
     * */
    public static keyFromPEM(pem: any): KeyObject {
        return new eck(pem, "pem");
    }

    /**
     * Signs the message with the given private key
     * @param payload The payload to sign as string
     *
     */
    public static sign(payload: string, private_key: KeyObject): string {
        return private_key
            .createSign("SHA256")
            .update(payload) // double hash!!!
            .sign("base64");
    }

    /**
     * Verifies the signature
     */
    public static verify(payload: string, public_key: KeyObject, signature: string) {
        return public_key
            .createVerify("SHA256")
            .update(payload)
            .verify(signature, "base64");
    }
}
