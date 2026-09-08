from unittest.mock import MagicMock, patch

import pytest

from api.services.risk_manager import check
from tests.conftest import make_signal


@pytest.fixture(autouse=True)
def _fixed_settings(settings):
    with patch("api.services.risk_manager.get_settings", return_value=settings):
        yield


def _chain_sb(data=None, count=0):
    sb = MagicMock()
    node = sb.table.return_value
    for name in ("select", "eq", "neq", "in_", "gte", "limit", "upsert",
                 "insert", "update"):
        getattr(node, name).return_value = node
    node.execute.return_value = MagicMock(data=data or [], count=count)
    return sb


def _pass_patches():
    return (
        patch("api.services.risk_manager._book_depth_shares", return_value=1000.0),
        patch("api.modules.shared.config_store.module_bankroll", return_value=1000.0),
        patch("api.services.risk_manager._drawdown_exceeded", return_value=False),
        patch("api.services.risk_manager._realized_pnl_since", return_value=0.0),
        patch("api.services.risk_manager._correlated_exposure", return_value=0.0),
        patch("api.services.risk_manager._module_exposure", return_value=0.0),
        patch("api.services.risk_manager._open_exposure", return_value=(0.0, {})),
        patch("api.services.risk_manager.get_supabase", return_value=_chain_sb()),
    )


class TestEarlyRejects:
    def test_bad_price_zero(self):
        v = check(make_signal(price=0))
        assert not v.approved
        assert "bad_price" in v.reason

    def test_bad_price_one(self):
        v = check(make_signal(price=1.0))
        assert not v.approved
        assert "bad_price" in v.reason

    def test_bad_size(self):
        v = check(make_signal(size=0))
        assert not v.approved
        assert v.reason == "bad_size"

    def test_missing_token_id(self):
        v = check(make_signal(token_id=""))
        assert not v.approved
        assert v.reason == "missing_token_id"


class TestExitsAndBreaker:
    def test_sell_bypasses_entry_gates(self):
        v = check(make_signal(side="SELL", spread=None, best_ask=None, edge=None))
        assert v.approved
        assert v.reason == "exit"

    def test_is_exit_bypasses_entry_gates(self):
        v = check(make_signal(is_exit=True, spread=None, edge=None))
        assert v.approved
        assert v.reason == "exit"

    def test_breaker_blocks_entries(self):
        v = check(make_signal(), breaker_tripped=True)
        assert not v.approved
        assert v.reason == "circuit_breaker"

    def test_breaker_does_not_block_exits(self):
        v = check(make_signal(side="SELL"), breaker_tripped=True)
        assert v.approved
        assert v.reason == "exit"


class TestSpreadAndEdge:
    def test_no_spread_data_fails_closed(self):
        v = check(make_signal(spread=None, best_ask=0.31))
        assert not v.approved
        assert v.reason == "no_spread_data"

    def test_spread_over_tolerance_fails(self):
        v = check(make_signal(spread=0.20, best_ask=0.50))
        assert not v.approved
        assert v.reason.startswith("spread_")

    def test_missing_edge_fails(self):
        v = check(make_signal(edge=None))
        assert not v.approved
        assert "edge_" in v.reason

    def test_edge_below_floor_fails(self):
        v = check(make_signal(edge=0.01))
        assert not v.approved
        assert "edge_" in v.reason

    def test_dust_notional_fails(self):
        v = check(make_signal(price=0.10, size=5))
        assert not v.approved
        assert v.reason == "stake_below_floor"


class TestDatabaseGates:
    def test_duplicate_resting_order_rejected(self):
        with patch("api.services.risk_manager.get_supabase", return_value=_chain_sb(count=1)):
            v = check(make_signal())
        assert not v.approved
        assert v.reason == "duplicate_resting_order"

    def test_db_error_fails_closed(self):
        sb = MagicMock()
        sb.table.side_effect = Exception("DB down")
        with patch("api.services.risk_manager.get_supabase", return_value=sb):
            v = check(make_signal())
        assert not v.approved
        assert v.reason.startswith("db_error:")

    def test_single_market_cap(self):
        # bankroll 1000 * 0.15 = 150; existing 140 + notional 6 = 146? 
        # make_signal notional = 0.30 * 20 = 6. Need existing > 144.
        patches = _pass_patches()
        patches = patches[:-2] + (
            patch("api.services.risk_manager._open_exposure",
                  return_value=(200.0, {"test-market": 148.0})),
            patch("api.services.risk_manager.get_supabase", return_value=_chain_sb()),
        )
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7]:
            v = check(make_signal())
        assert not v.approved
        assert v.reason == "single_market_cap"

    def test_portfolio_cap(self):
        patches = _pass_patches()
        patches = patches[:-2] + (
            patch("api.services.risk_manager._open_exposure",
                  return_value=(496.0, {})),
            patch("api.services.risk_manager.get_supabase", return_value=_chain_sb()),
        )
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7]:
            v = check(make_signal())
        assert not v.approved
        assert v.reason == "portfolio_cap"

    def test_daily_loss_limit(self):
        patches = _pass_patches()
        patches = list(patches)
        patches[3] = patch("api.services.risk_manager._realized_pnl_since", return_value=-51.0)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7]:
            v = check(make_signal())
        assert not v.approved
        assert v.reason == "daily_loss_limit"


class TestDepthAndPass:
    def test_no_depth_data_fails_closed(self):
        patches = _pass_patches()
        patches = list(patches)
        patches[0] = patch("api.services.risk_manager._book_depth_shares", return_value=None)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7]:
            v = check(make_signal())
        assert not v.approved
        assert v.reason == "no_depth_data"

    def test_order_exceeds_depth_fraction(self):
        patches = _pass_patches()
        patches = list(patches)
        patches[0] = patch("api.services.risk_manager._book_depth_shares", return_value=50.0)
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7]:
            v = check(make_signal(size=20))
        assert not v.approved
        assert v.reason.startswith("depth_")

    def test_valid_buy_passes(self):
        patches = _pass_patches()
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7]:
            v = check(make_signal())
        assert v.approved, v.reason
        assert v.reason == "ok"
