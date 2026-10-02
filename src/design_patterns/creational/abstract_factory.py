"""Abstract Factory Design Pattern.

Classification: Creational
Intent:
    Provide an interface for creating families of related or dependent objects
    without specifying their concrete classes.

Motivation & Real-World Analogy:
    In a multi-cloud orchestration tool, provisioning infrastructure requires
    creating coherent families of resources (e.g., Virtual Machines and Storage Buckets).
    An AWS Virtual Machine (EC2) must work seamlessly with an S3 Bucket, while an
    Azure VM should pair with Azure Blob Storage. Mixing cloud providers arbitrarily
    creates configuration bugs.

Mermaid Architecture Diagram:
    ```mermaid
    classDiagram
        class CloudResourceFactory {
            <<protocol>>
            +create_compute() ComputeInstance
            +create_storage() StorageBucket
        }
        class AWSCloudFactory {
            +create_compute() ComputeInstance
            +create_storage() StorageBucket
        }
        class GCPCloudFactory {
            +create_compute() ComputeInstance
            +create_storage() StorageBucket
        }
        class ComputeInstance {
            <<protocol>>
            +launch(instance_type: str) str
        }
        class StorageBucket {
            <<protocol>>
            +upload(file_name: str, data: bytes) str
        }
        CloudResourceFactory <|.. AWSCloudFactory
        CloudResourceFactory <|.. GCPCloudFactory
        AWSCloudFactory ..> ComputeInstance : creates EC2
        AWSCloudFactory ..> StorageBucket : creates S3
        GCPCloudFactory ..> ComputeInstance : creates GCE
        GCPCloudFactory ..> StorageBucket : creates GCS
    ```
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


# ==============================================================================
# 1. Anti-Pattern / Naive Approach (Hardcoded Cloud Couplings)
# ==============================================================================
class NaiveInfrastructureProvisioner:
    """Anti-pattern: Client code manually instantiates vendor-specific classes.

    Mix-and-match errors (e.g., pairing AWS EC2 with GCP Cloud Storage accidentally)
    are caught only at runtime during deployment.
    """

    def provision_stack(self, provider: str, vm_size: str, bucket_name: str) -> dict[str, str]:
        if provider == "aws":
            return {
                "compute": f"AWS EC2 instance launched with size {vm_size}",
                "storage": f"AWS S3 bucket '{bucket_name}' initialized",
            }
        elif provider == "gcp":
            return {
                "compute": f"GCP Compute Engine instance launched with size {vm_size}",
                "storage": f"GCP Storage bucket '{bucket_name}' initialized",
            }
        else:
            raise ValueError(f"Unknown cloud provider: {provider}")


# ==============================================================================
# 2. Clean Pattern Implementation (GoF Abstract Factory with Protocols)
# ==============================================================================
class ComputeInstance(Protocol):
    """Abstract Product A: Interface for computing instances."""

    def launch(self, instance_type: str) -> str: ...


class StorageBucket(Protocol):
    """Abstract Product B: Interface for object storage buckets."""

    def upload(self, file_name: str, data: bytes) -> str: ...


# --- Concrete Products for AWS ---
@dataclass(frozen=True)
class EC2Instance:
    region: str = "us-east-1"

    def launch(self, instance_type: str) -> str:
        return f"[AWS] EC2 instance ({instance_type}) launched in {self.region}"


@dataclass(frozen=True)
class S3Bucket:
    bucket_name: str

    def upload(self, file_name: str, data: bytes) -> str:
        return f"[AWS] Uploaded {len(data)} bytes to s3://{self.bucket_name}/{file_name}"


# --- Concrete Products for GCP ---
@dataclass(frozen=True)
class ComputeEngineInstance:
    zone: str = "us-central1-a"

    def launch(self, instance_type: str) -> str:
        return f"[GCP] Compute Engine ({instance_type}) launched in {self.zone}"


@dataclass(frozen=True)
class GoogleCloudStorageBucket:
    bucket_name: str

    def upload(self, file_name: str, data: bytes) -> str:
        return f"[GCP] Uploaded {len(data)} bytes to gs://{self.bucket_name}/{file_name}"


# --- Abstract Factory Interface ---
class CloudResourceFactory(Protocol):
    """Abstract Factory: Declares creation methods for each abstract product family."""

    def create_compute(self) -> ComputeInstance: ...

    def create_storage(self, bucket_name: str) -> StorageBucket: ...


# --- Concrete Factories ---
class AWSCloudFactory:
    """Concrete Factory producing AWS resource family."""

    def __init__(self, region: str = "us-east-1") -> None:
        self.region = region

    def create_compute(self) -> ComputeInstance:
        return EC2Instance(region=self.region)

    def create_storage(self, bucket_name: str) -> StorageBucket:
        return S3Bucket(bucket_name=bucket_name)


class GCPCloudFactory:
    """Concrete Factory producing GCP resource family."""

    def __init__(self, zone: str = "us-central1-a") -> None:
        self.zone = zone

    def create_compute(self) -> ComputeInstance:
        return ComputeEngineInstance(zone=self.zone)

    def create_storage(self, bucket_name: str) -> StorageBucket:
        return GoogleCloudStorageBucket(bucket_name=bucket_name)


# --- Client Code ---
class CloudInfrastructureDeployer:
    """Client orchestrating deployment using an abstract cloud factory."""

    def __init__(self, factory: CloudResourceFactory) -> None:
        self._factory = factory

    def deploy_stack(self, vm_type: str, bucket_name: str, initial_data: bytes) -> tuple[str, str]:
        compute = self._factory.create_compute()
        storage = self._factory.create_storage(bucket_name)

        vm_status = compute.launch(vm_type)
        upload_status = storage.upload("bootstrap.log", initial_data)
        return vm_status, upload_status


# ==============================================================================
# 3. Pythonic Twist: Factory via Callable Mapping / Module Exports
# ==============================================================================
CloudFactoryBuilder = tuple[type[ComputeInstance], type[StorageBucket]]

CLOUD_PROVIDERS: dict[str, CloudFactoryBuilder] = {
    "aws": (EC2Instance, S3Bucket),
    "gcp": (ComputeEngineInstance, GoogleCloudStorageBucket),
}


def create_cloud_stack(provider: str, bucket_name: str) -> tuple[ComputeInstance, StorageBucket]:
    """Lightweight Pythonic factory using mapping tuples instead of classes."""
    if provider not in CLOUD_PROVIDERS:
        raise ValueError(f"Unsupported provider: {provider}")
    compute_cls, storage_cls = CLOUD_PROVIDERS[provider]
    return compute_cls(), storage_cls(bucket_name)  # type: ignore[call-arg]


# ==============================================================================
# 4. Driver / Demonstration
# ==============================================================================
if __name__ == "__main__":
    print("=== GoF Abstract Factory: AWS Stack ===")
    aws_deployer = CloudInfrastructureDeployer(AWSCloudFactory(region="eu-west-1"))
    vm_log, storage_log = aws_deployer.deploy_stack("t3.medium", "acme-assets", b"init")
    print(vm_log)
    print(storage_log)

    print("\n=== GoF Abstract Factory: GCP Stack ===")
    gcp_deployer = CloudInfrastructureDeployer(GCPCloudFactory(zone="europe-west3-a"))
    vm_log, storage_log = gcp_deployer.deploy_stack("n2-standard-4", "acme-gcp-data", b"init")
    print(vm_log)
    print(storage_log)
