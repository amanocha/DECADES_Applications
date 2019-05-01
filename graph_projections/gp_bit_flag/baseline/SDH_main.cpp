/*Author: Jesun Firoz@PNNL*/

#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <random>
#include <chrono>
#include <algorithm>
#include <unordered_map>
#include <omp.h>
#include <assert.h>
#include "compressed.hpp"
#include <set>
// Tyler, enable this to run parallel
#define RUN_WITH_OPENMP 1
#define FILTERED_OP 1
#define CHUNK 5000
//#define PRINT_DEBUG 1

std::string edgelistFile = "";
std::size_t seed = 0; 
std::size_t bucketSize = 1;

typedef std::pair<uint64_t, uint64_t> edgeTypes;

auto hashFunction = [](const edgeTypes& edgeT) {
  return ((std::hash<uint64_t>{} (edgeT.first)
	   ^ (std::hash<uint64_t>{} (edgeT.second) << 1)) >> 1);
};

auto equalComparator = [] (const edgeTypes &l,const edgeTypes &r)  {
  return (l.first == r.first && l.second == r.second);
};

typedef std::unordered_map<edgeTypes, edgeTypes, decltype(hashFunction), decltype(equalComparator)> complementaryEdgeInfoType;

typedef std::unordered_map<edgeTypes, int, decltype(hashFunction), decltype(equalComparator)> complementaryEdgeWeightType;



void readEdgelist(std::string _edgelistFile, uint64_t* nEdges, uint64_t* nVertices,
		  compressed_sparse& csr) {
  std::string line;
  std::ifstream inputFile;
  inputFile.open(_edgelistFile.c_str(), std::ifstream::in);

  uint64_t source, destination; 
  double weight;

  std::random_device rd;  
  std::mt19937 gen(rd());
  std::uniform_real_distribution<> dis(0.0, 1.0);

  uint64_t max_vertex=0;
  std::vector<std::tuple<uint64_t,uint64_t,double>> line_vector;  
  //  for (uint64_t i = 0; i < nEdges; i++) {
  while (!inputFile.eof()) {
    std::getline(inputFile, line);
    //std::getline(inputFile, line);
    std::istringstream lineStream(line);
    lineStream >> source >> destination;
    /*For now, generating random weight*/
    weight = dis(gen);
    
#ifdef PRINT_DEBUG
    std::cout << source << " " << destination << " " << weight 
	      << std::endl;
#endif
    line_vector.push_back(std::make_tuple(source,destination,weight));
    if (destination>max_vertex || source>max_vertex)
      max_vertex=std::max(destination, source);
    
    (*nEdges)++;
  }
  *nVertices=max_vertex+1;
  csr.nVertices=*nVertices;
  csr.nEdges=*nEdges;
  csr.ptrs.resize((*nVertices)+1);
  std::cout << "Num_vertices: " << *nVertices << "; Num_edges: " << *nEdges << std::endl;
  //assert(false);
  
  for(auto& line_tuple: line_vector) {
    uint64_t source=std::get<0>(line_tuple);
    uint64_t destination=std::get<1>(line_tuple);
    double weight=std::get<2>(line_tuple);
    csr.push_back(source, destination, weight); 
  }
}

int main(int argc, char* argv[]) {
  uint64_t nVertices=0;// = *(new uint64_t(0));
  uint64_t nEdges=0;//=*(new uint64_t(0));
  uint64_t depth=0;//=*(new uint64_t(0));
  std::string samplingType;  
  int simple = 0;

  if (argc != 2) {
    printf("ERROR: Please provide an edge list file.\n");
    return 1;
  }

  edgelistFile = std::string(argv[1]);

  // edgelist
  std::cout << "Constructing CSR" << std::endl;
  compressed_sparse csr(nVertices, nEdges);
  readEdgelist(edgelistFile, &nEdges, &nVertices, csr);
  csr.accumulate();
  std::cout << "Construction of CSR done" << std::endl;

  std::vector<complementaryEdgeWeightType> perVertexEdgeHashMap(nVertices, complementaryEdgeWeightType(bucketSize, hashFunction, equalComparator));
  
#ifdef RUN_WITH_OPENMP
  /*create a set of locks for each vertex*/
  std::vector<omp_lock_t> vertexLocks(nVertices);
  for (uint64_t i = 0; i < nVertices; i ++) {
    omp_init_lock(&(vertexLocks[i]));
  }
#endif

  std::cout << "Started computing graph projection..." << std::endl;
  auto start = std::chrono::system_clock::now();

  int inserts = 0;
  int lookups = 0;
#ifdef RUN_WITH_OPENMP
   int nthreads, tid;
#pragma omp parallel private(nthreads, tid)
   {
     /* Obtain thread number */
     tid = omp_get_thread_num();
  
     /* Only master thread does this */
     if (tid == 0) {
       nthreads = omp_get_num_threads();
       std::cout << "Number of threads: " << nthreads << std::endl;
     }
#pragma omp for  // shared(perVertexEdgeHashMap, vertexLocks) // schedule (dynamic, CHUNK)
#endif
    /*Bi-partite case*/
    for (uint64_t i = 0; i < nVertices; i++) {
      /* For bi-partite graph, we can directly create links between siblings */
      for (uint64_t e_1 = csr.ptrs[i]; e_1 < csr.ptrs[i + 1] - 1; e_1++) {
	for (uint64_t e_2 = e_1; e_2 < csr.ptrs[i + 1]; 
	     e_2++) {
            auto complementaryEdge = std::make_pair(csr.indices[e_1].first, 
					      csr.indices[e_2].first);
	    /*weight calculation is done as in the ref. Scala code*/
            auto edgeWeight = 1;
	    //auto edgeWeight = csr.indices[e_1].second / ((csr.indices[e_1].second + csr.indices[e_2].second) * 2);
	    auto newEdgeSource = csr.indices[e_1].first;
#ifdef RUN_WITH_OPENMP
	    omp_set_lock(&(vertexLocks[newEdgeSource]));
#endif
	    /*Check whether the current edge already exists in the hashmap.*/
            auto edgeExists = perVertexEdgeHashMap[newEdgeSource].find(complementaryEdge);
	    /*If not, insert the new edge along with the weight*/
	    if (edgeExists == perVertexEdgeHashMap[newEdgeSource].end()) {
	      perVertexEdgeHashMap[newEdgeSource].insert({complementaryEdge, edgeWeight});
	    } else { /*Otherwise update weight.*/
	      auto currentWeightPair = perVertexEdgeHashMap[newEdgeSource].find(complementaryEdge);
	      currentWeightPair->second = edgeWeight;
	    }
#ifdef RUN_WITH_OPENMP
	    omp_unset_lock(&(vertexLocks[newEdgeSource]));
#endif
	}
      }
    }
#ifdef RUN_WITH_OPENMP
   }
#endif

  auto end = std::chrono::system_clock::now();
  std::chrono::duration<double> elapsed_seconds = end-start;
  std::cout << "Elapsed time: " << elapsed_seconds.count() << "s\n";

  uint64_t totalEdges = 0;
  for (uint64_t newEdgeSource = 0; newEdgeSource < nVertices; newEdgeSource++) {
    for (std::pair<edgeTypes, double> edge : perVertexEdgeHashMap[newEdgeSource]) {
#ifdef PRINT_DEBUG
       std::cout << edge.first.first <<  " " << edge.first.second << " " 
		 << edge.second << std::endl;
#endif      
      totalEdges += 1;
    }
  }
  std::cout << "Total newly generated edges: " << totalEdges << std::endl;
}
