import {DockerInstance, DockerInterface} from "./DockerInterface";

export interface StartBenchmarkConfig {
    benchmark_name: string;
    environment_type: string;
    nodecount?: number;
    docker_receiver?: DockerInstance[];
    specific_target_url?: string;
    specific_target_port?: number;
    transactionCount?: number;
}

export interface BenchmarkData {
    transaction_hash: string;
    start_time?: number;
    end_time?: number;
}

export class BenchmarkEngine {
    _startBenchmarkConfig: StartBenchmarkConfig;
    constructor(startBenchmarkConfig: StartBenchmarkConfig) {
        this._startBenchmarkConfig = startBenchmarkConfig;
    }

    /**
     * Sends 'n' simple transactions to the receiver specified in the constructor and measures
     * the average time until those transactions become visible in the block of a sampler.
     * */
    benchmarkSimpleTransactions(n: number): Promise<any> {
        this._startBenchmarkConfig.transactionCount = n;
        return DockerInterface.benchmarkSimple(this._startBenchmarkConfig);
    }
}
