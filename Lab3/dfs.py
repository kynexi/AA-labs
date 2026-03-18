def dfs(graph, start):
    visited = set()
    
    def _dfs(node):
        if node in visited:
            return
        visited.add(node)
        for neighbor in graph[node]:
            _dfs(neighbor)
    
    _dfs(start)
    return visited