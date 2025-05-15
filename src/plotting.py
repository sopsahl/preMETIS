import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os
import json
import glob
import re


def load_results(path="results"):
    raw_results = _load_all_results(path)
    flat_results = [_flatten_result(res) for res in raw_results]
    df = pd.DataFrame(flat_results)
    return df


def plot_runtime_vs_reductions_per_graph(results, graphs, tests):
    num_graphs = len(graphs)
    fig, axes = plt.subplots(nrows=1, ncols=num_graphs, figsize=(10 * num_graphs, 6), sharey=False)

    if num_graphs == 1:
        axes = [axes]  # Make it iterable

    for ax1, graph in zip(axes, graphs):
        graph_df = results[results['graph'] == graph].copy()
        graph_df['test'] = pd.Categorical(graph_df['test'], categories=tests, ordered=True)

        # Expand runtime values
        expanded = []
        for _, row in graph_df.iterrows():
            for rt in row["METIS_runtimes"]:
                expanded.append({
                    'test': row['test'],
                    'runtime': rt,
                    'reductions': row['Total_Reductions']
                })
        runtime_df = pd.DataFrame(expanded)
        runtime_df['test'] = pd.Categorical(runtime_df['test'], categories=tests, ordered=True)

        # Plot runtime as boxplot + stripplot
        sns.boxplot(data=runtime_df, x='test', y='runtime', ax=ax1, color='lightblue')
        sns.stripplot(data=runtime_df, x='test', y='runtime', ax=ax1, color='black', size=3, jitter=True)
        ax1.set_ylabel("Runtime (s)")
        ax1.set_xlabel("Preprocessing Method")
        ax1.set_title(f"{graph}")

        # Twin axis for reductions
        ax2 = ax1.twinx()
        red_means = graph_df.set_index('test').loc[tests]['Total_Reductions']
        ax2.plot(tests, red_means.values, color='gray', marker='o', linewidth=2, label='Total Reductions')
        ax2.set_ylabel("Total Reductions", color='gray')
        ax2.tick_params(axis='y', labelcolor='gray')

    fig.suptitle("METIS Runtime Distribution and Total Reductions", fontsize=16)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to include title
    plt.show()

def plot_operation_flamegraph(df, tests, graphs):
    # Filter the dataframe for the preMETIS tests
    filtered_df = df[df['test'].isin(tests)]

    operation_cols = [col for col in filtered_df.columns if col.startswith("Operation_")]

    # Melt operation components
    melt_df = filtered_df.melt(
        id_vars=['test', 'graph', 'Total_Operations'],  # Include 'graph' as an identifier
        value_vars=operation_cols,
        var_name='component',
        value_name='count'
    )

    # Clean component names
    melt_df['component'] = melt_df['component'].str.replace('Operation_', '').str.replace('_', ' ').str.title()

    # Create subplots with 3 columns (one for each graph)
    fig, axes = plt.subplots(1, 3, figsize=(20, 10), sharey=True)

    # Loop over each graph and create a plot in the corresponding axis
    for i, graph in enumerate(graphs):
        # Filter data for the current graph
        graph_df = melt_df[melt_df['graph'] == graph]

        # Pivot data to stacked format for the current graph
        pivot_df = graph_df.pivot_table(index='test', columns='component', values='count', aggfunc='sum', fill_value=0)

        # Plot the data for the current graph
        pivot_df.plot(
            kind='bar',
            stacked=True,
            ax=axes[i],
            colormap='Set2'
        )
        axes[i].legend(title="Reduction")

        # Set titles and labels for each plot
        axes[i].set_title(f"Operation Count ({graph})")
        axes[i].set_ylabel("Operation Count")
        axes[i].set_xlabel("Preprocessing Method")
        axes[i].tick_params(axis='x', rotation=45)

    # Adjust layout to prevent overlap
    plt.tight_layout()
    plt.show()


def plot_reduction_flamegraph(df, tests, graphs):
    # Filter the dataframe for the selected tests
    filtered_df = df[df['test'].isin(tests)]

    reduction_cols = [col for col in filtered_df.columns if col.startswith("Reduction_")]

    # Melt reduction components
    melt_df = filtered_df.melt(
        id_vars=['test', 'graph', 'Total_Reductions'],  # Include 'graph' as an identifier
        value_vars=reduction_cols,
        var_name='component',
        value_name='count'
    )

    # Clean component names
    melt_df['component'] = melt_df['component'].str.replace('Reduction_', '').str.replace('_', ' ').str.title()

    # Create subplots with 3 columns (one for each graph)
    fig, axes = plt.subplots(1, 3, figsize=(20, 10), sharey=True)

    # Loop over each graph and create a plot in the corresponding axis
    for i, graph in enumerate(graphs):
        # Filter data for the current graph
        graph_df = melt_df[melt_df['graph'] == graph]

        # Pivot data to stacked format for the current graph
        pivot_df = graph_df.pivot_table(index='test', columns='component', values='count', aggfunc='sum', fill_value=0)

        # Plot the data for the current graph
        pivot_df.plot(
            kind='bar',
            stacked=True,
            ax=axes[i],
            colormap='Set2'
        )
        axes[i].legend(title="Reduction")

        # Set titles and labels for each plot
        axes[i].set_title(f"Reduction Count ({graph})")
        axes[i].set_ylabel("Reduction Count")
        axes[i].set_xlabel("Preprocessing Method")
        axes[i].tick_params(axis='x', rotation=45)

    # Adjust layout
    plt.tight_layout()
    plt.show()


def plot_fillin(df, tests, graphs):
    # Filter relevant tests
    filtered_df = df[df['test'].isin(['METIS'] + tests)]

    # Pivot: rows = (graph, test), columns = fill-in
    pivot_df = filtered_df.pivot(index='graph', columns='test', values='Nonzero_Fill_in')

    # Normalize to METIS
    norm_df = pivot_df.div(pivot_df['METIS'], axis=0).reset_index()

    # Melt to long-form for seaborn
    melt_df = norm_df.melt(id_vars='graph', value_vars=tests, var_name='test', value_name='normalized_fillin')

    # Plot using seaborn
    plt.figure(figsize=(10, 6))
    sns.stripplot(
        data=melt_df,
        x='graph',
        y='normalized_fillin',
        hue='test',
        jitter=False,
        dodge=True,
        size=8,
        palette='Set2'
    )

    plt.axhline(1.0, color='gray', linestyle='--', linewidth=1)
    plt.title("Normalized Fill-In in Cholesky Factorization")
    plt.ylabel("Normalized Non-Zero Fill-In")
    plt.xlabel("Graph")
    plt.legend(title="Test", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()


def _flatten_result(data):
    flattened = {
        "graph": data["graph"],
        "test": data["test"],
        "METIS_Runtime": data["METIS Runtime"],
        "METIS_Runtime_Avg": sum(data["METIS runtimes"]) / len(data["METIS runtimes"]),
        "METIS_Runtime_Min": min(data["METIS runtimes"]),
        "METIS_Runtime_Max": max(data["METIS runtimes"]),
        "Nonzero_Fill_in": data["Nonzero Fill-in"],
        "Total_Reductions": data["Total Reductions"],
        "Original_Nodes": data["Original Nodes"],
        "Original_NNZ": data["Original NNZ"],
        "Total_Operations": data["Total Operations"],
        "METIS_runtimes": data.get("METIS runtimes", [])  # <--- this line added
    }
    for k, v in data["Reductions"].items():
        flattened[f"Reduction_{k}"] = v
    for k, v in data["Operations"].items():
        flattened[f"Operation_{k}"] = v
    return flattened

def _parse_filename(filepath):
    filename = os.path.basename(filepath)
    match = re.match(r"(.+?)_(.+?)_results\.json", filename)
    if match:
        return match.group(1), match.group(2)
    else:
        raise ValueError(f"Filename {filename} does not match expected pattern.")

def _load_all_results(path="results"):
    result_files = glob.glob(os.path.join(path, "*_results.json"))
    results = []
    for file in result_files:
        with open(file, 'r') as f:
            data = json.load(f)
            graph_name, test_name = _parse_filename(file)
            data["graph"] = graph_name
            data["test"] = test_name
            results.append(data)
    return results
