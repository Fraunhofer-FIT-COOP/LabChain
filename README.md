# LabChain

In our BitLab Blockchain Course we develop our own blockchain platform.

### Objectives for the Platform are:

- Exchangeable components
- Strong documentation
- Excellent test coverage
- Well established software engineering processes
- Good maintainability and extendability  after project - conclusion


## Project Prerequisites
- Python3 (>= Python 3.5+) (https://www.python.org/)
  - PEP 8 Style Guide for Python Code (https://www.python.org/dev/peps/pep-0008/)
- Git Repository (https://git-scm.com/)
- Agile development
  - Code reviews, iterative development, extensive testing, no requirement spec. overhead
- Test first approach (Almost every function deserves a unit test)
  - Python3 Unit Testing Framework (https://docs.python.org/3/library/unittest.html)

Please use git precommit hooks to style check before commiting. We created a global pre-commit hook which you have to install by calling ```./scripts/install-hooks.bash```.

For the Hook to work, you'll need to install pycodestyle: ```pip install pycodestyle```

This script creats a symlink from ```.git//hooks/pre-commit``` to ```scripts/pre-commit.bash```. It is based on a script of sigmoidal.io (https://sigmoidal.io/automatic-code-quality-checks-with-git-hooks/) and the pep8-git-hook by cbrueffer (https://github.com/cbrueffer/pep8-git-hook).


# Setup

This software is tested with Python 3.5+

Run the following to install all dependencies:

```bash
pip3 install -r requirements.txt

```

# Run the Node

```
python3 node.py --port 8080 --peers <ip1>:<port1> <ip2>:<port2> ...
```

`-v` and `-vv` set the log level to INFO or DEBUG.

# Run the Client

```
python3 client.py <blockchain-node-ip> <blockchain-node-port>
```

`--doc` to start the Workflow Management System

# Run the unit tests

Executing a single test:

```
python3 -m unittest test.<test_name>
```

Notice that you must not add a `.py` to the name of the test.

For running all the unit tests execute:

```
python3 -m unittest discover
```

# TODO

- [x] Check if README is still correct
- [x] Changed directory structure
- [x] Remove presentations
- [x] Refactor names
- [x] Remove Node red stuff and MQTT
- [x] Remove visualizer
- [x] Clean up existing branches
- [x] Remove `nogas` and check PEP8 Styleguide
- [x] The `test_account.py` uses the `MockCryptoHelper` but should use the real CryptoHelper
- [x] Update versions in PIP requirements file
- [ ] Check unit tests
- [ ] Add an example (quick start/ getting started) to the README
- [ ] Remove mocks
- [ ] Introduce version number
- [ ] Remove constraint to store only a certain number of preceding blocks
- [ ] Check difficulty calculation
- [ ] Check block timestamp
- [ ] Put every class into a file
- [ ] Remove 10 seconds delay to wait for incoming transactions
- [ ] Currently the blocksynchronisation seems not to work ( > 2 peers) -> fix it
- [ ] Remove auto discovery mechanism
- [ ] Check the calls of the crypto helper methods (First `json.dumps(...)` then in the crypto helper `json.loads(...)`. There must be a better way.)
- [ ] Add Status Information when starting the node (without verbose mode)
- [ ] Clean up logging (better differentiation between log levels)

# TODO for Workflow Management System

- [x] Improve the current status of workflows by showing at which user it is at the moment
- [x] Improve retrieving the type of workflow while showing the workflow status
- [x] Add comments in the workflow for the addresses while creating the workflow, so that client can see a better explanation about the receiver of his transaction.
- [ ] Provide feedback to the client if the transaction is not validated
- [ ] Implement a malicious test client
- [ ] Look for a better way of ending a workflow. (It currently gets hanged in check tasks of the last user)
- [ ] Optimize current workflow status page as it takes long time to show the workflows
- [ ] Now, if same adress is chosen for 2 entities, the workflow will look completed even though it is not because of the numbers after "_".
      i.e: if wf: reviewer1_0 -> orderer_0 and if these two have same address, the workflow will look completed at the level of reviewer1_0. Maybe adding some kind of control to not use one address for multiple entities?

## Nice to have

- [ ] Use JSON for configuration
- [ ] Remove SQLite file from ressource directory
- [ ] Rename configuration in default_configuration and copy it in case there is no configuration provided
- [ ] Check and refactor block explorer
- [ ] Blockchain instance as singleton
- [ ] Check networking class (max number of connections,...)
- [ ] Remove large number of parameters in functions
- [ ] Create a setup.py
- [ ] Create a docker file (data directory must be mountable and the node must be configurable)
