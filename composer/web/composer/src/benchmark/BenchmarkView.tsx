import React, { useState, useEffect } from "react";
import BenchmarkTable from "./BenchmarkTable";
import FooterComponent from "../FooterComponent";
import { DockerInterface } from "../docker/DockerInterface";

export default function BenchmarkView(props: any) {
    const [files, setFiles] = useState<string[]>([]);

    useEffect(() => {
        DockerInterface.getBenchmarkFiles().then(_files => {
            console.log(_files);
            setFiles(_files);
        });
    }, []);

    return (
        <div className="container-fluid">
            <div className="row">
                <div className="col-md-12">
                    <h1>Benchmark Overview</h1>
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
