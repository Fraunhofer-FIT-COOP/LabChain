import React from "react";

export default function BenchmarkBatchTable(props: any) {
    let rows: any[] = [];

    props.benchmarks.forEach((file: string, i: number) => {
        rows.push(
            <tr key={file}>
                <td>{i + 1}</td>
                <td>{file}</td>
            </tr>
        );
    });

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
