import React from "react";

export default function ApplyBenchmarkControl(props: any) {
    let send10Transactions = async function() {
        props.clicked("10Simple");
    };

    let send100Transactions = async function() {
        props.clicked("100Simple");
    };

    let send1000Transactions = async function() {
        props.clicked("1000Simple");
    };

    let send10000Transactions = async function() {
        props.clicked("10000Simple");
    };

    let send100000Transactions = async function() {
        props.clicked("100000Simple");
    };

    return (
        <div className="dropdown">
            <button
                className="btn btn-primary dropdown-toggle"
                type="button"
                id="dropdownMenuButton"
                data-toggle="dropdown"
                aria-haspopup="true"
                aria-expanded="false"
            >
                Apply benchmark...
            </button>
            <div className="dropdown-menu" aria-labelledby="dropdownMenuButton">
                <button className="dropdown-item" title="Send 10 tranasctions to the blockchain network and measure the time" onClick={send10Transactions}>
                    10 Transactions
                </button>
                <button className="dropdown-item" title="Send 100 tranasctions to the blockchain network and measure the time" onClick={send100Transactions}>
                    100 Transactions
                </button>
                <button className="dropdown-item" title="Send 1,000 tranasctions to the blockchain network and measure the time" onClick={send1000Transactions}>
                    1,000 Transactions
                </button>
                <button
                    className="dropdown-item"
                    title="Send 10,000 tranasctions to the blockchain network and measure the time"
                    onClick={send10000Transactions}
                >
                    10,000 Transactions
                </button>
                <button
                    className="dropdown-item"
                    title="Send 100,000 tranasctions to the blockchain network and measure the time"
                    onClick={send100000Transactions}
                >
                    100,000 Transactions
                </button>
            </div>
        </div>
    );
}
