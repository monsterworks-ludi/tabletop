import sympy as sp
import itertools as it
from collections import defaultdict

from typing import Callable, Optional


Connections = dict[int, set[int]]
"""Key is vertex index.
Value is the set of indices of adjacent vertices."""


def connection(conn: Connections, row: int, col: int) -> int:
    """
    Determines whether orig is connected to dest.

    :param conn: a connection dictionary indicating adjacent vertices
    :param row: the destination (row)
    :param col: the origination (column)
    :return: 1 if there is an edge from orig to dest, 0 otherwise
    """
    return 0 if col not in conn or row not in conn[col] else 1


def build_matrix(conn: Connections) -> sp.Matrix:
    """
    Builds an adjacency matrix from a connection dictionary

    :param conn: a connection dictionary using vertex indices
    :return: the adjacency matrix associated with the graph defined by conn
    """
    return sp.Matrix(
        len(conn),
        len(conn),
        lambda row, col: connection(conn, row, col),
    )


Symbols = tuple[sp.Symbol, ...]
"""kth entry is the symbol associated with the vertex with index k."""

SymbolicConnections = dict[sp.Symbol, set[sp.Symbol]]
"""Key is vertex symbol.
Value i the set of symbols of adjacent vertices."""


def connection_symbolic(
    conn: SymbolicConnections,
    dest: sp.Symbol,
    orig: sp.Symbol,
) -> int:
    """
    Determines whether orig is connected to dest.

    :param conn: a connection dictionary indicating adjacent vertices using symbolic names
    :param dest: the destination
    :param orig: the column
    :return: 1 if there is an edge from orig to dest, 0 otherwise
    """
    return 0 if orig not in conn or dest not in conn[orig] else 1


def build_matrix_symbolic(spaces: Symbols, conn: SymbolicConnections) -> sp.Matrix:
    """
    Computes an adjacency matrix based on symbolic connections.

    :param spaces: a tuple specifying the symbols associated with each index
    :param conn: a connection dictionary using vertex indices
    :return: adjacency matrix based on conn
    """
    return sp.Matrix(
        len(spaces),
        len(spaces),
        lambda row, col: connection_symbolic(conn, spaces[row], spaces[col]),
    )


LabeledConnections = dict[sp.Symbol, dict[sp.Symbol, tuple[str, ...]]]
"""Key is the symbol of a vertex.
Value is a dictionary
whose subkeys are the symbols associated with adjacent vertices
and whose subvalues are data encoded as a string.

Note that the ordering of the tuple does not matter, but we
need to allow for multiple edges with the same label. May consider
using the multiset package."""


def weighted_connection_symbolic(
    spaces: Symbols,
    conn: LabeledConnections,
    weigh: Callable,
    row: int,
    col: int,
) -> sp.Expr:
    """
    Computes the weight associated with the connection between orig and dest using the weigh function and the symbols in

    :param spaces: a tuple specifying the symbols associated with each index
    :param conn: a connection dictionary using vertex indices
    :param weigh: a function which specifies the weight of the connection
    :param col: the originating vertex
    :param row: the destination vertex
    :return: the weight associated with the connection
    """
    dest = spaces[row]
    orig = spaces[col]
    if orig not in conn or dest not in conn[orig]:
        return sp.Integer(0)
    else:
        total_weight = sp.Integer(0)
        for label in conn[dest][orig]:
            total_weight += weigh(label)
        return total_weight


def build_weighted_matrix_symbolic(
    spaces: Symbols,
    conn: LabeledConnections,
    weigh: Callable,
) -> sp.Matrix:
    """
    Computes a weighted adjacency matrix based on symbolic connections and function

    :param spaces: a tuple specifying the symbols associated with each index
    :param conn: a connection dictionary using vertex indices
    :param weigh: a function which specifies the weight of the connection
    :return: weighted adjacency matrix based on labels in conn and weights determined by weigh
    """
    return sp.Matrix(
        len(spaces),
        len(spaces),
        lambda row, col: weighted_connection_symbolic(spaces, conn, weigh, row, col),
    )


def vertex_degrees(
    conn: Connections | SymbolicConnections,
) -> dict[int | sp.Symbol, int]:
    """
    Determines the degrees of the vertices in the graph.

    The keys of the return value match the keys of conn.

    :param conn: connections
    :return: a dictionary whose keys are vertices and whose values are their degrees
    """
    return {vertex: len(adjacents) for vertex, adjacents in conn.items()}


def vertex_degrees_multi(conn: LabeledConnections) -> dict[sp.Symbol, int]:
    """
    Determines the degrees of the vertices in the graph.

    :param conn: connections determining the graph
    :return: a dictionary whose keys are vertices and whose values are their degrees
    """
    degrees = {}
    for vertex, adjacents in conn.items():
        degree = 0
        for edges in adjacents.values():
            degree += len(edges)
        degrees[vertex] = degree
    return degrees


def submatrix_symbolic(
    spaces: Symbols,
    matrix: sp.Matrix,
    dests: tuple[sp.Symbol, ...],
    origs: tuple[sp.Symbol, ...],
) -> sp.Matrix:
    """
    Generates a submatrix based on symbols

    :param spaces: a tuple specifying the symbols associated with each index
    :param matrix: matrix from which the submatrix will be taken
    :param dests: list of symbols associated with destinations to be selected
    :param origs: list of symbols associated with originations to be selected
    :return:
    """
    rows = [spaces.index(row) for row in dests]
    cols = [spaces.index(col) for col in origs]
    return matrix[rows, cols]


def spaces_by_centrality(
    spaces: Symbols, matrix: sp.Matrix
) -> dict[int, set[sp.Symbol]]:
    """

    :param spaces: a tuple specifying the symbols associated with each index
    :param matrix: a matrix interpreted as an adjacency matrix
    :return: a dictionary whose keys are the number of neighbors and values are the spaces with that many neighbors
    """
    rows = len(spaces)
    neighbors = matrix.applyfunc(lambda x: min(x, 1)) * sp.ones(rows, 1)
    result = {}
    for size in range(
        rows + 1
    ):  # a city could be adjacent to all other cities, including itself
        if size in neighbors:
            result[size] = set(
                {spaces[index] for index in range(rows) if neighbors[index] == size}
            )
    return result


def centers(spaces: Symbols, matrix: sp.Matrix) -> tuple[int, set[sp.Symbol]]:
    """

    :param spaces: a tuple specifying the symbols associated with each index
    :param matrix: a matrix interpreted as an adjacency matrix
    :return: the maximum number of neighbors and the spaces with that many neighbors
    """
    neighbors = spaces_by_centrality(spaces, matrix)
    most_neighbors = max(neighbors)
    return most_neighbors, neighbors[most_neighbors]


def terminated(matrix: sp.Matrix, absorbing_states: set[int]) -> bool:
    """

    :param matrix: an adjacency matrix
    :param absorbing_states: indices of vertices which only have an edge back to themselves
    :return: True if all walks end in an absorbing state, False otherwise
    """
    for row in range(matrix.rows):
        if row in absorbing_states:
            continue
        for col in range(matrix.cols):
            if not matrix[row, col] == 0:
                return False
    return True


def terminal_matrix(matrix: sp.Matrix, absorbing_states: set[int], max_hops=100) -> tuple[int, sp.Matrix]:
    """

    :param matrix: an adjacency matrix
    :param absorbing_states: indices of vertices which only have an edge back to themselves
    :param max_hops: limits the number of hops in the walks
    :return: the result of raising the adjacency matrix to a high
    enough power that all walks terminate at an absorbing state
    """
    hops = 0
    ad_power = sp.eye(matrix.cols)
    for hops in it.count(1):
        ad_power = ad_power * matrix  # one steps here
        if terminated(ad_power, absorbing_states):
            break
        if hops > max_hops:
            raise RuntimeError("hop limit exceeded")
    return hops, ad_power


Pendant = tuple[str, sp.Symbol]
""" Consists of a label for the edge and a symbol for the incident vertex. """
Path = tuple[Pendant, ...]
""" A list of labelled edges. """

def new_pendants_from_path(conn: LabeledConnections, path: Path) -> tuple[Pendant, ...]:
    """

    :param conn: the labeled edges in the graph
    :param path: the path constructed up to this point
    :return: all pendants which do not form a cycle when appended to the path
    """
    neighbors = conn[path[-1][1]]

    visited_spaces = {pendant[1] for pendant in path}
    new_spaces = [
        space for space in neighbors if space not in visited_spaces
    ]
    pendantss = [
        [(stem, new_space) for stem in neighbors[new_space]] for new_space in new_spaces
    ]
    pendants = (pendant for pendants in pendantss for pendant in pendants)
    return tuple(pendants)


def find_all_paths(
    conn: LabeledConnections,
    path: Path,
    all_paths: Optional[dict[int, set[Path]]] = None,
    dest: Optional[sp.Symbol] = None,
    max_length: Optional[int] = None,
) -> Optional[dict[int, set[Path]]]:
    """

    :param conn: the labelled edges in the graph
    :param path: the current path
    :param all_paths: all paths previously determined in the graph that originate with path
    :param dest: if provided, paths halt once arriving at this node
    :param max_length: if provided, paths halt once they achieve this length
    :return: all paths in the graph that originate with path
    """
    assert len(path) > 0, "Must have a starting point for all_paths"
    if max_length and len(path) > max_length:
        return all_paths
    if all_paths is None:
        all_paths = defaultdict(set)
    new_pendants = new_pendants_from_path(conn, path)
    if len(new_pendants) == 0 and dest is None:
        all_paths[len(path) - 1].add(path)
    for pendant in new_pendants:
        new_path = path + (pendant,)
        if pendant[1] == dest:
            all_paths[len(new_path) - 1].add(new_path)
        else:
            find_all_paths(conn, new_path, all_paths, dest, max_length)
    return all_paths


def path_string(path: Path) -> str:
    """

    :param path: a path
    :return: a nicely formatted string that identifies the path
    """
    string = ""
    for i, edge in enumerate(path):
        if i == 0:
            string += f"{edge[1]}"  # type: ignore  # (seems to think edge is a sp.Symbol)
        else:
            string += f" -({edge[0]})- {edge[1]}"  # type: ignore  # (seems to think edge is a sp.Symbol)
    return string


def reverse_connections(conn: Connections) -> Connections:
    """

    :param conn: connections, organized by originating edge
    :return: connections, organized by destination edge
    """
    rev_conn = {}
    for row in conn:
        edges = {col for col in conn if row in conn[col]}
        rev_conn[row] = edges
    return rev_conn


def count_directed_paths(
    rev_conn: Connections,
    to_vert: int,
    from_vert: int = 0,
    counts: Optional[dict[int, int]] = None,
) -> int:
    """

    :param rev_conn: a reverse connection
    :param to_vert: ending vertex for the path
    :param from_vert: starting vertex for the path
    :param counts: the number of paths starting at from_vert and ending at the key, useful for batch searches
    :return: the number of paths (from_vert ~ ~ ~ to_vert)
    """
    if counts is None:
        # initial call, no global count register
        counts = defaultdict(lambda: -1)
        counts[from_vert] = 1
    if not counts[to_vert] == -1:
        # we have computed this value already, return it
        count = counts[to_vert]
        return count

    # we have not computed this value yet
    count = 0
    visited_verts = {to_vert}  # prevents infinite recursion if graph has self-loops
    while rev_conn[to_vert] - visited_verts:
        # there are some incoming edges we have not tallied yet
        vert = list(rev_conn[to_vert] - visited_verts).pop()
        # count the number of paths coming from that edge
        incoming_paths = count_directed_paths(rev_conn, vert, from_vert, counts)
        # and increase the count
        count += incoming_paths
        # indicate that we have tallied that edge
        visited_verts.add(vert)
    counts[to_vert] = count
    return count


def count_all_directed_paths(rev_conn: Connections, from_vert: int = 0) -> dict[int, int]:
    """

    :param rev_conn: a reverse connection
    :param from_vert: starting vertex for the path
    :return: key is the ending vertex and value is the number of paths (from_vert ~ ~ ~ key)
    """
    counts = defaultdict(lambda: -1)
    counts[from_vert] = 1
    for to_vertex in rev_conn:
        count_directed_paths(rev_conn, to_vertex, from_vert, counts)
    return dict(counts)


if __name__ == "__main__":
    ...
