import re
from collections import defaultdict

from pytest_check import check

from mwgame.letter_jam import mux_word, search_scrabble, indexed_words, bad_pairs

def test_gnomes():
    with check():
        # calculations on page 166
        assert (3 + 4) % 5 == 2
        assert (8 + 7) % 5 == 0
        assert (3 - 4) % 5 == 4
        assert (3 * 4) % 5 == 2
    # Leading 0s in lists allow us to use gnome numbers as indices in the calculations
    colors = [0, 1, 3, 1, 2, 0, 1]
    with check():
        # Table 9.1
        expected_sums = [0, 2, 0, 2, 1, 3, 2]
        expected_guesses = [0, 4, 2, 1, 3, 2, 4]
        for gnome_number in range(1, len(colors)):
            gnome_sum = sum(color for index, color in enumerate(colors) if index != gnome_number)
            assert gnome_sum % 5 == expected_sums[gnome_number]
            assert (gnome_number - gnome_sum) % 5 == expected_guesses[gnome_number]
    with check():
        # Table 9.2
        signal = sum(color for index, color in enumerate(colors) if index != 1) % 5
        assert signal == 2
        expected_sums = [0, 2, 4, 1, 0, 2, 1]
        for gnome_number in range(2, len(colors)):
            gnome_sum = sum(color for index, color in enumerate(colors) if index not in {1, gnome_number})
            assert gnome_sum % 5 == expected_sums[gnome_number]
            assert (signal - gnome_sum) % 5 == colors[gnome_number]

def test_mux():
    # Example, p. X, see Errata
    assert mux_word('BLCNO') == 17

def test_scrabble():
    assert bad_pairs(search=search_scrabble) == {('F', 'C'), ('F', 'K'), ('G', 'C'), ('N', 'C'), ('U', 'W')}

def test_nltk():
    assert bad_pairs() == {('F', 'C'), ('F', 'H'), ('F', 'K'), ('L', 'H'), ('G', 'C'), ('U', 'W')}

def test_differences():
    scrabble_words = indexed_words(search=search_scrabble)
    nltk_words = indexed_words()
    with check():
        assert bad_pairs(search=search_scrabble) - bad_pairs() == {('N', 'C')}
    with check():
        assert nltk_words[('N', 'C')] == {'NICI'}
    with check():
        assert bad_pairs() - bad_pairs(search=search_scrabble) == {('F', 'H'), ('L', 'H')}
    with check():
        assert scrabble_words[('F', 'H')] == {'FOH', 'FAH', 'FEH'}
    with check():
        assert scrabble_words[('L', 'H')] == {'LAH', 'LAHAL'}

def test_job_clue():

    # player with the O
    pattern = re.compile(f"^[A-Z][A-Z]B$")
    words = search_scrabble(pattern)
    with check():
        assert len(words) == 57
    letters = defaultdict(set)
    for word in words:
        letters[word[1]].add(word)
    with check():
        assert len(letters) == 8

    # player with the B
    pattern = re.compile(f"^[A-Z]O[A-Z]$")
    words = search_scrabble(pattern)
    with check():
        assert len(words) == 239
    letters = defaultdict(set)
    for word in words:
        letters[word[2]].add(word)
    with check():
        assert len(letters) == 24
    with check():
        assert 'J' not in letters and 'Q' not in letters

def test_balloon_clue():

    # player with the B
    pattern = re.compile(f"^[A-Z][A-Z]LLOON$")
    words = search_scrabble(pattern)
    print(words)
    letters = {word[0] for word in words}
    with check():
        assert len(letters) == 2
    with check():
        assert letters == {'B', 'G'}

    # player with the L
    pattern = re.compile(f"^B[A-Z](?P<letter>[A-Z])(?P=letter)OON$")
    words = search_scrabble(pattern)
    letters = {word[2] for word in words}
    with check():
        assert len(letters) == 3
    with check():
        assert letters == {'L', 'F', 'S'}

    # player with the O
    pattern = re.compile(f"^B[A-Z]LL(?P<letter>[A-Z])(?P=letter)N$")
    words = search_scrabble(pattern)
    letters = {word[4] for word in words}
    with check():
        assert len(letters) == 1
    with check():
        assert letters == {'O'}

    # player with the N
    pattern = re.compile(f"^B[A-Z]LLOO[A-Z]$")
    words = search_scrabble(pattern)
    letters = {word[6] for word in words}
    with check():
        assert len(letters) == 1
    with check():
        assert letters == {'N'}
