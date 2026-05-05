import heapq

def prim(graph, start=0):
    n = len(graph)
    visited = [False] * n
    min_heap = [(0, start, -1)]  # (weight, node, parent)

    mst_weight = 0
    mst_edges = []

    while min_heap:
        weight, node, parent = heapq.heappop(min_heap)

        if visited[node]:
            continue

        visited[node] = True
        mst_weight += weight

        if parent != -1:
            mst_edges.append((parent, node, weight))

        for neighbor, w in graph[node]:
            if not visited[neighbor]:
                heapq.heappush(min_heap, (w, neighbor, node))

    return mst_weight, mst_edges


# Example usage
graph = {
    0: [(1, 2), (3, 6)],
    1: [(0, 2), (2, 3), (3, 8), (4, 5)],
    2: [(1, 3), (4, 7)],
    3: [(0, 6), (1, 8), (4, 9)],
    4: [(1, 5), (2, 7), (3, 9)]
}

print(prim(graph))