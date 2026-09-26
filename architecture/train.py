import torch
import torch.nn as nn
from pathlib import Path
from torch.utils.data import DataLoader, TensorDataset

from architecture.data import DataReader
from architecture.model import RegressionModel
from architecture.config import Config


class Trainer:
    def __init__(self):
        self.config = Config()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.reader = DataReader(self.config.data)
        self.model  = RegressionModel().to(self.device)

        csv_path = self.config.data["csv_path"]
        print(f"Reading: {csv_path}")

    def _build(self) -> DataLoader:
        X, y = self.reader.create_sequences()
        return DataLoader(
            TensorDataset(torch.from_numpy(X), torch.from_numpy(y)), # dataset
            batch_size=self.config.training["batch_size"],
            shuffle=True
        )

    def train(self):
        dataloader = self._build()
        optimizer  = torch.optim.Adam(self.model.parameters(), lr=self.config.training["lr"])
        criterion  = nn.MSELoss()
        epochs     = self.config.training["epochs"]

        self.model.train()
        for epoch in range(epochs):
            loss = self._epoch(dataloader, optimizer, criterion)
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch + 1}/{epochs} | Loss: {loss:.6f}")

    def _epoch(self, dataloader, optimizer, criterion) -> float:
        total_loss = 0
        for X_batch, y_batch in dataloader:
            X_batch, y_batch = X_batch.to(self.device), y_batch.to(self.device)
            optimizer.zero_grad()
            loss = criterion(self.model(X_batch), y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * X_batch.size(0)
        return total_loss / len(dataloader.dataset)

    def save_model(self):
        model_path = self.config.output["model_path"]
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), model_path)
        print(f"Model saved --> {model_path}")

    def run(self):
        self.train()
        self.save_model()
