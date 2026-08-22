from risk.risk_engine import RiskEngine


def test_position_sizing_respects_lot_size():
    result = RiskEngine().size_position(capital=100000, entry=100, stop=95, lot_size=25)
    assert result.quantity % 25 == 0
    assert result.quantity > 0


def test_risk_reward_gate():
    engine = RiskEngine()
    assert not engine.validate_trade(entry=100, stop=99, target=101, capital=100000).approved
    assert engine.validate_trade(entry=100, stop=99, target=103, capital=100000).approved
