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
        let benchmarkData: BenchmarkData[] = [];
        let client: LabchainClient = new LabchainClient("http://localhost:8082");

        let ac: Account = Account.createAccount();
        let rec: Account = Account.createAccount();

        for (let i = 0; i < n; ++i) {
            console.log("Send transaction #" + i);
            let tr: Transaction = new Transaction(ac, rec, "This is a very important payload #" + i);
            tr = ac.signTransaction(tr);
            let tx_hash: string = tr.hash();
            let tx: BenchmarkData = { transaction_hash: tx_hash, start_time: new Date().getTime() / 1000 };
            benchmarkData.push(tx);

            client.sendTransaction(tr).then();
        }

        console.log("Analyse mining progress");
        return DockerInterface.addWatchTransactions(benchmarkData);
    }
}
