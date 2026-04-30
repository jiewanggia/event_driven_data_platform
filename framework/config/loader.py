from pathlib import Path
from typing import Any

import yaml


def load_yaml_config(path: str | Path) -> dict[str, Any]:
    """
    Load a YAML configuration file.

    This is a shared platform utility so individual jobs do not need to
    duplicate YAML loading logic.
    """
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if config is None:
        raise ValueError(f"Config file is empty: {config_path}")

    if not isinstance(config, dict):
        raise TypeError(f"Config file must contain a YAML mapping: {config_path}")

    return config
