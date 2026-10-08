from architecture.train import Trainer
from architecture.inference import Inferencer
from architecture.data import DataReader
from architecture.model import RegressionModel
from architecture.config import Config


if __name__ == "__main__":
    config = Config()
    reader = DataReader(config.data)
    model  = RegressionModel()

    Trainer(config, reader, model).run()
    Inferencer(config, reader, model).run()