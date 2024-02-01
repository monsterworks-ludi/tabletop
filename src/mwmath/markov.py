import sympy as sp
from icecream import ic  # type: ignore

def mat_max(matrix):
    return max(abs(matrix.row(i)[j]) for i in range(matrix.rows) for j in range(matrix.cols))


def rat_mat(mat: list[list[int]], q: int, *, exact=True) -> sp.Matrix:
    if exact:
        return sp.Rational(1, q) * sp.Matrix(mat)
    else:
        return 1 / q * sp.Matrix(mat)


def transition_matrix(states, transition_distribution):
    return sp.Matrix(
        [
            [col[row] if row in col else 0 for row in range(1, 1 + states)]
            for col in [transition_distribution(i) for i in range(1, 1 + states)]
        ]
    ).transpose()


def markov(q, r) -> sp.Matrix:
    if not q.cols == r.cols:
        raise sp.ShapeError(
            f"The matrices have incompatible number of cols ({q.cols} and {r.cols})"
        )
    if not q.is_square:
        raise sp.ShapeError(f"The matrix q is not square ({q.rows} x {q.cols})")

    qz = q.row_join(sp.zeros(1, r.rows))
    ri = r.row_join(sp.eye(r.rows))

    p = qz.col_join(ri)

    return p


def markov_n(q: sp.Matrix) -> sp.Matrix:
    return (sp.eye(q.cols) - q).inv()


def to_infinity(mat: sp.Matrix) -> sp.Matrix:
    and_beyond = sp.Symbol("and_beyond")
    matoo = (mat**and_beyond).applyfunc(
        lambda expr: sp.limit(expr, and_beyond, sp.oo)
    )
    return matoo


def distribution_to_column(state_count, distribution):
    prob_list = []
    for state in range(1, state_count + 1):
        prob_list.append([distribution[state]] if state in distribution else [0])
    return sp.Matrix(prob_list)


def is_distribution(dist):
    return abs(sum(value for value in dist.values()) - 1) < 10**-15

def zero():
    return sp.Rational(0, 1)
