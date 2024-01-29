import sympy as sp


def rat_mat(mat: list[list[int]], q: int, *, exact=True) -> sp.Matrix:
    if exact:
        return sp.Rational(1, q) * sp.Matrix(mat)
    else:
        return 1 / q * sp.Matrix(mat)


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
    and_beyond = sp.Symbol('and_beyond')
    matoo = (mat**and_beyond).applyfunc(lambda expr: sp.limit(expr, and_beyond, sp.oo))
    return matoo


if __name__ == "__main__":
    Q = rat_mat([[5]], 12)
    R = rat_mat([[5], [1], [1]], 12)
    P = sp.Matrix(markov(Q, R))
    print(to_infinity(P))
