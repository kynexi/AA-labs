import time
import matplotlib.pyplot as plt
import numpy as np

from graph_generator import (
    generate_sparse_graph_adjacency,
    generate_dense_graph_adjacency,
    generate_sparse_graph_matrix,
    generate_dense_graph_matrix,
)
from dijkstra import dijkstra
from floyd_warshall import floyd_warshall


NODE_SIZES = [10, 50, 100, 200, 500]
FW_NODE_SIZES = [10, 50, 100, 200, 500]   
RUNS = 5


def average_time(func, *args):
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        func(*args)
        end = time.perf_counter()
        times.append(end - start)
    return (sum(times) / len(times)) * 1000


def run_analysis():
    dijkstra_sparse_times = []
    dijkstra_dense_times  = []
    floyd_sparse_times    = []
    floyd_dense_times     = []

    print(f"{'Nodes':<8} {'D-Sparse(ms)':<16} {'D-Dense(ms)':<16} "
          f"{'FW-Sparse(ms)':<18} {'FW-Dense(ms)'}")
    print("-" * 75)

    for n in NODE_SIZES:
        run_floyd = n in FW_NODE_SIZES

        sparse_adj = generate_sparse_graph_adjacency(n)
        dense_adj  = generate_dense_graph_adjacency(n)

        t_d_sparse = average_time(dijkstra, sparse_adj, 0)
        t_d_dense  = average_time(dijkstra, dense_adj,  0)

        dijkstra_sparse_times.append(t_d_sparse)
        dijkstra_dense_times.append(t_d_dense)

        if run_floyd:
            sparse_mat = generate_sparse_graph_matrix(n)
            dense_mat  = generate_dense_graph_matrix(n)
            t_fw_sparse = average_time(floyd_warshall, sparse_mat)
            t_fw_dense  = average_time(floyd_warshall, dense_mat)
            floyd_sparse_times.append(t_fw_sparse)
            floyd_dense_times.append(t_fw_dense)
            fw_sparse_str = f"{t_fw_sparse:<18.4f}"
            fw_dense_str  = f"{t_fw_dense:.4f}"
        else:
            fw_sparse_str = f"{'skipped':<18}"
            fw_dense_str  = "skipped"

        print(f"{n:<8} {t_d_sparse:<16.4f} {t_d_dense:<16.4f} "
              f"{fw_sparse_str}{fw_dense_str}")

    return (dijkstra_sparse_times, dijkstra_dense_times,
            floyd_sparse_times,    floyd_dense_times)


def plot_results(dijkstra_sparse, dijkstra_dense, floyd_sparse, floyd_dense):

    all_values = (
        dijkstra_sparse +
        dijkstra_dense  +
        floyd_sparse    +
        floyd_dense
    )
    y_max = max(all_values) * 1.1  

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Dijkstra vs Floyd-Warshall: Execution Time Analysis", fontsize=14)

    axes[0].plot(NODE_SIZES, dijkstra_sparse, marker='o',
                 label='Sparse', color='steelblue', linewidth=2)
    axes[0].plot(NODE_SIZES, dijkstra_dense,  marker='s',
                 label='Dense',  color='tomato',    linewidth=2)
    axes[0].set_title("Dijkstra's Algorithm (single-source)")
    axes[0].set_xlabel("Number of Nodes (V)")
    axes[0].set_ylabel("Average Execution Time (ms)")
    axes[0].set_ylim(0, y_max)
    axes[0].legend()
    axes[0].grid(True, linestyle='--', alpha=0.6)

    axes[1].plot(FW_NODE_SIZES, floyd_sparse, marker='o',
                 label='Sparse', color='steelblue', linewidth=2)
    axes[1].plot(FW_NODE_SIZES, floyd_dense,  marker='s',
                 label='Dense',  color='tomato',    linewidth=2)
    axes[1].set_title("Floyd-Warshall Algorithm (all-pairs)")
    axes[1].set_xlabel("Number of Nodes (V)")
    axes[1].set_ylabel("Average Execution Time (ms)")
    axes[1].set_ylim(0, y_max)
    axes[1].legend()
    axes[1].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.savefig("analysis_results.png", dpi=150, bbox_inches='tight')
    plt.show()
    print("\nGraph saved as analysis_results.png")