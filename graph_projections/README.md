## Graph Projections 

# Gathering the Data
1. Select a dataset from http://konect.uni-koblenz.de/downloads/ (see below for the ones we used).
2. Run the following:

        mkdir data

# get datasets and then run utiles/complete_flow.sh on the out.* file (FROM THE 'utils' DIRECTORY!)
# this will give you x_to_y_graph.txt and y_to_x_graph.txt.
# DECADES kernels can run on either.

# youtube dataset needs a second line comment showing number of edges, x_nodes and y_nodes

# Example Datasets
- Small: http://konect.uni-koblenz.de/downloads/tsv/brunson_revolution.tar.bz2
- Also pretty small (probably a good one to simulate on): http://konect.uni-koblenz.de/downloads/tsv/moreno_crime.tar.bz2
- Medium (simulate on this one if you feel brave!): http://konect.uni-koblenz.de/downloads/tsv/opsahl-collaboration.tar.bz2
- Pretty big: http://konect.uni-koblenz.de/downloads/tsv/youtube-groupmemberships.tar.bz2
- Slightly bigger: http://konect.uni-koblenz.de/downloads/tsv/dbpedia-writer.tar.bz2
