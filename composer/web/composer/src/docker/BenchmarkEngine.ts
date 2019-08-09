import { DockerInstance } from "./DockerInterface";
import { Account } from "../labchainSDK/Account";
import { Transaction } from "../labchainSDK/Transaction";
import { LabchainClient } from "../labchainSDK/Client";

interface BenchmarkData {
    transaction_hash: string;
    start_time?: Date;
    end_time?: Date;
}

export default class BenchmarkEngine {
    _receiver: DockerInstance[];
    _sampler: DockerInstance[];
    constructor(receiver: DockerInstance[], sampler: DockerInstance[]) {
        this._receiver = receiver;
        this._sampler = sampler;
    }

    /**
     * Sends 'n' simple transactions to the receiver specified in the constructor and measures
     * the average time until those transactions become visible in the block of a sampler.
     * */
    benchmarkSimpleTransactions(n: number): Promise<any> {
        let benchmark_data: BenchmarkData[] = [];
        let hashesToTest: string[] = [];
        let client: LabchainClient = new LabchainClient("http://localhost:8082");

        let ac: Account = Account.createAccount();
        let rec: Account = Account.createAccount();

        for (let i = 0; i < n; ++i) {
            console.log("Send transaction #" + i);
            let tr: Transaction = new Transaction(ac, rec, "This is a very important payload #" + i);
            tr = ac.signTransaction(tr);
            let tx_hash: string = tr.hash();
            let data: BenchmarkData = { transaction_hash: tx_hash, start_time: new Date() };
            benchmark_data.push(data);
            hashesToTest.push(tx_hash);

            client.sendTransaction(tr).then();
        }

        console.log("Analyse mining progress");

        return new Promise((resolve, reject) => {
            let timer_id: any = setInterval(() => {
                if (hashesToTest.length === 0) {
                    clearInterval(timer_id);
                    console.log(benchmark_data);
                    resolve(benchmark_data);
                }

                client.getBlock().then(blocks => {
                    for (let block of blocks) {
                        for (let tx of block.transactions) {
                            let tx_hash = tx.hash();
                            console.log("Located transaction: " + tx.hash());
                            let mdata: BenchmarkData = benchmark_data.filter(m => m.transaction_hash === tx_hash)[0];

                            if (!mdata) continue;
                            mdata.end_time = new Date(block.timestamp);
                            hashesToTest = hashesToTest.filter(m => m !== tx_hash);
                        }
                    }
                });
            }, 500);
        });
    }
}
