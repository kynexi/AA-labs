import matplotlib.pyplot as plt

def plot_results(values, dfs_times, bfs_times):
    plt.figure()
    plt.plot(values, dfs_times, marker='o')
    plt.xlabel('Number of Nodes (n)')
    plt.ylabel('Execution Time (seconds)')
    plt.title('DFS Empirical Analysis')
    plt.grid()
    plt.show()

    plt.figure()
    plt.plot(values, bfs_times, marker='o')
    plt.xlabel('Number of Nodes (n)')
    plt.ylabel('Execution Time (seconds)')
    plt.title('BFS Empirical Analysis')
    plt.grid()
    plt.show()

    plt.figure()
    plt.plot(values, dfs_times, marker='o', label='DFS')
    plt.plot(values, bfs_times, marker='o', label='BFS')
    plt.xlabel('Number of Nodes (n)')
    plt.ylabel('Execution Time (seconds)')
    plt.title('DFS vs BFS Empirical Analysis')
    plt.legend()
    plt.grid()
    plt.show()