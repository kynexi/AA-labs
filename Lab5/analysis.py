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
        num_edges = int(n * (n - 1) / 4)

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

sizes = [10, 50, 100, 200, 500]

prim_sparse_times = []
prim_dense_times = []
kruskal_sparse_times = []
kruskal_dense_times = []

for n in sizes:
    # Sparse
    graph, edges = generate_graph(n, "sparse")

    start = time.time()
    prim(graph)
    prim_sparse_times.append(time.time() - start)

    start = time.time()
    kruskal(n, edges)
    kruskal_sparse_times.append(time.time() - start)

    # Dense
    graph, edges = generate_graph(n, "dense")

    start = time.time()
    prim(graph)
    prim_dense_times.append(time.time() - start)

    start = time.time()
    kruskal(n, edges)
    kruskal_dense_times.append(time.time() - start)
    
all_times = (
    prim_sparse_times +
    prim_dense_times +
    kruskal_sparse_times +
    kruskal_dense_times
)

y_max = max(all_times) * 1.1  

print("=== Prim's Algorithm Results ===")
for i, n in enumerate(sizes):
    print(f"Nodes: {n} | Sparse: {prim_sparse_times[i]:.6f}s | Dense: {prim_dense_times[i]:.6f}s")

print("\n=== Kruskal's Algorithm Results ===")
for i, n in enumerate(sizes):
    print(f"Nodes: {n} | Sparse: {kruskal_sparse_times[i]:.6f}s | Dense: {kruskal_dense_times[i]:.6f}s")


plt.figure()
plt.plot(sizes, prim_sparse_times, label="Sparse Graph")
plt.plot(sizes, prim_dense_times, label="Dense Graph")
plt.xlabel("Number of Nodes")
plt.ylabel("Execution Time (seconds)")
plt.title("Prim's Algorithm Runtime")
plt.ylim(0, y_max)
plt.legend()
plt.savefig("prim_runtime.png")


plt.figure()
plt.plot(sizes, kruskal_sparse_times, label="Sparse Graph")
plt.plot(sizes, kruskal_dense_times, label="Dense Graph")
plt.xlabel("Number of Nodes")
plt.ylabel("Execution Time (seconds)")
plt.title("Kruskal's Algorithm Runtime")
plt.ylim(0, y_max)
plt.legend()
plt.savefig("kruskal_runtime.png")


plt.figure()
plt.plot(sizes, prim_sparse_times, label="Prim Sparse")
plt.plot(sizes, prim_dense_times, label="Prim Dense")
plt.plot(sizes, kruskal_sparse_times, label="Kruskal Sparse")
plt.plot(sizes, kruskal_dense_times, label="Kruskal Dense")
plt.xlabel("Number of Nodes")
plt.ylabel("Execution Time (seconds)")
plt.title("Prim vs Kruskal Runtime Comparison")
plt.ylim(0, y_max)
plt.legend()
plt.savefig("combined_runtime.png")

plt.show()