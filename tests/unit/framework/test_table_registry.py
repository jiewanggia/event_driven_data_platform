import pytest

from framework.catalog.table_registry import TableRegistry
from framework.config.loader import load_yaml_config


def test_table_registry_loads_catalog_config() -> None:
    config = load_yaml_config("configs/platform/catalog.yaml")
    tables = TableRegistry.from_config(config)

    assert tables.get("user_events.bronze") == "glue_catalog.bronze.user_events_bronze"
    assert tables.get("user_events.silver") == "glue_catalog.silver.user_events_clean"
    assert tables.get("orders.bronze") == "glue_catalog.bronze.orders_bronze"
    assert tables.get("orders.silver") == "glue_catalog.silver.orders_clean"
    assert tables.get("dau.gold") == "glue_catalog.gold.dau_daily"
    assert tables.get("retention.gold") == "glue_catalog.gold.retention_daily"
    assert tables.get("revenue.gold") == "glue_catalog.gold.revenue_daily"
    assert (
        tables.get("order_conversion.gold")
        == "glue_catalog.gold.order_conversion_daily"
    )


def test_table_registry_raises_for_unknown_table() -> None:
    config = load_yaml_config("configs/platform/catalog.yaml")
    tables = TableRegistry.from_config(config)

    with pytest.raises(KeyError, match="Unknown table logical name"):
        tables.get("unknown.table")


def test_table_registry_raises_for_unknown_layer() -> None:
    config = {
        "catalog_name": "glue_catalog",
        "databases": {
            "bronze": "bronze",
            "silver": "silver",
            "gold": "gold",
        },
        "tables": {
            "bad.table": {
                "layer": "platinum",
                "table_name": "bad_table",
            }
        },
    }

    tables = TableRegistry.from_config(config)

    with pytest.raises(KeyError, match="Unknown data layer"):
        tables.get("bad.table")
