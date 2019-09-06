import React, { useState } from "react";
import Modal from "react-modal";
import { DockerInstance } from "../docker/DockerInterface";
import Select from "react-select";

const pruneDialogStyle = {
    content: {
        top: "50%",
        left: "50%",
        right: "auto",
        bottom: "auto",
        marginRight: "-50%",
        transform: "translate(-50%, -50%)"
    }
};

export default function BenchmarkDialog(props: any) {
    const [selectedReceiver, setSelectedReceiver] = useState<DockerInstance[]>([]);
    const [filename, setFilename] = useState<string>("testData");
    const [nodecount, setNodecount] = useState<number>(-1);
    const [configureNetwork, setConfigureNetwork] = useState<boolean>(false);

    let handleReceiverChange = function(_sel: any) {
        setSelectedReceiver(_sel);
    };

    let selectAllReceivers = function() {
        setSelectedReceiver(
            props.dockerInstances.map(function(x: DockerInstance) {
                return { label: x.name, value: x };
            })
        );
    };

    let deselectAllReceivers = function() {
        setSelectedReceiver([]);
    };

    let handleFilenameChange = function(evt: any) {
        setFilename(evt.target.value);
    };

    let handleNodecountChange = function(evt: any) {
        setNodecount(+evt.target.value);
    };

    let toggleControlNetwork = function() {
        setConfigureNetwork(!configureNetwork);
    };

    return (
        <Modal isOpen={props.show} contentLabel="Benchmark Configuration" style={pruneDialogStyle}>
            <div className="container">
                <div className="row">
                    <div className="col-md-12">
                        <h2>Benchmark Configuration</h2>
                    </div>
                </div>
                {props.errorMessage.length > 0 && (
                    <div className="row">
                        <div className="col-md-12">
                            <div className="alert alert-danger" role="alert">
                                {props.errorMessage}
                            </div>
                        </div>
                    </div>
                )}
                <div className="row">
                    <div className="col-md-2">
                        <h4>Filename:</h4>
                    </div>
                    <div className="col-md-10">
                        <input type="text" name="filename" value={filename} onChange={handleFilenameChange} />
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-12">
                        <div className="form-check">
                            <input type="checkbox" className="from-check-input" onChange={toggleControlNetwork} id="configureNetwork" />
                            <label className="form-check-label">Configure Network for benchmark</label>
                        </div>
                    </div>
                </div>
                {configureNetwork && (
                    <div className="row">
                        <div className="col-md-12">
                            <div className="card">
                                <div className="card-header">Network Configuration</div>
                                <div className="card-body">
                                    <div className="container">
                                        <div className="row">
                                            <div className="col-md-12">
                                                <p className="card-text">
                                                    Configure the network for the benchmark. Note that the transactions are transmitted to all the configured
                                                    peers in equal parts.
                                                </p>
                                            </div>
                                        </div>
                                        <div className="row">
                                            <div className="col-md-4">Define the number of nodes to create:</div>
                                            <div className="col-md-8">
                                                <input type="text" name="nodecount" value={nodecount} onChange={handleNodecountChange} />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
                {!configureNetwork && (
                    <div className="row">
                        <div className="col-md-12">
                            <h4>Select the receiving nodes:</h4>
                        </div>
                    </div>
                )}
                {!configureNetwork && (
                    <div className="row">
                        <div className="col-md-8">The send transactions will be evenly distributed between the selected nodes.</div>
                        <div className="col-md-2">
                            <button className="btn btn-secondary" onClick={selectAllReceivers}>
                                Select all
                            </button>
                        </div>
                        <div className="col-md-2">
                            <button className="btn btn-secondary" onClick={deselectAllReceivers}>
                                Deselect all
                            </button>
                        </div>
                    </div>
                )}
                {!configureNetwork && (
                    <div className="row">
                        <div className="col-md-12">
                            <Select
                                value={selectedReceiver}
                                onChange={handleReceiverChange}
                                isMulti={true}
                                options={props.dockerInstances.map(function(x: DockerInstance) {
                                    return { label: x.name, value: x };
                                })}
                            />
                        </div>
                    </div>
                )}
                <div className="row">
                    <div className="col-md-6">
                        <button className="btn btn-secondary" onClick={props.cancel}>
                            Cancel
                        </button>
                    </div>
                    <div className="col-md-6 text-right">
                        <button
                            className="btn btn-primary"
                            onClick={() => {
                                props.ok(selectedReceiver.map(x => (x as any).value), filename, nodecount);
                            }}
                        >
                            Ok
                        </button>
                    </div>
                </div>
            </div>
        </Modal>
    );
}

Modal.setAppElement("#root");
