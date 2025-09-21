# Portfolio Simulator Web Application

A Flask-based web application that allows users to run portfolio simulations using your existing Portfolio and StockData classes.

## 🚀 Features

- **Interactive Web Interface**: User-friendly form to configure portfolio parameters
- **Real-time Simulation**: Live updates showing portfolio performance day by day
- **Customizable Trading Rules**: Set buy/sell conditions for different stocks
- **Performance Metrics**: Automatic calculation of Sharpe ratio, volatility, and returns
- **Responsive Design**: Works on desktop and mobile devices

## 📁 Project Structure

```
PennApps-Project/
├── app.py                 # Flask web application
├── Portfolio.py           # Your existing portfolio class
├── StockData.py           # Your existing stock data class
├── main.py               # Original command-line simulation
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Main web interface
└── static/
    ├── css/
    │   └── style.css     # Styling
    └── js/
        └── app.js        # Frontend JavaScript
```

## 🛠️ Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python3 app.py
   ```

3. **Access the Web Interface**:
   - Open your browser and go to: `http://localhost:5000`
   - The application will start automatically

## 🎯 How to Use

### 1. Configure Your Portfolio
- **Initial Cash**: Set your starting investment amount
- **Start Date**: Choose when to begin the simulation
- **Duration**: Select how many days to simulate (1-60 days)

### 2. Add Stocks
- Add stock tickers (e.g., NVDA, AAPL, GOOG)
- Specify how many shares to buy initially
- Add/remove stocks as needed

### 3. Set Trading Rules
- Choose which stocks to monitor
- Set conditions (price > threshold or price < threshold)
- Define how many shares to sell when conditions are met

### 4. Run Simulation
- Click "Start Simulation" to begin
- Watch real-time updates as the simulation progresses
- View daily portfolio values, trades, and positions

### 5. View Results
- See final performance metrics including:
  - Total return percentage
  - Sharpe ratio
  - Volatility
  - Final portfolio value

## 🔧 API Endpoints

The Flask application provides the following API endpoints:

- `POST /start_simulation` - Start a new portfolio simulation
- `GET /simulation_status/<id>` - Get current simulation status
- `POST /stop_simulation/<id>` - Stop a running simulation
- `DELETE /cleanup_simulation/<id>` - Clean up completed simulation

## 🎨 Customization

### Adding New Features
- Modify `app.py` to add new API endpoints
- Update `templates/index.html` for UI changes
- Extend `static/js/app.js` for frontend functionality

### Styling
- Edit `static/css/style.css` to customize the appearance
- Uses Bootstrap 5 for responsive design
- Custom gradients and animations included

## 📊 Example Simulation

1. **Setup**: $100,000 initial cash, 30-day simulation
2. **Stocks**: 100 shares NVDA, 120 shares AMZN, 100 shares GOOG
3. **Rules**: Sell 10 NVDA shares when price > $180
4. **Result**: Real-time tracking of portfolio performance

## 🚀 Advanced Features

- **Background Processing**: Simulations run in separate threads
- **Real-time Updates**: AJAX polling for live results
- **Error Handling**: Graceful handling of market data issues
- **Responsive Design**: Mobile-friendly interface
- **Performance Metrics**: Automatic risk/return calculations

## 🔍 Technical Details

- **Backend**: Flask with threading for concurrent simulations
- **Frontend**: HTML5, CSS3, JavaScript with Bootstrap
- **Data**: Real-time stock data via yfinance
- **Charts**: Ready for Chart.js integration (commented out)

## 🐛 Troubleshooting

1. **Port already in use**: Change port in `app.py` (line 154)
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Stock data errors**: Check internet connection and ticker symbols
4. **Simulation not starting**: Verify form inputs are valid

## 📈 Future Enhancements

- Add interactive charts with Chart.js
- Implement multiple simulation comparison
- Add export functionality (CSV/PDF)
- Include more advanced trading strategies
- Add user authentication and saved simulations

## 🤝 Contributing

Feel free to extend the application with new features:
- Additional trading indicators
- More sophisticated risk metrics
- Enhanced visualization
- Mobile app version

---

**Note**: This web application wraps your existing Portfolio and StockData classes, making them accessible through a modern web interface while preserving all the original functionality.