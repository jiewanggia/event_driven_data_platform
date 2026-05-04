import pytest

from framework.policies.write_policy import WriteMode, WritePolicy


def test_append_policy_is_valid() -> None:
    policy = WritePolicy.append()

    policy.validate()

    assert policy.mode == WriteMode.APPEND
    assert policy.partition_column is None


def test_overwrite_partition_policy_is_valid() -> None:
    policy = WritePolicy.overwrite_partition("event_date")

    policy.validate()

    assert policy.mode == WriteMode.OVERWRITE_PARTITION
    assert policy.partition_column == "event_date"


def test_overwrite_partition_requires_partition_column() -> None:
    policy = WritePolicy(mode=WriteMode.OVERWRITE_PARTITION)

    with pytest.raises(
        ValueError,
        match="partition_column is required",
    ):
        policy.validate()


def test_append_should_not_have_partition_column() -> None:
    policy = WritePolicy(
        mode=WriteMode.APPEND,
        partition_column="dt",
    )

    with pytest.raises(
        ValueError,
        match="partition_column should not be set",
    ):
        policy.validate()
