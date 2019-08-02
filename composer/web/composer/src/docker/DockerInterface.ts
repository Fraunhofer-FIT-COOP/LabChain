export default class DockerInterface {
    url = "";

    constructor(url: string) {
        this.url = url;
    }

    public async getInstances() {
        const response = await fetch(this.url + "/getInstances");
        const json_resp = await response.json();

        return json_resp;
    }
}
