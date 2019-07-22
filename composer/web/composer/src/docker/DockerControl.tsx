import React from 'react'

export default function DockerControl(props: any) {

    return (
        props.instance.status === 'running' ? <button className="btn btn-dark" onClick={(e) => { props.stopInstance(props.instance.name) }}>Stop</button> : <span><button className="btn btn-dark" onClick={(e) => { props.startInstance(props.instance.name) }}>Start</button> <button className="btn btn-dark" onClick={(e) => { props.deleteInstance(props.instance.name) }}>Delete</button></span>
    )
}
