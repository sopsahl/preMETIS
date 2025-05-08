# preMETIS

This repository stores the implementation of a preprocessing method proposed by [Ost et al. \[1\]](https://arxiv.org/pdf/2004.11315). The method offers an improvement over METIS on the task of nested dissection, a graph partitioning approach to the minimum fill-in problem. 

Implentation can be found in `algorithm/`, and all testing an outputs can be seen in `results/`.


This was implemented by Simon Opsahl (sopsahl@mit.edu) for MIT's Sp2025 offering of 18.335: Introduction to Numerical Methods.

## Using the Algorithm
1. Install the required dependencies: 
```bash
conda env create
conda activate preMETIS
```
2. Run the profiling with ...

## References
[1] Ost, L., Schulz, C., & Strash, D. (2020). Engineering Data Reduction for Nested Dissection (No.
arXiv:2004.11315). arXiv. https://doi.org/10.48550/arXiv.2004.11315