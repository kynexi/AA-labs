from analysis import run_analysis, plot_results


if __name__ == "__main__":
    print("=" * 75)
    print()

    dijkstra_sparse, dijkstra_dense, floyd_sparse, floyd_dense = run_analysis()

    plot_results(dijkstra_sparse, dijkstra_dense, floyd_sparse, floyd_dense)