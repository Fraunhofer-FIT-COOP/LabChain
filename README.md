# LabChain

In our BitLab Blockchain Course we develop our own blockchain platform.

### Objectives for the Platform are:

- Exchangeable components
- Strong documentation
- Excellent test coverage
- Well established software engineering processes
- Good maintainability and extendability  after project - conclusion


## Project Prerequisites
- Python3 (https://www.python.org/)
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

Run the following to install all dependencies:

```bash
pip install -r requirements.txt

```