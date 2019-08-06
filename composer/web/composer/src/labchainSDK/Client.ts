import { Transaction } from "./Transaction";

export interface Block {
    creator: string;
    difficulty: number;
    merkleHash: string | null;
    nonce: number;
    nr: number;
    predecessorBlock: string;
    timestamp: number;
    transactions: string[];
}

export class LabchainClient {
    url: string = "";
    rpc_id_count: number = 0;
    constructor(url: string) {
        this.url = url;
    }

    /**
     * Returns the connected peers of the node
     * */
    async getConnectedPeers(): Promise<string[]> {
        if ("" === this.url) {
            throw Error("Not connected to a node");
        }

        return this.sendJSONRPC("getPeers");
    }

    /**
     * Returns the n'th block. If no number is given
     * it returns the latest block
     * */
    async getBlock(n?: number): Promise<Block[]> {
        if (!n) return this.sendJSONRPC("requestBlock");
        else return this.sendJSONRPC("requestBlock", [n]);
    }

    /**
     * Sends a transaction to the node
     * */
    async sendTransaction(tx: Transaction): Promise<any> {
        return this.sendJSONRPC("sendTransaction", [tx.toTransmittableString()]);
    }

    sendJSONRPC(method: string, params?: any): Promise<any> {
        if ("" === this.url) {
            throw Error("Not connected to a node");
        }

        let data: any = {
            method: method,
            jsonrpc: "2.0",
            id: this.rpc_id_count
        };

        if (params) {
            data.params = params;
        }

        return new Promise((resolve, reject) => {
            fetch(this.url, {
                method: "POST",
                body: JSON.stringify(data)
            })
                .then(res => {
                    res.json().then(res2 => {
                        resolve(res2.result);
                        ++this.rpc_id_count;
                    });
                })
                .catch(error => {
                    reject(error);
                });
        });
    }
}
