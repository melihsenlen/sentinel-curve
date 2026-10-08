import numpy as np
import pandas as pd
import torch


class Inferencer:
    def __init__(self, config, reader, model):
        self.config = config
        self.reader = reader
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model  = model.to(self.device)

        model_path = self.config.model()
        self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
        print(f"Model loaded <-- {model_path}")

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
        df = pd.DataFrame(predictions, columns=["cpu", "memory"])
        df.insert(0, "timestep", range(len(df)))

        historical  = len(predictions) - self.config.inference["future"]
        df["forecast"] = df["timestep"] >= historical

        output = self.config.predictions()
        output.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output, index=False)
        print(f"Predictions saved: {output}")

    def run(self):
        self.save(self.predict())