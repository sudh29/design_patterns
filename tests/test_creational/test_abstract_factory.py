"""Tests for the Abstract Factory pattern implementation."""

import pytest

from design_patterns.creational.abstract_factory import (
    AWSCloudFactory,
    CloudInfrastructureDeployer,
    ComputeEngineInstance,
    ComputeInstance,
    EC2Instance,
    GCPCloudFactory,
    GoogleCloudStorageBucket,
    NaiveInfrastructureProvisioner,
    S3Bucket,
    StorageBucket,
    create_cloud_stack,
)


class TestNaiveInfrastructureProvisioner:
    def test_naive_aws(self) -> None:
        provisioner = NaiveInfrastructureProvisioner()
        result = provisioner.provision_stack("aws", "t3.large", "my-bucket")
        assert "EC2" in result["compute"]
        assert "my-bucket" in result["storage"]

    def test_naive_gcp(self) -> None:
        provisioner = NaiveInfrastructureProvisioner()
        result = provisioner.provision_stack("gcp", "e2-medium", "gcp-bucket")
        assert "Compute Engine" in result["compute"]
        assert "gcp-bucket" in result["storage"]

    def test_naive_invalid_provider(self) -> None:
        provisioner = NaiveInfrastructureProvisioner()
        with pytest.raises(ValueError, match="Unknown cloud provider"):
            provisioner.provision_stack("azure", "Standard_D2", "azure-container")


class TestGoFAbstractFactory:
    def test_aws_factory_family(self) -> None:
        factory = AWSCloudFactory(region="ap-south-1")
        vm = factory.create_compute()
        storage = factory.create_storage("user-uploads")

        assert isinstance(vm, EC2Instance)
        assert isinstance(storage, S3Bucket)
        assert "ap-south-1" in vm.launch("m5.large")
        assert "s3://user-uploads/file.txt" in storage.upload("file.txt", b"content")

    def test_gcp_factory_family(self) -> None:
        factory = GCPCloudFactory(zone="asia-south1-a")
        vm = factory.create_compute()
        storage = factory.create_storage("user-coldline")

        assert isinstance(vm, ComputeEngineInstance)
        assert isinstance(storage, GoogleCloudStorageBucket)
        assert "asia-south1-a" in vm.launch("c2-standard-8")
        assert "gs://user-coldline/archive.tar" in storage.upload("archive.tar", b"archive-data")

    def test_deployer_client(self) -> None:
        deployer = CloudInfrastructureDeployer(AWSCloudFactory())
        vm_res, storage_res = deployer.deploy_stack("t4g.nano", "deploy-bucket", b"test")
        assert "EC2" in vm_res
        assert "deploy-bucket" in storage_res

    def test_custom_cloud_provider_extension(self) -> None:
        """Verifies Open/Closed Principle: Can add Azure without modifying client."""

        class AzureVM:
            def launch(self, instance_type: str) -> str:
                return f"[Azure] VM ({instance_type}) started"

        class AzureBlob:
            def __init__(self, container: str) -> None:
                self.container = container

            def upload(self, file_name: str, data: bytes) -> str:
                return f"[Azure] Uploaded {len(data)}b to {self.container}/{file_name}"

        class AzureFactory:
            def create_compute(self) -> ComputeInstance:
                return AzureVM()

            def create_storage(self, bucket_name: str) -> StorageBucket:
                return AzureBlob(bucket_name)

        deployer = CloudInfrastructureDeployer(AzureFactory())
        vm_res, storage_res = deployer.deploy_stack("Standard_B1s", "media", b"video")
        assert "[Azure] VM" in vm_res
        assert "[Azure] Uploaded" in storage_res


class TestPythonicCloudFactory:
    def test_create_cloud_stack_aws(self) -> None:
        vm, storage = create_cloud_stack("aws", "my-data")
        assert isinstance(vm, EC2Instance)
        assert isinstance(storage, S3Bucket)

    def test_create_cloud_stack_gcp(self) -> None:
        vm, storage = create_cloud_stack("gcp", "my-data")
        assert isinstance(vm, ComputeEngineInstance)
        assert isinstance(storage, GoogleCloudStorageBucket)

    def test_create_cloud_stack_unsupported(self) -> None:
        with pytest.raises(ValueError, match="Unsupported provider"):
            create_cloud_stack("oracle", "my-data")
