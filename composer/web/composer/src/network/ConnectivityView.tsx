import React from "react";
import { DockerInterface, DockerInstance } from "../docker/DockerInterface";
import FooterComponent from "../FooterComponent";
import "../../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "./ConnectivityView.css";
import { Graph } from "react-d3-graph";
import LabchainClient from "../labchainSDK/Client";

export interface GraphNode {
    id: string;
}

export interface GraphLink {
    source: string;
    target: string;
}

export interface GraphData {
    nodes: GraphNode[];
    links: GraphLink[];
}

interface IState {
    data?: GraphData;
}

interface IProps {}

export default class ConnectivityView extends React.Component<IProps, IState> {
    _isMounted: Boolean = false;
    timerID: any;

    graphConfig: any = {
        nodeHighlightBehavior: true,
        width: 1600,
        height: 800,
        node: {
            color: "lightgreen",
            size: 300,
            highlightStrokeColor: "blue"
        },
        link: {
            highlightColor: "lightblue"
        }
    };

    constructor(props: any) {
        super(props);
        this.state = { data: { nodes: [{ id: "None" }], links: [] } };
    }

    componentDidMount() {
        this._isMounted = true;
        this.timerID = setInterval(() => {
            this.tick();
        }, 1000);
    }

    private getNameByIP(dockerInstances: DockerInstance[], ip: string): string {
        for (let inst of dockerInstances) {
            if (inst.ipv4.startsWith(ip)) return inst.name;
        }

        return "";
    }

    private renderGraph(dockerInstances: DockerInstance[], _data: { peer: DockerInstance; peers: string[] }[]) {
        if (_data.length === 0) return;

        let nodes: GraphNode[] = [];
        let links: GraphLink[] = [];
        console.log(_data);

        nodes = _data.map(d => {
            return { id: (" " + d.peer.name).slice(1) };
        });

        links = _data
            .map(d => {
                return Object.keys(d.peers)
                    .map(d2 => {
                        return this.getNameByIP(dockerInstances, d2);
                    })
                    .filter(a => a !== d.peer.name)
                    .map(d3 => {
                        return { source: d.peer.name, target: d3 };
                    });
            })
            .flat();

        let newData = { nodes: nodes, links: links };

        // the comparation might fail sometimes, but its fast and nothing bad will happen anyway
        if (this._isMounted && JSON.stringify(this.state.data) !== JSON.stringify(newData)) this.setState({ data: newData });
    }

    tick() {
        DockerInterface.getInstances().then(instances => {
            let getPeersProms: Promise<{ peer: DockerInstance; peers: string[] }>[] = [];
            for (let inst of instances) {
                if (inst.status !== "running") continue;

                let id: number = +inst.name.split("_")[1];

                let client = new LabchainClient("http://localhost:" + (id + 5000) + "/");

                getPeersProms.push(
                    new Promise((resolve, reject) => {
                        client.getConnectedPeers().then(peers => {
                            resolve({ peer: inst, peers: peers });
                        });
                    })
                );
            }

            Promise.all(getPeersProms).then(peerData => {
                this.renderGraph(instances, peerData);
            });
        });
    }

    componentWillUnmount() {
        clearInterval(this.timerID);
        this._isMounted = false;
    }

    render() {
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-md-12">
                        <h1>Network View</h1>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-12">
                        <Graph id="graph-id" data={this.state.data} config={this.graphConfig}></Graph>
                    </div>
                </div>
                <FooterComponent></FooterComponent>
            </div>
        );
    }
}
