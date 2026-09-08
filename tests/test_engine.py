from unittest.mock import MagicMock, patch

from api.services.engine import Engine
from api.services.executor import PaperExecutor


class TestEngineInit:
    def test_stores_registry_and_paper_executor(self):
        registry = MagicMock()
        engine = Engine(registry)
        assert engine.registry is registry
        assert isinstance(engine.paper, PaperExecutor)
        assert engine.cycles == 0


class TestEngineCycle:
    @patch("api.services.engine.get_supabase")
    def test_modules_query_failure_returns_empty_summary(self, mock_sb):
        mock_sb.return_value.table.return_value.select.return_value.neq.return_value.execute.side_effect = (
            Exception("DB down")
        )
        summary = Engine(MagicMock()).cycle()
        assert summary["modules"] == 0
        assert summary["signals"] == 0
        assert summary["approved"] == 0

    @patch("api.services.halt.is_halted", return_value=False)
    @patch("api.services.position_manager.sweep_stuck_closing")
    @patch("api.services.engine.get_supabase")
    def test_empty_module_list_still_sweeps_paper_fills(
        self, mock_sb, _sweep, _halt
    ):
        mock_sb.return_value.table.return_value.select.return_value.neq.return_value.execute.return_value.data = []
        engine = Engine(MagicMock())
        engine.paper = MagicMock()
        engine.paper.check_fills.return_value = 2
        engine._expire_stale_orders = MagicMock()
        engine._write_price_snapshots = MagicMock()
        engine._live_quotes = MagicMock(return_value={})

        summary = engine.cycle()
        assert summary["paper_fills"] == 2
        assert summary["modules"] == 0
        engine.paper.check_fills.assert_called_once()
