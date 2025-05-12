# preMETIS

This repository stores the implementation of a preprocessing method proposed by [Ost et al. \[1\]](https://arxiv.org/pdf/2004.11315). The method offers an improvement over METIS on the task of nested dissection, a graph partitioning approach to the minimum fill-in problem. 

Implentation can be found in `src/`, and all outputs can be seen in `results/`.


This was implemented by Simon Opsahl (sopsahl@mit.edu) for MIT's Sp2025 offering of 18.335: Introduction to Numerical Methods.

## Using the Algorithm
1. Install the required dependencies: 
```bash
conda env create
conda activate preMETIS
```
2. Run the profiling with your selected network data. The command is structured as follows:

```bash
python run.py  --tests <test_names>
```



`<test_names>` is a set of tests to run. If all, use `all`.

Example:

```bash
python run.py  --tests SITDTr SITP12 
```

This command will run the `SITDTr` and `SITP12` tests on the `road` workload.

3. Visualize the results by running the `visulization.ipynb` notebook.

## Graph Data:

The graph datasets can be automatically downloaded from the [SNAP](http://snap.stanford.edu/data) website [2]. When running the profiling, the code will download the required datasets if they are not already available locally. The datasets include road networks like roadNet-TX, roadNet-CA, and roadNet-PA.

## Directory Structure
`src/`: Contains the implementation of the preMETIS algorithm. Also contains helper scripts for graph manipulation, profiling, and result handling.

`results/`: Stores the outputs and profiling results.

`data/`: Stores the downloaded test graphs.

`run.py`: The main script for running the tests.

`visualization.ipynb` : A notebook for visualizing generated results.

## References
[1] Ost, L., Schulz, C., & Strash, D. (2020). Engineering Data Reduction for Nested Dissection (No.
arXiv:2004.11315). arXiv. https://doi.org/10.48550/arXiv.2004.11315

[2] J. Leskovec and A. Krevl. SNAP Datasets: Stanford large network dataset collection.
http://snap.stanford.edu/data, 2014.