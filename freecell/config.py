import yaml


class Config:
    """Class that loads the game configuration"""

    _instance = None

    def __init__(self):
        """Instantiate the game configuration"""
        with open("conf/config.yaml") as file:
            self.default: dict = yaml.safe_load(file)

    @classmethod
    def instance(cls):
        """Returns the game configuration instance"""
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance
