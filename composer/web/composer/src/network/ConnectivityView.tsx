import React from "react";
import FooterComponent from "../FooterComponent";
import "../../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "./ConnectivityView.css";
import { Graph } from "react-d3-graph";

const data = {
    nodes: [{ id: "Harry" }, { id: "Sally" }, { id: "Alice" }],
    links: [{ source: "Harry", target: "Sally" }, { source: "Harry", target: "Alice" }]
};
const myConfig = {
    nodeHighlightBehavior: true,
    node: {
        color: "lightgreen",
        size: 120,
        highlightStrokeColor: "blue"
    },
    link: {
        highlightColor: "lightblue"
    }
};

export default function ConnectivityView() {
    console.log("abc");

    return (
        <div className="container-fluid">
            <div className="row">
                <div className="col-md-12">
                    <h1>Network View</h1>
                </div>
            </div>
            <div className="row">
                <div className="col-md-12">
                    <Graph id="graph-id" data={data} config={myConfig}></Graph>
                </div>
            </div>
            <FooterComponent></FooterComponent>
        </div>
    );
}
