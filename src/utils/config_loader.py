"""Configuration file loader."""
import yaml
import os
from typing import Dict, Any, List
from pathlib import Path


def load_database_configs(config_path: str = "config/databases.yaml") -> List[Dict[str, Any]]:
    """Load database configurations from YAML file."""
    config_file = Path(config_path)
    
    if not config_file.exists():
        return []
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    databases = config.get('databases', [])
    
    # Resolve environment variables
    for db_config in databases:
        db_config = _resolve_env_vars(db_config)
    
    return databases


def _resolve_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve environment variables in configuration."""
    resolved = {}
    
    for key, value in config.items():
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            # Extract env var name
            env_var = value[2:-1]
            resolved[key] = os.getenv(env_var, value)
        elif isinstance(value, dict):
            resolved[key] = _resolve_env_vars(value)
        elif isinstance(value, list):
            resolved[key] = [
                _resolve_env_vars(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            resolved[key] = value
    
    return resolved

