"""Template Method Design Pattern.

Classification: Behavioral
Intent:
    Define the skeleton of an algorithm in an operation, deferring some steps to subclasses.
    Template Method lets subclasses redefine certain steps of an algorithm without changing
    the algorithm's structure.

Motivation & Real-World Analogy:
    In modern data engineering and ETL (Extract, Transform, Load) pipelines, ingestion workflows
    share a strict, invariant sequence: extract raw payloads, parse serialized records,
    validate and sanitize entries, normalize data structures, and load into a datastore.
    While the overall sequence must never deviate, the specific details—such as parsing CSV delimiters,
    decoding JSON strings, or fetching from HTTP REST endpoints—differ across file formats.
    The Template Method encapsulates the immutable execution pipeline in a base class,
    while delegating format-specific hooks to concrete subclasses.
    In Python, this is further enriched with `__init_subclass__` for automatic registry of
    supported data source handlers.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class DataMiner {
            <<abstract>>
            +mine(source: str) dict
            #extract(source: str)* bytes
            #parse(raw: bytes)* list
            #clean(records: list) list
            #transform(records: list) list
            #load(records: list) dict
            #hook_after_mine(result: dict) void
        }
        class CSVDataMiner {
            #extract(source: str) bytes
            #parse(raw: bytes) list
        }
        class JSONDataMiner {
            #extract(source: str) bytes
            #parse(raw: bytes) list
        }
        class APIDataMiner {
            #extract(source: str) bytes
            #parse(raw: bytes) list
        }
        DataMiner <|-- CSVDataMiner
        DataMiner <|-- JSONDataMiner
        DataMiner <|-- APIDataMiner
    ```
"""

from __future__ import annotations

import csv
import io
import json
from abc import ABC, abstractmethod
from typing import Any, ClassVar


# ==============================================================================
# 1. Abstract Base Class with Template Method & Subclass Registry
# ==============================================================================
class DataMiner(ABC):
    """Abstract Template: Defines skeleton of data mining ETL workflow."""

    # Registry for auto-discovery via Pythonic __init_subclass__
    registry: ClassVar[dict[str, type[DataMiner]]] = {}
    format_name: ClassVar[str] = "base"

    def __init_subclass__(cls, format_name: str | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if format_name:
            cls.format_name = format_name
            DataMiner.registry[format_name] = cls

    def mine(self, source: str) -> dict[str, Any]:
        """Template Method: Invariant algorithm defining the ETL pipeline sequence."""
        if not source:
            raise ValueError("Data source identifier cannot be empty")

        self.hook_before_mine(source)
        raw_bytes = self.extract(source)
        records = self.parse(raw_bytes)
        cleaned = self.clean(records)
        transformed = self.transform(cleaned)
        result = self.load(transformed)
        self.hook_after_mine(result)
        return result

    # --- Abstract steps (must be implemented by concrete miners) ---
    @abstractmethod
    def extract(self, source: str) -> bytes:
        """Extract raw bytes from the given source identifier."""
        ...

    @abstractmethod
    def parse(self, raw_data: bytes) -> list[dict[str, Any]]:
        """Parse raw bytes into a list of record dictionaries."""
        ...

    # --- Hook steps (default implementations with optional override) ---
    def clean(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter out records with missing values or invalid entries."""
        valid_records: list[dict[str, Any]] = []
        for record in records:
            # Drop entries where all values are None or empty
            if any(v is not None and v != "" for v in record.values()):
                valid_records.append(record)
        return valid_records

    def transform(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Normalize records by stripping whitespace and standardizing keys."""
        transformed: list[dict[str, Any]] = []
        for rec in records:
            norm_rec: dict[str, Any] = {}
            for k, v in rec.items():
                clean_key = str(k).strip().lower()
                clean_val = v.strip() if isinstance(v, str) else v
                norm_rec[clean_key] = clean_val
            transformed.append(norm_rec)
        return transformed

    def load(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        """Persist transformed records and return ingestion summary."""
        return {
            "status": "success",
            "format": self.format_name,
            "record_count": len(records),
            "records": records,
        }

    def hook_before_mine(self, source: str) -> None:
        """Optional hook executed before extraction."""
        return None

    def hook_after_mine(self, result: dict[str, Any]) -> None:
        """Optional hook executed after loading."""
        return None


# ==============================================================================
# 2. Concrete Template Implementations
# ==============================================================================
class CSVDataMiner(DataMiner, format_name="csv"):
    """Concrete Miner for CSV text streams."""

    def __init__(self, delimiter: str = ",") -> None:
        self.delimiter = delimiter

    def extract(self, source: str) -> bytes:
        # In a real system, source could be a file path; here we treat source as inline data or path
        return source.encode("utf-8")

    def parse(self, raw_data: bytes) -> list[dict[str, Any]]:
        text = raw_data.decode("utf-8").strip()
        if not text:
            return []
        stream = io.StringIO(text)
        reader = csv.DictReader(stream, delimiter=self.delimiter)
        return [dict(row) for row in reader]


class JSONDataMiner(DataMiner, format_name="json"):
    """Concrete Miner for JSON payloads."""

    def extract(self, source: str) -> bytes:
        return source.encode("utf-8")

    def parse(self, raw_data: bytes) -> list[dict[str, Any]]:
        text = raw_data.decode("utf-8").strip()
        if not text:
            return []
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [dict(item) for item in parsed if isinstance(item, dict)]
        if isinstance(parsed, dict):
            return [parsed]
        raise ValueError("JSON payload must be an object or list of objects")


class APIDataMiner(DataMiner, format_name="api"):
    """Concrete Miner for simulated REST API responses."""

    def __init__(self, mock_responses: dict[str, str] | None = None) -> None:
        self._responses = mock_responses or {}

    def extract(self, source: str) -> bytes:
        if source not in self._responses:
            raise ConnectionError(f"Failed to fetch data from API endpoint: {source}")
        return self._responses[source].encode("utf-8")

    def parse(self, raw_data: bytes) -> list[dict[str, Any]]:
        payload = json.loads(raw_data.decode("utf-8"))
        if isinstance(payload, dict) and "data" in payload:
            data = payload["data"]
            if isinstance(data, list):
                return [dict(item) for item in data]
        if isinstance(payload, list):
            return [dict(item) for item in payload]
        return [payload]


# ==============================================================================
# 3. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    csv_input = "name,role,salary\nAlice,Engineer,120000\nBob,Designer,95000\n"
    csv_miner = CSVDataMiner()
    csv_result = csv_miner.mine(csv_input)
    print("CSV Extraction Result:", csv_result)

    json_input = '[{"name": "Carol", "role": "VP Product"}, {"name": "Dave", "role": "SRE"}]'
    json_miner = JSONDataMiner()
    json_result = json_miner.mine(json_input)
    print("JSON Extraction Result:", json_result)

    api_miner = APIDataMiner(
        mock_responses={"https://api.internal/metrics": '{"data": [{"cpu": 42}, {"cpu": 68}]}'}
    )
    api_result = api_miner.mine("https://api.internal/metrics")
    print("API Extraction Result:", api_result)
    print(f"Registered Miners via __init_subclass__: {list(DataMiner.registry.keys())}")
