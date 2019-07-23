import React from 'react'
import Modal from 'react-modal'

const pruneDialogStyle = {
    content: {
        top: '50%',
        left: '50%',
        right: 'auto',
        bottom: 'auto',
        marginRight: '-50%',
        transform: 'translate(-50%, -50%)'
    }
}

export default function PruneConfirmation(props: any) {

    return (
        <Modal isOpen={props.show} contentLabel="Prune Network" style={pruneDialogStyle}>
            <div className="container">
                <div className="row">
                    <div className="col-md-12">
                        <h2>Prune Network</h2>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-12">
                        <h4>Are you sure?</h4>
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-6">
                        <button className="btn btn-secondary" onClick={props.cancel}>Cancel</button>
                    </div>
                    <div className="col-md-6 text-right">
                        <button className="btn btn-primary" onClick={props.ok}>Ok</button>
                    </div>
                </div>
            </div>
        </Modal>
    )
}

Modal.setAppElement('#root')
