
x=$(dirname $1)

bash add_random_weights.sh $1 > $x/x_to_y_graph_tmp.txt
bash create_y_graph.sh $x/x_to_y_graph_tmp.txt > $x/y_to_x_graph_tmp.txt
bash get_zero_index.sh $x/x_to_y_graph_tmp.txt > $x/x_to_y_graph.txt
bash get_zero_index.sh $x/y_to_x_graph_tmp.txt > $x/y_to_x_graph.txt
rm $x/x_to_y_graph_tmp.txt $x/y_to_x_graph_tmp.txt
