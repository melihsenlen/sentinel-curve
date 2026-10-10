from architecture.curve import Curve
from architecture.data import DataReader
from architecture.model import RegressionModel
from architecture.config import Config


if __name__ == "__main__":
    config = Config()
    reader = DataReader(config.data)
    model  = RegressionModel()

    curve = Curve(config, reader, model)
    curve.train()
    curve.save(curve.predict())