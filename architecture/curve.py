import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


class Curve:
    def __init__(self, config, reader, model):
        self.config = config
        self.reader = reader
        self.X, self.y = self.reader.sequences()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model  = model.to(self.device)

        print(f"Reading: {self.config.data['data_path']}")

    def train(self):
        dataloader = DataLoader(
            TensorDataset(torch.from_numpy(self.X), torch.from_numpy(self.y)), # dataset
            self.config.training["batch_size"], # batch_size
            True # shuffle
        )

        optimizer  = torch.optim.Adam(self.model.parameters(), lr=self.config.training["lr"])
        criterion  = nn.MSELoss()
        epochs     = self.config.training["epochs"]

        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for Xb, yb in dataloader:
                Xb, yb = Xb.to(self.device), yb.to(self.device)
                optimizer.zero_grad()
                loss = criterion(self.model(Xb), yb)
                loss.backward()
                optimizer.step()
                total_loss += loss.item() * Xb.size(0)
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch + 1}/{epochs} | Loss: {total_loss / len(dataloader.dataset):.6f}")

    def predict(self) -> np.ndarray:
        future = self.config.inference["future"]
        noise  = self.config.inference["noise"]

        self.model.eval()
        predictions = []

        with torch.no_grad():
            fitted = self.model(torch.from_numpy(self.X).float().to(self.device)).cpu().numpy()
            predictions.extend(fitted)

            sequence = self.X[-1].copy()
            for _ in range(future):
                seq_tensor = torch.from_numpy(sequence[np.newaxis]).float().to(self.device)
                step = self.model(seq_tensor).cpu().numpy()[0]
                step += np.random.normal(scale=noise, size=step.shape)
                predictions.append(step)
                sequence = np.vstack([sequence[1:], step])
        return self.reader.inverse(np.array(predictions))

    def save(self, predictions: np.ndarray):
        df = pd.DataFrame(predictions, columns=["cpu", "memory"])
        df.insert(0, "timestep", range(len(df)))

        historical     = len(predictions) - self.config.inference["future"]
        df["forecast"] = df["timestep"] >= historical

        output = self.config.predictions()
        output.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output, index=False)

        print(f"Predictions saved: {output}")
