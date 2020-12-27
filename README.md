# RPL Network Visualizer

A tool for drawing the topology of a RPL network. It works out of the box with Contiki-NG, by using the data extracted from its build-in HTTP webserver which reads routing and neighbor tables in Contiki-NG OS.

## Requirements

### Python 3

The following python packages are required to run the script:

```
Flask==1.1.2
matplotlib==3.3.3
networkx==2.5
beautifulsoup4==4.9.3
```

You can install them using `requirements.txt` and `pip`. If you like, you can use a python virtual environment.

### Contiki-NG

In the mote which you connected by tunslip interface, an HTTP server is required to be included in the project. **Also you need to know the Global IPV6 Address of this mote.**

`
MODULES_REL += webserver
`

Note that in Contiki-NG, this is included in RPL border router example already.

## Run the Network Visualizer

### Run in the Terminal

Open a Terminal window where you cloned this repo, then run:
`python3 rpl_visualizer.py -i -w -p`
The program takes 3 optional arguments:

`-i` : global IPv6 address of your Border Router i.e fd00::302:304:506:708

`-w` : Open interactive view in a web browser

`-p` : Port to run webserver, default is 8002

If the global IPv6 address of the Border Router is not specified by `-i`, the program will use an existing `index.html` file.

**Recommendation**: Use `-w` flag. This runs a local webserver and draws the nodes and links of the given RPL network using d3-force JS. This provides an interactive, beautiful, and better view of the network with many options and controls like zoom, drag, etc.

By default, both of scripts try to download the `index.php` from Contiki-NG every 5 seconds. This means that basically you will have an updated output in SVG every 5 seconds. For interactive view, you can refresh manually or add an Update interval more than 5 seconds.

### Run in Jupyter Notebook

There is also a Notebook version of the program. You need to install jupyter-notebook in order to open and run.

## Output

### Interactive view in Web Browser

Using `-w` option and browsing to <http://127.0.0.1:8002> (by default), opens an interactive view of the network with many options and controls.

### As SVG file (Scalable Vector Graphics)

`Netgraph.svg` is the output of the program in SVG format.

## Contribution

Everybody is welcomed to use the code, modify, improve and add other features to it.

For example a useful feature could be adding an other command line argument to get the interval of re-downloading the tables from Contiki-NG border router in order to have an updated viw every `N` seconds.

## Screenshot
