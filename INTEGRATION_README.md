# PennApps Trading Platform Integration

This project integrates a Next.js frontend with a Flask backend to create a comprehensive trading platform.

## Architecture

- **Frontend**: Next.js application running on port 3000
- **Backend**: Flask application running on port 5002
- **Integration**: The frontend displays the Flask app in an iframe when "Execute Trade" is clicked

## Features

### Frontend (Next.js)
- Modern landing page with typing animation
- Responsive design with Tailwind CSS
- Smooth transition to trading platform
- Back button to return to landing page

### Backend (Flask)
- Portfolio simulation engine
- Real-time stock data integration
- AI-powered portfolio analysis (Cerebras API)
- Interactive trading rules configuration
- Performance metrics and charts
- Beta hedging capabilities

## Quick Start

### Option 1: Use the startup script (Recommended)
```bash
cd /Users/michaelsaleev/PennApps-Project
./start_apps.sh
```

### Option 2: Manual startup

1. **Start Flask backend:**
   ```bash
   cd /Users/michaelsaleev/PennApps-Project
   pip install -r requirements.txt
   python app.py
   ```

2. **Start Next.js frontend (in a new terminal):**
   ```bash
   cd /Users/michaelsaleev/PennApps-Project/frontend
   npm install
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:5002

## How It Works

1. **Landing Page**: Users see the modern Next.js landing page with animated code examples
2. **Execute Trade Button**: Clicking this button reveals the Flask trading platform in an iframe
3. **Trading Platform**: Full-featured portfolio simulation with:
   - Portfolio configuration
   - Trading rules setup
   - Real-time simulation
   - AI analysis
   - Performance charts
4. **Back Button**: Users can return to the landing page anytime

## Configuration

### Flask Backend
- Port: 5002
- CORS enabled for iframe integration
- AI analysis powered by Cerebras API (optional)

### Next.js Frontend
- Port: 3000
- Tailwind CSS for styling
- Typing animation component
- Responsive iframe integration

## Dependencies

### Backend (Python)
- Flask 2.3.3
- flask-cors 4.0.0+
- yfinance for stock data
- matplotlib for charts
- pandas for data processing
- requests for API calls

### Frontend (Node.js)
- Next.js 15.5.3
- React 19.1.0
- Tailwind CSS 4.1.13
- Motion for animations
- TypeScript support

## Troubleshooting

1. **Iframe not loading**: Ensure Flask backend is running on port 5002
2. **CORS errors**: Make sure flask-cors is installed and enabled
3. **Port conflicts**: Check if ports 3000 or 5002 are already in use
4. **Dependencies**: Run `pip install -r requirements.txt` and `npm install` in the frontend directory

## Development

- Frontend code: `/frontend/src/app/`
- Backend code: `/app.py`
- Static assets: `/static/`
- Templates: `/templates/`

## API Endpoints

The Flask backend provides several API endpoints:
- `GET /` - Main trading interface
- `POST /start_simulation` - Start portfolio simulation
- `GET /simulation_status/<id>` - Get simulation status
- `POST /ai_analysis` - Get AI portfolio analysis
- `GET /plot/<id>/<type>` - Generate performance charts

## Security Notes

- The iframe uses sandbox attributes for security
- CORS is configured to allow iframe embedding
- API endpoints are protected with proper error handling
