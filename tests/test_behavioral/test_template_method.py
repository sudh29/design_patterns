"""Tests for the Template Method pattern implementation."""

from design_patterns.behavioral.template_method import (
    APIDataPipeline,
    CSVDataPipeline,
)


class TestTemplateMethodPattern:
    def test_csv_pipeline_execution(self) -> None:
        pipeline = CSVDataPipeline("users.csv")
        result = pipeline.run_pipeline()

        assert result["status"] == "SUCCESS"
        assert result["records_processed"] == 2
        assert result["records_loaded"] == 2
        assert pipeline.is_connected is False  # disconnect was called

    def test_api_pipeline_execution_and_hook(self) -> None:
        pipeline = APIDataPipeline("https://test.api")
        assert pipeline.metrics_notified is False

        result = pipeline.run_pipeline()
        assert result["status"] == "SUCCESS"
        assert result["records_processed"] == 2
        assert pipeline.metrics_notified is True  # post_load_hook executed
