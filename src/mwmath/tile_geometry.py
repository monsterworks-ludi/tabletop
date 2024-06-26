import sympy as sp

def interior_percentage(number_of_edges: int) -> sp.Rational:
    """
    Computes the percentage of a regular polygon closer to the center than to any point on the edge.

    For derivation of the formula, see https://math.stackexchange.com/questions/1688936/

    :param number_of_edges: the number of edges of the regular polygon
    :return: the percentage of the polygon closer to the center than the edge
    """
    x = sp.symbols("x")
    return sp.integrate(
        (1 + sp.cos(x)) ** (-2) / 2, (x, 0, sp.pi / number_of_edges)
    ) / (sp.tan(sp.pi / number_of_edges) / 2)


if __name__ == "__main__":
    ...
