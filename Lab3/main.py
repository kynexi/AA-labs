from analysis import run_experiment
from plot import plot_results


if __name__ == "__main__":
    values, dfs_times, bfs_times = run_experiment()

    print("Nodes:", values)
    print("DFS times:", dfs_times)
    print("BFS times:", bfs_times)

    plot_results(values, dfs_times, bfs_times)