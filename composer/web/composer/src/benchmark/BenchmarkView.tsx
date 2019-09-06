import React from "react";
import BenchmarkTable from "./BenchmarkTable";
import BenchmarkBatchTable from "./BenchmarkBatchTable";
import BenchmarkBatchControl from "./BenchmarkBatchControl";
import FooterComponent from "../FooterComponent";
import { DockerInterface, BenchmarkStatus } from "../docker/DockerInterface";
import "./BenchmarkView.css";

interface IState {
    files: string[];
    benchmarkStatus: BenchmarkStatus[];
}

interface IProps {}

export default class BenchmarkView extends React.Component<IProps, IState> {
    _isMounted: Boolean = false;
    timerID: any;

    constructor(props: any) {
        super(props);
        this.state = { files: [], benchmarkStatus: [{ remaining_txs: 0, found_txs: 0, total_txs: 0 }] };
    }

    componentDidMount() {
        this._isMounted = true;
        this.timerID = setInterval(() => {
            this.tick();
        }, 1000);
    }

    componentWillUnmount() {
        clearInterval(this.timerID);
        this._isMounted = false;
    }

    tick() {
        DockerInterface.getBenchmarkFiles().then(_files => {
            DockerInterface.getBenchmarkStatus().then(_status => {
                console.log("Received benchmark status");
                console.log(_status);
                this.setState({ files: _files, benchmarkStatus: _status });
            });
        });
    }

    dumpBenchmarkData() {}

    render() {
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-md-12">
                        <h1>Benchmark Overview</h1>
                    </div>
                </div>
                {this.state.benchmarkStatus.length > 0 && (
                    <div className="row">
                        <div className="col-md-6">
                            <h4>Remaining transactions to analyse:</h4>
                        </div>
                        <div className="col-md-1">
                            <h4>
                                {this.state.benchmarkStatus[0].found_txs}/{this.state.benchmarkStatus[0].total_txs}
                            </h4>
                        </div>
                        <div className="col-md-5">
                            <button className="btn btn-primary" onClick={this.dumpBenchmarkData}>
                                Dump current benchmark data
                            </button>
                        </div>
                    </div>
                )}
                <div className="row">
                    <div className="col-md-12">
                        <h3>Benchmark Batch Queue</h3>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-12">
                        <BenchmarkBatchControl></BenchmarkBatchControl>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-12">
                        <BenchmarkBatchTable></BenchmarkBatchTable>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-12">
                        <h3>Benchmark Files</h3>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-12 benchmarkTable">
                        <BenchmarkTable files={this.state.files}></BenchmarkTable>
                    </div>
                </div>
                <FooterComponent></FooterComponent>
            </div>
        );
    }
}
