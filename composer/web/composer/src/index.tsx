import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import { Route, BrowserRouter as Router } from "react-router-dom";
import App from "./App";
import ConnectivityView from "./network/ConnectivityView";
import * as serviceWorker from "./serviceWorker";
import BenchmarkView from "./benchmark/BenchmarkView";

const routing = (
    <Router>
        <div>
            <Route exact path="/" component={App} />
            <Route path="/network" component={ConnectivityView} />
            <Route path="/benchmarks" component={BenchmarkView} />
        </div>
    </Router>
);

ReactDOM.render(routing, document.getElementById("root"));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
