import networkx as nx
import pymetis
import time
from copy import deepcopy

from .preMETIS import preMETIS
from .tests import TESTS

def profile(graph, number_of_partitions):

    def graph_to_metis_format(g: nx.Graph):
        node_mapping = {node: i for i, node in enumerate(g.nodes())}
        adj_list = [[node_mapping[nbr] for nbr in g.neighbors(node)] for node in g.nodes()]
        return adj_list
    

    def estimate_fill_in(graph: nx.Graph, elimination_order: list):
        """Estimate fill-in edges created during elimination."""
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

    # Step 1: Original graph METIS
    original_graph = deepcopy(graph)
    original_adj = graph_to_metis_format(original_graph)

    start = time.time()
    _, original_ordering = pymetis.nested_dissection(graph_to_metis_format(original_graph))
    original_fill = estimate_fill_in(original_graph, original_ordering)
    original_runtime = time.time() - start

    # Estimate fill-in from natural elimination order
    original_fill = estimate_fill_in(original_graph, list(original_graph.nodes()))

    # Step 2: Reduced graph METIS
    reduced_instance = reducer(graph)
    reduced_instance.simplicial_reduction()
    reduced_instance.indistinguishable_reduction()
    reduced_instance.twin_reduction()
    reduced_instance.path_compression()
    reduced_instance.degree_2_elimination()
    reduced_instance.triangle_contraction()

    reduced_graph = reduced_instance.graph
    reduced_adj = graph_to_metis_format(reduced_graph)

    start = time.time()
    _, reduced_partition = pymetis.part_graph(k, adjacency=reduced_adj)
    reduced_runtime = time.time() - start

    reduced_fill = estimate_fill_in(reduced_graph, list(reduced_graph.nodes()))

    # Summary
    return {
        "original": {
            "runtime": original_runtime,
            "fill_in": original_fill,
            "nodes": len(original_graph),
            "edges": original_graph.number_of_edges()
        },
        "reduced": {
            "runtime": reduced_runtime,
            "fill_in": reduced_fill,
            "nodes": len(reduced_graph),
            "edges": reduced_graph.number_of_edges()
        },
        "reduction_summary": reduced_instance.summary()
    }

