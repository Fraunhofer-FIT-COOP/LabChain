import React from 'react'
import DockerInstanceTable from './DockerInstanceTable'
import '../node_modules/bootstrap/dist/css/bootstrap.min.css'

const App: React.FC = () => {
    return (
        <div className="container-fluid">
            <div className="row">
                <div className="col-md-12">
                    <h1>Labchain Composer</h1>
                </div>
            </div>
            <div className="row">
                <div className="col-md-12">
                    <DockerInstanceTable></DockerInstanceTable>
                </div>
            </div>
        </div>
    );
}

export default App;
