#!/usr/bin/env python

# Copyright (c) 2020, Mahboob Karimian (mahboob.karimiyan{at}gmail.com)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the owner nor the names of its contributors may be
#     used to endorse or promote products derived from this software without
#     specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


import subprocess
import argparse
import threading
from bs4 import BeautifulSoup
import re
import networkx as nx
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
import json
import flask

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--br_global_ip", action="store", dest="br_global_ip", 
                    help="Add 'global IPv6 address' of your Border Router i.e fd00::302:304:506:708")
parser.add_argument("-w", "--web", action="store_true", help="Open interactive view in web browser")
parser.add_argument("-p", "--port", action="store", dest="port", default=8002, 
                    help="Port to run webserver, default=8002")
args = parser.parse_args()

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#
# ADD "global IPv6 address" OF YOUR BORDER ROUTER to br_global_ip
# EXAMPLE:
# br_global_ip = "fd00::302:304:506:708"
def get_data():
    if args.br_global_ip:
        print(args.br_global_ip)
        subprocess.call(f"wget -O index.html http://[{args.br_global_ip}]", shell=True)
        print("Updating routing table ...")
    else:
        print("No BR IP specified, using the last data file\n")

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#
root = 'BR'
def process_data():
    IpList = []
    get_data()
    # Open and parse html
    with open('index.html', 'r') as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'lxml')
        llsList = soup.find_all('body')
        for l in llsList:
            # Get all list tags in html
            ulList = l.find_all('li')
            for li in ulList:
                if "via" in li.text:
                    # Routing table as tuples
                    via = re.sub('\)','', li.text.split(' ')[2].replace('fe80', 'fd00'))
                    dst = re.sub(r'/\w+','', li.text.split(' ')[0])
                    if via != dst: IpList.append((dst, via))
                else:
                    # BR Neighbors
                    nbr = li.text.replace('fe80', 'fd00')
                    IpList.append((nbr, root))

    # Remove duplicates from list using set
    return list(set(IpList))

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#
def create_graph():
    IpList = process_data()
    # Generating Directed graph
    Mesh = nx.DiGraph()
    # All destinations are nodes, get them from IpList
    dst = [dst[0] for dst in IpList]
    Mesh.add_nodes_from(dst)
    # All elements in IpList are edges
    Mesh.add_edges_from(IpList)
    # Add labels, we take the last 2 sections of the ipv6 address
    lblist = [':'.join(lbl.split(':')[-2:]) for lbl in dst]
    lbdict = dict(zip(dst, lblist))
    lbdict['BR'] = 'BR'
    #print(Mesh.nodes())
    #print(Mesh.edges())
    #print(dst)
    return Mesh, lbdict

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#
def write_graph():
    Mesh, lbdict = create_graph()
    pos = nx.nx_agraph.graphviz_layout(Mesh, prog="dot", root='BR')
    options = {
        'node_color': 'crimson',
        'node_shape': 'o',
        "edgecolors": 'k',
        'linewidths': 0.5,
        'alpha': 0.8,
        'node_size': 600,
        'edge_color':'k',
        'width': 2,
        'arrowstyle': '-|>',
        'arrowsize': 12,
        'font_size': 11,
        'labels': lbdict
    }
    nx.draw_networkx(Mesh, pos, arrows=True, **options)
    G = nx.DiGraph(directed=True)
    plt.gca().invert_yaxis()
    plt.gca().set_axis_off()
    plt.savefig("Netgraph.svg")
    #plt.show()
    # write json formatted data
    d = json_graph.node_link_data(Mesh)  # node-link format to serialize
    # add degree of each node
    for dict_i in d['nodes']:
        dict_i['degree'] = str(dict(Mesh.degree()).get(dict_i.get('id')))
    # write json
    json.dump(d, open("force/force.json", "w"))
    # Serve the file over http to allow for cross origin requests

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#
N=0
def run_program():
    write_graph()
    global N
    N+=1
    threading.Timer(5, run_program).start()
    print("running program: ", N)
run_program()

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#
"""
pos = nx.spring_layout(Mesh)
#pos = nx.nx_agraph.graphviz_layout(Mesh, prog="dot", root=root_node)
nx.draw_networkx_nodes(Mesh, pos, node_color='royalblue', alpha = 1, node_size = 200)
nx.draw_networkx_edges(Mesh, pos, edge_color='r', width = 2, arrows=True)
nx.draw_networkx_labels(Mesh, pos, labels = lbdict, font_size = 10)
plt.gca().set_axis_off()
plt.show()
"""
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#
if args.web:
    app = flask.Flask(__name__, static_folder="force")

    @app.route("/")
    def static_proxy():
        return app.send_static_file("force.html")

    print(f"\nGo to http://localhost:{args.port}\n")
    app.run(port = args.port)