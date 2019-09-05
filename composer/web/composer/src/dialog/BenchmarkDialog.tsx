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
                        <h4>Select the receiving nodes:</h4>
                    </div>
                </div>
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
                                props.ok(selectedReceiver.map(x => (x as any).value), filename);
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
