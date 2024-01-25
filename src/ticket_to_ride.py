import sympy as sp
from collections import defaultdict

from icecream import ic  # type: ignore

import adjacency_matrices as am

ic.disable()

x = sp.Symbol("x")
v = sp.Symbol("v")
COLORS = (
    b,
    k,
    g,
    p,
    r,
    t,
    w,
    y,
) = sp.symbols(
    """
    b,
    k,
    g,
    p,
    r,
    t,
    w,
    y,
"""
)

POINTS = {1: 1, 2: 2, 3: 4, 4: 7, 5: 10, 6: 15}


def weight_by_adjacency(_string: str) -> sp.Expr:
    return sp.parsing.sympy_parser.parse_expr('1')


def weight_by_cost(string: str) -> sp.Expr:
    return x ** len(string)


def weight_by_points(string: str) -> sp.Expr:
    return v ** POINTS[len(string)]


def weight_by_cost_and_points(string: str) -> sp.Expr:
    return weight_by_cost(string) * weight_by_points(string)


def weight_by_card_color(string: str) -> sp.Expr:
    weight = sp.parsing.sympy_parser.parse_expr('1')
    for char in string:
        weight *= sp.parsing.sympy_parser.parse_expr(char)
    return weight


def weight_by_card_color_and_points(string: str) -> sp.Expr:
    weight = weight_by_points(string)
    for char in string:
        weight *= sp.parsing.sympy_parser.parse_expr(char)
    return weight


def connection_weight(matrix: sp.Matrix, dest: sp.Symbol, orig: sp.Symbol) -> sp.Expr:
    return matrix[CITIES.index(dest), CITIES.index(orig)]


NE_CITIES = (
    montreal,
    boston,
    toronto,
    new_york,
    pittsburgh,
    washington,
) = sp.symbols(
    """
    montreal,
    boston,
    toronto,
    new_york,
    pittsburgh,
    washington,
"""
)

NE_CONNECTIONS: am.LabeledConnections = {
    montreal: {toronto: ("xx",), new_york: ("bbb",)},
    toronto: {montreal: ("xx",), pittsburgh: ("xx",)},
    pittsburgh: {toronto: ("xx",), new_york: ("ww", "gg")},
    new_york: {
        montreal: ("bbb",),
        boston: ("rr", "yy"),
        washington: ("tt", "bb"),
        pittsburgh: ("gg", "ww"),
    },
    boston: {new_york: ("yy", "rr")},
    washington: {new_york: ("tt", "bb")},
}


assert am.vertex_degrees_multi(NE_CONNECTIONS) == {
    montreal: 2,
    boston: 2,
    toronto: 2,
    new_york: 7,
    pittsburgh: 3,
    washington: 2,
}

NE_ADJACENCY_MATRIX = am.build_weighted_matrix_symbolic(
    NE_CITIES, NE_CONNECTIONS, weight_by_adjacency
)
NE_COST_MATRIX = am.build_weighted_matrix_symbolic(NE_CITIES, NE_CONNECTIONS, weight_by_cost)
NE_POINTS_MATRIX = am.build_weighted_matrix_symbolic(NE_CITIES, NE_CONNECTIONS, weight_by_points)
NE_COMBINED_MATRIX = am.build_weighted_matrix_symbolic(
    NE_CITIES, NE_CONNECTIONS, weight_by_cost_and_points
)
NE_COLOR_MATRIX = am.build_weighted_matrix_symbolic(
    NE_CITIES, NE_CONNECTIONS, weight_by_card_color
)

assert NE_ADJACENCY_MATRIX.is_symmetric()
assert NE_COST_MATRIX.is_symmetric()
assert NE_POINTS_MATRIX.is_symmetric()
assert NE_COLOR_MATRIX.is_symmetric()

CITIES = (
    vancouver,
    calgary,
    winnipeg,
    sault_st_marie,
    montreal,
    seattle,
    helena,
    duluth,
    toronto,
    boston,
    portland,
    salt_lake_city,
    denver,
    omaha,
    chicago,
    pittsburgh,
    new_york,
    san_francisco,
    los_angeles,
    las_vegas,
    phoenix,
    santa_fe,
    oklahoma_city,
    kansas_city,
    saint_louis,
    nashville,
    raleigh,
    washington,
    el_paso,
    dallas,
    little_rock,
    new_orleans,
    atlanta,
    charleston,
    houston,
    miami,
) = sp.symbols(
    """
    vancouver,
    calgary,
    winnipeg,
    sault_st_marie,
    montreal,
    seattle,
    helena,
    duluth,
    toronto,
    boston,
    portland,
    salt_lake_city,
    denver,
    omaha,
    chicago,
    pittsburgh,
    new_york,
    san_francisco,
    los_angeles,
    las_vegas,
    phoenix,
    santa_fe,
    oklahoma_city,
    kansas_city,
    saint_louis,
    nashville,
    raleigh,
    washington,
    el_paso,
    dallas,
    little_rock,
    new_orleans,
    atlanta,
    charleston,
    houston,
    miami,
"""
)

CONNECTIONS: am.LabeledConnections = {
    vancouver: {calgary: ("xxx",), seattle: ("x", "x")},
    calgary: {
        winnipeg: ("wwwwww",),
        vancouver: ("xxx",),
        seattle: ("xxxx",),
        helena: ("xxxx",),
    },
    winnipeg: {
        sault_st_marie: ("xxxxxx",),
        calgary: ("wwwwww",),
        helena: ("bbbb",),
        duluth: ("kkkk",),
    },
    sault_st_marie: {
        montreal: ("kkkkk",),
        winnipeg: ("xxxxxx",),
        duluth: ("xxx",),
        toronto: ("xx",),
    },
    montreal: {
        sault_st_marie: ("kkkkk",),
        toronto: ("xxx",),
        new_york: ("bbb",),
        boston: ("xx", "xx"),
    },
    seattle: {
        calgary: ("xxxx",),
        vancouver: ("x", "x"),
        portland: ("x", "x"),
        helena: ("yyyyyy",),
    },
    helena: {
        duluth: ("tttttt",),
        winnipeg: ("bbbb",),
        calgary: ("xxxx",),
        seattle: ("yyyyyy",),
        salt_lake_city: ("ppp",),
        denver: ("gggg",),
        omaha: ("rrrrr",),
    },
    duluth: {
        toronto: ("pppppp",),
        sault_st_marie: ("xxx",),
        winnipeg: ("kkkk",),
        helena: ("tttttt",),
        omaha: ("xx", "xx"),
        chicago: ("rrr",),
    },
    toronto: {
        montreal: ("xxx",),
        sault_st_marie: ("xx",),
        duluth: ("pppppp",),
        chicago: ("wwww",),
        pittsburgh: ("xx",),
    },
    boston: {montreal: ("xx", "xx"), new_york: ("yy", "rr")},
    portland: {
        seattle: ("x", "x"),
        san_francisco: ("ggggg", "ppppp"),
        salt_lake_city: ("bbbbbb",),
    },
    salt_lake_city: {
        helena: ("ppp",),
        portland: ("bbbbbb",),
        san_francisco: ("ttttt", "wwwww"),
        las_vegas: ("ttt",),
        denver: ("rrr", "yyy"),
    },
    denver: {
        kansas_city: ("kkkk", "tttt"),
        omaha: ("pppp",),
        helena: ("gggg",),
        salt_lake_city: ("rrr", "yyy"),
        phoenix: ("wwwww",),
        santa_fe: ("xx",),
        oklahoma_city: ("rrrr",),
    },
    omaha: {
        chicago: ("bbbb",),
        duluth: ("xx", "xx"),
        helena: ("rrrrr",),
        denver: ("pppp",),
        kansas_city: ("x", "x"),
    },
    chicago: {
        pittsburgh: ("ttt", "kkk"),
        toronto: ("wwww",),
        duluth: ("rrr",),
        omaha: ("bbbb",),
        saint_louis: ("gg", "ww"),
    },
    pittsburgh: {
        new_york: ("ww", "gg"),
        toronto: ("xx",),
        chicago: ("ttt", "kkk"),
        saint_louis: ("ggggg",),
        nashville: ("yyyy",),
        raleigh: ("xx",),
        washington: ("xx",),
    },
    new_york: {
        boston: ("yy", "rr"),
        montreal: ("bbb",),
        pittsburgh: ("ww", "gg"),
        washington: ("tt", "kk"),
    },
    san_francisco: {
        salt_lake_city: ("ttttt", "wwwww"),
        portland: ("ggggg", "ppppp"),
        los_angeles: ("ppp", "yyy"),
    },
    los_angeles: {
        las_vegas: ("xx",),
        san_francisco: ("ppp", "yyy"),
        el_paso: ("kkkkkk",),
        phoenix: ("xxx",),
    },
    las_vegas: {salt_lake_city: ("ttt",), los_angeles: ("xx",)},
    phoenix: {
        santa_fe: ("xxx",),
        denver: ("wwwww",),
        los_angeles: ("xxx",),
        el_paso: ("xxx",),
    },
    santa_fe: {
        oklahoma_city: ("bbb",),
        denver: ("xx",),
        phoenix: ("xxx",),
        el_paso: ("xx",),
    },
    oklahoma_city: {
        kansas_city: ("xx", "xx"),
        denver: ("rrrr",),
        santa_fe: ("bbb",),
        el_paso: ("yyyyy",),
        dallas: ("xx", "xx"),
        little_rock: ("xx",),
    },
    kansas_city: {
        saint_louis: ("bb", "pp"),
        omaha: ("x", "x"),
        denver: ("kkkk", "tttt"),
        oklahoma_city: ("xx", "xx"),
    },
    saint_louis: {
        pittsburgh: ("ggggg",),
        chicago: ("gg", "ww"),
        kansas_city: ("bb", "pp"),
        little_rock: ("xx",),
        nashville: ("xx",),
    },
    little_rock: {
        nashville: ("www",),
        saint_louis: ("xx",),
        oklahoma_city: ("xx",),
        dallas: ("xx",),
        new_orleans: ("ggg",),
    },
    nashville: {
        raleigh: ("kkk",),
        pittsburgh: ("yyyy",),
        saint_louis: ("xx",),
        little_rock: ("www",),
        atlanta: ("x",),
    },
    raleigh: {
        washington: ("xx", "xx"),
        pittsburgh: ("xx",),
        nashville: ("kkk",),
        atlanta: ("xx", "xx"),
        charleston: ("xx",),
    },
    washington: {
        new_york: ("kk", "tt"),
        pittsburgh: ("xx",),
        raleigh: ("xx", "xx"),
    },
    el_paso: {
        dallas: ("rrrr",),
        oklahoma_city: ("yyyyy",),
        santa_fe: ("xx",),
        phoenix: ("xxx",),
        los_angeles: ("kkkkkk",),
        houston: ("gggggg",),
    },
    dallas: {
        little_rock: ("xx",),
        oklahoma_city: ("xx", "xx"),
        el_paso: ("rrrr",),
        houston: ("x", "x"),
    },
    houston: {
        new_orleans: ("xx",),
        dallas: ("x", "x"),
        el_paso: ("gggggg",),
    },
    new_orleans: {
        atlanta: ("yyyy", "tttt"),
        little_rock: ("ggg",),
        houston: ("xx",),
        miami: ("rrrrrr",),
    },
    atlanta: {
        charleston: ("xx",),
        raleigh: ("xx", "xx"),
        nashville: ("x",),
        new_orleans: ("yyyy", "tttt"),
        miami: ("bbbbb",),
    },
    charleston: {
        raleigh: ("xx",),
        atlanta: ("xx",),
        miami: ("pppp",),
    },
    miami: {
        charleston: ("pppp",),
        atlanta: ("bbbbb",),
        new_orleans: ("rrrrrr",),
    },
}

assert am.vertex_degrees_multi(CONNECTIONS) == {
    vancouver: 3,
    calgary: 4,
    winnipeg: 4,
    sault_st_marie: 4,
    montreal: 5,
    seattle: 6,
    helena: 7,
    duluth: 7,
    toronto: 5,
    boston: 4,
    portland: 5,
    salt_lake_city: 7,
    denver: 9,
    omaha: 7,
    chicago: 7,
    pittsburgh: 9,
    new_york: 7,
    san_francisco: 6,
    los_angeles: 5,
    las_vegas: 2,
    phoenix: 4,
    santa_fe: 4,
    oklahoma_city: 8,
    kansas_city: 8,
    saint_louis: 7,
    nashville: 5,
    raleigh: 7,
    washington: 5,
    el_paso: 6,
    dallas: 6,
    little_rock: 5,
    new_orleans: 5,
    atlanta: 7,
    charleston: 3,
    houston: 4,
    miami: 3,
}

ADJACENCY_MATRIX = am.build_weighted_matrix_symbolic(CITIES, CONNECTIONS, weight_by_adjacency)
COST_MATRIX = am.build_weighted_matrix_symbolic(CITIES, CONNECTIONS, weight_by_cost)
POINTS_MATRIX = am.build_weighted_matrix_symbolic(CITIES, CONNECTIONS, weight_by_points)
COMBINED_MATRIX = am.build_weighted_matrix_symbolic(
    CITIES, CONNECTIONS, weight_by_cost_and_points
)
COLOR_POINTS_MATRIX = am.build_weighted_matrix_symbolic(
    CITIES, CONNECTIONS, weight_by_card_color_and_points
)
CITY_POINTS_MATRIX = sp.Matrix(
    len(CITIES),
    len(CITIES),
    lambda row, col: CITIES[row] * POINTS_MATRIX[row, col],
)
COLOR_CITY_POINTS_MATRIX = sp.Matrix(
    len(CITIES),
    len(CITIES),
    lambda row, col: CITIES[row] * COLOR_POINTS_MATRIX[row, col],
)

assert ADJACENCY_MATRIX.is_symmetric()
assert COST_MATRIX.is_symmetric()
assert POINTS_MATRIX.is_symmetric()
assert COMBINED_MATRIX.is_symmetric()
assert COLOR_POINTS_MATRIX.is_symmetric()

if __name__ == "__main__":
    ...
