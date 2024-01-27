import sympy as sp

import tile_geometry as tg


class TestTileGeometry:
    @staticmethod
    def test_interior_percentage() -> None:
        # triangles, p. 31
        assert tg.interior_percentage(3).equals(5 / 27)
        # squares, p. 32
        assert tg.interior_percentage(4).equals((4 * sp.sqrt(2) - 5) / 3)
        # hexagons, p. 33
        assert tg.interior_percentage(6).equals((16 - 9 * sp.sqrt(3)) / sp.sqrt(3))


if __name__ == "__main__":
    ...
