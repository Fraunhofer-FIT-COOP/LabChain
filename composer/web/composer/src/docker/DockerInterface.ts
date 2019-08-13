import { BenchmarkData } from "./BenchmarkEngine";

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

    public static async deleteInstance(name: string): Promise<DockerInstance[]> {
        const response = await fetch(DockerInterface.url + "/deleteInstance?name=" + name);
        const instances = await response.json();

        return instances;
    }

    public static async stopInstance(name: string): Promise<DockerInstance[]> {
        const response = await fetch(DockerInterface.url + "/stopInstance?name=" + name);
        const instances = await response.json();

        return instances;
    }

    public static async pruneNetwork(): Promise<DockerInstance[]> {
        const response = await fetch(DockerInterface.url + "/pruneNetwork");
        const instances = await response.json();

        return instances;
    }

    public static async spawnNetwork(n: number): Promise<DockerInstance[]> {
        const response = await fetch(DockerInterface.url + "/spawnNetwork?number=" + n);
        const instances = await response.json();

        return instances;
    }

    public static async addWatchTransactions(txs: BenchmarkData[]): Promise<any> {
        const response = await fetch(DockerInterface.url + "/watchTransactions", {
            method: "POST",
            body: JSON.stringify(txs)
        });

        return response.toString();
    }

    public static async storeData(data: any): Promise<String> {
        const response = await fetch(DockerInterface.url + "/storeBenchmarkData", {
            method: "POST",
            body: JSON.stringify(data)
        });

        return response.toString();
    }
}
