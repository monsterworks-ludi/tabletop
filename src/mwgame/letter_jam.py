import os
import re
import pickle

from collections import defaultdict

from nltk.corpus import words as nltkwords

def absolute_filename(search):
    """
    Consistent data file naming.

    :param search: the search function to be used, must have the __name__ attribute
    :return: an absolute filename to the parsed search data
    """
    script_dir = os.path.dirname(__file__)
    abs_file_path = os.path.join(script_dir, f"letter_jam_{search.__name__}.pickle")
    return abs_file_path

""" Letters used in Letter Jam game """
LETTERS = 'ABCDEFGHIKLMNOPRSTUWY'
assert len(LETTERS) == 21

def mux_word(letters: str):
    """

    :param letters: the letters to be muxed together
    :return: the signal to be sent associated with the letters
    """
    value = 0
    for letter in letters.upper():
        # index will raise exception if letter is not found
        value += LETTERS.index(letter)
    return value % len(LETTERS)

def search_scrabble(pattern):
    """
    Search using the letter_jam_words.txt file (based on the 2019 Scrabble Dictionary)

    :param pattern: the pattern to search for
    :return: a set of words which match the pattern
    """
    words = set()
    script_path = os.path.dirname(__file__)
    words_path = os.path.join(script_path, 'letter_jam_words.txt')
    with open(words_path) as lexicon:
        for n, line in enumerate(lexicon):
            for match in re.finditer(pattern, line):
                potential_word = match.group().rstrip()
                words.add(potential_word)
    return words
search_scrabble.__name__ = 'scrabble'


def search_nltk(pattern):
    """
    Search using Python's Natural Language Toolkit (NLTK) package

    :param pattern: the pattern to search for
    :return: a set of words which match the pattern
    """
    words = set()
    for word in nltkwords.words():
        for match in re.finditer(pattern, word.upper()):
            potential_word = match.group().rstrip()
            words.add(potential_word)
    return words
search_nltk.__name__ = 'nltk'

def words_using(c1, c2, *, search=search_nltk):
    """
    finds words using wildchar, c1, c2 with c1, c2 as first non-wildcard characters
    words may only use wildchar, c1, and c2

    :param c1: first character
    :param c2: second character
    :param search: the function used to determine valid words
    :return: set of words matching criteria
    """
    words = set()
    # wildcard before first player
    pattern = re.compile(f"^((?P<letter>[^{c2}{c1}])(?P=letter)*{c1}(?P=letter)*{c2}((?P=letter)|{c1}|{c2})*)$")
    words |= search(pattern)
    # wildcard between first and second players
    pattern = re.compile(f"^({c1}(?P<letter>[^{c1}{c2}])(?P=letter)*{c2}((?P=letter)|{c1}|{c2})*)$")
    words |= search(pattern)
    # wildcard after second player
    pattern = re.compile(f"^({c1}{c2}(?P<letter>[^{c1}{c2}])?((?P=letter)|{c1}|{c2})*)$")
    words |= search(pattern)
    return words


def indexed_words(*, search=search_nltk):
    """
    For each pair of letters, determine what words are possible using those two letters (and a wildcard)

    :return:
    """

    filename = absolute_filename(search)
    try:
        letters_dict = pickle.load(open(filename, 'rb'))
    except OSError:
        # 5 minutes for scrabble, 11 minutes for nltk
        letters_dict = {}
        for c1, c2 in [(chr(ord('A') + i), chr(ord('A') + j)) for i in range(26) for j in range(26)]:
            letters_dict[(c1, c2)] = all_words_using(c1, c2, search=search)
        pickle.dump(letters_dict, open(filename, 'wb'))

    return letters_dict


def bad_pairs(*, search=search_nltk):
    """

    :param search: the word list to be used in the search
    :return: all pairs of letters for which a word cannot be found to be used as a signal
    """
    result = set()
    for c1, c2 in [
        (chr(ord('A') + i), chr(ord('A') + j)) for i in range(26) for j in range(26)
        if (chr(ord('A') + i) not in {'J', 'Q', 'V', 'X', 'Z'}
            and chr(ord('A') + j) not in {'J', 'Q', 'V', 'X', 'Z'})
    ]:
        if (c1, c2) not in indexed_words(search=search):
            result.add((c1, c2))
        elif len(indexed_words(search=search)[(c1, c2)]) == 0:
            result.add((c1, c2))
    return result

# Functions below are part of an incomplete analysis of probability of being completely locked out of giving a clue
# This code does not use any pickling, so it will run very slowly

def all_words_using(c1, c2, search=search_nltk):
    """
    finds words using wildchar, c1, c2 with c1, c2 as first non-wildcard characters
    words may use any extra characters after c2

    :param c1: first character
    :param c2: second character
    :param search: the function used to determine valid words
    :return: set of words matching criteria
    """

    words = set()
    # wildcard before first player
    pattern = re.compile(f"^((?P<letter>[A-Z])(?P=letter)*{c1}(?P=letter)*{c2}[A-Z]*)$")
    words |= search(pattern)
    # wildcard between first and second players
    pattern = re.compile(f"^({c1}(?P<letter>[A-Z])(?P=letter)*{c2}[A-Z]*)$")
    words |= search(pattern)
    # wildcard after second player
    pattern = re.compile(f"^({c1}{c2}[A-Z]*)$")
    words |= search(pattern)
    return words

def indexed_words_using(c1, c2, search=search_nltk):
    """

    :param c1: this character must occur in the word before c2
    :param c2: this character must occur in the word after c1
    :param search: the function used to determine valid words
    :return: dictionary whose keys are the remaining necessary letters to create a word and whose values are the words
    """
    words = all_words_using(c1, c2, search=search)
    words_indexed_by_other_letters = defaultdict(set)
    for word in words:
        letters = set(word)
        letters.remove(c1)
        letters.remove(c2)
        letters = frozenset(letters)
        found = False
        bad_keys = set()
        for key in words_indexed_by_other_letters:
            if key == letters:
                words_indexed_by_other_letters[key].add(word)
                found = True
                break
            if key.issubset(letters):
                found = True
                break
            if letters.issubset(key):
                bad_keys.add(key)
                # keep looping, it may be subset of multiple keys
                found = True
        if bad_keys:
            for key in bad_keys:
                del words_indexed_by_other_letters[key]
            words_indexed_by_other_letters[letters].add(word)
        elif not found:
            words_indexed_by_other_letters[letters].add(word)
    words_indexed_by_other_letters = dict(sorted(words_indexed_by_other_letters.items()))

    return words_indexed_by_other_letters

def count_words_using(c1, c2, search=search_nltk):
    """ Attempts to find words with c1 preceding c2.

    This function returns a dictionary:
        whose keys are the number of additional letters required
        whose values are the number of words using that many letters

    :param c1: this character must occur in the word before c2
    :param c2: this character must occur in the word after c1
    :param search: the function used to determine valid words
    :return: a dictionary
    """
    set_words = indexed_words_using(c1, c2, search=search)
    letters_count = defaultdict(int)
    for letters, words in set_words.items():
        letters_count[len(letters)] += len(words)
    return letters_count


if __name__ == "__main__":
    pass
