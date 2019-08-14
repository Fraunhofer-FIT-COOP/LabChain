import { DockerInstance, DockerInterface } from "./DockerInterface";
import { Account } from "../labchainSDK/Account";
import { Transaction } from "../labchainSDK/Transaction";
import { LabchainClient } from "../labchainSDK/Client";

export interface BenchmarkData {
    transaction_hash: string;
    start_time?: number;
    end_time?: number;
}

export default class BenchmarkEngine {
    _receiver: DockerInstance[];
    _filename: string;
    constructor(receiver: DockerInstance[], filename: string) {
        this._receiver = receiver;
        this._filename = filename;
    }

    /**
     * Sends 'n' simple transactions to the receiver specified in the constructor and measures
     * the average time until those transactions become visible in the block of a sampler.
     * */
    benchmarkSimpleTransactions(n: number): Promise<any> {
        let ac: Account = Account.createAccount();
        let rec: Account = Account.createAccount();

        let n_txs: number = Math.ceil(n / (this._receiver.length === 0 ? 1 : this._receiver.length));

        let proms: any[] = [];

        this._receiver.forEach(receiver => {
            proms.push(DockerInterface.getClientInterface(receiver));
        });

        return new Promise(p2 => {
            Promise.all(proms).then((clients: LabchainClient[]) => {
                proms = [];
                clients.forEach((client: LabchainClient, i: number) => {
                    for (let j = 0; j < n_txs; ++j) {
                        console.log("Prepare transaction #" + (i + j * n_txs));
                        let tr: Transaction = new Transaction(ac, rec, "This is a very important payload #" + (i + j * n_txs));
                        tr = ac.signTransaction(tr);
                        let tx_hash: string = tr.hash();
                        let tx: BenchmarkData = { transaction_hash: tx_hash, start_time: new Date().getTime() / 1000 };

                        proms.push(
                            new Promise((resolve, reject) => {
                                client.sendTransaction(tr).then(() => {
                                    resolve(tx);
                                });
                            })
                        );
                    }
                });

                console.log("Analyse mining process");
                Promise.all(proms).then(benchmarkData => {
                    DockerInterface.addWatchTransactions(benchmarkData, this._filename).then(() => {
                        p2();
                    });
                });
            });
        });
    }
}
