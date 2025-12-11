import yaml
from pathlib import Path
from typing import Dict, Any  # Type hints for clarity

# Path to config file, relative to this module
CONFIG_PATH = Path(__file__).parent.parent / 'config' / 'config.yaml'

def load_config() -> Dict[str, Any]:
    """
    Load YAML configuration from file.

    Returns:
        Dict[str, Any]: Parsed config data.

    Raises:
        FileNotFoundError: If config file is missing.
        yaml.YAMLError: If YAML parsing fails.
    """
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config: {e}")

# Global settings dict; load once on import
settings = load_config()