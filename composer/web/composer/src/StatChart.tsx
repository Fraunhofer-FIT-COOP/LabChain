import React from "react";
import "../node_modules/bootstrap/dist/css/bootstrap.min.css";

interface IState {}

interface IProps {}

export default class StateChart extends React.Component<IProps, IState> {
    current_miner: string = "";
    current_block: number = 0;
    current_difficulty: number = -1;
    render() {
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-md-4">Current Miner: {this.current_miner}</div>
                    <div className="col-md-4">Current Block: {this.current_block}</div>
                    <div className="col-md-4">Current Difficulty: {this.current_difficulty}</div>
                </div>
            </div>
        );
    }
}
