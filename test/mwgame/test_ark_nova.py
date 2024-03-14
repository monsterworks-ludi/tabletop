from mwmath.combinations import fact, perm, comb

def test_ark_nova() -> None:
        # Example, p. 12
        assert perm(11, 2) / fact(2) == 55
        assert comb(11, 2) == 55
        assert perm(212, 8) / fact(8) == 88_535_640_906_570
        assert comb(212, 8) == 88_535_640_906_570
        assert perm(11, 2) / fact(2) * perm(212, 8) / fact(8) == 4_869_460_249_861_350

if __name__ == "__main__":
    ...
