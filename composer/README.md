# LabChain Network Composer

The LabChain network composer is a web-based GUI component heavily relying on docker, that provides the following features:

* Spawning networks of arbitrary sizes locally (at some point your machine overburdened)
* Measures the connectivity. What node is connect to what other nodes?
* Easy application of benchmarks.

The general idea is to provide a benchmark application that can easily be executed to measure the performance continuously during
development.

## Usage

One requirement is that you have installed *docker* and that you can execute docker as non-root user

`sudo usermod -aG docker $USER` on Ubuntu

Then start the network composer by:

```
cd composer
pip3 install -r requirements.txt
python3 composer.py
```

Next:
TODO: Automate this step and serve the webpage as static content via the composer.py.

```
cd composer/web/composer
npm install
npm start
```
