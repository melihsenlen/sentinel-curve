import yaml
from pathlib import Path


class Config:
    def __init__(self):
        config = self._load()
        self.data = config["data"]
        self.training = config["training"]
        self.inference = config["inference"]
        
    def _load(self, config_path: str = "config.yaml") -> dict:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")
        with open(path) as y:
            return yaml.safe_load(y)

    def predictions(self) -> Path:
        return Path(self.data["predictions_path"])