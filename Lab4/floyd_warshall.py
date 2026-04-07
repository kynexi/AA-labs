import copy


def floyd_warshall(matrix):
    n = len(matrix)
    dist = copy.deepcopy(matrix)

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist


def has_negative_cycle(dist):
    """Check if any node has a negative distance to itself."""
    for i in range(len(dist)):
        if dist[i][i] < 0:
            return True
    return False