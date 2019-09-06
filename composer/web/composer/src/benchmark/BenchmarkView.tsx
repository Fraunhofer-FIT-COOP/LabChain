import React from "react";
import BenchmarkTable from "./BenchmarkTable";
import BenchmarkBatchTable from "./BenchmarkBatchTable";
import FooterComponent from "../FooterComponent";
import { DockerInterface, BenchmarkStatus } from "../docker/DockerInterface";
import "./BenchmarkView.css";

interface IState {
    files: string[];
    benchmarkQueue: string[];
    benchmarkStatus: BenchmarkStatus;
}

interface IProps {}

export default class BenchmarkView extends React.Component<IProps, IState> {
    _isMounted: Boolean = false;
    timerID: any;

    constructor(props: any) {
        super(props);
        this.state = { files: [], benchmarkQueue: [], benchmarkStatus: { name: "", remaining_txs: 0, found_txs: 0, total_txs: 0 } };
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
                DockerInterface.getBenchmarkQueue().then(_queue => {
                    console.log("Received benchmark status");
                    console.log(_status);
                    this.setState({ files: _files, benchmarkQueue: _queue, benchmarkStatus: _status });
                });
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
                {this.state.benchmarkStatus.name !== "" && (
                    <div className="row">
                        <div className="col-md-6">
                            <h4>
                                Active Benchmark <b>{this.state.benchmarkStatus.name}</b> Remaining transactions to analyse:
                            </h4>
                        </div>
                        <div className="col-md-1">
                            <h4>
                                {this.state.benchmarkStatus.found_txs}/{this.state.benchmarkStatus.total_txs}
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
                        <BenchmarkBatchTable benchmarks={this.state.benchmarkQueue}></BenchmarkBatchTable>
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
