#!/usr/bin/env python

"""
    snap_scan_statistics.py
"""

from __future__ import division, print_function

import sys
import snap
import json
import argparse
from time import time

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inpath', type=str, default='./_data/enron/enron_edgelist_2017-10-20.edgelist')
    #parser.add_argument('--inpath', type=str, default='./_data/actor-collaboration/new_actors_data/edge_list.tsv')
    parser.add_argument('--undirected', action="store_true")
    parser.add_argument('--verbose', action="store_true")
    return parser.parse_args()

def node_local_subgraph(node):
    neibs = snap.TIntV()        
    subgraph = set(node.GetOutEdges()).union([node.GetId()])
    _ = [neibs.Add(n) for n in subgraph]
    return neibs



if __name__ == '__main__':
    args = parse_args()
    
    # --
    # IO
    
    t = time()
    #if args.undirected:
    G = snap.LoadEdgeList(snap.PUNGraph, args.inpath, 0, 1, '\t')
    #else:
    #    G = snap.LoadEdgeList(snap.PNGraph, args.inpath, 0, 1, '\t')
    
    assert G.GetNodes() > 0
    print('test.py: load time = %f' % (time() - t))
    
    # --
    # Run
    
    t = time()
    best = {"node" : -1, "scan_stat" : -float('inf')}

    for i, node in enumerate(G.Nodes()):
        
        if not i % 10000:
            print('%d nodes | %fs' % (i, time() - t), file=sys.stderr)
        
        # Compute scan statistic
        # Moved to function for better profiling information
        #neibs = snap.TIntV()        
        #subgraph = set(node.GetOutEdges()).union([node.GetId()])
        #_ = [neibs.Add(n) for n in subgraph]

        neibs = node_local_subgraph(node)
    
        induced_subgraph = snap.GetSubGraph(G, neibs)
        tmp = {
            "node" : node.GetId(),
            "scan_stat" : induced_subgraph.GetEdges(),
        }
        
        if args.verbose:
            print(json.dumps(tmp))
        
        # Save best
        if tmp['scan_stat'] > best['scan_stat']:
            best = tmp
    
    print(json.dumps(best))
    print('test.py: compute time = %f' % (time() - t))

