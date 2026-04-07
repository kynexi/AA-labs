import random


def generate_sparse_graph_adjacency(n):
    # Adjacency list for Dijkstra
    graph = {i: [] for i in range(n)}
    for i in range(n):
        neighbors = random.sample(
            [j for j in range(n) if j != i],
            min(2, n - 1)
        )
        for j in neighbors:
            weight = random.randint(1, 100)
            graph[i].append((j, weight))
    return graph


def generate_dense_graph_adjacency(n):
    # Adjacency list for Dijkstra
    graph = {i: [] for i in range(n)}
    for i in range(n):
        for j in range(n):
            if i != j:
                weight = random.randint(1, 100)
                graph[i].append((j, weight))
    return graph


def generate_sparse_graph_matrix(n):
    # Adjacency matrix for Floyd-Warshall
    INF = float('inf')
    matrix = [[INF] * n for _ in range(n)]
    for i in range(n):
        matrix[i][i] = 0
    for i in range(n):
        neighbors = random.sample(
            [j for j in range(n) if j != i],
            min(2, n - 1)
        )
        for j in neighbors:
            weight = random.randint(1, 100)
            matrix[i][j] = weight
    return matrix


def generate_dense_graph_matrix(n):
    # Adjacency matrix for Floyd-Warshall
    INF = float('inf')
    matrix = [[INF] * n for _ in range(n)]
    for i in range(n):
        matrix[i][i] = 0
        for j in range(n):
            if i != j:
                weight = random.randint(1, 100)
                matrix[i][j] = weight
    return matrix


def count_edges_adjacency(graph):
    return sum(len(v) for v in graph.values())


def count_edges_matrix(matrix):
    INF = float('inf')
    count = 0
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if i != j and matrix[i][j] != INF:
                count += 1
    return count