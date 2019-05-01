#include <stdio.h>
#include "DECADES/DECADES.h"

#define SIZE 1024*1024*2

void _kernel_(int* a, int* b, int* c, int size, int tid, int num_tiles) {
   int chunk_size = size / num_tiles;
   int begin_chunk = chunk_size * tid;
   int end_chunk = begin_chunk + chunk_size;

  for (int i = begin_chunk; i < end_chunk; i++) {
    c[i] = a[i] + b[i];
  }
}

int main() {
  printf("Performing vector addition!\n");

  int* a = (int*) malloc(SIZE*sizeof(int));
  int* b = (int*) malloc(SIZE*sizeof(int));
  int* c = (int*) malloc(SIZE*sizeof(int));
  
  _kernel_(a, b, c, SIZE, DECADES_TILE_ID, DECADES_NUM_TILES);
  
  printf("Success!\n");

  return 0;
}
