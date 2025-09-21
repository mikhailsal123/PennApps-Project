from flask import Flask, render_template, jsonify, request
from Portfolio import Portfolio
from StockData import StockData
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import time
import threading
import uuid

app = Flask(__name__)

# Store active simulations
active_simulations = {}

class SimulationManager:
    def __init__(self, simulation_id, initial_cash, start_date, duration_days, trading_frequency, tickers, trading_rules):
        self.simulation_id = simulation_id
        self.initial_cash = initial_cash
        self.start_date = start_date
        self.duration_days = duration_days
        self.trading_frequency = trading_frequency  # 'daily' or 'intraday'
        self.tickers = tickers
        self.trading_rules = trading_rules
        self.results = []
        self.is_running = False
        self.is_complete = False
        self.thread = None
        
    def run_simulation(self):
        """Run the portfolio simulation"""
        try:
            self.is_running = True
            
            # Initialize portfolio and stock data
            currtime = datetime.strptime(self.start_date, '%Y-%m-%d')
            start_date_str = currtime.strftime('%Y-%m-%d')
            end_date_str = (currtime + relativedelta(months=2)).strftime('%Y-%m-%d')
            
            port = Portfolio(self.initial_cash, start_date_str, end_date_str)
            
            # Initial purchases
            for ticker, shares in self.tickers.items():
                port.buy(ticker, 500, shares, currtime)  # High price limit to ensure purchase
            
            # Initialize stock data with appropriate interval
            data = {}
            interval = '30m' if self.trading_frequency == 'intraday' else '1d'
            for ticker in self.tickers.keys():
                data[ticker] = StockData(ticker, start_date_str, end_date_str)
                # Update the stock data with the correct interval
                data[ticker].get_stock_data(ticker, start_date_str, end_date_str, interval)
            
            # Run simulation based on trading frequency
            if self.trading_frequency == 'intraday':
                # For intraday: simulate 30-minute intervals within each day
                total_intervals = self.duration_days * 13  # 13 intervals per day (6.5 hours / 30 min)
                interval_delta = timedelta(minutes=30)
            else:
                # For daily: simulate day by day
                total_intervals = self.duration_days
                interval_delta = timedelta(days=1)
            
            for i in range(total_intervals):
                if not self.is_running:  # Check if simulation was stopped
                    break
                    
                # Move to next interval
                currtime = currtime + interval_delta
                
                # Update current time for all stock data objects
                for ticker in self.tickers.keys():
                    data[ticker].curtime = currtime
                
                # Get current prices
                current_prices = {}
                for ticker in self.tickers.keys():
                    price = data[ticker].get_price()
                    if price is not None:
                        current_prices[ticker] = price
                
                # Check trading conditions and execute trades
                trades_executed = []
                
                for ticker, rules in self.trading_rules.items():
                    if ticker in current_prices:
                        price = current_prices[ticker]
                        for rule in rules:
                            # Handle sell rules
                            if rule['action'] == 'sell':
                                if rule['condition'] == 'greater_than' and price > rule['threshold']:
                                    if port.positions.get(ticker, 0) >= rule['shares']:
                                        port.sell(ticker, price, rule['shares'], currtime)
                                        trades_executed.append(f"Sold {rule['shares']} {ticker} @ ${price:.2f}")
                                elif rule['condition'] == 'less_than' and price < rule['threshold']:
                                    if port.positions.get(ticker, 0) >= rule['shares']:
                                        port.sell(ticker, price, rule['shares'], currtime)
                                        trades_executed.append(f"Sold {rule['shares']} {ticker} @ ${price:.2f}")
                            
                            # Handle buy rules
                            elif rule['action'] == 'buy':
                                if rule['condition'] == 'greater_than' and price > rule['threshold']:
                                    # Check if we have enough cash to buy
                                    cost = price * rule['shares']
                                    if port.cash >= cost:
                                        port.buy(ticker, price + 1, rule['shares'], currtime)  # Add small buffer to ensure purchase
                                        trades_executed.append(f"Bought {rule['shares']} {ticker} @ ${price:.2f}")
                                elif rule['condition'] == 'less_than' and price < rule['threshold']:
                                    # Check if we have enough cash to buy
                                    cost = price * rule['shares']
                                    if port.cash >= cost:
                                        port.buy(ticker, price + 1, rule['shares'], currtime)  # Add small buffer to ensure purchase
                                        trades_executed.append(f"Bought {rule['shares']} {ticker} @ ${price:.2f}")
                
                # Get current portfolio value
                current_value = port.get_value(currtime)
                
                # Store interval result
                interval_label = f"Interval {i + 1}"
                if self.trading_frequency == 'intraday':
                    day_num = (i // 13) + 1
                    interval_in_day = (i % 13) + 1
                    interval_label = f"Day {day_num}, Interval {interval_in_day}"
                
                daily_result = {
                    'day': i + 1,
                    'interval_label': interval_label,
                    'date': currtime.strftime('%Y-%m-%d %H:%M') if self.trading_frequency == 'intraday' else currtime.strftime('%Y-%m-%d'),
                    'prices': current_prices.copy(),
                    'portfolio_value': current_value,
                    'trades': trades_executed.copy(),
                    'positions': port.positions.copy(),
                    'cash': port.cash,
                    'pnl': port.get_PNL(currtime)
                }
                self.results.append(daily_result)
                
                # Small delay for real-time effect
                time.sleep(0.1)
            
            # Calculate final metrics
            if self.results:
                initial_value = self.results[0]['portfolio_value']
                final_value = self.results[-1]['portfolio_value']
                total_return = (final_value - initial_value) / initial_value * 100 if initial_value > 0 else 0
                
                sharpe_ratio = port.calculate_sharpe_ratio()
                volatility = port.calculate_volatility()
                
                self.final_metrics = {
                    'total_return_pct': round(total_return, 2),
                    'final_value': round(final_value, 2),
                    'total_pnl': round(final_value - self.initial_cash, 2),
                    'sharpe_ratio': round(sharpe_ratio, 3) if sharpe_ratio else None,
                    'volatility_pct': round(volatility * 100, 2) if volatility else None,
                    'total_trades': len(port.past_trades),
                    'final_positions': port.positions
                }
            
            self.is_complete = True
            
        except Exception as e:
            self.error = str(e)
            self.is_complete = True

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/start_simulation', methods=['POST'])
def start_simulation():
    """Start a new portfolio simulation"""
    try:
        data = request.json
        
        # Generate unique simulation ID
        simulation_id = str(uuid.uuid4())
        
        # Extract parameters
        initial_cash = float(data.get('initial_cash', 100000))
        start_date = data.get('start_date', '2025-07-21')
        duration_days = int(data.get('duration_days', 30))
        trading_frequency = data.get('trading_frequency', 'daily')
        
        # Extract tickers and shares
        tickers = {}
        for ticker_data in data.get('tickers', []):
            ticker = ticker_data['ticker'].upper()
            shares = int(ticker_data['shares'])
            tickers[ticker] = shares
        
        # Extract trading rules
        trading_rules = {}
        for rule_data in data.get('trading_rules', []):
            ticker = rule_data['ticker'].upper()
            if ticker not in trading_rules:
                trading_rules[ticker] = []
            trading_rules[ticker].append({
                'action': rule_data.get('action', 'sell'),  # Default to sell for backward compatibility
                'condition': rule_data['condition'],
                'threshold': float(rule_data['threshold']),
                'shares': int(rule_data['shares'])
            })
        
        # Create and start simulation
        simulation = SimulationManager(
            simulation_id, initial_cash, start_date, duration_days, 
            trading_frequency, tickers, trading_rules
        )
        
        # Start simulation in background thread
        simulation.thread = threading.Thread(target=simulation.run_simulation)
        simulation.thread.daemon = True
        simulation.thread.start()
        
        # Store simulation
        active_simulations[simulation_id] = simulation
        
        return jsonify({
            'success': True,
            'simulation_id': simulation_id,
            'message': 'Simulation started successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/simulation_status/<simulation_id>')
def simulation_status(simulation_id):
    """Get current status of a simulation"""
    if simulation_id not in active_simulations:
        return jsonify({'error': 'Simulation not found'}), 404
    
    simulation = active_simulations[simulation_id]
    
    response = {
        'is_running': simulation.is_running,
        'is_complete': simulation.is_complete,
        'results': simulation.results,
        'progress': len(simulation.results) / simulation.duration_days if simulation.duration_days > 0 else 0
    }
    
    if hasattr(simulation, 'final_metrics'):
        response['final_metrics'] = simulation.final_metrics
    
    if hasattr(simulation, 'error'):
        response['error'] = simulation.error
    
    return jsonify(response)

@app.route('/stop_simulation/<simulation_id>', methods=['POST'])
def stop_simulation(simulation_id):
    """Stop a running simulation"""
    if simulation_id not in active_simulations:
        return jsonify({'error': 'Simulation not found'}), 404
    
    simulation = active_simulations[simulation_id]
    simulation.is_running = False
    
    return jsonify({'success': True, 'message': 'Simulation stopped'})

@app.route('/cleanup_simulation/<simulation_id>', methods=['DELETE'])
def cleanup_simulation(simulation_id):
    """Clean up a completed simulation"""
    if simulation_id in active_simulations:
        del active_simulations[simulation_id]
        return jsonify({'success': True, 'message': 'Simulation cleaned up'})
    
    return jsonify({'error': 'Simulation not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
