from itertools import product, chain

from typing import Iterable, Callable, Generator
from icecream import ic  # type: ignore

ic.disable()


def all_fixed_tiles(edge_count: int, edge_types: int) -> product:
    """
    Generates all possible fixed tiles with specified number of edges and specified types of edges.

    :param edge_count: number of edges on each tile
    :param edge_types: number of possible sides on each tile
    :return: all possible fixed tiles
    """
    return product(range(edge_types), repeat=edge_count)


def tile_orbit(tile: tuple[int, ...], actions: Iterable) -> tuple[tuple[int, ...], ...]:
    """
    Determines the orbit of a tile, returns all tiles in the orbit

    :param tile: the initial tile
    :param actions: all actions to apply to the tile
    :return: the orbit of the tile as a tuple in lexicographic order
    """
    return tuple(sorted(list({action(tile) for action in actions})))


def rotate_tile(zero_to: int) -> Callable:
    """
    Defines the function which rotates a tile, sending vertex 0 to vertex "zero_to"

    :param zero_to: the vertex to which 0 is sent
    :return: the function which rotates the tile
    """
    return lambda x: tuple(x[(zero_to + i) % len(x)] for i in range(len(x)))


def reflect_tile(zero_to: int) -> Callable:
    """
    Defines the function which rotates a tile, sending vertex 0 to vertex "zero_to"

    :param zero_to: the vertex to which 0 is sent
    :return: the function which reflects the tile
    """
    return lambda x: tuple(x[(zero_to - i) % len(x)] for i in range(len(x)))


def rotation_group(edge_count: int) -> Generator:
    """
    Generates the rotation group associated with regular polygons with edge_count edges

    :param edge_count: the number of edges of the polygons being rotated
    :return: a generator listing all rotations
    """
    return (rotate_tile(zero_target) for zero_target in range(edge_count))

group = rotation_group(4)
print(type(group))

# maybe update this to return generator instead of tuple
def dihedral_group(edge_count: int) -> Generator:
    """
    Generates the dihedral group associated with regular polygons with edge_count edges

    :param edge_count: the number of edges of the polygons being transformed
    :return: a generator listing all reflections and rotations
    """
    return (action for action in chain(
        (rotate_tile(zero_target) for zero_target in range(edge_count)),
        (reflect_tile(zero_target) for zero_target in range(edge_count))))


# edge_count and group need to match up in some way
def partition_tiles(edge_count: int,
                    edge_types: int,
                    group: Callable) -> dict[tuple[int, ...], tuple[tuple[int, ...], ...]]:
    """
    Returns a partition of the tiles by orbit, with a unique key (the minimal tile) provided for each orbit

    :param edge_count: the number of edges of the regular polygon being transformed
    :param edge_types: the number of edge types of the regular polygon being transformed
    :param group: a function which generates the action group (will be called with edge_count to generate actions)
    :return: a dictionary whose values are the orbits and whose keys are the minimal tile in each orbit
    """
    dictionary = {}
    for tile in all_fixed_tiles(edge_count, edge_types):
        orbit = tuple(tile_orbit(tile, group(edge_count)))
        ic(orbit)
        key = min(orbit)
        dictionary[key] = orbit
    return dictionary


def onesided_tiles(edge_count: int,
                   edge_types: int) -> dict[tuple[int, ...], tuple[tuple[int, ...], ...]]:
    """
    Computes all one-sided tiles as a dictionary

    :param edge_count: the number of edges of the regular polygon
    :param edge_types: the number of edge types of the regular polygon
    :return: a dictionary whose values are the orbits and whose keys are the minimal tile in each orbit
    """
    return partition_tiles(edge_count, edge_types, rotation_group)


def count_onesided_tiles(edge_count: int, edge_types: int) -> int:
    """
    Determines the number of distinct one-sided tiles of a regular polygon

    :param edge_count: the number of edges of the regular polygon
    :param edge_types: the number of edge types
    :return: the number of distinct one-sided tiles
    """
    return len(onesided_tiles(edge_count, edge_types))


def free_tiles(edge_count: int,
               edge_types: int) -> dict[tuple[int, ...], tuple[tuple[int, ...], ...]]:
    """
    Computes all free tiles as a dictionary

    :param edge_count: the number of edges of the regular polygon
    :param edge_types: the number of edge types of the regular polygon
    :return: a dictionary whose values are the orbits and whose keys are the minimal tile in each orbit
    """
    return partition_tiles(edge_count, edge_types, dihedral_group)


def count_free_tiles(edge_count: int, edge_types: int) -> int:
    """
    Determines the number of distinct free tiles of a regular polygon

    :param edge_count: the number of edges of the regular polygon
    :param edge_types: the number of edge types
    :return: the number of distinct free tiles
    """
    return len(free_tiles(edge_count, edge_types))


# todo: cascadia & galaxy trucker examples cannot be done "automatically"
#   as they do not start with "all_fixed_tiles"

if __name__ == "__main__":
    ...
