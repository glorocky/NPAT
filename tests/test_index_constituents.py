from data.reference.constituent_loader import ConstituentLoader


def test_selected_index_constituents_are_not_always_nifty50():
    nifty = ConstituentLoader.load_for_index("NIFTY", "NSE")
    bank = ConstituentLoader.load_for_index("BANKNIFTY", "NSE")
    fin = ConstituentLoader.load_for_index("FINNIFTY", "NSE")
    mid = ConstituentLoader.load_for_index("MIDCPNIFTY", "NSE")

    assert len(nifty) == 50
    assert len(bank) == 14
    assert len(fin) == 20
    assert len(mid) == 25
    assert set(bank.symbol) != set(nifty.symbol)
    assert set(fin.symbol) != set(nifty.symbol)


def test_bse_indices_use_bse_exchange_reference():
    sensex = ConstituentLoader.load_for_index("SENSEX", "BSE")
    bankex = ConstituentLoader.load_for_index("BANKEX", "BSE")

    assert len(sensex) == 30
    assert len(bankex) == 14
    assert set(sensex.exchange) == {"BSE"}
    assert set(bankex.exchange) == {"BSE"}
