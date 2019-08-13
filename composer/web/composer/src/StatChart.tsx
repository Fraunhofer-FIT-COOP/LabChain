import React from "react";
import "../node_modules/bootstrap/dist/css/bootstrap.min.css";
import { LabchainClient } from "./labchainSDK/Client";
import { DockerInterface } from "./docker/DockerInterface";

interface IState {
    current_miner: string;
    current_block: number;
    current_difficulty: number;
}

interface IProps {}

export default class StateChart extends React.Component<IProps, IState> {
    _isMounted: Boolean = false;
    timer: any;
    client: LabchainClient | undefined;

    constructor(props: any) {
        super(props);
        this.state = {
            current_miner: "",
            current_block: 0,
            current_difficulty: 0
        };

        DockerInterface.getClientInterface().then(intf => {
            this.client = intf;
        });
    }

    componentDidMount() {
        this._isMounted = true;
        this.timer = setInterval(() => {
            this.tick();
        }, 1000);
    }

    tick() {
        if (!this.client) return;

        this.client.getBlock().then(blocks => {
            if (this._isMounted) {
                if (0 === blocks.length) return;
                let block = blocks[0];
                this.setState({
                    current_miner: block.creator,
                    current_block: block.nr,
                    current_difficulty: block.difficulty
                });
            }
        });
    }

    componentWillUnmount() {
        this._isMounted = false;
        clearInterval(this.timer);
    }

    render() {
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-md-4">Current Miner: {this.state.current_miner}</div>
                    <div className="col-md-4">Current Block: {this.state.current_block}</div>
                    <div className="col-md-4">Current Difficulty: {this.state.current_difficulty}</div>
                </div>
            </div>
        );
    }
}
