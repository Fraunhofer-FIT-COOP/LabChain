import React from "react";

export default function BenchmarkBatchTable(props: any) {
    let rows: any[] = [];

    return (
        <table className="table table-striped">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Name</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    );
}
