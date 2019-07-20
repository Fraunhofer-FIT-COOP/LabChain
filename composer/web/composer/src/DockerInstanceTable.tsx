import React from 'react'

export default function DockerInstanceTable() {
    let rows = []

    for (let i = 0; i < 10; ++i) {
        rows.push(<tr><td>{i}</td><td>id_</td><td>_name</td><td>ports</td></tr>)
    }

    return (
        <table className="table table-striped">
            <thead>
                <tr>
                    <th>#</th>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Ports</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    )
}
