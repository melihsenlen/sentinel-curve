import numpy as np
import pandas as pd
import torch
from pathlib import Path

from architecture.data import DataReader
from architecture.model import RegressionModel
from architecture.config import Config


class Inferencer:
    def __init__(self):
        self.config = Config()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.reader = DataReader(self.config.data)
        self.model  = self._load_model()

    def _load_model(self) -> RegressionModel:
        model_path = self.config.output["model_path"]
        model      = RegressionModel().to(self.device)

        model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
        print(f"Model loaded <-- {model_path}")
        return model

    def predict(self) -> np.ndarray:
        X, _   = self.reader.create_sequences()
        future = self.config.inference["future"]
        noise  = self.config.inference["noise"]

        self.model.eval()
        predictions = []

        with torch.no_grad():
            fitted = self.model(torch.from_numpy(X).float().to(self.device)).cpu().numpy()
            predictions.extend(fitted)

            sequence = X[-1].copy()
            for _ in range(future):
                seq_tensor = torch.from_numpy(sequence[np.newaxis]).float().to(self.device)
                step = self.model(seq_tensor).cpu().numpy()[0]
                step += np.random.normal(scale=noise, size=step.shape)
                predictions.append(step)
                sequence = np.vstack([sequence[1:], step])
        return self.reader.inverse_transform(np.array(predictions))

    def save(self, predictions: np.ndarray):
        output_path = self.config.output["predictions_path"]
        historical  = len(predictions) - self.config.inference["future"]

        df = pd.DataFrame(predictions, columns=["cpu", "memory"])
        df.insert(0, "timestep", range(len(df)))
        df["forecast"] = df["timestep"] >= historical

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Predictions saved: {output_path}")

    def run(self):
        self.save(self.predict())