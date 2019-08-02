import React, { useState, useEffect } from "react";
import DockerInstanceTable from "./DockerInstanceTable";
import Notifications, { notify } from "react-notify-toast";
import PruneConfirmation from "./dialog/PruneConfirmation";
import SpawnNetworkDialog from "./dialog/SpawnDialog";
import FooterComponent from "./FooterComponent";
import DockerInterface from "./docker/DockerInterface";
import "../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "./App.css";

const App: React.FC = () => {
    const [dockerInstances, setDockerInstances] = useState([]);
    const [showPruneConfirmation, setShowPruneConfirmation] = useState(false);
    const [showSpawnDialog, setShowSpawnDialog] = useState(false);

    let noteColor = { background: "#0E1717", text: "#FFFFFF" };
    const base_url = "http://localhost:8080";

    const di = new DockerInterface(base_url);

    useEffect(() => {
        di.getInstances().then(instances => {
            setDockerInstances(instances);
        });
        // eslint-disable-next-line
    }, []);

    let createNewDockerInstance = async function(evt: any) {
        const response = await fetch(base_url + "/startInstance");
        const instances = await response.json();
        setDockerInstances(instances);
        notify.show("Instance created", "custom", 5000, noteColor);
    };

    let startInstance = async function(name: string) {
        const response = await fetch(base_url + "/startInstance?name=" + name);
        const instances = await response.json();
        setDockerInstances(instances);
        notify.show("Instance started", "custom", 5000, noteColor);
    };

    let deleteInstance = async function(name: string) {
        const response = await fetch(base_url + "/deleteInstance?name=" + name);
        const instances = await response.json();
        setDockerInstances(instances);
        notify.show("Instance deleted", "custom", 5000, noteColor);
    };

    let stopInstance = async function(name: string) {
        const response = await fetch(base_url + "/stopInstance?name=" + name);
        const instances = await response.json();
        setDockerInstances(instances);
        notify.show("Instance stopped", "custom", 5000, noteColor);
    };

    let pruneNetwork = async function() {
        setShowPruneConfirmation(false);
        const response = await fetch(base_url + "/pruneNetwork");
        const instances = await response.json();
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
        const response = await fetch(base_url + "/spawnNetwork?number=" + n);
        const instances = await response.json();
        setDockerInstances(instances);
        notify.show("Network generated", "custom", 5000, noteColor);
    };

    return (
        <div className="container-fluid">
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
                <div className="col-md-6"></div>
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
