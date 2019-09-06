import { DockerInstance, DockerInterface } from "./DockerInterface";

export interface BenchmarkData {
    transaction_hash: string;
    start_time?: number;
    end_time?: number;
}

export default class BenchmarkEngine {
    _receiver: DockerInstance[];
    _filename: string;
    _nodecount: number;
    constructor(receiver: DockerInstance[], filename: string, nodecount: number) {
        this._receiver = receiver;
        this._filename = filename;
        this._nodecount = nodecount;
    }

    /**
     * Sends 'n' simple transactions to the receiver specified in the constructor and measures
     * the average time until those transactions become visible in the block of a sampler.
     * */
    benchmarkSimpleTransactions(n: number): Promise<any> {
        return DockerInterface.benchmarkSimple(this._filename, n, this._receiver.map(x => x.name), this._nodecount);
    }
}
