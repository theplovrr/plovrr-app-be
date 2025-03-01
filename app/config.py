import json

class Config:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        with open("config.json", "r") as file:
            self.settings = json.load(file)

    def get(self, key, default=None):
        """Get a setting using dot notation (e.g., 'AppSettings.Debug')."""
        keys = key.split(".")
        value = self.settings
        for k in keys:
            value = value.get(k, default)
            if value is None:
                return default
        return value
