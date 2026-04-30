from dataclasses import dataclass


@dataclass(frozen=True)
class StorageConfig:
    """
    StorageConfig defines the base S3 layout used by the platform.
    """

    bucket: str
    raw_prefix: str = "raw"
    warehouse_prefix: str = "warehouse"
    spark_event_logs_prefix: str = "spark-event-logs"
    athena_results_prefix: str = "athena-results"
    monitoring_prefix: str = "monitoring"


class PathBuilder:
    """
    PathBuilder centralizes S3 path construction.

    This avoids hardcoding S3 paths inside individual pipeline jobs.
    """

    def __init__(self, storage_config: StorageConfig) -> None:
        self.storage_config = storage_config

    def raw_path(self, domain: str, business_date: str) -> str:
        """
        Build the raw landing path for a given domain and business date.

        Example:
        s3://my-bucket/raw/user_events/dt=2026-04-22/
        """
        return self._s3_path(
            self.storage_config.raw_prefix,
            domain,
            f"dt={business_date}",
        )

    def warehouse_path(self) -> str:
        """
        Build the Iceberg warehouse base path.

        Example:
        s3://my-bucket/warehouse/
        """
        return self._s3_path(self.storage_config.warehouse_prefix)

    def spark_event_logs_path(self) -> str:
        """
        Build the Spark event logs path.

        Example:
        s3://my-bucket/spark-event-logs/
        """
        return self._s3_path(self.storage_config.spark_event_logs_prefix)

    def athena_results_path(self) -> str:
        """
        Build the Athena query results path.

        Example:
        s3://my-bucket/athena-results/
        """
        return self._s3_path(self.storage_config.athena_results_prefix)

    def monitoring_path(self, pipeline_name: str, job_name: str, run_id: str) -> str:
        """
        Build a monitoring output path for a specific job run.

        Example:
        s3://my-bucket/monitoring/user_events/ingest_to_bronze/run_id=.../
        """
        return self._s3_path(
            self.storage_config.monitoring_prefix,
            pipeline_name,
            job_name,
            f"run_id={run_id}",
        )

    def _s3_path(self, *parts: str) -> str:
        """
        Join S3 path parts safely.

        This prevents duplicated or missing slashes.
        """
        cleaned_parts = [part.strip("/") for part in parts if part]
        suffix = "/".join(cleaned_parts)
        return f"s3://{self.storage_config.bucket}/{suffix}/"
