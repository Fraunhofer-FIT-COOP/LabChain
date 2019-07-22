import React from 'react'
import DockerControl from './docker/DockerControl'

export default function DockerInstanceTable(props: any) {
    let rows: any[] = []

    let stopInstance = async function(name: string) {
        props.stopInstance(name)
    }

    let startInstance = async function(name: string) {
        props.startInstance(name)
    }

    let deleteInstance = async function(name: string) {
        props.deleteInstance(name)
    }

    // eslint-disable-next-line
    props.instances.map((inst: any, i: number) => {
        rows.push(<tr key={inst.name}><td>{i + 1}</td><td>{inst.id.substring(0, 10)}...</td><td>{inst.name}</td><td>{inst.status}</td><td>{inst.port}</td><td>
            <DockerControl instance={inst} stopInstance={stopInstance} startInstance={startInstance} deleteInstance={deleteInstance}></DockerControl>
        </td></tr>)
    })

    return (
        <table className="table table-striped">
            <thead>
                <tr>
                    <th>#</th>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Status</th>
                    <th>Ports</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    )
}
