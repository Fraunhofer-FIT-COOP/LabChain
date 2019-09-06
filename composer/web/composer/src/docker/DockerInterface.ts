import { LabchainClient } from "../labchainSDK/Client";

export interface BenchmarkStatus {
    remaining_txs: number;
    found_txs: number;
    total_txs: number;
    name: string;
}

export interface DockerInstance {
    id: string;
    ipv4: string;
    ipv6: string;
    mac: string;
    name: string;
    status: string;
    port: string[];
}

export class DockerInterface {
    public static url = "http://localhost:8080";

    /**
     * Returns a labchain client connected to an arbitrary docker instance, or if an
     * instance is provided to this instance
     * */
    public static getClientInterface(instance?: DockerInstance): Promise<LabchainClient> {
        if (instance) {
            return new Promise<LabchainClient>((resolve, reject) => {
                let id: number = +instance.name.split("_")[1];
                resolve(new LabchainClient("http://localhost:" + (id + 5000)));
            });
        }
        return new Promise<LabchainClient>((resolve, reject) => {
            DockerInterface.getInstances().then(instances => {
                if (instances.length === 0) {
                    reject();
                } else {
                    let instance: DockerInstance = instances[0];
                    let id: number = +instance.name.split("_")[1];
                    resolve(new LabchainClient("http://localhost:" + (id + 5000)));
                }
            });
        });
    }

    /**
     * Returns the labchain interfaces to the running docker instances
     * */
    public static getClientInterfaces(): Promise<{ instance: DockerInstance; client: LabchainClient }[]> {
        return new Promise<{ instance: DockerInstance; client: LabchainClient }[]>((resolve, reject) => {
            let clients: { instance: DockerInstance; client: LabchainClient }[] = [];
            DockerInterface.getInstances().then(instances => {
                for (let inst of instances) {
                    if (inst.status !== "running") continue;
                    let id: number = +inst.name.split("_")[1];

                    let client: LabchainClient = new LabchainClient("http://localhost:" + (id + 5000) + "/");

                    clients.push({ instance: inst, client: client });
                }

                resolve(clients);
            });
        });
    }

    public static async getInstances(): Promise<DockerInstance[]> {
        const response = await fetch(DockerInterface.url + "/getInstances");
        const json_resp = await response.json();

        return json_resp;
    }

    public static async createInstance(): Promise<DockerInstance[]> {
        const response = await fetch(DockerInterface.url + "/startInstance");
        const instances = await response.json();

        return instances;
    }

    public static async startInstance(name: string): Promise<DockerInstance[]> {
        const response = await fetch(DockerInterface.url + "/startInstance?name=" + name);
        const instances = await response.json();

        return instances;
    }

    public static async stopInstance(name: string): Promise<DockerInstance[]> {
        const response = await fetch(DockerInterface.url + "/stopInstance?name=" + name);
        const instances = await response.json();

        return instances;
    }

    public static async deleteInstance(name: string): Promise<DockerInstance[]> {
        const response = await fetch(DockerInterface.url + "/deleteInstance?name=" + name);
        const instances = await response.json();

        return instances;
    }

    public static async spawnNetwork(n: number): Promise<DockerInstance[]> {
        const response = await fetch(DockerInterface.url + "/spawnNetwork?number=" + n);
        const instances = await response.json();

        return instances;
    }

    public static async pruneNetwork(): Promise<DockerInstance[]> {
        const response = await fetch(DockerInterface.url + "/pruneNetwork");
        const instances = await response.json();

        return instances;
    }

    public static async benchmarkSimple(benchmarkName: string, transaction_count: number, peers: string[]): Promise<any> {
        return new Promise<any>((resolve, reject) => {
            fetch(DockerInterface.url + "/benchmarkSimple", {
                method: "POST",
                body: JSON.stringify({ benchmark_name: benchmarkName, n_transactions: transaction_count, peers: peers }),
                headers: {
                    "Content-Type": "application/json"
                }
            })
                .then(result => {
                    if (result.status !== 200) {
                        result.text().then(t => {
                            reject(t);
                        });
                    } else {
                        result.text().then(t => {
                            resolve(t);
                        });
                    }
                })
                .catch(error => {
                    reject(error);
                });
        });
    }

    public static async getBenchmarkFiles(): Promise<string[]> {
        const response = await fetch(DockerInterface.url + "/benchmarkFiles");
        const files = await response.json();

        return files;
    }

    public static async getBenchmarkQueue(): Promise<string[]> {
        const response = await fetch(DockerInterface.url + "/benchmarkQueue");
        const benchmarks = await response.json();

        return benchmarks;
    }

    public static async getBenchmarkStatus(): Promise<BenchmarkStatus> {
        const response = await fetch(DockerInterface.url + "/benchmarkStatus");
        const data = await response.json();

        return data;
    }
}
