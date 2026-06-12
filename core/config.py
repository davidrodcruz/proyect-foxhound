import os
from pathlib import Path
from typing import Any, Optional

import yaml
from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()
        self._root_dir = Path(__file__).parent.parent

    def get_team_config(self, team: str, test_type: str) -> dict[str, Any]:
        if test_type == "ui":
            config_path = self._root_dir / "webui" / "teams" / team / "config.yaml"
        elif test_type == "api":
            config_path = self._root_dir / "api" / "teams" / team / "config.yaml"
        else:
            raise ValueError(f"Invalid test type: {test_type}. Use 'ui' or 'api'.")

        if not config_path.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        return self._apply_env_overrides(config)

    def _apply_env_overrides(self, config: dict) -> dict:
        for key, value in config.items():
            env_key = f"FOXHOUND_{key.upper()}"
            env_value = os.getenv(env_key)
            if env_value is not None:
                config[key] = env_value
        return config

    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return os.getenv(key, default)

    @property
    def root_dir(self) -> Path:
        return self._root_dir


config = Config()
