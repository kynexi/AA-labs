import random

def generate_graph(n, edges_per_node=3):
    graph = {i: set() for i in range(n)}
    
    for node in range(n):
        for _ in range(edges_per_node):
            neighbor = random.randint(0, n - 1)
            if neighbor != node:
                graph[node].add(neighbor)
                graph[neighbor].add(node)  
    
    return graph