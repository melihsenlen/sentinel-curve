import yaml
from pathlib import Path


class Config:
    def __init__(self):
        config = self._load_config()
        self.data = config["data"]
        self.training = config["training"]
        self.inference = config["inference"]
        self.output = config["output"]
        
    def _load_config(self, config_path: str = "config.yaml") -> dict:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")
        with open(path) as y:
            return yaml.safe_load(y)