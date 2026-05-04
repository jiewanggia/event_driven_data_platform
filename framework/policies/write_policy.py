"""Write policy models for platform-managed table writes.

This module defines the write semantics used by pipeline jobs when writing
to Bronze, Silver, and Gold Iceberg tables.

Typical usage:
    - Bronze tables use append mode.
    - Silver tables use partition overwrite mode.
    - Gold tables use partition overwrite mode.
"""

from dataclasses import dataclass
from enum import Enum


class WriteMode(str, Enum):
    """Supported write modes for platform-managed tables."""

    APPEND = "append"
    OVERWRITE_PARTITION = "overwrite_partition"


@dataclass(frozen=True)
class WritePolicy:
    """Define how a job writes output data to a target table.

    Attributes:
        mode: The write mode used by the job.
        partition_column: The partition column used for partition overwrite.
            This is required for OVERWRITE_PARTITION and must be omitted for
            APPEND.

    Examples:
        Bronze tables normally use append mode.

        Silver and Gold tables normally use partition overwrite mode.
    """

    mode: WriteMode
    partition_column: str | None = None

    def validate(self) -> None:
        """Validate that the write policy configuration is internally consistent.

        Raises:
            ValueError: If overwrite_partition does not define a partition column,
                or if append mode incorrectly defines one.
        """
        if self.mode == WriteMode.OVERWRITE_PARTITION and not self.partition_column:
            raise ValueError(
                "partition_column is required for overwrite_partition mode"
            )

        if self.mode == WriteMode.APPEND and self.partition_column is not None:
            raise ValueError("partition_column should not be set for append mode")

    @classmethod
    def append(cls) -> "WritePolicy":
        """Create an append write policy.

        Returns:
            A WritePolicy configured with APPEND mode.
        """
        return cls(mode=WriteMode.APPEND)

    @classmethod
    def overwrite_partition(cls, partition_column: str) -> "WritePolicy":
        """Create a partition overwrite write policy.

        Args:
            partition_column: The partition column to overwrite.

        Returns:
            A WritePolicy configured with OVERWRITE_PARTITION mode.
        """
        return cls(
            mode=WriteMode.OVERWRITE_PARTITION,
            partition_column=partition_column,
        )
