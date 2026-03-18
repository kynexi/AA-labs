from analysis import run_experiment
from plot import plot_results


def print_results(values, dfs_times, bfs_times):
    print("\nDFS Results:")
    print("N\tTime (s)")
    for n, t in zip(values, dfs_times):
        print(f"{n}\t{t:.6f}")

    print("\nBFS Results:")
    print("N\tTime (s)")
    for n, t in zip(values, bfs_times):
        print(f"{n}\t{t:.6f}")


if __name__ == "__main__":
    values, dfs_times, bfs_times = run_experiment()

    print_results(values, dfs_times, bfs_times)

    plot_results(values, dfs_times, bfs_times)