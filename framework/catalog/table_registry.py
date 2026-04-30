from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class CatalogConfig:
    """
    CatalogConfig defines the physical catalog and database names used by the platform.

    These values may vary by environment, such as dev vs prod.
    """

    catalog_name: str
    databases: Mapping[str, str]

    def database(self, layer: str) -> str:
        if layer not in self.databases:
            known_layers = ", ".join(sorted(self.databases.keys()))
            raise KeyError(f"Unknown data layer: {layer}. Known layers: {known_layers}")

        return self.databases[layer]


@dataclass(frozen=True)
class TableDefinition:
    """
    Logical-to-physical table definition.

    logical_name:
        Stable platform key, such as "user_events.bronze" or "dau.gold".

    layer:
        Data layer, such as bronze, silver, or gold.

    table_name:
        Physical table name inside the layer database.
    """

    logical_name: str
    layer: str
    table_name: str


class TableRegistry:
    """
    Generic table registry.

    It maps logical table keys to fully qualified catalog table names.

    Example:
        tables.get("user_events.bronze")
        -> glue_catalog.bronze.user_events_bronze

        tables.get("dau.gold")
        -> glue_catalog.gold.dau_daily
    """

    def __init__(
        self,
        catalog_config: CatalogConfig,
        table_definitions: Mapping[str, TableDefinition],
    ) -> None:
        self.catalog_config = catalog_config
        self.table_definitions = dict(table_definitions)

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> "TableRegistry":
        """
        Build a TableRegistry from parsed YAML config.

        Expected config shape:

        catalog_name: glue_catalog

        databases:
          bronze: bronze
          silver: silver
          gold: gold

        tables:
          user_events.bronze:
            layer: bronze
            table_name: user_events_bronze
        """
        catalog_name = config["catalog_name"]
        databases = config["databases"]
        raw_tables = config["tables"]

        catalog_config = CatalogConfig(
            catalog_name=catalog_name,
            databases=databases,
        )

        table_definitions = {
            logical_name: TableDefinition(
                logical_name=logical_name,
                layer=table_config["layer"],
                table_name=table_config["table_name"],
            )
            for logical_name, table_config in raw_tables.items()
        }

        return cls(
            catalog_config=catalog_config,
            table_definitions=table_definitions,
        )

    def get(self, logical_name: str) -> str:
        """
        Return the fully qualified table name for a logical table key.
        """
        if logical_name not in self.table_definitions:
            known_tables = ", ".join(sorted(self.table_definitions.keys()))
            raise KeyError(
                f"Unknown table logical name: {logical_name}. "
                f"Known tables: {known_tables}"
            )

        table_def = self.table_definitions[logical_name]
        database = self.catalog_config.database(table_def.layer)

        return f"{self.catalog_config.catalog_name}.{database}.{table_def.table_name}"
