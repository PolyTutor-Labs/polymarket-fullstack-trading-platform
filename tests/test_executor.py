import pytest
from unittest.mock import MagicMock, patch

from api.services.executor import LiveExecutor, PaperExecutor
from tests.conftest import make_signal


class TestPaperExecutor:
    @patch("api.services.executor.get_supabase")
    def test_execute_rests_open_maker_order(self, mock_sb):
        sb = MagicMock()
        mock_sb.return_value = sb
        result = PaperExecutor().execute(make_signal(price=0.30, size=20))
        assert result["status"] == "open"
        assert result["clob_order_id"].startswith("paper-")
        sb.table.assert_called_with("orders")
        row = sb.table.return_value.insert.call_args[0][0]
        assert row["status"] == "open"
        assert row["post_only"] is True
        assert row["order_type"] == "GTC"
        assert row["price"] == 0.30
        assert row["size"] == 20
        assert row["side"] == "BUY"

    @patch("api.services.executor.get_supabase")
    def test_execute_does_not_write_trades_until_fill(self, mock_sb):
        sb = MagicMock()
        mock_sb.return_value = sb
        PaperExecutor().execute(make_signal())
        tables = [call.args[0] for call in sb.table.call_args_list]
        assert "orders" in tables
        assert "trades" not in tables


class TestLiveExecutor:
    @patch("api.services.clob.get_clob_client")
    @patch("api.services.executor.get_settings")
    def test_refuses_without_dual_live_guard(self, mock_gs, mock_clob):
        mock_gs.return_value = MagicMock(
            environment="development", paper_mode=True, allow_live_trading=False
        )
        with pytest.raises(RuntimeError, match="dual live guard"):
            LiveExecutor()
        mock_clob.assert_not_called()

    @patch("api.services.clob.get_clob_client")
    @patch("api.services.executor.get_settings")
    def test_missing_private_key_raises(self, mock_gs, mock_clob):
        mock_gs.return_value = MagicMock(
            environment="production", paper_mode=False, allow_live_trading=True
        )
        mock_clob.side_effect = RuntimeError("Missing POLYMARKET_PRIVATE_KEY")
        with pytest.raises(RuntimeError, match="Missing POLYMARKET_PRIVATE_KEY"):
            LiveExecutor()

    @patch("api.services.order_state.record_submitted")
    @patch("api.services.clob.place_post_only")
    @patch("api.services.clob.get_clob_client")
    @patch("api.services.executor.get_settings")
    def test_execute_submits_post_only(self, mock_gs, mock_client, mock_place, mock_rec):
        mock_gs.return_value = MagicMock(
            environment="production", paper_mode=False, allow_live_trading=True
        )
        mock_place.return_value = {"orderID": "oid-1"}
        sig = make_signal()
        result = LiveExecutor().execute(sig)
        assert result == {"status": "submitted", "clob_order_id": "oid-1"}
        mock_place.assert_called_once_with(sig.token_id, sig.side, sig.price, sig.size)
        mock_rec.assert_called_once()

    @patch("api.services.clob.place_post_only")
    @patch("api.services.clob.get_clob_client")
    @patch("api.services.executor.get_settings")
    def test_missing_order_id_is_rejected(self, mock_gs, mock_client, mock_place):
        mock_gs.return_value = MagicMock(
            environment="production", paper_mode=False, allow_live_trading=True
        )
        mock_place.return_value = {"error": "CLOB error"}
        result = LiveExecutor().execute(make_signal())
        assert result["status"] == "rejected"
