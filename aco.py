"""
services/aco.py
Core Ant Colony Optimization logic for TSP.
Includes:
  - AntColonyBase (shared infrastructure)
  - AntSystem
  - ElitistAntSystem
  - RankBasedAntSystem
"""

import numpy as np
import random
import time
from typing import List, Tuple


# ─── Utility ─────────────────────────────────────────────────────────────────

def euclidean_distance(c1, c2) -> float:
    return float(np.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2))


def build_distance_matrix(coords) -> np.ndarray:
    n = len(coords)
    dm = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                dm[i][j] = euclidean_distance(coords[i], coords[j])
    return dm


def route_distance(route: List[int], distance_matrix: np.ndarray) -> float:
    return float(sum(
        distance_matrix[route[i], route[(i + 1) % len(route)]]
        for i in range(len(route))
    ))


# ─── Base class ──────────────────────────────────────────────────────────────

class AntColonyBase:
    """
    Shared infrastructure for all ACO variants.
    Subclasses override `optimize()` with variant-specific pheromone logic.
    """

    def __init__(self, coords, n_ants=10, alpha=1.0, beta=5.0,
                 rho=0.5, Q=100.0):
        self.coords = np.array(coords, dtype=float)
        self.n_ants = n_ants
        self.alpha = alpha          # pheromone importance
        self.beta = beta            # heuristic (1/distance) importance
        self.rho = rho              # evaporation rate
        self.Q = Q                  # pheromone deposit constant
        self.num_cities = len(coords)
        self.distance_matrix = build_distance_matrix(self.coords)
        self.pheromone = np.ones((self.num_cities, self.num_cities))
        self.best_path = None
        self.best_distance = float("inf")

    def _route_distance(self, route):
        return route_distance(route, self.distance_matrix)

    def _transition_probs(self, current: int, unvisited: List[int]) -> np.ndarray:
        """Compute normalised selection probabilities from current city."""
        tau = self.pheromone[current][unvisited] ** self.alpha
        eta = (1.0 / self.distance_matrix[current][unvisited]) ** self.beta
        scores = tau * eta
        total = scores.sum()
        return scores / total if total > 0 else np.ones(len(unvisited)) / len(unvisited)

    def _build_solution(self, start_city: int) -> List[int]:
        """Greedy-probabilistic tour construction for one ant."""
        unvisited = list(range(self.num_cities))
        unvisited.remove(start_city)
        route = [start_city]
        while unvisited:
            probs = self._transition_probs(route[-1], unvisited)
            next_city = int(np.random.choice(unvisited, p=probs))
            route.append(next_city)
            unvisited.remove(next_city)
        return route

    def _deposit(self, route: List[int], dist: float, weight: float = 1.0):
        """Deposit pheromone on edges of a route."""
        delta = weight * self.Q / dist
        for i in range(len(route)):
            a, b = route[i], route[(i + 1) % len(route)]
            self.pheromone[a][b] += delta
            self.pheromone[b][a] += delta

    def optimize(self, iterations: int = 50) -> Tuple[List[int], float, List[float]]:
        raise NotImplementedError


# ─── Ant System ──────────────────────────────────────────────────────────────

class AntSystem(AntColonyBase):
    """
    Classic Ant System (Dorigo, 1992).
    All ants deposit pheromone proportional to 1/distance.
    """

    def optimize(self, iterations=50):
        convergence = []
        for _ in range(iterations):
            solutions = []
            for _ in range(self.n_ants):
                route = self._build_solution(random.randint(0, self.num_cities - 1))
                dist = self._route_distance(route)
                solutions.append((route, dist))
                if dist < self.best_distance:
                    self.best_distance = dist
                    self.best_path = route[:]

            # Evaporation
            self.pheromone *= (1 - self.rho)

            # All-ant deposit
            for route, dist in solutions:
                self._deposit(route, dist)

            convergence.append(self.best_distance)

        return self.best_path, self.best_distance, convergence


# ─── Elitist Ant System ──────────────────────────────────────────────────────

class ElitistAntSystem(AntColonyBase):
    """
    Elitist Ant System.
    Best-so-far solution gets extra pheromone reinforcement each iteration.
    """

    def __init__(self, coords, n_ants=10, alpha=1.0, beta=5.0,
                 rho=0.5, Q=100.0, e=5):
        super().__init__(coords, n_ants, alpha, beta, rho, Q)
        self.e = e  # elitism multiplier for best-so-far path

    def optimize(self, iterations=50):
        convergence = []
        for _ in range(iterations):
            solutions = []
            for _ in range(self.n_ants):
                route = self._build_solution(random.randint(0, self.num_cities - 1))
                dist = self._route_distance(route)
                solutions.append((route, dist))
                if dist < self.best_distance:
                    self.best_distance = dist
                    self.best_path = route[:]

            self.pheromone *= (1 - self.rho)

            # Normal deposit for all ants
            for route, dist in solutions:
                self._deposit(route, dist)

            # Extra deposit for best-so-far
            if self.best_path:
                self._deposit(self.best_path, self.best_distance, weight=self.e)

            convergence.append(self.best_distance)

        return self.best_path, self.best_distance, convergence


# ─── Rank-Based Ant System ───────────────────────────────────────────────────

class RankBasedAntSystem(AntColonyBase):
    """
    Rank-Based Ant System (AS_rank).
    Only the top-w ants deposit pheromone, weighted by rank.
    Best-so-far ant also contributes with weight w.
    """

    def __init__(self, coords, n_ants=10, alpha=1.0, beta=5.0,
                 rho=0.5, Q=100.0, w=5):
        super().__init__(coords, n_ants, alpha, beta, rho, Q)
        self.w = w  # number of ranked ants to use

    def optimize(self, iterations=50):
        convergence = []
        for _ in range(iterations):
            solutions = []
            for _ in range(self.n_ants):
                route = self._build_solution(random.randint(0, self.num_cities - 1))
                dist = self._route_distance(route)
                solutions.append((route, dist))
                if dist < self.best_distance:
                    self.best_distance = dist
                    self.best_path = route[:]

            # Sort best → worst
            solutions.sort(key=lambda x: x[1])
            self.pheromone *= (1 - self.rho)

            # Rank-weighted deposit for top (w-1) ants
            for rank, (route, dist) in enumerate(solutions[: self.w - 1]):
                weight = self.w - rank  # best ant gets weight w-1, etc.
                self._deposit(route, dist, weight=weight)

            # Best-so-far gets weight w
            if self.best_path:
                self._deposit(self.best_path, self.best_distance, weight=self.w)

            convergence.append(self.best_distance)

        return self.best_path, self.best_distance, convergence


# ─── Factory ─────────────────────────────────────────────────────────────────

ALGORITHM_MAP = {
    "ant_system": AntSystem,
    "elitist": ElitistAntSystem,
    "rank_based": RankBasedAntSystem,
}


def run_algorithm(name: str, coords, n_ants: int, iterations: int):
    """
    Instantiate and run one ACO algorithm.
    Returns (best_path, best_distance, exec_time, convergence).
    """
    cls = ALGORITHM_MAP.get(name)
    if cls is None:
        raise ValueError(f"Unknown algorithm: {name}. Choose from {list(ALGORITHM_MAP)}")

    algo = cls(coords, n_ants=n_ants)
    start = time.time()
    best_path, best_distance, convergence = algo.optimize(iterations=iterations)
    exec_time = time.time() - start

    return best_path, best_distance, exec_time, convergence
