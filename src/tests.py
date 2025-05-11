import networkx as nx
import os
import json
import gzip
import shutil
import urllib.request

from .profiling import profile

SNAP_URL = 'https://snap.stanford.edu/data/'
OUTPUT_DIR = 'results'
DATA_DIR = 'data'

def run(workload, tests):

    for name, filename in workload.items():
        print("================================================")
        print("================================================")
        print(f"Processing: {name}")
        file_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(file_path):
            _download_and_extract(SNAP_URL + filename + '.gz', file_path)
        graph = _load_graph(file_path)

        if not nx.is_connected(graph):
            largest_cc = max(nx.connected_components(graph), key=len)
            graph = graph.subgraph(largest_cc).copy()
            
        for test in tests:
            results = profile(graph, test)
            _save_results(results, name, test.__name__)
        print(f"All tests for {name} run")

def _save_results(results, graph_name, test_name):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{graph_name}_{test_name}_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=4)

def _load_graph(file_path):
    G = nx.Graph()
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue  # Skip comments
            u, v = map(int, line.strip().split())
            G.add_edge(u, v)
    return G

def _download_and_extract(url, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    gz_path = dest_path + '.gz'
    print(f"Downloading {url}...")
    urllib.request.urlretrieve(url, gz_path)
    print(f"Extracting {gz_path}...")
    with gzip.open(gz_path, 'rb') as f_in:
        with open(dest_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(gz_path)
    print(f"Saved to {dest_path}")