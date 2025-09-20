from StockData import StockData
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

df = StockData("AAPL", "2025-08-08", "2025-10-08")

for i in range(60):
    