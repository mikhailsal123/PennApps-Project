let currentSimulationId = null;
let statusInterval = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Duration slider update
    const durationSlider = document.getElementById('durationDays');
    const durationValue = document.getElementById('durationValue');
    
    durationSlider.addEventListener('input', function() {
        durationValue.textContent = this.value;
    });
    
    // Form submission
    document.getElementById('simulationForm').addEventListener('submit', startSimulation);
    
    // Stop button
    document.getElementById('stopBtn').addEventListener('click', stopSimulation);
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

function startSimulation(e) {
    e.preventDefault();
    
    const formData = collectFormData();
    
    if (!validateForm(formData)) {
        return;
    }
    
    // Show loading state
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const progressCard = document.getElementById('progressCard');
    
    startBtn.disabled = true;
    startBtn.innerHTML = '<span class="loading-spinner"></span> Starting...';
    progressCard.style.display = 'block';
    
    // Start simulation
    fetch('/start_simulation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentSimulationId = data.simulation_id;
            startBtn.style.display = 'none';
            stopBtn.style.display = 'block';
            
            // Start polling for status updates
            startStatusPolling();
            
            // Clear previous results
            document.getElementById('resultsContainer').innerHTML = '';
            document.getElementById('finalMetricsCard').style.display = 'none';
        } else {
            alert('Error: ' + data.error);
            resetForm();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error starting simulation');
        resetForm();
    });
}

function stopSimulation() {
    if (currentSimulationId) {
        fetch(`/stop_simulation/${currentSimulationId}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                resetForm();
            }
        });
    }
}

function startStatusPolling() {
    statusInterval = setInterval(() => {
        fetch(`/simulation_status/${currentSimulationId}`)
        .then(response => response.json())
        .then(data => {
            updateProgress(data);
            updateResults(data);
            
            if (data.is_complete) {
                clearInterval(statusInterval);
                showFinalResults(data);
                resetForm();
            }
        })
        .catch(error => {
            console.error('Error fetching status:', error);
        });
    }, 500); // Poll every 500ms
}

function updateProgress(data) {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    
    const progress = Math.round(data.progress * 100);
    progressBar.style.width = progress + '%';
    progressBar.setAttribute('aria-valuenow', progress);
    
    if (data.is_complete) {
        progressText.textContent = 'Simulation Complete!';
    } else {
        progressText.textContent = `Day ${data.results.length} of ${data.results.length / data.progress} - Running...`;
    }
}

function updateResults(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (data.results && data.results.length > 0) {
        // Clear loading message if it exists
        if (resultsContainer.innerHTML.includes('Configure your portfolio')) {
            resultsContainer.innerHTML = '';
        }
        
        // Add new results
        const latestResults = data.results.slice(-5); // Show last 5 days
        latestResults.forEach(result => {
            if (!document.getElementById(`day-${result.day}`)) {
                addDayResult(result);
            }
        });
    }
}

function addDayResult(result) {
    const resultsContainer = document.getElementById('resultsContainer');
    
    const dayDiv = document.createElement('div');
    dayDiv.className = 'day-result';
    dayDiv.id = `day-${result.day}`;
    
    if (result.trades.length > 0) {
        dayDiv.classList.add('trading-day');
    }
    
    if (Object.keys(result.prices).length === 0) {
        dayDiv.classList.add('market-closed');
    }
    
    let pricesHtml = '';
    if (Object.keys(result.prices).length > 0) {
        pricesHtml = '<div class="price-display">';
        for (const [ticker, price] of Object.entries(result.prices)) {
            pricesHtml += `<span class="badge bg-primary me-1">${ticker}: $${price.toFixed(2)}</span>`;
        }
        pricesHtml += '</div>';
    } else {
        pricesHtml = '<div class="text-muted"><i class="fas fa-calendar-times"></i> Market Closed</div>';
    }
    
    let tradesHtml = '';
    if (result.trades.length > 0) {
        tradesHtml = '<div class="mt-2">';
        result.trades.forEach(trade => {
            const isBuy = trade.toLowerCase().includes('bought');
            const tradeClass = isBuy ? 'trade-executed buy' : 'trade-executed sell';
            const icon = isBuy ? 'fa-plus-circle' : 'fa-minus-circle';
            tradesHtml += `<div class="${tradeClass}"><i class="fas ${icon}"></i> ${trade}</div>`;
        });
        tradesHtml += '</div>';
    }
    
    dayDiv.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
            <div>
                <h6 class="mb-1">${result.interval_label || `Day ${result.day}`} - ${result.date}</h6>
                ${pricesHtml}
                ${tradesHtml}
            </div>
            <div class="text-end">
                <div class="portfolio-value">$${result.portfolio_value.toLocaleString()}</div>
                <small class="text-muted">P&L: $${result.pnl ? result.pnl.toFixed(2) : '0.00'}</small>
            </div>
        </div>
    `;
    
    resultsContainer.appendChild(dayDiv);
    dayDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showFinalResults(data) {
    if (data.final_metrics) {
        const finalMetricsCard = document.getElementById('finalMetricsCard');
        const finalMetrics = document.getElementById('finalMetrics');
        
        finalMetrics.innerHTML = `
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value">$${data.final_metrics.final_value.toLocaleString()}</div>
                    <div class="metric-label">Final Value</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value ${data.final_metrics.total_return_pct >= 0 ? 'positive' : 'negative'}">
                        ${data.final_metrics.total_return_pct >= 0 ? '+' : ''}${data.final_metrics.total_return_pct}%
                    </div>
                    <div class="metric-label">Total Return</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value ${data.final_metrics.total_pnl >= 0 ? 'positive' : 'negative'}">
                        $${data.final_metrics.total_pnl.toLocaleString()}
                    </div>
                    <div class="metric-label">Total P&L</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value">
                        ${data.final_metrics.sharpe_ratio ? data.final_metrics.sharpe_ratio.toFixed(3) : 'N/A'}
                    </div>
                    <div class="metric-label">Sharpe Ratio</div>
                </div>
            </div>
        `;
        
        finalMetricsCard.style.display = 'block';
    }
    
    // Update progress to 100%
    document.getElementById('progressBar').style.width = '100%';
    document.getElementById('progressText').textContent = 'Simulation Complete!';
}

function collectFormData() {
    const tickers = [];
    const tickerInputs = document.querySelectorAll('#tickersContainer .ticker-input');
    
    tickerInputs.forEach(input => {
        const tickerInput = input.querySelector('input[type="text"]');
        const sharesInput = input.querySelector('input[type="number"]');
        
        if (tickerInput.value.trim() && sharesInput.value) {
            tickers.push({
                ticker: tickerInput.value.trim().toUpperCase(),
                shares: parseInt(sharesInput.value)
            });
        }
    });
    
    const tradingRules = [];
    const ruleInputs = document.querySelectorAll('#tradingRulesContainer .trading-rule');
    
    ruleInputs.forEach(input => {
        const tickerSelect = input.querySelector('select:first-child');
        const actionSelect = input.querySelector('.action-select');
        const conditionSelect = input.querySelector('select:last-of-type');
        const thresholdInput = input.querySelector('input[type="number"]:first-of-type');
        const sharesInput = input.querySelector('input[type="number"]:last-of-type');
        
        if (tickerSelect.value && actionSelect.value && conditionSelect.value && thresholdInput.value && sharesInput.value) {
            tradingRules.push({
                ticker: tickerSelect.value,
                action: actionSelect.value,
                condition: conditionSelect.value,
                threshold: parseFloat(thresholdInput.value),
                shares: parseInt(sharesInput.value)
            });
        }
    });
    
    return {
        initial_cash: parseFloat(document.getElementById('initialCash').value),
        start_date: document.getElementById('startDate').value,
        duration_days: parseInt(document.getElementById('durationDays').value),
        trading_frequency: document.getElementById('tradingFrequency').value,
        tickers: tickers,
        trading_rules: tradingRules
    };
}

function validateForm(data) {
    if (data.tickers.length === 0) {
        alert('Please add at least one stock to trade.');
        return false;
    }
    
    if (data.initial_cash < 1000) {
        alert('Initial cash must be at least $1,000.');
        return false;
    }
    
    // Dynamic validation based on trading frequency
    const maxDays = data.trading_frequency === 'intraday' ? 60 : 365;
    if (data.duration_days < 1 || data.duration_days > maxDays) {
        const frequencyText = data.trading_frequency === 'intraday' ? 'intraday' : 'daily';
        alert(`Duration must be between 1 and ${maxDays} days for ${frequencyText} trading.`);
        return false;
    }
    
    return true;
}

function resetForm() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    
    startBtn.disabled = false;
    startBtn.innerHTML = '<i class="fas fa-play"></i> Start Simulation';
    startBtn.style.display = 'block';
    stopBtn.style.display = 'none';
    
    if (statusInterval) {
        clearInterval(statusInterval);
        statusInterval = null;
    }
    
    currentSimulationId = null;
}

function addTicker() {
    const container = document.getElementById('tickersContainer');
    const tickerInput = document.createElement('div');
    tickerInput.className = 'ticker-input mb-2';
    tickerInput.innerHTML = `
        <div class="input-group">
            <input type="text" class="form-control" placeholder="Ticker (e.g., AAPL)">
            <input type="number" class="form-control" placeholder="Shares" value="100" min="1">
            <button type="button" class="btn btn-outline-danger" onclick="removeTicker(this)">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    container.appendChild(tickerInput);
}

function removeTicker(button) {
    button.closest('.ticker-input').remove();
}

function addTradingRule() {
    const container = document.getElementById('tradingRulesContainer');
    const ruleInput = document.createElement('div');
    ruleInput.className = 'trading-rule mb-2';
    ruleInput.innerHTML = `
        <div class="input-group">
            <select class="form-select">
                <option value="NVDA">NVDA</option>
                <option value="AMZN">AMZN</option>
                <option value="GOOG">GOOG</option>
            </select>
            <select class="form-select action-select">
                <option value="sell">Sell</option>
                <option value="buy">Buy</option>
            </select>
            <select class="form-select">
                <option value="greater_than">Price ></option>
                <option value="less_than">Price <</option>
            </select>
            <input type="number" class="form-control" placeholder="Threshold" step="0.01">
            <input type="number" class="form-control" placeholder="Shares" value="10" min="1">
            <button type="button" class="btn btn-outline-danger" onclick="removeTradingRule(this)">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    container.appendChild(ruleInput);
}

function removeTradingRule(button) {
    button.closest('.trading-rule').remove();
}

function updateDurationLimits() {
    const tradingFrequency = document.getElementById('tradingFrequency').value;
    const durationSlider = document.getElementById('durationDays');
    const durationUnit = document.getElementById('durationUnit');
    const minDuration = document.getElementById('minDuration');
    const maxDuration = document.getElementById('maxDuration');
    const frequencyHelp = document.getElementById('frequencyHelp');
    
    if (tradingFrequency === 'intraday') {
        // Intraday: 30-minute intervals, max 60 days
        durationSlider.max = 60;
        durationUnit.textContent = 'days';
        minDuration.textContent = '1 day';
        maxDuration.textContent = '60 days';
        frequencyHelp.textContent = 'Intraday: 30-minute intervals, up to 60 days (13 trades per day)';
        if (parseInt(durationSlider.value) > 60) {
            durationSlider.value = 60;
            document.getElementById('durationValue').textContent = '60';
        }
    } else {
        // Daily: 1 day intervals, max 365 days
        durationSlider.max = 365;
        durationUnit.textContent = 'days';
        minDuration.textContent = '1 day';
        maxDuration.textContent = '365 days';
        frequencyHelp.textContent = 'Daily: 1-day intervals, up to 365 days (1 trade per day)';
    }
}
