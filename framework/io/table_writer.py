"""Table writer utilities for platform-managed Iceberg table writes.

This module centralizes DataFrame write behavior so pipeline jobs do not
hardcode Spark/Iceberg write operations directly.

The writer uses WritePolicy to determine whether a job should append data
or overwrite a specific partition.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col

from framework.policies.write_policy import WriteMode, WritePolicy


class TableWriter:
    """Write Spark DataFrames to platform-managed tables.

    The writer applies the write semantics defined by WritePolicy.

    Supported modes:
        - append
        - overwrite_partition
    """

    def write(
        self,
        df: DataFrame,
        table_name: str,
        policy: WritePolicy,
        partition_value: str | None = None,
    ) -> None:
        """Write a DataFrame to a target table using the provided write policy.

        Args:
            df: Spark DataFrame to write.
            table_name: Fully qualified target table name.
            policy: WritePolicy defining the write semantics.
            partition_value: Partition value to overwrite when using
                overwrite_partition mode.

        Raises:
            ValueError: If the policy is invalid or required arguments are missing.
            NotImplementedError: If the write mode is not supported.
        """
        policy.validate()

        if policy.mode == WriteMode.APPEND:
            self._append(df=df, table_name=table_name)
            return

        if policy.mode == WriteMode.OVERWRITE_PARTITION:
            if partition_value is None:
                raise ValueError(
                    "partition_value is required for overwrite_partition writes"
                )

            self._overwrite_partition(
                df=df,
                table_name=table_name,
                partition_column=policy.partition_column,
                partition_value=partition_value,
            )
            return

        raise NotImplementedError(f"Unsupported write mode: {policy.mode}")

    def _append(self, df: DataFrame, table_name: str) -> None:
        """Append a DataFrame to an Iceberg table."""
        df.writeTo(table_name).append()

    def _overwrite_partition(
        self,
        df: DataFrame,
        table_name: str,
        partition_column: str | None,
        partition_value: str,
    ) -> None:
        """Overwrite one partition in an Iceberg table.

        Args:
            df: Spark DataFrame to write.
            table_name: Fully qualified target table name.
            partition_column: Partition column used by the target table.
            partition_value: Partition value to overwrite.
        """
        if partition_column is None:
            raise ValueError(
                "partition_column is required for overwrite_partition writes"
            )

        (df.writeTo(table_name).overwrite(col(partition_column) == partition_value))
