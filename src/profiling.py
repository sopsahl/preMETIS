import networkx as nx
import pymetis
import time
from sksparse.cholmod import cholesky
import scipy.sparse as sp



from .preMETIS import preMETIS

N = 10

def profile(graph:nx.Graph, test:preMETIS):
    print("***********************************************************")
    
    print(f"Running {test.__name__} test:")
    print("Transforming the graph...")
    test_graph = test(graph)
    print(f"\tTransformation done. {test_graph.total_reductions()} total reductions made.")
    
    print("Running METIS...")
    avg_runtime, ordering, idx_mapping, runtimes= _run_METIS(test_graph.graph)
    print(f'\tMETIS done. Process took {avg_runtime} seconds to run.')
    
    print("Estimating fill-in...")
    print("\tGenerating true ordering ...")
    ordering = test_graph.get_ordering(ordering, idx_mapping)
    print("\tPerforming factorization ...")
    fill_in = _estimate_fill_in_cholesky(graph, ordering)
    print(f'\tFill-in done. {fill_in} fill-ins required.')

    print(f"All testing for {test_graph} done.")
    print("***********************************************************")
    
    return {
        "METIS Runtime" : avg_runtime,
        "METIS runtimes" : runtimes,
        "Nonzero Fill-in" : fill_in,
        "Reductions" : test_graph.reductions,
        "Total Reductions" : test_graph.total_reductions(),
        "Original Nodes": test_graph.total_nodes,
        "Original NNZ" : test_graph.total_edges,
        "Operations" : test_graph.operations,
        "Total Operations" : test_graph.total_operations(),
    }


def _estimate_fill_in_cholesky(graph: nx.Graph, elimination_order: list):
    laplacian = nx.laplacian_matrix(graph, nodelist=elimination_order)    
    laplacian += 1e-5 * sp.eye(laplacian.shape[0])  # Regularization
    
    # laplacian = laplacian.tocsc()

    factor = cholesky(laplacian, beta=0, ordering_method="natural") 
    L = factor.L()

    return L.nnz - laplacian.nnz


def _run_METIS(graph:nx.Graph):
    adj_list, idx_mapping = _graph_to_adj_list(graph)

    runtimes = []
    total_runtime = 0
    for _ in range(N):
        start = time.time()
        _, ordering = pymetis.nested_dissection(adj_list)
        iteration_runtime = time.time() - start
        runtimes.append(iteration_runtime)  # Store each iteration runtime
        total_runtime += iteration_runtime

    # Compute average runtime
    avg_runtime = total_runtime / N

    return avg_runtime, ordering, idx_mapping, runtimes

def _graph_to_adj_list(g: nx.Graph):
    node_mapping, idx_mapping = {}, {}

    for idx, node in enumerate(g.nodes()):
        node_mapping[node] = idx
        idx_mapping[idx] = node

    adj_list = [[node_mapping[nbr] for nbr in g.neighbors(idx_mapping[idx])] for idx in range(g.number_of_nodes())]
   
    return adj_list, idx_mapping
