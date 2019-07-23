import React from 'react'
import Modal from 'react-modal'

const pruneDialogStyle = {
    content: {
        top: '50%',
        left: '50%',
        right: 'auto',
        bottom: 'auto',
        width: '500px',
        marginRight: '-50%',
        transform: 'translate(-50%, -50%)'
    }
}

export default function SpawnNetworkDialog(props: any) {

    let count = 3

    return (
        <Modal isOpen={props.show} contentLabel="Spawn Network" style={pruneDialogStyle}>
            <div className="container">
                <div className="row">
                    <div className="col-md-12">
                        <h2>Spawn Network</h2>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-4">
                        <h4>Nodecount:</h4>
                    </div>
                    <div className="col-md-8">
                        <input type="text" onChange={(e) => { count = +e.target.value }} />
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-6">
                        <button className="btn btn-secondary" onClick={props.cancel}>Cancel</button>
                    </div>
                    <div className="col-md-6 text-right">
                        <button className="btn btn-primary" onClick={() => { props.ok(count) }}>Ok</button>
                    </div>
                </div>
            </div>
        </Modal>
    )
}

Modal.setAppElement('#root')
