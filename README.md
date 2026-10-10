# Sentinel Curve

A Windows resource monitoring and prediction tool, made to anticipate resource pressure before it builds up.

It samples CPU and memory usage in real time, learns the pattern in those readings with a [PyTorch](https://pytorch.org/) LSTM regression model, and projects where both trends are heading.

## Features

- Real-time CPU and memory monitoring in C++ on Windows
- LSTM regression model trained on the collected time-series data
- Autoregressive future rollout with configurable length and noise
- Separate pipelines for the monitor and for training & inference
- Jupyter notebook for visualizing fitted & forecasted trends

## Prerequisites

- Windows
- Python 3.10+
- `g++` on your PATH. The monitor is built with `g++ -std=c++17`.

## Installation

```bash
pip install -r requirements.txt
```

This installs PyTorch, pandas, NumPy, Matplotlib, scikit-learn, PyYAML and Jupyter.

## How the Curve is Shaped

It works like a weather forecast for your PC. It takes a look at the last few readings, predicts the next one, then keeps on going from its own predictions.

1. **Collect:** The monitor reads system-wide CPU usage (%) and used physical memory (MB) through the Windows API, once per `--interval`, and writes each reading to a CSV with its timestamp.
   
2. **Prepare:** Each column is scaled to the 0 to 1 range. A sliding window of `window_size` consecutive readings becomes the input, and the reading right after it becomes the target. With the defaults, five readings predict the sixth.
   
3. **Train:** An LSTM reads each window, and a linear layer turns its last output into the next CPU and memory pair. It's trained for `epochs` with mean squared error and Adam.
   
4. **Fit:** The trained model predicts one step ahead across all of the collected data, always from real readings. This is the "fitted" line, which shows how closely the model follows the history.
   
5. **Forecast:** Starting from the last real window, the model predicts a step, adds a little noise, slides it into the window, and repeats `future` times. The noise keeps the forecast from following a single smooth line. Each step builds on earlier guesses, so errors compound and the far end of the forecast is the least reliable part.

## Configuration

### Monitor arguments

You can customize how the monitor runs by passing arguments to `pipeline\monitor.bat`:

| Argument | Default | Description |
|----------|---------|-------------|
| `--interval` | `1` | Time between measurements, in seconds. |
| `--duration` | `60` | Total run time, in seconds. A negative value runs until you stop it. |
| `--output` | `data/data.csv` | Path of the CSV file the measurements are saved to. |

For example:

```bash
pipeline\monitor.bat --interval 2 --duration 300
```

### Training & Forecasting

Parameters live in `config.yaml`:

```yaml
data:
  window_size: 5 # number of past time steps to use for prediction

  data_path: "data/data.csv"
  predictions_path: "data/predictions.csv"

training:
  batch_size: 16
  epochs: 50
  lr: 0.001

inference:
  future: 50 # number of future time steps to predict
  noise: 0.005
```

`noise` is the standard deviation of the noise added at each forecast step, in the model's scaled 0 to 1 space.

## Usage

### 1. Collect data

```bash
pipeline\monitor.bat
```

The monitor samples for 60 seconds by default and creates `data/data.csv`, containing timestamp, CPU (%) and memory (MB).

See [Configuration](#configuration) to change how long and how often the monitor samples.

### 2. Train and forecast

The CSV needs more rows than `window_size`, and a longer collection run gives the model more to learn from.

From the repository root:

```bash
python -m pipeline.run
```

This trains the model and then runs the forecast in the same run, creating `data/predictions.csv`. The model isn't saved, so every run trains a fresh one on the current data.

### 3. See the results

Open `analysis.ipynb` to see your own machine's curves :)

<img src="assets/example.png" width="1024">

## License

[MIT license](LICENSE)