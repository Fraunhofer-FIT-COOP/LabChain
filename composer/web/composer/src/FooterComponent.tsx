import React from "react";
import { Link } from "react-router-dom";
import "../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "./FooterComponent.css";

export default function FooterComponent() {
    return (
        <footer className="page-footer footer navbar-fixed-bottom">
            <div className="container-fluid">
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
