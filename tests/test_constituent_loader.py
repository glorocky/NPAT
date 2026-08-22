from data.reference.constituent_loader import ConstituentLoader


def test_selected_indexes_have_distinct_constituent_sets():
    nifty = ConstituentLoader.load_for_index("NIFTY")
    bank = ConstituentLoader.load_for_index("BANKNIFTY")
    sensex = ConstituentLoader.load_for_index("SENSEX", "BSE")
    assert len(nifty) == 50
    assert len(bank) >= 10
    assert len(sensex) >= 20
    assert set(nifty.symbol) != set(bank.symbol)
    assert set(bank.symbol) != set(sensex.symbol)
