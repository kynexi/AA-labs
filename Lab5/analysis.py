import random
import time
import heapq
import matplotlib.pyplot as plt

def generate_graph(n, density="sparse"):
    graph = {i: [] for i in range(n)}
    edges = []

    if density == "sparse":
        num_edges = int(1.5 * n)
    else:
        num_edges = int(n * (n - 1) / 4)  # not full dense to keep runtime reasonable

    added = set()

    while len(edges) < num_edges:
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)

        if u == v or (u, v) in added or (v, u) in added:
            continue

        w = random.randint(1, 100)
        graph[u].append((v, w))
        graph[v].append((u, w))
        edges.append((u, v, w))
        added.add((u, v))

    return graph, edges

def prim(graph, start=0):
    visited = set()
    min_heap = [(0, start)]

    total_weight = 0

    while min_heap:
        weight, node = heapq.heappop(min_heap)

        if node in visited:
            continue

        visited.add(node)
        total_weight += weight

        for neighbor, w in graph[node]:
            if neighbor not in visited:
                heapq.heappush(min_heap, (w, neighbor))

    return total_weight

def find(parent, x):
    if parent[x] != x:
        parent[x] = find(parent, parent[x])
    return parent[x]

def union(parent, rank, x, y):
    rx, ry = find(parent, x), find(parent, y)
    if rx != ry:
        if rank[rx] < rank[ry]:
            parent[rx] = ry
        elif rank[rx] > rank[ry]:
            parent[ry] = rx
        else:
            parent[ry] = rx
            rank[rx] += 1

def kruskal(n, edges):
    edges = sorted(edges, key=lambda x: x[2])
    parent = list(range(n))
    rank = [0] * n

    total_weight = 0

    for u, v, w in edges:
        if find(parent, u) != find(parent, v):
            union(parent, rank, u, v)
            total_weight += w

    return total_weight