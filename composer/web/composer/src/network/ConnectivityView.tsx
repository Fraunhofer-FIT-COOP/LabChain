import React from "react";
import FooterComponent from "../FooterComponent";
import "../../node_modules/bootstrap/dist/css/bootstrap.min.css";

export default function ConnectivityView() {
    return (
        <div className="container-fluid">
            <div className="row">
                <div className="col-md-12">
                    <h1>Network View</h1>
                </div>
            </div>
            <FooterComponent></FooterComponent>
        </div>
    );
}
