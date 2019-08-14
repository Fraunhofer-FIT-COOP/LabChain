import React, { useState, useEffect } from "react";
import BenchmarkTable from "./BenchmarkTable";
import FooterComponent from "../FooterComponent";
import { DockerInterface } from "../docker/DockerInterface";

export default function BenchmarkView(props: any) {
    const [files, setFiles] = useState<string[]>([]);
    const [benchmarkStatus, setBenchmarkStatus] = useState<{ remaining_txs: number; found_txs: number }>({ remaining_txs: 0, found_txs: 0 });

    useEffect(() => {
        DockerInterface.getBenchmarkFiles().then(_files => {
            console.log(_files);
            setFiles(_files);
        });

        DockerInterface.getBenchmarkStatus().then(_status => {
            setBenchmarkStatus(_status);
        });
    }, []);

    let dumpBenchmarkData = () => {
        DockerInterface.dumpBenchmarkData().then();
    };

    return (
        <div className="container-fluid">
            <div className="row">
                <div className="col-md-12">
                    <h1>Benchmark Overview</h1>
                </div>
            </div>
            <div className="row">
                <div className="col-md-6">
                    <h4>Remaining transactions to analyse:</h4>
                </div>
                <div className="col-md-1">
                    <h4>{benchmarkStatus.remaining_txs}</h4>
                </div>
                <div className="col-md-5">
                    <button className="btn btn-primary" onClick={dumpBenchmarkData}>
                        Dump current benchmark data
                    </button>
                </div>
            </div>
            <div className="row">
                <div className="col-md-12">
                    <BenchmarkTable files={files}></BenchmarkTable>
                </div>
            </div>
            <FooterComponent></FooterComponent>
        </div>
    );
}
