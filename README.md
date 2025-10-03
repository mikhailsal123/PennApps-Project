# TradeSphere.ai

A sophisticated portfolio simulation and trading platform with AI-powered insights.

## Features

- **Real-time Portfolio Simulation**: Test trading strategies with historical data
- **Multiple Time Intervals**: Daily, hourly, 15-minute, 5-minute, and 1-minute simulations
- **AI Portfolio Advisor**: Get intelligent insights and recommendations
- **Advanced Trading Rules**: Set automated buy/sell conditions
- **Risk Management**: Beta hedging and portfolio optimization
- **Interactive Charts**: Visualize performance and trends

## Live Demo

🌐 **[View Live Demo](https://your-username.github.io/PennApps-Project/)**

## Local Development

### Prerequisites
- Python 3.8+
- Node.js 16+

### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
export CEREBRAS_TOKEN="your-cerebras-token-here"

# Run the Flask server
python app.py
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## Technology Stack

- **Backend**: Python Flask, yfinance, pandas
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **AI**: Cerebras API for portfolio analysis
- **Charts**: Chart.js for data visualization
- **Styling**: Inter font, modern CSS with gradients

## API Endpoints

- `POST /start_simulation` - Start a new portfolio simulation
- `GET /simulation_status/<id>` - Get simulation progress
- `POST /ai_analysis` - Get AI portfolio insights
- `GET /validate_ticker/<ticker>` - Validate stock ticker symbols

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For questions or support, please open an issue on GitHub.