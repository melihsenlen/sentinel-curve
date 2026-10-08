import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


class Trainer:
    def __init__(self, config, reader, model):
        self.config = config
        self.reader = reader
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model  = model.to(self.device)

        print(f"Reading: {self.config.data['data_path']}")

    def train(self):
        X, y = self.reader.create_sequences()
        dataloader = DataLoader(
            TensorDataset(torch.from_numpy(X), torch.from_numpy(y)), # dataset
            batch_size=self.config.training["batch_size"],
            shuffle=True
        )

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
        for Xb, yb in dataloader:
            Xb, yb = Xb.to(self.device), yb.to(self.device)
            optimizer.zero_grad()
            loss = criterion(self.model(Xb), yb)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * Xb.size(0)
        return total_loss / len(dataloader.dataset)

    def save_model(self):
        model = self.config.model()
        model.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), model)
        print(f"Model saved --> {model}")

    def run(self):
        self.train()
        self.save_model()
