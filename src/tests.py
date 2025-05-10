import networkx as nx
import os
import json

from .profiling import profile

def run(workload, tests, test_name):
    for name, path, fmt in workload:
        print("================================================")
        print("================================================")
        print("")
        print(f"Processing: {name}")
        graph = _load_graph(path, fmt)

        if not nx.is_connected(graph):
            largest_cc = max(nx.connected_components(graph), key=len)
            graph = graph.subgraph(largest_cc).copy()
        
        results = profile(graph, tests)
        _save_results(results, name, test_name)
        print(f"Results saved for: {name}")

def _save_results(results, graph_name, test_name, output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{graph_name}_{test_name}_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=4)

def _load_graph(path: str, fmt: str = "edgelist"):
    """
    Loads a graph from a file. Supports 'edgelist', 'gml', 'graphml'.
    """
    if fmt == "edgelist":
        return nx.read_edgelist(path, nodetype=int)
    elif fmt == "gml":
        return nx.read_gml(path, label="id")
    elif fmt == "graphml":
        return nx.read_graphml(path)
    else:
        raise ValueError(f"Unsupported format: {fmt}")