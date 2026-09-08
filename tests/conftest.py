import pytest
from unittest.mock import MagicMock
from api.services.risk_manager import Signal
from api.config import Settings


def make_signal(**overrides):
    defaults = {
        "module_id": "test-module",
        "market_id": "test-market",
        "bracket": "100-119",
        "side": "BUY",
        "price": 0.30,
        "size": 20.0,
        "token_id": "tok-test-1",
        "fair_value": 0.35,
        "edge": 0.05,
        "auction_slug": "elon-musk-of-tweets-test",
        "spread": 0.01,
        "best_bid": 0.29,
        "best_ask": 0.31,
        "is_exit": False,
        "metadata": {},
    }
    defaults.update(overrides)
    return Signal(**defaults)


@pytest.fixture
def signal():
    return make_signal()


@pytest.fixture
def settings():
    return Settings(
        paper_mode=True,
        bankroll=1000.0,
        max_portfolio_exposure=0.50,
        max_single_market_exposure=0.15,
        max_correlated_exposure=0.30,
        daily_loss_limit=0.05,
        weekly_loss_limit=0.10,
        max_drawdown=0.15,
        min_edge_threshold=0.02,
        slippage_tolerance=0.05,
        kelly_fraction=0.25,
        circuit_breaker_enabled=True,
        circuit_breaker_max_consecutive_losses=5,
        circuit_breaker_cooldown_minutes=30,
    )


@pytest.fixture
def mock_supabase():
    sb = MagicMock()
    node = sb.table.return_value
    for name in ("select", "eq", "neq", "in_", "gte", "limit", "upsert",
                 "insert", "update", "order"):
        getattr(node, name).return_value = node
    node.execute.return_value = MagicMock(data=[], count=0)
    return sb
