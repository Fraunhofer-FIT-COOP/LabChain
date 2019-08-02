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
}
