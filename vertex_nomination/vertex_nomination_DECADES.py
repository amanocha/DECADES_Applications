#!/usr/bin/env python


from __future__ import division, print_function
import argparse
from time import time
import numpy as np
from numba import int32, float32, float64,jitclass, njit
from numba.types import Tuple
from scipy.sparse import csr_matrix

from DEC_Pipeline import DEC_Pipeline
from DEC_Numba_Lib import DecSparseGraph, LoadDecSparseGraph, DecSparseGraphSpec

@njit(int32[:](DecSparseGraphSpec(), int32[:]), nogil=True)
def multi_bfs(graph, roots):
    node_visit_list = np.ones(graph.num_nodes, dtype=np.int32) * np.int32(-1)
    top_layer = list(roots)
    next_layer = [np.int32(x) for x in range(0)]
    hop = 1

    while len(top_layer) > 0:
        for each_node in top_layer:
            for e in graph.indices[graph.indptr[each_node]:graph.indptr[each_node + 1]]:
                if node_visit_list[e] == -1:
                    node_visit_list[e] = hop
                    next_layer.append(e)
        # reset top_layer and next_layer list:            
        top_layer = next_layer
        next_layer = [np.int32(x) for x in range(0)]
        hop += 1

    return node_visit_list


@njit(float64[:](DecSparseGraphSpec(), int32[:]), nogil=True)
def getContentScore(graph, roots):
    top_layer = list(roots)
    # get # of direct connection score
    directConnectionScore =  np.zeros(graph.num_nodes, dtype=np.int32)
    for each_node in top_layer:
        for e in graph.indices[graph.indptr[each_node]:graph.indptr[each_node + 1]]:
            directConnectionScore[e] +=1
    directConnectionScore = np.log(directConnectionScore+2)
              
    # get node attribute score
    beta = 0.25
    node_score = beta * np.log10(np.max(graph.node_attr)/graph.node_attr)
    
              
    contentscore = node_score + directConnectionScore

    return contentscore


@njit(Tuple((int32, float32))(DecSparseGraphSpec(), int32[:]), nogil=True)
def vertex_nomination__kernel__(G, seeds):
    
    # context score : computed via distance map from multi BFS
    bfs_results = multi_bfs(G, seeds)
    context_sim = 1/bfs_results

    # content score : placeholder computed via a random number generator
    content_sim = getContentScore(G, seeds)

    # fusion score : content_sim * context_sim 
    fusion_score = np.multiply(content_sim, context_sim)

    # remove original seeds from ranking
    for seed in seeds:
        fusion_score[seed] = np.float64(-1)
          
    top_nominee = np.int32(np.argmax(fusion_score))
    top_score = fusion_score[top_nominee]

    return top_nominee, top_score


def parse_args():
    parser = argparse.ArgumentParser()
    #parser.add_argument('--inpath', type=str, default='./_data/enron/enron_edgelist_2017-10-20.edgelist')
    parser.add_argument('--inpath', type=str, default='./_data/actor-collaborations')
    parser.add_argument('--seed', type=int, default=123)
    parser.add_argument('--num-runs', type=int, default=1)
    parser.add_argument('--num-seeds', type=int, default=5)
    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    t = time()

    # load graph
    G = LoadDecSparseGraph(args.inpath)
    print('load time = %f' % (time() - t))

    # initialize set of seeds
    seeds = set()
    np.random.seed(113)

    # get number of nodes in graph
    num_nodes_connected = len(G.indptr)
    print('number of nodes:',num_nodes_connected)
    print('number of nodes from G:', G.num_nodes)
    # get seeds
    seed_input = input('Please enter five seeds separated by comma:')
    if seed_input:
        seeds = list(map(int,seed_input.split(',')))
        if len(seeds)<5 or all(i >= G.num_nodes for i in seeds):
            print('Incorrect input entry!')
            raise
    else:
        # get random nodes in graph:
        seeds = np.random.choice(num_nodes_connected, 5, replace=False)

    seeds = np.array(list(seeds), dtype=np.int32)
    print('Starting with seeds:', seeds)


    # Vertex Nomination
    start = time()
    top_nominee, top_score = vertex_nomination__kernel__(G, seeds)        
    end = time()
    print('Top nominee:',top_nominee,';Top score:',top_score)
    print("Compute time: " + str(end - start))
    
