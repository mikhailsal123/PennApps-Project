from flask import Flask, render_template, jsonify, request
from Portfolio import Portfolio
from StockData import StockData
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import time
import threading
import uuid
import os
import requests
from dotenv import load_dotenv
import base64
import io
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Store active simulations
active_simulations = {}

# Global portfolio state for AI memory
current_portfolio_state = {
    'has_simulation': False,
    'simulation_id': None,
    'initial_cash': None,
    'start_date': None,
    'duration_days': None,
    'tickers': {},
    'trading_rules': [],
    'final_metrics': {},
    'final_positions': {},
    'results': [],
    'last_updated': None
}

# Initialize Cerebras API
# TODO: Replace 'YOUR_CEREBRAS_TOKEN' with your actual Cerebras API token
cerebras_token = os.getenv('CEREBRAS_TOKEN') or 'csk-42x2pme9cv39vddm69tpmec5exyv4r6ch5c8n8rdfdrcrmnh'
cerebras_api_url = "https://api.cerebras.ai/v1/chat/completions"

def update_portfolio_state(simulation_id, simulation_data):
    """Update the global portfolio state with the latest simulation results"""
    global current_portfolio_state
    
    if simulation_id in active_simulations:
        simulation = active_simulations[simulation_id]
        
        current_portfolio_state.update({
            'has_simulation': True,
            'simulation_id': simulation_id,
            'initial_cash': simulation.initial_cash,
            'start_date': simulation.start_date,
            'duration_days': simulation.duration_days,
            'tickers': simulation.tickers,
            'trading_rules': simulation.trading_rules,
            'final_metrics': getattr(simulation, 'final_metrics', {}),
            'final_positions': getattr(simulation, 'final_metrics', {}).get('final_positions', {}),
            'results': simulation.results,
            'last_updated': datetime.now().isoformat()
        })
        
        print(f"✅ Portfolio state updated for simulation {simulation_id}")
        print(f"   Final positions: {current_portfolio_state['final_positions']}")
        print(f"   Final value: ${current_portfolio_state['final_metrics'].get('final_value', 'N/A')}")
        print(f"   Total return: {current_portfolio_state['final_metrics'].get('total_return_pct', 'N/A')}%")

class AIAdvisor:
    def __init__(self):
        self.system_prompt = """You are a friendly and knowledgeable AI portfolio advisor with dynamic knowledge of your user's current portfolio state. You can have casual conversations and also provide expert financial analysis.

Your capabilities include:
- Having friendly, natural conversations
- Knowing the user's CURRENT portfolio state at all times
- Analyzing portfolio performance, risk metrics, and allocation
- Identifying strengths and weaknesses in trading strategies
- Suggesting improvements for diversification and risk management
- Providing market insights and investment recommendations
- Explaining financial concepts in simple terms

Always be:
- Friendly and approachable in conversation
- Professional and informative when discussing finance
- Data-driven in your analysis using the user's ACTUAL portfolio data
- Cautious about market predictions
- Focused on helping users make informed decisions
- Clear about risks and limitations
- ACCURATE about the user's current portfolio holdings and performance

IMPORTANT: You have access to the user's current portfolio state. Always reference their ACTUAL holdings, performance, and metrics when discussing their portfolio. If asked about their portfolio, provide specific details about their current positions, returns, and risk metrics.

For casual conversation, respond naturally and warmly.
For financial analysis, format responses with clear headings, bullet points, and specific recommendations based on their actual portfolio data."""

    def analyze_portfolio(self, portfolio_data=None, user_question="", simulation_data=None):
        """Analyze portfolio data and provide AI-powered insights with dynamic portfolio memory"""
        try:
            print(f"Starting AI analysis with token: {cerebras_token[:10] if cerebras_token else 'None'}...")
            if not cerebras_token or cerebras_token == 'YOUR_CEREBRAS_TOKEN':
                print("No valid token found, using fallback")
                return """I'm sorry, but the AI advisor is not currently available. To enable AI portfolio analysis, please:

1. Get a Cerebras API token from https://www.cerebras.net/
2. Set the CEREBRAS_TOKEN environment variable
3. Restart the application

Example: export CEREBRAS_TOKEN='your-cerebras-token-here'

In the meantime, you can still analyze your portfolio manually using the performance metrics and charts provided."""
            
            # Use global portfolio state if no specific data provided
            if portfolio_data is None:
                portfolio_data = {
                    'final_metrics': current_portfolio_state['final_metrics'],
                    'results': current_portfolio_state['results']
                }
                simulation_data = {
                    'initial_cash': current_portfolio_state['initial_cash'],
                    'start_date': current_portfolio_state['start_date'],
                    'duration_days': current_portfolio_state['duration_days'],
                    'trading_frequency': 'daily',
                    'tickers': current_portfolio_state['tickers'],
                    'trading_rules': current_portfolio_state['trading_rules']
                }
            
            # Check if it's a general conversation or portfolio-specific question
            question_lower = user_question.lower().strip()
            
            # Handle portfolio state queries
            if any(query in question_lower for query in ['what is my portfolio', 'my portfolio', 'current portfolio', 'show my portfolio', 'portfolio holdings', 'what do i own', 'my positions']):
                context = self._prepare_portfolio_context(portfolio_data, simulation_data)
                user_message = f"""User is asking about their current portfolio. Here is their ACTUAL portfolio state:

{context}

User Question: "{user_question}"

Please provide a comprehensive overview of their current portfolio including:
1. Current holdings and positions
2. Portfolio value and performance
3. Risk metrics and analysis
4. Recent trading activity
5. Overall assessment and recommendations

Be specific about their actual holdings, values, and performance metrics."""
            
            # Handle general greetings and non-portfolio questions
            elif any(greeting in question_lower for greeting in ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']):
                user_message = f"""User said: "{user_question}"

Please respond naturally and friendly to this greeting. You can mention that you're a portfolio advisor ready to help with investment questions. If they have a portfolio simulation, you can mention that you're aware of their current holdings and ready to help analyze it."""
            
            elif any(general in question_lower for general in ['how are you', 'what can you do', 'help', 'what do you do']):
                user_message = f"""User asked: "{user_question}"

Please explain that you're an AI portfolio advisor who can help analyze investment portfolios, provide financial advice, and answer questions about trading strategies, risk management, and portfolio optimization. You have access to their current portfolio state and can provide specific insights about their holdings and performance."""
            
            else:
                # Portfolio analysis questions
                context = self._prepare_portfolio_context(portfolio_data, simulation_data)
                user_message = f"""Please analyze this portfolio data and provide insights:

{context}

User Question: {user_question if user_question else "Please provide a comprehensive analysis of this portfolio and any recommendations for improvement."}

Please provide a detailed analysis covering:
1. Overall performance assessment
2. Risk analysis
3. Portfolio diversification
4. Trading strategy evaluation
5. Specific recommendations for improvement"""

            # Call Cerebras API
            print(f"Making API call to Cerebras...")
            
            # Debug: Print what we're sending to AI
            print(f"\n{'='*50}")
            print(f"REQUEST TO AI:")
            print(f"{'='*50}")
            print(f"User Question: {user_question}")
            if 'context' in locals():
                print(f"Context Length: {len(context)} characters")
            print(f"User Message Length: {len(user_message)} characters")
            print(f"Model: llama3.1-8b")
            print(f"Max Tokens: 1500")
            print(f"{'='*50}\n")
            
            headers = {
                "Authorization": f"Bearer {cerebras_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama3.1-8b",  # Cerebras model
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 1500,
                "temperature": 0.7
            }
            
            response = requests.post(cerebras_api_url, headers=headers, json=payload, timeout=30)
            print(f"API Response Status: {response.status_code}")
            response.raise_for_status()
            
            result = response.json()
            print(f"API Success! Returning AI response...")
            
            # Debug: Print the full AI response
            ai_response = result['choices'][0]['message']['content']
            print(f"\n{'='*50}")
            print(f"AI RESPONSE DEBUG:")
            print(f"{'='*50}")
            print(ai_response)
            print(f"{'='*50}\n")
            
            return ai_response
            
        except Exception as e:
            # Provide a fallback analysis when API is not available
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ["quota", "billing", "limit", "unauthorized", "forbidden", "404", "not found"]):
                return self._generate_fallback_analysis(portfolio_data, user_question, simulation_data)
            else:
                return f"I apologize, but I encountered an error while analyzing your portfolio: {str(e)}. Please check your Cerebras API token and try again."

    def _generate_fallback_analysis(self, portfolio_data, user_question="", simulation_data=None):
        """Generate a fallback analysis when AI API is not available"""
        metrics = portfolio_data.get('final_metrics', {})
        
        # Extract key metrics
        total_return = metrics.get('total_return_pct', 0)
        final_value = metrics.get('final_value', 0)
        total_pnl = metrics.get('total_pnl', 0)
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        volatility = metrics.get('volatility_pct', 0)
        beta = metrics.get('beta', 0)
        beta_interpretation = metrics.get('beta_interpretation', 'N/A')
        correlation = metrics.get('correlation', 0)
        total_trades = metrics.get('total_trades', 0)
        positions = metrics.get('final_positions', {})
        
        # Generate analysis based on user question
        analysis = "🤖 **AI Portfolio Analysis (Demo Mode)**\n\n"
        question_lower = user_question.lower()
        
        # Always show performance analysis for "analyze my portfolio" or similar requests
        if ("analyze" in question_lower or "performance" in question_lower or 
            "how" in question_lower or "doing" in question_lower or not user_question.strip()):
            analysis += "📊 **Performance Analysis:**\n"
            if total_return > 0:
                analysis += f"• Your portfolio achieved a **{total_return:.1f}% return** - excellent performance!\n"
            else:
                analysis += f"• Your portfolio shows a **{total_return:.1f}% return** - consider reviewing your strategy\n"
            analysis += f"• Final Value: ${final_value:,.2f}\n"
            analysis += f"• Total P&L: ${total_pnl:,.2f}\n\n"
        
        # Risk analysis
        if ("risk" in question_lower or "volatile" in question_lower or "safe" in question_lower):
            analysis += "⚠️ **Risk Assessment:**\n"
            if sharpe_ratio > 1.0:
                analysis += f"• Sharpe Ratio: {sharpe_ratio:.2f} - **Excellent risk-adjusted returns**\n"
            elif sharpe_ratio > 0.5:
                analysis += f"• Sharpe Ratio: {sharpe_ratio:.2f} - **Good risk-adjusted returns**\n"
            else:
                analysis += f"• Sharpe Ratio: {sharpe_ratio:.2f} - **Consider improving risk management**\n"
            analysis += f"• Volatility: {volatility:.1f}% - {'Low' if volatility < 10 else 'Moderate' if volatility < 20 else 'High'} risk level\n"
            analysis += f"• Beta: {beta:.3f} - **{beta_interpretation}**\n"
            analysis += f"• Market Correlation: {correlation:.3f} - {'Strong' if abs(correlation) > 0.7 else 'Moderate' if abs(correlation) > 0.3 else 'Weak'} correlation with market\n"
            analysis += f"• Total Trades: {total_trades} - {'Conservative' if total_trades < 20 else 'Active' if total_trades < 50 else 'Very Active'} strategy\n\n"
        
        # Diversification analysis
        if ("diversif" in question_lower or "position" in question_lower or "stock" in question_lower):
            analysis += "🎯 **Portfolio Composition:**\n"
            if positions:
                analysis += "• Current Positions:\n"
                for ticker, shares in positions.items():
                    analysis += f"  - {ticker}: {shares} shares\n"
                if len(positions) < 3:
                    analysis += "• **Recommendation**: Consider adding more positions for better diversification\n"
                else:
                    analysis += "• Good diversification across multiple positions\n"
            analysis += "\n"
        
        # Beta analysis
        if ("beta" in question_lower or "market" in question_lower or "correlation" in question_lower):
            analysis += "📊 **Beta & Market Analysis:**\n"
            analysis += f"• Portfolio Beta: {beta:.3f}\n"
            analysis += f"• Interpretation: **{beta_interpretation}**\n"
            analysis += f"• Market Correlation: {correlation:.3f}\n"
            if beta > 1.0:
                analysis += "• **High Beta Strategy**: Your portfolio is more volatile than the market\n"
            elif beta < 1.0 and beta > 0:
                analysis += "• **Defensive Strategy**: Your portfolio is less volatile than the market\n"
            elif beta < 0:
                analysis += "• **Hedge Strategy**: Your portfolio moves opposite to the market\n"
            analysis += "\n"

        # Trading strategy analysis
        if ("strategy" in question_lower or "trading" in question_lower or "rules" in question_lower):
            analysis += "📈 **Trading Strategy Analysis:**\n"
            analysis += f"• Total Trades Executed: {total_trades}\n"
            if total_trades > 50:
                analysis += "• **High-frequency trading** - watch transaction costs\n"
            elif total_trades > 20:
                analysis += "• **Active trading strategy** - good balance of activity\n"
            else:
                analysis += "• **Conservative approach** - lower transaction costs\n"
            analysis += f"• Sharpe Ratio: {sharpe_ratio:.2f} - {'Excellent' if sharpe_ratio > 1.0 else 'Good' if sharpe_ratio > 0.5 else 'Needs improvement'} risk-adjusted performance\n\n"
        
        # Add general recommendations
        analysis += "💡 **Key Recommendations:**\n"
        if total_return > 15:
            analysis += "• **Excellent performance!** Consider taking some profits\n"
        elif total_return > 5:
            analysis += "• **Solid performance** - your strategy is working well\n"
        else:
            analysis += "• **Review your strategy** - consider different entry/exit points\n"
        
        if volatility > 20:
            analysis += "• **High volatility detected** - consider reducing position sizes\n"
        
        if total_trades > 50:
            analysis += "• **Active trading strategy** - watch out for transaction costs\n"
        
        analysis += "• **Regular rebalancing** helps maintain target allocation\n"
        analysis += "• **Dollar-cost averaging** can reduce timing risk\n\n"
        
        analysis += "🔧 **To enable full AI analysis:** Set up your Cerebras API token in the environment variables."
        
        return analysis

    def _prepare_portfolio_context(self, portfolio_data, simulation_data=None):
        """Prepare portfolio data for AI analysis"""
        context = "PORTFOLIO ANALYSIS DATA:\n\n"
        
        # Add simulation parameters if available
        if simulation_data:
            context += f"SIMULATION PARAMETERS:\n"
            context += f"- Initial Cash: ${simulation_data.get('initial_cash', 'N/A')}\n"
            context += f"- Start Date: {simulation_data.get('start_date', 'N/A')}\n"
            context += f"- Duration: {simulation_data.get('duration_days', 'N/A')} days\n"
            context += f"- Trading Frequency: {simulation_data.get('trading_frequency', 'N/A')}\n"
            context += f"- Initial Tickers: {simulation_data.get('tickers', {})}\n"
            context += f"- Trading Rules: {simulation_data.get('trading_rules', {})}\n\n"
        
        # Add performance metrics
        if 'final_metrics' in portfolio_data:
            metrics = portfolio_data['final_metrics']
            context += f"PERFORMANCE METRICS:\n"
            context += f"- Total Return: {metrics.get('total_return_pct', 'N/A')}%\n"
            context += f"- Final Portfolio Value: ${metrics.get('final_value', 'N/A')}\n"
            context += f"- Total P&L: ${metrics.get('total_pnl', 'N/A')}\n"
            context += f"- Sharpe Ratio: {metrics.get('sharpe_ratio', 'N/A')}\n"
            context += f"- Volatility: {metrics.get('volatility_pct', 'N/A')}%\n"
            context += f"- Beta: {metrics.get('beta', 'N/A')}\n"
            context += f"- Beta Interpretation: {metrics.get('beta_interpretation', 'N/A')}\n"
            context += f"- Market Correlation: {metrics.get('correlation', 'N/A')}\n"
            context += f"- Total Trades: {metrics.get('total_trades', 'N/A')}\n"
            context += f"- Final Positions: {metrics.get('final_positions', {})}\n\n"
        
        # Add detailed trading activity
        if 'results' in portfolio_data and portfolio_data['results']:
            results = portfolio_data['results']
            context += f"TRADING ACTIVITY:\n"
            context += f"- Simulation Duration: {len(results)} intervals\n"
            
            # Analyze trading patterns
            trades_count = 0
            all_trades = []
            price_movements = {}
            
            for result in results:
                if result.get('trades'):
                    trades_count += len(result['trades'])
                    all_trades.extend(result['trades'])
                
                # Track price movements
                if result.get('prices'):
                    for ticker, price in result['prices'].items():
                        if ticker not in price_movements:
                            price_movements[ticker] = []
                        price_movements[ticker].append(price)
            
            context += f"- Total Trading Activity: {trades_count} trades\n"
            
            # Show recent positions
            if results:
                latest_positions = results[-1].get('positions', {})
                context += f"- Current Positions: {latest_positions}\n"
                
                # Show price trends with more detail
                if len(results) > 1:
                    first_result = results[0]
                    last_result = results[-1]
                    context += f"\nPRICE MOVEMENTS:\n"
                    for ticker in first_result.get('prices', {}):
                        if ticker in first_result['prices'] and ticker in last_result.get('prices', {}):
                            first_price = first_result['prices'][ticker]
                            last_price = last_result['prices'][ticker]
                            change_pct = ((last_price - first_price) / first_price) * 100
                            context += f"- {ticker}: ${first_price:.2f} → ${last_price:.2f} ({change_pct:+.2f}%)\n"
            
            # Add recent trades detail
            if all_trades:
                context += f"\nRECENT TRADES (last 5):\n"
                recent_trades = all_trades[-5:] if len(all_trades) > 5 else all_trades
                for trade in recent_trades:
                    context += f"- {trade}\n"
            
            # Add portfolio value progression
            if len(results) > 1:
                context += f"\nPORTFOLIO VALUE PROGRESSION:\n"
                # Show first, middle, and last values
                first_value = results[0].get('portfolio_value', 0)
                middle_idx = len(results) // 2
                middle_value = results[middle_idx].get('portfolio_value', 0)
                last_value = results[-1].get('portfolio_value', 0)
                context += f"- Start: ${first_value:,.2f}\n"
                context += f"- Midpoint: ${middle_value:,.2f}\n"
                context += f"- Final: ${last_value:,.2f}\n"
        
        return context

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
            
            # If start date is a weekend, move to next weekday
            while currtime.weekday() >= 5:  # Saturday=5, Sunday=6
                currtime += timedelta(days=1)
                print(f"Start date was weekend, moving to {currtime.strftime('%Y-%m-%d')}")
            
            # For intraday simulations, start at market open (9:30 AM)
            if self.trading_frequency == 'intraday':
                currtime = currtime.replace(hour=9, minute=30, second=0, microsecond=0)
            
            start_date_str = currtime.strftime('%Y-%m-%d')
            end_date_str = (currtime + timedelta(days=self.duration_days + 30)).strftime('%Y-%m-%d')
            
            port = Portfolio(self.initial_cash, start_date_str, end_date_str)
            
            # Initialize stock data with appropriate interval
            data = {}
            interval = '60m' if self.trading_frequency == 'intraday' else '1d'
            for ticker in self.tickers.keys():
                data[ticker] = StockData(ticker, start_date_str, end_date_str)
                # Update the stock data with the correct interval
                data[ticker].get_stock_data(ticker, start_date_str, end_date_str, interval)
            
            # Initial purchases with real market prices using the same stock data objects
            print(f"Starting with cash: ${port.cash:,.2f}")
            for ticker, shares in self.tickers.items():
                # Use the first available trading day from the stock data
                if not data[ticker].stock_data.empty:
                    first_trading_day = data[ticker].stock_data.index[0]
                    data[ticker].curtime = first_trading_day
                    current_price = data[ticker].get_price()
                    
                    print(f"First trading day for {ticker}: {first_trading_day}")
                    print(f"Price on first trading day: ${current_price}")
                    
                    if current_price is not None:
                        # Buy at exact market price to ensure execution
                        purchase_price = current_price
                        port.buy(ticker, purchase_price, shares, first_trading_day)
                        print(f"Initial purchase: {shares} shares of {ticker} at ${purchase_price:.2f}")
                        print(f"  Cash after purchase: ${port.cash:,.2f}")
                        print(f"  Positions after purchase: {port.positions}")
                    else:
                        print(f"Warning: Could not get price for {ticker} on {first_trading_day}, skipping initial purchase")
                else:
                    print(f"Warning: No stock data available for {ticker}, skipping initial purchase")
            
            print(f"Final cash after all purchases: ${port.cash:,.2f}")
            print(f"Final positions after all purchases: {port.positions}")
            
            # Calculate portfolio value right after initial purchases
            initial_portfolio_value = port.get_value(currtime)
            print(f"Portfolio value after initial purchases: ${initial_portfolio_value:,.2f}")
            
            # Record initial state (after purchases) as first result
            initial_interval_label = 'Day 0 (Initial)' if self.trading_frequency == 'daily' else 'Day 0, Initial'
            initial_result = {
                'day': 0,
                'interval_label': initial_interval_label,
                'date': currtime.strftime('%Y-%m-%d %H:%M') if self.trading_frequency == 'intraday' else currtime.strftime('%Y-%m-%d'),
                'prices': {ticker: data[ticker].get_price() for ticker in self.tickers.keys() if data[ticker].get_price() is not None},
                'portfolio_value': initial_portfolio_value,
                'trades': [],
                'positions': port.positions.copy(),
                'cash': port.cash,
                'pnl': port.get_PNL(currtime)
            }
            self.results.append(initial_result)
            print(f"Recorded initial result: positions={port.positions}, value=${initial_portfolio_value:,.2f}")
            
            # Run simulation based on trading frequency
            if self.trading_frequency == 'intraday':
                # For intraday: simulate 60-minute intervals within each day
                total_intervals = self.duration_days * 6  # 6 intervals per day (6 hours / 60 min)
                interval_delta = timedelta(hours=1)
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
                
                # Get current prices for portfolio tickers
                current_prices = {}
                for ticker in self.tickers.keys():
                    price = data[ticker].get_price()
                    if price is not None:
                        current_prices[ticker] = price
                
                # Get current prices for trading rule tickers (if not already fetched)
                for ticker in self.trading_rules.keys():
                    if ticker not in current_prices:
                        # Use dummy price for trading rule tickers (no stock validation)
                        current_prices[ticker] = 100.0  # Default dummy price
                
                # Check trading conditions and execute trades
                trades_executed = []
                
                for ticker, rules in self.trading_rules.items():
                    try:
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
                    except Exception as e:
                        print(f"Error processing trading rules for {ticker}: {e}")
                        continue
                
                # Get current portfolio value
                current_value = port.get_value(currtime)
                
                # Store interval result with meaningful labels
                if self.trading_frequency == 'daily':
                    interval_label = f"Day {i + 1}"
                else:  # intraday
                    day_num = (i // 6) + 1
                    interval_in_day = (i % 6) + 1
                    # Format as "Day X, Interval Y" with time
                    time_str = currtime.strftime('%H:%M')
                    interval_label = f"Day {day_num}, {time_str}"
                
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
                # Use the actual initial portfolio value after initial purchases
                initial_value = self.results[0]['portfolio_value']
                final_value = self.results[-1]['portfolio_value']
                
                # Calculate return based on actual starting portfolio value
                total_return = (final_value - initial_value) / initial_value * 100 if initial_value > 0 else 0
                
                print(f"Final metrics calculation:")
                print(f"  Initial portfolio value: ${initial_value:,.2f}")
                print(f"  Final portfolio value: ${final_value:,.2f}")
                print(f"  Total return: {total_return:.2f}%")
                
                sharpe_ratio = port.calculate_sharpe_ratio()
                volatility = port.calculate_volatility()
                
                # Calculate portfolio beta
                beta_result = port.calculate_portfolio_beta()
                
                self.final_metrics = {
                    'total_return_pct': round(total_return, 2),
                    'final_value': round(final_value, 2),
                    'total_pnl': round(final_value - self.initial_cash, 2),
                    'sharpe_ratio': round(sharpe_ratio, 3) if sharpe_ratio else None,
                    'volatility_pct': round(volatility * 100, 2) if volatility else None,
                    'total_trades': len(port.past_trades),
                    'final_positions': port.positions,
                    'beta': beta_result['beta'] if beta_result else None,
                    'beta_interpretation': beta_result['interpretation'] if beta_result else None,
                    'correlation': beta_result['correlation'] if beta_result else None
                }
            
            self.is_complete = True
            
            # Update global portfolio state for AI
            update_portfolio_state(self.simulation_id, {
                'initial_cash': self.initial_cash,
                'start_date': self.start_date,
                'duration_days': self.duration_days,
                'tickers': self.tickers,
                'trading_rules': self.trading_rules
            })
            
            print(f"Simulation {self.simulation_id} completed successfully")
            
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
            try:
                ticker = rule_data['ticker'].upper()
                if ticker not in trading_rules:
                    trading_rules[ticker] = []
                trading_rules[ticker].append({
                    'action': rule_data.get('action', 'sell'),  # Default to sell for backward compatibility
                    'condition': rule_data['condition'],
                    'threshold': float(rule_data['threshold']),
                    'shares': int(rule_data['shares'])
                })
            except Exception as e:
                print(f"Error processing trading rule: {e}")
                print(f"Rule data: {rule_data}")
                continue
        
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

@app.route('/ai_analysis', methods=['POST'])
def ai_analysis():
    """Get AI analysis of portfolio data with dynamic portfolio memory"""
    try:
        data = request.json
        simulation_id = data.get('simulation_id')
        user_question = data.get('question', '')
        
        # Initialize AI advisor
        advisor = AIAdvisor()
        
        # If no simulation_id provided, use global portfolio state
        if not simulation_id:
            if current_portfolio_state['has_simulation']:
                # Use current portfolio state
                analysis = advisor.analyze_portfolio(None, user_question, None)
                return jsonify({
                    'success': True,
                    'analysis': analysis,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'current_portfolio_state'
                })
            else:
                # No portfolio data available
                analysis = advisor.analyze_portfolio(None, user_question, None)
                return jsonify({
                    'success': True,
                    'analysis': analysis,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'no_portfolio_data'
                })
        
        # Handle specific simulation ID
        if simulation_id == 'test-simulation-123':
            # Use sample data for testing
            portfolio_data = {
                'final_metrics': {
                    'total_return_pct': 15.5,
                    'final_value': 115500.0,
                    'total_pnl': 15500.0,
                    'sharpe_ratio': 1.2,
                    'volatility_pct': 12.3,
                    'total_trades': 45,
                    'final_positions': {'AAPL': 100, 'MSFT': 50, 'GOOGL': 25}
                },
                'results': []
            }
            simulation_data = {
                'initial_cash': 100000,
                'start_date': '2023-01-03',
                'duration_days': 30,
                'trading_frequency': 'daily',
                'tickers': {'AAPL': 50, 'MSFT': 25, 'GOOGL': 10},
                'trading_rules': {'buy_threshold': 0.02, 'sell_threshold': 0.02}
            }
        elif simulation_id in active_simulations:
            simulation = active_simulations[simulation_id]
            
            # Prepare portfolio data for analysis
            portfolio_data = {
                'final_metrics': getattr(simulation, 'final_metrics', {}),
                'results': simulation.results
            }
            
            # Prepare simulation parameters
            simulation_data = {
                'initial_cash': simulation.initial_cash,
                'start_date': simulation.start_date,
                'duration_days': simulation.duration_days,
                'trading_frequency': simulation.trading_frequency,
                'tickers': simulation.tickers,
                'trading_rules': simulation.trading_rules
            }
        else:
            return jsonify({'error': 'Simulation not found'}), 404
        
        # Get analysis
        analysis = advisor.analyze_portfolio(portfolio_data, user_question, simulation_data)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat(),
            'source': 'specific_simulation'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/plot/<simulation_id>/<plot_type>')
def get_plot(simulation_id, plot_type):
    """Generate and return portfolio plots as base64 encoded images"""
    try:
        if simulation_id not in active_simulations:
            return jsonify({'error': 'Simulation not found'}), 404
        
        simulation = active_simulations[simulation_id]
        
        if not simulation.is_complete:
            return jsonify({'error': 'Simulation not complete'}), 400
        
        # Create a portfolio object and populate it with the actual simulation data
        currtime = datetime.strptime(simulation.start_date, '%Y-%m-%d')
        end_date_str = (currtime + timedelta(days=simulation.duration_days + 30)).strftime('%Y-%m-%d')
        
        port = Portfolio(simulation.initial_cash, simulation.start_date, end_date_str)
        
        # Populate the portfolio's change_over_time with actual simulation results
        for result in simulation.results:
            result_time = datetime.strptime(result['date'], '%Y-%m-%d %H:%M' if ':' in result['date'] else '%Y-%m-%d')
            portfolio_value = result['portfolio_value']
            
            # Store the actual portfolio value at this timestamp
            port.change_over_time[result_time] = portfolio_value
        
        # Generate the requested plot
        plt.clf()  # Clear any existing plots
        
        if plot_type == 'value':
            # Portfolio value over time
            port.plot_portfolio_value(title="Portfolio Value Over Time", show_percentage=False, save_path=None, show_plot=False)
        elif plot_type == 'percentage':
            # Portfolio value as percentage change
            port.plot_portfolio_value(title="Portfolio Performance (%)", show_percentage=True, save_path=None, show_plot=False)
        elif plot_type == 'pnl':
            # Profit/Loss over time
            port.plot_pnl(title="Portfolio P&L Over Time", save_path=None, show_plot=False)
        else:
            return jsonify({'error': 'Invalid plot type'}), 400
        
        # Convert plot to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()  # Close the plot to free memory
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_base64}',
            'plot_type': plot_type
        })
        
    except Exception as e:
        plt.close()  # Ensure plot is closed on error
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/plot/current/<plot_type>')
def get_current_plot(plot_type):
    """Generate plots from the current portfolio state"""
    try:
        if not current_portfolio_state['has_simulation']:
            return jsonify({'error': 'No simulation data available'}), 400
        
        simulation_id = current_portfolio_state['simulation_id']
        return get_plot(simulation_id, plot_type)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
