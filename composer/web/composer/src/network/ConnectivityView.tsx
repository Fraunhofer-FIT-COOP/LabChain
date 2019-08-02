import React, { useState, useEffect } from "react";
import DockerInterface from "../docker/DockerInterface";
import FooterComponent from "../FooterComponent";
import "../../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "./ConnectivityView.css";
import { Graph } from "react-d3-graph";
import { LabchainClient } from "../labchainSDK/Client";

const data = {
    nodes: [{ id: "Harry" }, { id: "Sally" }, { id: "Alice" }],
    links: [{ source: "Harry", target: "Sally" }, { source: "Harry", target: "Alice" }]
};
const myConfig = {
    nodeHighlightBehavior: true,
    node: {
        color: "lightgreen",
        size: 120,
        highlightStrokeColor: "blue"
    },
    link: {
        highlightColor: "lightblue"
    }
};

export default function ConnectivityView() {
    const [dockerInstances, setDockerInstances] = useState([]);
    const [graphData, setGraphData] = useState(data);

    const base_url = "http://localhost:8080";
    const di = new DockerInterface(base_url);

    let updateDockerInstances = () => {
        return new Promise((resolve, reject) => {
            di.getInstances().then(instances => {
                setDockerInstances(instances);
                resolve();
            });
        });
    };

    useEffect(() => {
        updateDockerInstances();
        setGraphData(graphData);
        // eslint-disable-next-line
    }, [!graphData]);

    let getNameByIP = function(ip: string): string {
        for (let inst of dockerInstances) {
            let i: any = inst;
            if (i.ipv4.startsWith(ip)) return i.name;
        }

        return "";
    };

    let renderGraph = function(_data: any) {
        if (_data.length === 0) return;

        data.nodes = [];
        data.links = [];

        for (let node of _data) {
            data.nodes.push({ id: node.peer.name });
            for (let con of Object.keys(node.peers)) {
                let name = getNameByIP(con);

                if ("" === name) continue;
                data.links.push({
                    source: node.peer.name,
                    target: name
                });
            }
        }
        setGraphData(data);
    };

    setInterval(() => {
        let getPeersProms: any = [];

        updateDockerInstances().then(() => {
            for (let inst of dockerInstances) {
                let i: any = inst;
                if (i.status !== "running") continue;
                let id = i.name.split("_")[1];
                let client = new LabchainClient("http://localhost:500" + id + "/");
                getPeersProms.push(
                    new Promise((resolve, reject) => {
                        client.getConnectedPeers().then(peers => {
                            resolve({ peer: inst, peers: peers });
                        });
                    })
                );
            }

            Promise.all(getPeersProms).then(peerData => {
                renderGraph(peerData);
            });
        });
    }, 1000);

    return (
        <div className="container-fluid">
            <div className="row">
                <div className="col-md-12">
                    <h1>Network View</h1>
                </div>
            </div>
            <div className="row">
                <div className="col-md-12">
                    <Graph id="graph-id" data={graphData} config={myConfig}></Graph>
                </div>
            </div>
            <FooterComponent></FooterComponent>
        </div>
    );
}
