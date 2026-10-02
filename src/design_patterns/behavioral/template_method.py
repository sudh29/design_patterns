"""Template Method Design Pattern.

Classification: Behavioral
Intent:
    Define the skeleton of an algorithm in an operation, deferring some steps to subclasses.
    Template Method lets subclasses redefine certain steps of an algorithm without changing
    the algorithm's structure.

Motivation & Real-World Analogy:
    In modern data engineering and ETL (Extract, Transform, Load) pipelines, the high-level
    workflow invariant is always the same:
    1. Connect to data source
    2. Extract raw records
    3. Clean and sanitize data
    4. Transform into target schema
    5. Load into warehouse / datastore
    6. Close connection & audit log
    Subclasses should customize specific extraction or transformation logic
    (e.g., CSV files vs REST APIs vs SQL databases) without altering the sequencing,
    error recovery, or audit steps.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class DataPipelineETL {
            <<abstract>>
            +run_pipeline() dict
            #connect() bool*
            #extract() list*
            #transform(data) list*
            #load(data) int*
            #hook_after_load()
        }
        class CSVDataPipeline {
            #connect() bool
            #extract() list
            #transform(data) list
            #load(data) int
        }
        class APIDataPipeline {
            #connect() bool
            #extract() list
            #transform(data) list
            #load(data) int
        }
        DataPipelineETL <|-- CSVDataPipeline
        DataPipelineETL <|-- APIDataPipeline
    ```
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class DataPipelineETL(ABC):
    """Abstract Class defining the Template Method skeleton."""

    def run_pipeline(self) -> dict[str, Any]:
        """Template Method: Dictates invariant step ordering across all ETL pipelines."""
        self.connect()
        raw_data = self.extract()
        cleaned_data = self.clean(raw_data)
        transformed = self.transform(cleaned_data)
        records_loaded = self.load(transformed)
        self.post_load_hook(records_loaded)
        self.disconnect()

        return {
            "status": "SUCCESS",
            "records_processed": len(transformed),
            "records_loaded": records_loaded,
        }

    @abstractmethod
    def connect(self) -> bool:
        """Primitive Step 1: Open source connection."""
        ...

    @abstractmethod
    def extract(self) -> list[dict[str, Any]]:
        """Primitive Step 2: Read raw data records."""
        ...

    def clean(self, raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Optional/Default Hook: Filter out nulls or invalid entries."""
        return [record for record in raw_data if record]

    @abstractmethod
    def transform(self, cleaned_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Primitive Step 3: Apply business transforms."""
        ...

    @abstractmethod
    def load(self, transformed_data: list[dict[str, Any]]) -> int:
        """Primitive Step 4: Write to destination warehouse."""
        ...

    def post_load_hook(self, count: int) -> None:  # noqa: B027
        """Hook method: Subclasses may override if custom notifications/metrics needed."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Primitive Step 5: Clean up connection/resources."""
        ...


# ==============================================================================
# Concrete Pipelines
# ==============================================================================
class CSVDataPipeline(DataPipelineETL):
    """Concrete pipeline reading local CSV file data."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.is_connected = False
        self.loaded_count = 0

    def connect(self) -> bool:
        self.is_connected = True
        return True

    def extract(self) -> list[dict[str, Any]]:
        if not self.is_connected:
            raise RuntimeError("Pipeline not connected")
        # Simulating parsed CSV rows
        return [
            {"id": "1", "name": "alice", "salary": "95000"},
            {"id": "2", "name": "bob", "salary": "82000"},
        ]

    def transform(self, cleaned_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        # Convert salary to float and uppercase names
        transformed = []
        for row in cleaned_data:
            transformed.append(
                {
                    "user_id": int(row["id"]),
                    "name": row["name"].capitalize(),
                    "salary": float(row["salary"]),
                }
            )
        return transformed

    def load(self, transformed_data: list[dict[str, Any]]) -> int:
        self.loaded_count = len(transformed_data)
        return self.loaded_count

    def disconnect(self) -> None:
        self.is_connected = False


class APIDataPipeline(DataPipelineETL):
    """Concrete pipeline querying REST API with custom metrics hook."""

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint
        self.is_connected = False
        self.metrics_notified = False

    def connect(self) -> bool:
        self.is_connected = True
        return True

    def extract(self) -> list[dict[str, Any]]:
        return [
            {"sensor_id": "SN-01", "temp_c": 22.5},
            {"sensor_id": "SN-02", "temp_c": 24.1},
        ]

    def transform(self, cleaned_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        # Convert C to F
        for item in cleaned_data:
            item["temp_f"] = round(item["temp_c"] * 9 / 5 + 32, 1)
        return cleaned_data

    def load(self, transformed_data: list[dict[str, Any]]) -> int:
        return len(transformed_data)

    def post_load_hook(self, count: int) -> None:
        self.metrics_notified = True

    def disconnect(self) -> None:
        self.is_connected = False


# ==============================================================================
# Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    csv_pipeline = CSVDataPipeline("/data/users.csv")
    csv_result = csv_pipeline.run_pipeline()
    print(f"CSV Pipeline Result: {csv_result}")

    api_pipeline = APIDataPipeline("https://telemetry.io/sensors")
    api_result = api_pipeline.run_pipeline()
    print(f"API Pipeline Result: {api_result} (Hook fired: {api_pipeline.metrics_notified})")
