export class LabchainClient {
    url: string = "";
    rpc_id_count: number = 0;
    constructor(url: string) {
        this.url = url;
    }

    getConnectedPeers(): Promise<any> {
        if ("" === this.url) {
            throw Error("Not connected to a node");
        }

        return this.sendJSONRPC("getPeers");
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
