import sympy as sp
import itertools as it
from collections import defaultdict

from typing import Callable
from icecream import ic  # type: ignore

ic.disable()


def connection(connections, dest, orig):
    return 0 if orig not in connections or dest not in connections[orig] else 1


# could be rewritten in terms of connection
def connection_symbolic(
    spaces: tuple[sp.Symbol],
    connections: dict[sp.Symbol, set[sp.Symbol]],
    dest: int,
    orig: int,
) -> int:
    if spaces[orig] not in connections or spaces[dest] not in connections[spaces[orig]]:
        return 0
    else:
        return 1


def weighted_connection_symbolic(
    spaces: tuple[sp.Symbol],
    connections: dict[sp.Symbol, dict[sp.Symbol, tuple[str, ...]]],
    weigh: Callable,
    destination: int,
    origin: int,
) -> int:
    orig = spaces[origin]
    dest = spaces[destination]
    if orig not in connections or dest not in connections[orig]:
        return 0
    else:
        total_weight = 0
        for route in connections[orig][dest]:
            total_weight += weigh(route)
        return total_weight


def vertex_degrees(connections):
    return {city: len(neighbors) for city, neighbors in connections.items()}


def vertex_degrees_multi(connections):
    degree_dict = {}
    for city, neighbor in connections.items():
        degree = 0
        for edges in neighbor.values():
            degree += len(edges)
        degree_dict[city] = degree
    return degree_dict


def build_matrix(connections):
    return sp.Matrix(
        len(connections),
        len(connections),
        lambda origin, destination: connection(connections, origin, destination),
    )


def build_matrix_symbolic(
    spaces: tuple, connections: dict[sp.Symbol, set[sp.Symbol]]
) -> sp.Matrix:
    return sp.Matrix(
        len(spaces),
        len(spaces),
        lambda origin, destination: connection_symbolic(
            spaces, connections, origin, destination
        ),
    )


def build_weighted_matrix_symbolic(
    spaces: tuple[sp.Symbol],
    connections: dict[sp.Symbol, dict[sp.Symbol, tuple[str, ...]]],
    weight: Callable,
) -> sp.Matrix:
    return sp.Matrix(
        len(spaces),
        len(spaces),
        lambda origin, destination: weighted_connection_symbolic(
            spaces, connections, weight, origin, destination
        ),
    )


def submatrix_symbolic(
    spaces: tuple[sp.Symbol],
    matrix: sp.Matrix,
    destinations: list[sp.Symbol],
    originations: list[sp.Symbol],
) -> sp.Matrix:
    rows = [spaces.index(row) for row in destinations]
    cols = [spaces.index(col) for col in originations]
    return matrix[rows, cols]


def connected(routes: int) -> int:
    return min(routes, 1)


def city_neighbors(
    cities: tuple[sp.Symbol], matrix: sp.Matrix
) -> dict[int, list[sp.Symbol]]:
    rows = len(cities)
    one_col = sp.ones(rows, 1)
    neighbors = matrix.applyfunc(lambda x: min(x, 1)) * one_col
    cities_by_neighbors = defaultdict(lambda: [])
    for city_index in range(rows):
        cities_by_neighbors[neighbors[city_index]].append(cities[city_index])
    return cities_by_neighbors


def most_connected_cities(
    cities: tuple, matrix: sp.Matrix
) -> tuple[int, list[sp.Symbol]]:
    city_matrix = matrix[0 : len(cities), 0 : len(cities)]
    neighbors = city_neighbors(cities, city_matrix)
    most_neighbors = max(neighbors)
    return most_neighbors, neighbors[most_neighbors]


def absorbed(matrix: sp.Matrix, absorbing_states):
    for dest in range(matrix.rows):
        if dest in absorbing_states:
            continue
        for orig in range(matrix.cols):
            if not matrix[dest, orig] == 0:
                return False
    return True

def terminal_matrix(matrix, absorbing_states):
    ad_power = sp.eye(matrix.cols)
    for steps in it.count(1):
        ad_power = ad_power * matrix  # one steps here
        if absorbed(ad_power, absorbing_states):
            break
        if steps > 100:
            raise RuntimeError("Too Many Steps")
    else:
        steps = None
    return steps, ad_power

