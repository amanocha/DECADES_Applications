#!/usr/bin/env python

"""

SDH_main.py

"""

from __future__ import division, print_function

import snap
import random
import argparse
from time import time
import numpy as np
# --
# Helpers

def random_content_similarity(G, edge_content, target_vertex, which_m_prime, interesting_average_topic_vector=None):
    """ random content similarity """ 
    return random.random()

def getContentScore(G, node_attr, node_id, seeds):
    seeds = list(seeds)
    neighbors = set(G.GetNI(node_id).GetOutEdges())
    
    # get # of direct connection score
    directConnectionScore = 0
    for seed in seeds:
	if seed in neighbors:
            directConnectionScore += 1
    
    # get # of edges score  
    edge_score = np.log10(len(neighbors))

    # get noad node score:
    beta = 0.25
    node_score = beta * np.log10(np.max(node_attr)/node_attr[node_id])
    
    contentscore = node_score + directConnectionScore

    return contentscore


content_similarities = {
    "random" : random_content_similarity,
    "connections": getContentScore
}


def min_path_distance_context_similarity(G, node_id, seeds):
    """ min distance from node_id to any of the seeds """
    min_path = float('inf')
    for seed in seeds:
        path_length = snap.GetShortPath_fast(G, seed, node_id).Len() - 1
        if (path_length < min_path) and (path_length > 0):
            min_path = path_length
    
    return 1 / min_path

context_similarities = {
    "min_path_distance" : min_path_distance_context_similarity,
}


fusions = {
    "context" : lambda edge_content, context: context,
    "edge_content" : lambda edge_content, context: edge_content,
    "product" : lambda edge_content, context: edge_content * context,
    "sum" : lambda edge_content, context: edge_content + context,
}

# --
# Vertex nomination

def vertex_nomination(
        G,
        seeds, 
        node_attr,
        edge_content=None,
        fusion_mode='product',
        context_similarity='min_path_distance',
        #content_similarity='random',
        content_similarity='connections',
        return_ranked_list=False,
        return_ranked_list_and_scores=False,
        condition_on_neighbors=False,
    ):
    
    seeds = set(seeds)
    
    if condition_on_neighbors:
        neighbors = [set(G.GetNI(seed).GetOutEdges()) for seed in seeds]
        neighbors = reduce(lambda a,b: a.union(b), neighbors)

    np.random.seed(max(seeds))
    num_nodes=G.GetMxNId() +1
    print(G.GetNodes()+1)
    content_sim_all = np.random.random(num_nodes)    
    best = {'fusion_score' : -1}
    for node in G.Nodes():
        node_id = node.GetId()
        
        if node_id in seeds:
            continue
        
        if (not condition_on_neighbors) or (node_id in neighbors):
            context_sim = context_similarities[context_similarity](G, node_id, seeds)
            content_sim =  content_similarities[content_similarity](G, node_attr, node_id, seeds)
            fusion_score = fusions[fusion_mode](content_sim, context_sim)
            
            if fusion_score > best['fusion_score']:
                best = {
                    "node" : node.GetId(),
                    "fusion_score" : fusion_score,
                    "content_sim" : content_sim,
                    "context_sim" : context_sim,
                }
    
    return best


def parse_args():
    parser = argparse.ArgumentParser()
    #parser.add_argument('--inpath', type=str, default='./data/enron/enron_edgelist_2017-10-20.edgelist')
    parser.add_argument('--inpath', type=str, default='./data/actor-collaborations')
    parser.add_argument('--seed', type=int, default=123)
    parser.add_argument('--num-runs', type=int, default=100)
    parser.add_argument('--num-seeds', type=int, default=5)
    return parser.parse_args()


if __name__ == "__main__":
    
    args = parse_args()
    random.seed(args.seed)
    rnd = snap.TRnd(args.seed)
    
    t = time()
    times = []
    start = time()
    G = snap.LoadEdgeList(snap.PUNGraph, '/'.join([args.inpath,'edge_list.tsv']), 0, 1, '\t')
    # load node_attr:
    with open('/'.join([args.inpath,'node_attr.tsv'])) as f:
        node_attr = np.fromfile(f, count=-1, sep='\t',dtype=np.int32)
        node_attr = np.reshape(node_attr, (int(len(node_attr) / 2), 2))
        node_attr = node_attr[:,1]
    print('num_nodes:',G.GetNodes()+1)
    
    print('test.py: load time = %f' % (time() - t))
    np.random.seed(113)

    # Randomly sample seeds
    seeds = set()
    n=G.GetNodes()+1
    seed_input = input('Please enter at least five seeds separated by comma:')
    if seed_input:
        seeds = list(seed_input)
        if len(seeds)<5:
            print('Incorrect input entry!')
            raise
    else:
        # get random nodes in graph:
        seeds = np.random.choice(num_nodes_connected, 5, replace=False)
            
    seeds=list(seeds)
    print('Starting with seeds:', seeds)
    
    start = time()
    vns = vertex_nomination(G, seeds=seeds, node_attr=node_attr, edge_content=None, condition_on_neighbors=False)
    end = time()
    print(vns)
    print("Compute time: " + str(end - start))

