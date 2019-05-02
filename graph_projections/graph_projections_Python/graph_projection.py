import numpy as np
from numba import jitclass, int32, njit, float32    # import the types
from numba import types as nb_types                 # creates type from input
import sys
from DEC_Pipeline import DEC_Pipeline, DEC_Options
from DEC_Numba_Lib import TriDenseGraph_num_ele_i_rows as num_ele_i_rows
from DEC_Numba_Lib import DecBipartiteGraph, DecBipartiteGraphSpec, LoadDecBipartiteGraph
from time import time
import pdb

@njit(int32[:](DecBipartiteGraphSpec()), nogil=True)
def projection_count__kernel__(graph):
    output = np.zeros(graph.projection_size, dtype=np.int32)
    tri_size = graph.tri_size
    for i in range(graph.x_nodes):
        for e1 in range(graph.node_array[i], graph.node_array[i+1]-1):
            y_node1 = graph.edge_array[e1]
            index_before_i = num_ele_i_rows(graph.y_nodes, y_node1, tri_size)
            for e2 in range(e1+1, graph.node_array[i+1]):
                y_node2 = graph.edge_array[e2]
                assert(y_node1 < y_node2)
                k = index_before_i + y_node2- y_node1 - 1
                if k<0:
                    print(y_node1, y_node2, k)
                assert(k >= 0)
                assert(k < graph.projection_size)
                # here to be used decades based increment function for random memory access
                output[k] += 1
    return output


@njit(float32[:](DecBipartiteGraphSpec()), nogil=True)
def projection_weighted__kernel__(graph):
    output = np.zeros(graph.projection_size, dtype=np.float32)
    tri_size = graph.tri_size
    for i in range(graph.x_nodes):
        for e1 in range(graph.node_array[i], graph.node_array[i+1]-1):
            y_node1 = graph.edge_array[e1]
            index_before_i = num_ele_i_rows(graph.y_nodes, y_node1, tri_size)
            current_size = graph.node_array[i+1] - graph.node_array[i]
            e1_weight = graph.edge_data[e1]
            for e2 in range(e1+1, graph.node_array[i+1]):
                y_node2 = graph.edge_array[e2]
                e2_weight = graph.edge_data[e2]
                assert(y_node1 < y_node2)
                k = index_before_i + y_node2 - y_node1 - 1
                assert(k >= 0)
                assert(k < graph.projection_size)
                # here to be used decades based increment function for random memory access
                # this one requires floating point operation.
                output[k] += (e1_weight * e2_weight) / current_size
    return output


@njit(int32[:](DecBipartiteGraphSpec()), nogil=True)
def projection_flag__kernel__(graph):
    output = np.zeros(graph.projection_size, dtype=np.int32)
    tri_size = graph.tri_size
    for i in range(graph.x_nodes):
        for e1 in range(graph.node_array[i], graph.node_array[i+1]-1):
            y_node1 = graph.edge_array[e1]
            index_before_i = num_ele_i_rows(graph.y_nodes, y_node1, tri_size)
            for e2 in range(e1+1, graph.node_array[i+1]):
                y_node2 = graph.edge_array[e2]
                assert(y_node1 < y_node2)
                k = index_before_i + y_node2 - y_node1 - 1
                assert(k >= 0)
                assert(k < graph.projection_size)
                # here to be used decades based increment function for random memory access
                output[k] = 1
    return output

if __name__ == "__main__":

    # read input arguments
    file_name = sys.argv[1]
    projection_type = sys.argv[2]

    # read the graph data
    t=time()
    G = LoadDecBipartiteGraph(file_name)
    print('load time:',time()-t)
    
    projection = {'count': projection_count__kernel__,
                  'flag': projection_flag__kernel__,
                  'weighted': projection_weighted__kernel__}

    # compute projection
    t=time()
    projected_graph = projection[projection_type](G)
    print('compute time:',time()-t)
    # save output
    np.savetxt('projected_graph.txt', projected_graph, fmt="%s")



