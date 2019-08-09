import { Transaction } from "./Transaction";

export interface Block {
    creator: string;
    difficulty: number;
    merkleHash: string | null;
    nonce: number;
    nr: number;
    predecessorBlock: string;
    timestamp: number;
    transactions: Transaction[];
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
        return new Promise<Block[]>((resolve, reject) => {
            if (!n) {
                this.sendJSONRPC("requestBlock").then(blocks => {
                    for (let block of blocks) {
                        block.transactions = block.transactions.map((tr: Transaction) => new Transaction(tr.sender, tr.receiver, tr.payload, tr.signature));
                        block.timestamp = new Date((block as Block).timestamp * 1000);
                    }
                    resolve(blocks);
                });
            } else {
                this.sendJSONRPC("requestBlock", [n]).then(blocks => {
                    for (let block of blocks) {
                        block.transactions = block.transactions.map((tr: Transaction) => new Transaction(tr.sender, tr.receiver, tr.payload, tr.signature));
                        block.timestamp = new Date((block as Block).timestamp * 1000);
                    }
                    resolve(blocks);
                });
            }
        });
    }

    /**
     * Sends a transaction to the node
     * */
    async sendTransaction(tx: Transaction): Promise<any> {
        return this.sendJSONRPC("sendTransaction", [tx.toTransmittableString()]);
    }

    /**
     * Returns true, if the transaction was mined otherwise false
     *
     * This methods fails if two blocks are mined quickly after another.
     * It only checks the  most recent block TODO
     * */
    isTransactionMined(tx_hash: string): Promise<boolean> {
        return new Promise((resolve, reject) => {
            this.getBlock().then(blocks => {
                for (let block of blocks) {
                    if (
                        block.transactions.filter(function(a: Transaction) {
                            return a.hash() === tx_hash;
                        }).length > 0
                    ) {
                        resolve(true);
                    }
                }
            });
        });
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
