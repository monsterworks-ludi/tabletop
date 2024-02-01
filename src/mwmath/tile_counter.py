import itertools as it
from typing import Iterable, Callable, Generator

Tile = tuple[int, ...]
""" Represents a tile, each entry is the type of the edge starting with the 'initial' edge and proceeding clockwise """

def all_fixed_tiles(number_of_edges: int, number_of_number_of_edge_types: int) -> set[Tile]:
    """
    Generates all possible fixed tiles with specified number of edges and specified types of edges.

    :param number_of_edges: number of edges on each tile
    :param number_of_number_of_edge_types: number of possible edge types on each tile
    :return: all possible fixed tiles
    """
    return set(it.product(range(number_of_number_of_edge_types), repeat=number_of_edges))


def tile_orbit(tile: Tile, actions: Iterable) -> set[Tile]:
    """
    Determines the orbit of a tile, returns all tiles in the orbit

    :param tile: the initial tile
    :param actions: all actions to apply to the tile
    :return: the orbit of the tile as a tuple in lexicographic order
    """
    return {action(tile) for action in actions}


def tile_rotation(zero_to: int) -> Callable:
    """
    Defines the function which rotates a tile, sending vertex 0 to vertex "zero_to"

    :param zero_to: the vertex to which 0 is sent
    :return: the function which rotates the tile
    """
    return lambda x: tuple(x[(zero_to + i) % len(x)] for i in range(len(x)))


def tile_reflection(zero_to: int) -> Callable:
    """
    Defines the function which rotates a tile, sending vertex 0 to vertex "zero_to"

    :param zero_to: the vertex to which 0 is sent
    :return: the function which reflects the tile
    """
    return lambda x: tuple(x[(zero_to - i) % len(x)] for i in range(len(x)))


def rotation_group(number_of_edges: int) -> Generator:
    """
    Generates the rotation group associated with regular polygons with number_of_edges edges

    :param number_of_edges: the number of edges of the polygons being rotated
    :return: a generator listing all rotations
    """
    return (tile_rotation(zero_target) for zero_target in range(number_of_edges))


# maybe update this to return generator instead of tuple
def dihedral_group(number_of_edges: int) -> Generator:
    """
    Generates the dihedral group associated with regular polygons with number_of_edges edges

    :param number_of_edges: the number of edges of the polygons being transformed
    :return: a generator listing all reflections and rotations
    """
    return (action for action in it.chain(
        (tile_rotation(zero_target) for zero_target in range(number_of_edges)),
        (tile_reflection(zero_target) for zero_target in range(number_of_edges))))


def partition_tiles(number_of_edges: int,
                    number_of_edge_types: int,
                    group: Callable) -> dict[Tile, set[Tile]]:
    """
    Returns a partition of the tiles by orbit, with a unique key (the minimal tile) provided for each orbit

    :param number_of_edges: the number of edges of the regular polygon being transformed
    :param number_of_edge_types: the number of edge types of the regular polygon being transformed
    :param group: a function which generates the action group (will be called with number_of_edges to generate actions)
    :return: a dictionary whose values are the orbits and whose keys are the minimal tile in each orbit
    """
    dictionary = {}
    for tile in all_fixed_tiles(number_of_edges, number_of_edge_types):
        orbit = tile_orbit(tile, group(number_of_edges))
        key = min(orbit)
        dictionary[key] = orbit
    return dictionary


def onesided_tiles(number_of_edges: int,
                   number_of_edge_types: int) -> dict[Tile, set[Tile]]:
    """
    Computes all one-sided tiles as a dictionary

    :param number_of_edges: the number of edges of the regular polygon
    :param number_of_edge_types: the number of edge types of the regular polygon
    :return: a dictionary whose values are the orbits and whose keys are the minimal tile in each orbit
    """
    return partition_tiles(number_of_edges, number_of_edge_types, rotation_group)


def count_onesided_tiles(number_of_edges: int, number_of_edge_types: int) -> int:
    """
    Determines the number of distinct one-sided tiles of a regular polygon

    :param number_of_edges: the number of edges of the regular polygon
    :param number_of_edge_types: the number of edge types
    :return: the number of distinct one-sided tiles
    """
    return len(onesided_tiles(number_of_edges, number_of_edge_types))


def free_tiles(number_of_edges: int,
               number_of_edge_types: int) -> dict[Tile, set[Tile]]:
    """
    Computes all free tiles as a dictionary

    :param number_of_edges: the number of edges of the regular polygon
    :param number_of_edge_types: the number of edge types of the regular polygon
    :return: a dictionary whose values are the orbits and whose keys are the minimal tile in each orbit
    """
    return partition_tiles(number_of_edges, number_of_edge_types, dihedral_group)


def count_free_tiles(number_of_edges: int, number_of_edge_types: int) -> int:
    """
    Determines the number of distinct free tiles of a regular polygon

    :param number_of_edges: the number of edges of the regular polygon
    :param number_of_edge_types: the number of edge types
    :return: the number of distinct free tiles
    """
    return len(free_tiles(number_of_edges, number_of_edge_types))


# todo: cascadia & galaxy trucker examples cannot be done "automatically"
#   as they do not start with "all_fixed_tiles"

if __name__ == "__main__":
    ...
