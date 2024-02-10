from game.azul import dfs

def test_dfs():
    assert dfs("", 0, ["b", "r", "t"]) == ((+3, -3), ('r', 't', 'b'))
