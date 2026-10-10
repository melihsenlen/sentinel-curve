import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler


class DataReader: 
    def __init__(self, data: dict):
        self.data_path = data["data_path"]
        self.window_size = data["window_size"]
        self.scaler = MinMaxScaler()

    def read(self) -> np.ndarray:
        df = pd.read_csv(self.data_path)
        df = df[["cpu", "memory"]]
        scaled = self.scaler.fit_transform(df)
        return scaled

    def sequences(self) -> tuple[np.ndarray, np.ndarray]:
        data = self.read()
        X, y = [], []
        for i in range(len(data) - self.window_size):
            X.append(data[i:i+self.window_size])
            y.append(data[i+self.window_size])
        X = np.array(X, dtype=np.float32)
        y = np.array(y, dtype=np.float32)
        return X, y

    def inverse(self, data):
        return self.scaler.inverse_transform(data)