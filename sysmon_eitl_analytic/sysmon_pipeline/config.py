from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
import yaml

def load_yaml(path: str | Path) -> Dict[str, Any]:
    """Load YAML into dict."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

@dataclass(frozen=True)
class ConfigBundle:
    config: Dict[str, Any]
    thresholds: Dict[str, Any]
    roles: Dict[str, Any]

def load_configs(config_path: str | Path, thresholds_path: str | Path, roles_path: str | Path) -> ConfigBundle:
    """Load all config files."""
    return ConfigBundle(
        config=load_yaml(config_path),
        thresholds=load_yaml(thresholds_path),
        roles=load_yaml(roles_path),
    )
