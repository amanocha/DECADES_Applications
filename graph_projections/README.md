# Graph Projections 

## Gathering the Data
1. Select a dataset from http://konect.uni-koblenz.de/downloads/ (see below for the ones we used).
2. Run the following:

        mkdir data
        cd data
        tar xjf [filename].tar.bz2
        rm [filename].tar.bz2
        cd [dataset]

3. Locate the out.* file in your newly created dataset directory and navigate to the utils/ directory:

        cd ../../utils
        
4. Run the following:

        ./complete_flow.sh out.[filename]

5. Navigate back to the dataset directory. You should now have x_to_y_graph.txt and y_to_x_graph.txt, which are the bipartite graphs from the dataset. DECADES kernels can run on either. 

## Example Datasets
- Small: http://konect.uni-koblenz.de/downloads/tsv/brunson_revolution.tar.bz2
- Also pretty small (probably a good one to simulate on): http://konect.uni-koblenz.de/downloads/tsv/moreno_crime.tar.bz2
- Medium (simulate on this one if you feel brave!): http://konect.uni-koblenz.de/downloads/tsv/opsahl-collaboration.tar.bz2
- Pretty big: http://konect.uni-koblenz.de/downloads/tsv/youtube-groupmemberships.tar.bz2
- Slightly bigger: http://konect.uni-koblenz.de/downloads/tsv/dbpedia-writer.tar.bz2

Note: the youtube dataset needs this line inserted after the first one: "% 293360 94238 30087" (number of edges, x_nodes, and y_nodes)

## Compiling Graph Projections

There are 2 variants of the algorithm:

- Bit Flag (gp_bit_flag): a projection with a binary edge
- Counter (gp_count): a projection that counts how many times the relation was seen

For more information on the algorithm, see https://en.wikipedia.org/wiki/Bipartite_network_projection.

-----

Each variant contains three directories:

- baseline: a standard version of the algorithm that can be compiled with g++ or DEC++ "n" (native) mode

        g++ -O3 -std=c++11 main.cpp -o main
        
  or 

        DEC++ -m n main.cpp

- decades: a multithreaded parallel version of the algorithm that can be compiled with DEC++ "db" (decades base) or "di" (decades decoupled implicit) mode and a set number of threads

        DEC++ -m [mode] -t [num_threads] main.cpp 

- decades_bit_serial: a SIMD parallel version of the algorithm that can be compiled with DEC++ "b" (biscuit) mode

        DEC++ -m b -s [sync mode] -sps [scratchpad size] main.cpp

## Running Graph Projections

To run the executables:

- If you compiled with g++, you need to input two graphs because the baseline version does bi-direction projection. Run the following:

        ./exec <PATH_TO_INPUTS>/x_to_y_graph.txt <PATH_TO_INPUTS>/y_to_x_graph.txt
        
- If you compiled with DEC++, you only need to input one graph, depending on which direction of projection you want. Run one of the following:

        ./decades_exec <PATH_TO_INPUTS>/x_to_y_graph.txt
        
  or
        
        ./decades_exec <PATH_TO_INPUTS>/y_to_x_graph.txt

## Interpreting The Results

If you compiled with "n" (native) or "db" (decades base) mode, then you will see output similar to the following (the graph information will be different depending on which dataset you decide to use):

        graph: ../../data/youtube-groupmemberships/y_to_x_graph.txt
        edges: 293360
        x_graph_nodes: 30087
        y_graph_nodes: 94238

        Running kernel
        Elapsed time: 3.65026s
        Finished hash: 66399082.000
        
This output highlights how many nodes are in each of the graph partitions (x and y), how long the kernel takes to run, and the hash (used to verify that the program is running correctly). Note: you should see the same hash for different DEC++ variants if they are run on the same input (i.e. Youtube y-to-x projection).

-----

If you compiled with "di" (decades decoupled implicit) mode, then you will see output similar to the following (with dataset differences in mind):

        graph: ../../data/youtube-groupmemberships/y_to_x_graph.txt
        edges: 293360
        x_graph_nodes: 30087
        y_graph_nodes: 94238
        
        Running kernel
        Elapsed time: 119.813s
        finished hash: 66399082.000
        
        
        -----
        decoupled runtime information:
        -----
        total predicate swaps: 0
        
        -----
        total stores: 66399082
          stores i32    : 66399082
          stores i64    : 0
          stores ptr    : 0
          stores float  : 0
          stores double : 0

        -----
        total loads: 133121616
          loads i32    : 133121613
          loads i64    : 1
          loads ptr    : 2
          loads float  : 0
          loads double : 0
        
        -----
        total opt. loads: 66399082 (33.28%)
          opt. loads i32    : 66399082 (33.28%)
          opt. loads i64    : 0 (0.00%)
          opt. loads ptr    : 0 (0.00%)
          opt. loads float  : 0 (0.00%)
          opt. loads double : 0 (0.00%)

You will see the same graph outputs from before, but you will also see decoupling information, including how many stores, loads, and optimized loads (terminal loads) took place, and the data types that these memory accesses operated on.

-----

If you compiled with "b" (biscuit) mode, then you will see output similar to the following (with dataset differences in mind):

        graph: ../../data/youtube-groupmemberships/y_to_x_graph.txt
        edges: 293360
        x_graph_nodes: 30087
        y_graph_nodes: 94238

        Running kernel
        Elapsed time: 4.23129s
        Finished hash: 66399082.000
        
        ------
        Bit Serial Stats:
        -
        Total # of items sent to bit serial: 66399082
        Sent in N batches: 81625
        Average size of batch: 813.47
        Max size of batch: 1024
        Min size of batch: 1
        Total amount of time compute spends waiting: 3.46
        Average amount of time compute spends waiting: 0.037
        Total amount of time spent on memcpy: 0.04
        ------

You will see the same graph outputs from before, but you will also see biscuit information, include how many computations were sent to the bit-serial processor, how many batches of computation were sent, the average size of these batches, and the smallest and largest batch sizes. You will also see the total and average amount of time that the computation kernel spends waiting for bit-serial batch computation, as well as the total amount of time that biscuit spends transferring data from the computation kernel to its scratchpad.
