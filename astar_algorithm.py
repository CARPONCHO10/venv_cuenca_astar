import heapq
from typing import Dict, List, Tuple, Optional
from utils import haversine_distance, euclidean_distance

class AStarPathFinder:
    def __init__(self, nodes: Dict, edges: Dict):
        self.nodes = nodes
        self.edges = edges
        self.explored: List[str] = []

    def heuristic(self, node: str, goal: str) -> float:
        """Heurística: Distancia Euclidiana al objetivo."""
        n_data = self.nodes[node]
        g_data = self.nodes[goal]
        return euclidean_distance(n_data["lat"], n_data["lon"], g_data["lat"], g_data["lon"])

    def get_distance(self, node1: str, node2: str) -> float:
        """Costo real entre nodos: Distancia de Haversine."""
        n1_data = self.nodes[node1]
        n2_data = self.nodes[node2]
        return haversine_distance(n1_data["lat"], n1_data["lon"], n2_data["lat"], n2_data["lon"])

    def find_path(self, start: str, goal: str) -> Tuple[Optional[List[str]], float, int]:
        """Ejecuta el algoritmo A* para encontrar el camino desde 'start' hasta 'goal'."""
        self.explored = []
        frontier = []
        counter = 0
        # Estructura de la frontera: (f_score, counter, current_node, path, g_score)
        heapq.heappush(frontier, (0.0, counter, start, [start], 0.0))
        visited = set()

        while frontier:
            f_score, _, current, path, g_score = heapq.heappop(frontier)

            if current in visited:
                continue

            visited.add(current)
            self.explored.append(current)

            if current == goal:
                return path, g_score, len(self.explored)

            for neighbor in self.edges.get(current, []):
                if neighbor in visited:
                    continue

                edge_cost = self.get_distance(current, neighbor)
                new_g_score = g_score + edge_cost
                h_score = self.heuristic(neighbor, goal)
                f_score = new_g_score + h_score

                counter += 1
                heapq.heappush(frontier, (f_score, counter, neighbor, path + [neighbor], new_g_score))

        return None, float('inf'), len(self.explored)