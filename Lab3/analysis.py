import time
import statistics

from graph_utils import generate_graph
from dfs import dfs
from bfs import bfs


def measure_time(func, graph, start):
    start_time = time.perf_counter()
    func(graph, start)
    end_time = time.perf_counter()
    return end_time - start_time


def run_experiment():
    values = [10, 50, 100, 200, 300, 400, 500]
    repetitions = 5

    dfs_times = []
    bfs_times = []

    for n in values:
        dfs_runs = []
        bfs_runs = []

        for _ in range(repetitions):
            graph = generate_graph(n)
            start_node = 0

            dfs_runs.append(measure_time(dfs, graph, start_node))
            bfs_runs.append(measure_time(bfs, graph, start_node))

        dfs_times.append(statistics.mean(dfs_runs))
        bfs_times.append(statistics.mean(bfs_runs))

    return values, dfs_times, bfs_times