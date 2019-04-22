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

There are 2 variants:

- Bit Flag (gp_bit_flag): a projection with a binary edge
- Counter (gp_count): a projection that counts how many times the relation was seen

-----

Each variant contains three directories:

- baseline: a standard version of the algorithm that can be compiled with g++ or DEC++ "n" (native) mode

        g++ -O3 -std=c++11 main.cpp -o main
        
or 

        DEC++ -m n main.cpp

- decades: a multithreaded parallel version of the algorithm that can be compiled with DEC++ "db" (decades base) or "di" decades decoupled implicity) modes and a set number of threads

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



