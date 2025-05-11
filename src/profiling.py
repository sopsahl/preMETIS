import networkx as nx
import pymetis
import time
from sksparse.cholmod import cholesky
from scipy.sparse import csr_matrix


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
    print(f'METIS done. Process took {avg_runtime} seconds to run.')
    
    print("Estimating fill-in...")
    ordering = test_graph.get_ordering(ordering, idx_mapping)
    fill_in = _estimate_fill_in_cholesky(graph, ordering)
    print(f'Fill-in done. {fill_in} fill-ins required.')

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


def _estimate_fill_in(graph: nx.Graph, elimination_order: list):
    g = graph.copy()
    fill_in = 0
    for node in elimination_order:
        if node not in g:
            continue
        neighbors = list(g.neighbors(node))
        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                if not g.has_edge(neighbors[i], neighbors[j]):
                    g.add_edge(neighbors[i], neighbors[j])
                    fill_in += 1
        g.remove_node(node)
    return fill_in

def _estimate_fill_in_cholesky(graph: nx.Graph, elimination_order: list):

    adj_matrix = nx.adjacency_matrix(graph)

    A_perm = adj_matrix[elimination_order, :][:, elimination_order]

    factor = cholesky(A_perm, beta=0) 
    L = factor.L()

    return L.nnz - adj_matrix.nnz


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
