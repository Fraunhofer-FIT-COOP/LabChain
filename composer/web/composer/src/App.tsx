import React, { useState, useEffect } from "react";
import DockerInstanceTable from "./DockerInstanceTable";
import Notifications, { notify } from "react-notify-toast";
import PruneConfirmation from "./dialog/PruneConfirmation";
import SpawnNetworkDialog from "./dialog/SpawnDialog";
import BenchmarkDialog from "./dialog/BenchmarkDialog";
import FooterComponent from "./FooterComponent";
import ApplyBenchmarkControl from "./ApplyBenchmarkControl";
import StatChart from "./StatChart";
import BenchmarkEngine from "./docker/BenchmarkEngine";
import { DockerInterface, DockerInstance } from "./docker/DockerInterface";
import "../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.min.js";
import "./App.css";

const App: React.FC = () => {
    const [dockerInstances, setDockerInstances] = useState<DockerInstance[]>([]);
    const [showPruneConfirmation, setShowPruneConfirmation] = useState(false);
    const [showSpawnDialog, setShowSpawnDialog] = useState(false);
    const [showBenchmarkDialog, setShowBenchmarkDialog] = useState(false);
    const [benchmarkId, setBenchmarkId] = useState("");
    const [benchmarkDialogErrorMessage, setBenchmarkDialogErrorMessage] = useState<string[]>([]);

    let noteColor = { background: "#0E1717", text: "#FFFFFF" };

    useEffect(() => {
        DockerInterface.getInstances().then(instances => {
            setDockerInstances(instances);
        });
        // eslint-disable-next-line
    }, []);

    let createNewDockerInstance = async function(evt: any) {
        let instances = await DockerInterface.createInstance();
        setDockerInstances(instances);
        notify.show("Instance created", "custom", 5000, noteColor);
    };

    let startInstance = async function(name: string) {
        let instances = await DockerInterface.startInstance(name);
        setDockerInstances(instances);
        notify.show("Instance started", "custom", 5000, noteColor);
    };

    let deleteInstance = async function(name: string) {
        let instances = await DockerInterface.deleteInstance(name);
        setDockerInstances(instances);
        notify.show("Instance deleted", "custom", 5000, noteColor);
    };

    let stopInstance = async function(name: string) {
        let instances = await DockerInterface.stopInstance(name);
        setDockerInstances(instances);
        notify.show("Instance stopped", "custom", 5000, noteColor);
    };

    let pruneNetwork = async function() {
        setShowPruneConfirmation(false);
        let instances = await DockerInterface.pruneNetwork();
        setDockerInstances(instances);
        notify.show("Network pruned", "custom", 5000, noteColor);
    };

    let pruneNetworkDialog = async function() {
        setShowPruneConfirmation(true);
    };

    let spawnNetworkDialog = async function() {
        setShowSpawnDialog(true);
    };

    let spawnNetwork = async function(n: number) {
        setShowSpawnDialog(false);
        let instances = await DockerInterface.spawnNetwork(n);
        setDockerInstances(instances);
        notify.show("Network generated", "custom", 5000, noteColor);
    };

    let startBenchmark = function(receiver: DockerInstance[], filename: string, nodecount: number) {
        console.log("Start benchmark: " + benchmarkId + " with name: " + filename);
        let bc: BenchmarkEngine = new BenchmarkEngine(receiver, filename, nodecount);
        let b: any;

        switch (benchmarkId) {
            case "10Simple":
                b = bc.benchmarkSimpleTransactions(10);
                break;
            case "100Simple":
                b = bc.benchmarkSimpleTransactions(100);
                break;
            case "1000Simple":
                b = bc.benchmarkSimpleTransactions(1000);
                break;
            case "10000Simple":
                b = bc.benchmarkSimpleTransactions(10000);
                break;
            case "100000Simple":
                b = bc.benchmarkSimpleTransactions(100000);
                break;
        }

        b.then((data: any) => {
            console.log("Its done");
            setShowBenchmarkDialog(false);
            setBenchmarkId("");
        }).catch((error: any) => {
            console.log("Could not create benchmark");
            console.log(error);
            setBenchmarkDialogErrorMessage([error]);
        });
    };

    let sendBenchmarkTransactions = function(benchmarkType: string) {
        setBenchmarkId(benchmarkType);
        setShowBenchmarkDialog(true);
    };

    return (
        <div className="container-fluid">
            <StatChart></StatChart>
            <div className="row">
                <div className="col-md-12">
                    <PruneConfirmation
                        show={showPruneConfirmation}
                        ok={pruneNetwork}
                        cancel={() => {
                            setShowPruneConfirmation(false);
                        }}
                    ></PruneConfirmation>
                    <SpawnNetworkDialog
                        show={showSpawnDialog}
                        ok={spawnNetwork}
                        cancel={() => {
                            setShowSpawnDialog(false);
                        }}
                    ></SpawnNetworkDialog>
                    <BenchmarkDialog
                        show={showBenchmarkDialog}
                        errorMessage={benchmarkDialogErrorMessage}
                        ok={startBenchmark}
                        dockerInstances={dockerInstances}
                        cancel={() => {
                            setShowBenchmarkDialog(false);
                            setBenchmarkId("");
                        }}
                    ></BenchmarkDialog>
                    <Notifications />
                </div>
            </div>
            <div className="row">
                <div className="col-md-10">
                    <h1>Labchain Composer</h1>
                </div>
                <div className="col-md-2 text-right">
                    <h3 className="counter">#Instances: {dockerInstances.length}</h3>
                </div>
            </div>
            <div className="row controlRow">
                <div className="col-md-2">
                    <button className="btn btn-primary" onClick={createNewDockerInstance}>
                        Create new Instance
                    </button>
                </div>
                <div className="col-md-2">
                    <button className="btn btn-primary" onClick={pruneNetworkDialog}>
                        Prune Network...
                    </button>
                </div>
                <div className="col-md-2">
                    <button className="btn btn-primary" onClick={spawnNetworkDialog}>
                        Spawn Network...
                    </button>
                </div>
                <div className="col-md-2">
                    <ApplyBenchmarkControl clicked={sendBenchmarkTransactions}></ApplyBenchmarkControl>
                </div>
                <div className="col-md-2"></div>
            </div>
            <div className="row">
                <div className="col-md-12">
                    <DockerInstanceTable
                        instances={dockerInstances}
                        startInstance={startInstance}
                        stopInstance={stopInstance}
                        deleteInstance={deleteInstance}
                    ></DockerInstanceTable>
                </div>
            </div>
            <FooterComponent></FooterComponent>
        </div>
    );
};

export default App;
