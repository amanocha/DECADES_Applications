#include "stdio.h"
#include "assert.h"
#include "DECADES/DECADES.h"

#define SIZE 1024

__attribute__((noinline))
void _kernel_(int *a, int *b, int *c, int tid, int num_threads) {

  for (int i = tid; i < SIZE; i+=num_threads) {
    c[i] = a[i] + b[i];
  }
  printf("Hello from thread ID %d!\n", tid);
}

int main() {

  int a[SIZE], b[SIZE], c[SIZE];

  for (int i = 0; i < SIZE; i++) {
    a[i] = b[i] = i;
  }

  _kernel_(a,b,c,0,1);

  for (int i = 0; i < SIZE; i++) {
    assert(c[i] == i * 2);
  }

  printf("Done!\n");
  return 0;
}
