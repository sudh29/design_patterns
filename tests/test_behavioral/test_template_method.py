"""Tests for the Template Method pattern implementation."""

from typing import Any

import pytest

from design_patterns.behavioral.template_method import (
    APIDataMiner,
    CSVDataMiner,
    DataMiner,
    JSONDataMiner,
)


class TestCSVDataMiner:
    def test_mine_valid_csv(self) -> None:
        csv_data = "name,score\nAlice,95\nBob,88\n"
        miner = CSVDataMiner()
        result = miner.mine(csv_data)

        assert result["status"] == "success"
        assert result["format"] == "csv"
        assert result["record_count"] == 2
        assert result["records"][0] == {"name": "Alice", "score": "95"}
        assert result["records"][1] == {"name": "Bob", "score": "88"}

    def test_custom_delimiter(self) -> None:
        tsv_data = "name\trole\nCharlie\tLead\n"
        miner = CSVDataMiner(delimiter="\t")
        result = miner.mine(tsv_data)

        assert result["record_count"] == 1
        assert result["records"][0] == {"name": "Charlie", "role": "Lead"}

    def test_empty_csv_content(self) -> None:
        miner = CSVDataMiner()
        result = miner.mine("   \n")
        assert result["record_count"] == 0


class TestJSONDataMiner:
    def test_mine_json_list(self) -> None:
        raw_json = '[{"user": "dev1", "status": "active"}, {"user": "dev2", "status": "idle"}]'
        miner = JSONDataMiner()
        result = miner.mine(raw_json)

        assert result["format"] == "json"
        assert result["record_count"] == 2
        assert result["records"][0] == {"user": "dev1", "status": "active"}

    def test_mine_single_json_object(self) -> None:
        raw_json = '{"server": "prod-1", "healthy": true}'
        miner = JSONDataMiner()
        result = miner.mine(raw_json)

        assert result["record_count"] == 1
        assert result["records"][0] == {"server": "prod-1", "healthy": True}

    def test_empty_json_string(self) -> None:
        miner = JSONDataMiner()
        with pytest.raises(ValueError, match="Data source identifier cannot be empty"):
            miner.mine("")
        assert miner.parse(b"") == []

    def test_invalid_json_type_raises(self) -> None:
        miner = JSONDataMiner()
        with pytest.raises(ValueError, match="JSON payload must be an object"):
            miner.parse(b'"just a string"')


class TestAPIDataMiner:
    def test_mine_api_with_data_envelope(self) -> None:
        endpoint = "https://api.example.com/v1/users"
        miner = APIDataMiner(mock_responses={endpoint: '{"data": [{"id": 1, "name": "John"}]}'})
        result = miner.mine(endpoint)

        assert result["format"] == "api"
        assert result["record_count"] == 1
        assert result["records"][0] == {"id": 1, "name": "John"}

    def test_api_connection_error(self) -> None:
        miner = APIDataMiner()
        with pytest.raises(ConnectionError, match="Failed to fetch data from API"):
            miner.mine("https://unknown.endpoint")

    def test_api_list_payload(self) -> None:
        endpoint = "https://api.example.com/v1/list"
        miner = APIDataMiner(mock_responses={endpoint: '[{"val": 100}]'})
        result = miner.mine(endpoint)
        assert result["record_count"] == 1

    def test_api_single_dict_without_envelope(self) -> None:
        endpoint = "https://api.example.com/v1/single"
        miner = APIDataMiner(mock_responses={endpoint: '{"status": "ok"}'})
        result = miner.mine(endpoint)
        assert result["records"][0] == {"status": "ok"}


class TestTemplateMethodSkeletonAndHooks:
    def test_empty_source_raises(self) -> None:
        miner = CSVDataMiner()
        with pytest.raises(ValueError, match="Data source identifier cannot be empty"):
            miner.mine("")

    def test_step_execution_order_and_hooks(self) -> None:
        execution_order: list[str] = []

        class TrackingMiner(DataMiner, format_name="tracking"):
            def hook_before_mine(self, source: str) -> None:
                execution_order.append("hook_before_mine")

            def extract(self, source: str) -> bytes:
                execution_order.append("extract")
                return source.encode("utf-8")

            def parse(self, raw_data: bytes) -> list[dict[str, str]]:
                execution_order.append("parse")
                return [{"RAW": "DATA"}]

            def clean(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
                execution_order.append("clean")
                return records

            def transform(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
                execution_order.append("transform")
                return [{"clean": "data"}]

            def load(self, records: list[dict[str, Any]]) -> dict[str, Any]:
                execution_order.append("load")
                return {"result": "saved"}

            def hook_after_mine(self, result: dict[str, Any]) -> None:
                execution_order.append("hook_after_mine")

        tracker = TrackingMiner()
        tracker.mine("test-source")

        expected_order = [
            "hook_before_mine",
            "extract",
            "parse",
            "clean",
            "transform",
            "load",
            "hook_after_mine",
        ]
        assert execution_order == expected_order

    def test_subclass_registration(self) -> None:
        assert "csv" in DataMiner.registry
        assert "json" in DataMiner.registry
        assert "api" in DataMiner.registry
        assert DataMiner.registry["csv"] is CSVDataMiner
        assert DataMiner.registry["json"] is JSONDataMiner
        assert DataMiner.registry["api"] is APIDataMiner

    def test_default_clean_drops_empty_records(self) -> None:
        class DummyMiner(DataMiner):
            def extract(self, source: str) -> bytes:
                return b""

            def parse(self, raw_data: bytes) -> list[dict[str, str | None]]:
                return [{"empty": None, "blank": ""}, {"valid": "yes"}]

        miner = DummyMiner()
        result = miner.mine("dummy")
        assert result["record_count"] == 1
        assert result["records"][0] == {"valid": "yes"}
