import networkx as nx
import pymetis
import time
from copy import deepcopy

from .preMETIS import preMETIS

def run(graph:nx.Graph, tests:list[preMETIS]):
    results = {}
    for test in tests:
        print("***********************************************************")
        
        print(f"Running {test} test:")
        print("Transforming the graph...")
        test = test(graph)
        print(f"\tTransformation done. {test.total_reductions()} total reductions made.")
        
        print("Running METIS...")
        runtime, ordering, idx_mapping = _run_METIS(test.graph)
        print(f'METIS done. Process took {runtime} seconds to run.')
        
        print("Estimating fill-in...")
        ordering = test.get_ordering(ordering, idx_mapping)
        fill_in = _estimate_fill_in(graph, ordering)
        print(f'Fill-in done. {fill_in} fill-ins required.')
        
        results[str(test)] = {
            "METIS Runtime" : runtime,
            "Nonzero Fill-in" : fill_in,
            "Reductions" : test.reductions,
            "Total Reductions" : test.total_reductions(),
            "Original Nodes": test.original_graph.number_of_nodes(),
            "Operations" : test.operations,
            "Total Operations" : test.total_operations(),
        }

        print(f"All testing for {test} done.")
        print("***********************************************************")
    
    return results

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

def _run_METIS(graph:nx.Graph):
    adj_list, idx_mapping = _graph_to_adj_list(graph)

    start = time.time()
    _, ordering = pymetis.nested_dissection(adj_list)
    runtime = time.time() - start

    return runtime, ordering, idx_mapping

def _graph_to_adj_list(g: nx.Graph):
    node_mapping, idx_mapping = {}, {}
    adj_list = []
    for idx, node in enumerate(g.nodes()):
        node_mapping[node] = idx
        idx_mapping[idx] = node

    adj_list = [[node_mapping[nbr] for nbr in g.neighbors(idx_mapping[idx])] for idx in range(g.number_of_nodes())]
   
    return adj_list, idx_mapping
