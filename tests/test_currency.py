from src.currency import convert_to_byn


def test_convert_byn_to_itself():
    assert convert_to_byn(100, 'BYN') == 100


def test_convert_none():
    assert convert_to_byn(None, "USD") is None