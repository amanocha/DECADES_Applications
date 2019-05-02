#!/usr/bin/env python

import argparse
from time import time
import numpy as np
from numba import int32, boolean, njit
from numba.types import Tuple

from DEC_Pipeline import DEC_Pipeline
from DEC_Numba_Lib import DecSparseGraph, LoadDecSparseGraph, DecSparseGraphSpec

@njit(Tuple((int32,int32))(DecSparseGraphSpec(), boolean), nogil=True)
def scan_statistics__kernel__(graph, directed=False):

    top_score = np.int32(0)
    top_node = np.int32(-1)
    n = len(graph.indptr)
    for i in range(n-1):
        if not i%10000:
            print('Computing Node',i,'...')
        A = graph.indices[graph.indptr[i]:graph.indptr[i + 1]]
        triangles = 0
        self_edge = 0
        for j in A:
            if i!=j:
                B = graph.indices[graph.indptr[j]:graph.indptr[j + 1]]
                a_i, b_j = 0, 0
                while a_i<len(A) and b_j<len(B):
                    if A[a_i] == B[b_j]:
                        if A[a_i]!=i:
                            if B[b_j]!=j:
                                triangles += 1
                            else:
                                self_edge +=1
                        a_i += 1
                        b_j += 1
                    elif A[a_i] < B[b_j]:
                        a_i += 1
                    else:
                        b_j += 1
        edge_num = graph.indptr[i + 1]- graph.indptr[i] + np.int32(triangles/2) + self_edge
        if edge_num > top_score:
            top_score = np.int32(edge_num)
            top_node = np.int32(i)
    
    return top_node, top_score


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inpath', type=str, default='./_data/enron/')
    parser.add_argument('--inpath', type=str, default='./_data/actor-collaboration/old')
    parser.add_argument('--seed', type=int, default=123)
    parser.add_argument('--num-runs', type=int, default=10)
    parser.add_argument('--num-seeds', type=int, default=5)
    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    # load graph:
    t = time()
    G = LoadDecSparseGraph(args.inpath)
    print('load time = %f' % (time() - t))

    start = time()
    top_nominee, top_score = scan_statistics__kernel__(G, directed=False)        
    print("time: ",(time() - start))
    print("top node:", top_nominee)
    print("top score:", top_score)
