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

## Running Graph Projections

There are 2 variants:

Bit Flag (gp_bit_flag): a projection with a binary edge

Counter (gp_count): a projection that counts how many times the relation was seen

-----

Each variant contains a "baseline" directory. This is just a standard
version of the algorithm that can be compiled with g++.

$ g++ -O3 -std=c++11 main.cpp -o main

Each variant contains a "decades" directory. This is a standard
version of the algorithm that can be compiled with DEC++. Inlined and
decoupled variants should be correct.

Two variants (gp_bit*) contain experimental decades bit serial
operations. They can be compiled with DEC++ but decoupling is
not valid (only inlined)

To compile a DEC++ version, just do:

$ DEC++ main.cpp

-----

To get inputs read the README in inputs

-----

the pp_kernel is not a graph projection, but a preprocessing step that
might occur after a graph projection has occurred. It is an
elementwise MAX followed by a division and tanh activation.

-----

To run in decades:

./exec <PATH_TO_INPUTS>/x_to_y_graph.txt

Baselines do bi-direction projection so you need to graphs (probably
don't need to worry about this)

./exec <PATH_TO_INPUTS>/x_to_y_graph.txt <PATH_TO_INPUTS>/y_to_x_graph.txt
