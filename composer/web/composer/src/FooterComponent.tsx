import React from "react";
import { Link } from "react-router-dom";
import "../node_modules/bootstrap/dist/css/bootstrap.min.css";

export default function FooterComponent() {
    return (
        <footer className="page-footer">
            <div className="container-fluid">
                <div className="row">
                    <div className="col-md-12">
                        <h4>Change View:</h4>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-1">
                        <Link to="/">Main</Link>
                    </div>
                    <div className="col-md-1">
                        <Link to="/network">Network</Link>
                    </div>
                    <div className="col-md-1">
                        <Link to="/benchmarks">Benchmarks</Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}
