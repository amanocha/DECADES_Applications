# Hello World

This is a simple example to illustrate the doall parallelism in DEC++. This example is vector addition, the "Hello World" equivalent for multithreaded parallel programs. All of the code is in main.cpp.

## Doall Parallelism

To compile the program for simple doall parallelism, run the following:

        DEC++ -m db -t [num_threads] main.cpp
        
Then run:

        decades_base/decades_base

## Decoupling

To compile the program with doall parallelism and decoupling (although you likely won't see anything too crazy), run the following:

        DEC++ -m di -t [num_threads] main.cpp
        
Then run:

        decades_decoupled_implicit/decades_decoupled_implicit
