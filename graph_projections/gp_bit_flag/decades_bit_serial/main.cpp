#include "DECADES/DECADES.h"
#include "DECADES/BitSerial/BitSerial.h"
#include "../../common/common.h"

typedef char weight_type;

void preprocess(bgraph g, weight_type *output) { }

__attribute__((noinline))
void _kernel_biscuit(int bid) {
  while(true) {
    while (BIs[bid].compute_task <= BIs[bid].supply_task) {}

    int curr_message = BIs[bid].message_from_compute;

    if (curr_message == MESSAGE_DIE) {
      return;
    }
 
    if (curr_message == MESSAGE_READY) { //biscuit is at work
      char * values = (char *) BMs[bid].local_memory;
 
      //load values into biscuit local memory
      decades_ist_load_char_values(0, values);

      //increment values
      for (int i = 0; i < BIs[bid].scratchpad_size; i++) {
        values[i] = 1;
      }

      //store values back to addresses in scratchpad_data;          
      decades_ist_store_char_values(0, values);
 
      BIs[bid].supply_task++;
    }
  }
}

__attribute__((noinline))
void _kernel_(bgraph g, weight_type *output, int tid, int num_threads) {
  int total = 0;

  IS_compute_context local_ist_context;

  for (unsigned int i = 0; i < g.x_nodes; i++) {   
    for (unsigned int e1 = g.node_array[i]; e1 < g.node_array[i+1] - 1; e1++) {
      int y_node_1 = g.edge_array[e1];
      ulong cached_second = i_j_to_k_get_second(g.y_nodes, y_node_1);
      for (unsigned int e2 = e1+1; e2 < g.node_array[i+1]; e2++) {
        
        int y_node_2 = g.edge_array[e2];

	ulong k = i_j_to_k_cached(y_node_1, y_node_2, g.y_nodes, g.first_val, cached_second);

	decades_ist_flag_set_char(0, &local_ist_context, output, k);
      }
    }
  }
  decades_ist_flush(0, &local_ist_context); 
  decades_ist_finalize(0);
}

#include "../../common/main_decades_biscuit.h"
