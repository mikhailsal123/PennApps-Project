let currentSimulationId = null;
let statusInterval = null;
let aiChatVisible = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Duration slider update
    const durationSlider = document.getElementById('durationDays');
    const durationValue = document.getElementById('durationValue');
    
    if (durationSlider && durationValue) {
        durationSlider.addEventListener('input', function() {
            durationValue.textContent = this.value;
        });
    }
    
    // Form submission
    const simulationForm = document.getElementById('simulationForm');
    if (simulationForm) {
        simulationForm.addEventListener('submit', startSimulation);
    }
    
    // Stop button
    document.getElementById('stopBtn').addEventListener('click', stopSimulation);
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize AI chat functionality
    initializeAIChat();
    
    // Set initial welcome time
    const welcomeTime = document.getElementById('aiWelcomeTime');
    if (welcomeTime) {
        welcomeTime.textContent = new Date().toLocaleTimeString();
    }
    
    // Set a test simulation ID for immediate AI testing
    currentSimulationId = 'test-simulation-123';
    
    // Initialize duration limits
    updateDurationLimits();
    
    // Plot type buttons
    document.querySelectorAll('[data-plot-type]').forEach(btn => {
        btn.addEventListener('click', function() {
            const plotType = this.getAttribute('data-plot-type');
            loadPlot(plotType);
        });
    });
    
    // Show AI advisor immediately for testing
    setTimeout(() => {
        showAIAdvisor();
    }, 500);
    
});

function startSimulation(e) {
    e.preventDefault();
    console.log('startSimulation called');
    
    const formData = collectFormData();
    console.log('Form data collected:', formData);
    
    if (!validateForm(formData)) {
        console.log('Form validation failed');
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
        
        // Check for executed one-time rules and trigger evaporation
        checkForExecutedOneTimeRules(data);
        
        // Update hedge margin balance display
        updateHedgeMarginBalance(data);
    }
}

// Function to trigger evaporation effect for one-time rules
function triggerRuleEvaporation() {
    const oneTimeRules = document.querySelectorAll('.trading-rule.one-time-mode');
    oneTimeRules.forEach(rule => {
        rule.classList.add('evaporating');
        // Remove the element after animation completes
        setTimeout(() => {
            rule.remove();
        }, 2000); // Match the CSS animation duration
    });
}

// Function to check for executed one-time rules in simulation results
function checkForExecutedOneTimeRules(data) {
    if (data && data.results && data.results.length > 0) {
        const latestResult = data.results[data.results.length - 1];
        if (latestResult.one_time_rules_executed > 0) {
            console.log(`DEBUG: ${latestResult.one_time_rules_executed} one-time rules were executed`);
            triggerRuleEvaporation();
        }
    }
}

// Function to update hedge margin balance display
function updateHedgeMarginBalance(data) {
    const hedgeMarginElement = document.getElementById('hedgeMarginBalance');
    if (hedgeMarginElement && data && data.results && data.results.length > 0) {
        const latestResult = data.results[data.results.length - 1];
        if (latestResult.hedge_margin_balance !== undefined) {
            const balance = latestResult.hedge_margin_balance;
            hedgeMarginElement.textContent = `Hedge Margin: $${balance.toFixed(2)}`;
            
            // Color code based on available margin
            if (balance < 1000) {
                hedgeMarginElement.className = 'text-danger';
            } else if (balance < 5000) {
                hedgeMarginElement.className = 'text-warning';
            } else {
                hedgeMarginElement.className = 'text-info';
            }
        }
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
            const isBuy = trade.toLowerCase().includes('bought') && !trade.toLowerCase().includes('bought back');
            const isHedge = trade.toLowerCase().includes('hedged') || trade.toLowerCase().includes('shorted') || trade.toLowerCase().includes('bought back');
            let tradeClass, icon;
            
            if (isHedge) {
                tradeClass = 'trade-executed hedge';
                icon = 'fa-shield-alt';
            } else if (isBuy) {
                tradeClass = 'trade-executed buy';
                icon = 'fa-plus-circle';
            } else {
                tradeClass = 'trade-executed sell';
                icon = 'fa-minus-circle';
            }
            
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
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value">
                        ${data.final_metrics.beta ? data.final_metrics.beta.toFixed(3) : 'N/A'}
                    </div>
                    <div class="metric-label">Beta</div>
                    ${data.final_metrics.beta_interpretation ? `<div class="metric-subtitle">${data.final_metrics.beta_interpretation}</div>` : ''}
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value">
                        ${data.final_metrics.correlation ? data.final_metrics.correlation.toFixed(3) : 'N/A'}
                    </div>
                    <div class="metric-label">Market Correlation</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value">
                        ${data.final_metrics.hedge_trades_count || 0}
                    </div>
                    <div class="metric-label">Hedge Trades</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value">
                        $${data.final_metrics.total_hedge_margin_used ? data.final_metrics.total_hedge_margin_used.toLocaleString() : '0'}
                    </div>
                    <div class="metric-label">Margin Used</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value">
                        $${data.final_metrics.hedge_margin_remaining ? data.final_metrics.hedge_margin_remaining.toLocaleString() : '0'}
                    </div>
                    <div class="metric-label">Margin Remaining</div>
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
    
    tickerInputs.forEach((input, index) => {
        const tickerInput = input.querySelector('input[type="text"]');
        const sharesInput = input.querySelector('input[type="number"]');
        
        if (tickerInput && tickerInput.value.trim() && sharesInput && sharesInput.value) {
            tickers.push({
                ticker: tickerInput.value.trim().toUpperCase(),
                shares: parseInt(sharesInput.value)
            });
        }
    });
    
    const tradingRules = [];
    const ruleInputs = document.querySelectorAll('#tradingRulesContainer .trading-rule');
    console.log('DEBUG: Found', ruleInputs.length, 'trading rule inputs');
    
    ruleInputs.forEach((input, index) => {
        const tickerSelect = input.querySelector('.ticker-select');
        const actionSelect = input.querySelector('.action-select');
        const conditionSelect = input.querySelector('select:last-of-type');
        const thresholdInput = input.querySelector('input[type="number"]:first-of-type');
        const sharesInput = input.querySelector('input[type="number"]:last-of-type');
        
        console.log(`Rule ${index}:`, {
            ticker: tickerSelect?.value,
            action: actionSelect?.value,
            condition: conditionSelect?.value,
            threshold: thresholdInput?.value,
            shares: sharesInput?.value
        });
        
        if (tickerSelect && tickerSelect.value.trim() && actionSelect.value && conditionSelect.value && thresholdInput.value && sharesInput.value) {
            const isOneTime = input.classList.contains('one-time-mode');
            tradingRules.push({
                ticker: tickerSelect.value.toUpperCase().trim(),
                action: actionSelect.value,
                condition: conditionSelect.value,
                threshold: parseFloat(thresholdInput.value),
                shares: parseInt(sharesInput.value),
                one_time: isOneTime
            });
        }
    });
    
    console.log('DEBUG: Final trading rules array:', tradingRules);
    
    const formData = {
        initial_cash: parseFloat(document.getElementById('initialCash').value),
        start_date: document.getElementById('startDate').value,
        duration_days: parseInt(document.getElementById('durationDays').value),
        trading_frequency: document.getElementById('tradingFrequency').value,
        tickers: tickers,
        trading_rules: tradingRules,
        beta_hedge_enabled: document.getElementById('betaHedgeEnabled').checked
    };
    
    return formData;
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
            <input type="text" class="form-control" placeholder="Ticker (e.g., AAPL)" maxlength="10" style="text-transform: uppercase;" oninput="validateTicker(this)">
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
    ruleInput.onclick = function() { toggleOneTimeMode(this); };
    ruleInput.title = 'Click to toggle one-time execution mode';
    ruleInput.innerHTML = `
        <div class="input-group">
            <select class="form-select ticker-select">
                <option value="NVDA">NVDA</option>
                <option value="AAPL">AAPL</option>
                <option value="TSLA">TSLA</option>
                <option value="MSFT">MSFT</option>
                <option value="GOOGL">GOOGL</option>
                <option value="AMZN">AMZN</option>
                <option value="META">META</option>
                <option value="NFLX">NFLX</option>
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
            <button type="button" class="btn btn-outline-danger" onclick="removeTradingRule(this); event.stopPropagation();">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    container.appendChild(ruleInput);
}


function validateTicker(input) {
    const ticker = input.value.toUpperCase().trim();
    const isValid = /^[A-Z0-9.]{1,10}$/.test(ticker) && ticker.length >= 1;
    
    // Remove existing validation classes
    input.classList.remove('is-valid', 'is-invalid');
    
    if (ticker.length === 0) {
        // No validation styling for empty input
        return;
    } else if (isValid) {
        input.classList.add('is-valid');
        input.title = `Valid ticker symbol: ${ticker}`;
    } else {
        input.classList.add('is-invalid');
        input.title = 'Invalid ticker format. Use 1-10 uppercase letters/numbers (e.g., AAPL, TSLA, BRK.A)';
    }
}

function removeTradingRule(button) {
    button.closest('.trading-rule').remove();
}

function toggleOneTimeMode(tradingRule) {
    const isOneTime = tradingRule.classList.contains('one-time-mode');
    
    if (isOneTime) {
        // Turn off one-time mode
        tradingRule.classList.remove('one-time-mode');
        tradingRule.title = 'Click to toggle one-time execution mode';
    } else {
        // Turn on one-time mode
        tradingRule.classList.add('one-time-mode');
        tradingRule.title = 'One-time mode active - rule will execute once then be removed';
    }
}

function updateDurationLimits() {
    const tradingFrequency = document.getElementById('tradingFrequency').value;
    const durationSlider = document.getElementById('durationDays');
    const durationUnit = document.getElementById('durationUnit');
    const minDuration = document.getElementById('minDuration');
    const maxDuration = document.getElementById('maxDuration');
    const durationMidpoint = document.getElementById('durationMidpoint');
    const frequencyHelp = document.getElementById('frequencyHelp');
    
    if (tradingFrequency === 'intraday') {
        // Intraday: 60-minute intervals, max 60 days
        durationSlider.max = 60;
        durationUnit.textContent = 'days';
        minDuration.textContent = '1 day';
        maxDuration.textContent = '60 days';
        durationMidpoint.textContent = '30';
        frequencyHelp.textContent = 'Intraday: 60-minute intervals, up to 60 days (6 intervals per day)';
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
        durationMidpoint.textContent = '183';
        frequencyHelp.textContent = 'Daily: 1-day intervals, up to 365 days (1 trade per day)';
    }
}

// AI Chat Functions
function initializeAIChat() {
    // Chat input and send button
    const chatInput = document.getElementById('aiChatInput');
    const sendBtn = document.getElementById('aiSendBtn');
    
    if (chatInput && sendBtn) {
        sendBtn.addEventListener('click', sendAIMessage);
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendAIMessage();
            }
        });
    }
    
    // Quick question buttons
    const quickQuestionBtns = document.querySelectorAll('.quick-question-btn');
    quickQuestionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            if (question) {
                document.getElementById('aiChatInput').value = question;
                sendAIMessage();
            }
        });
    });
}

function showAIAdvisor() {
    console.log('showAIAdvisor called, currentSimulationId:', currentSimulationId);
    const aiAdvisorCard = document.getElementById('aiAdvisorCard');
    if (aiAdvisorCard && currentSimulationId) {
        console.log('Showing AI advisor card');
        aiAdvisorCard.style.display = 'block';
        
        // Auto-expand chat if not visible
        if (!aiChatVisible) {
            const chatCollapse = document.getElementById('aiChatCollapse');
            if (chatCollapse && !chatCollapse.classList.contains('show')) {
                const collapseInstance = new bootstrap.Collapse(chatCollapse, {show: true});
                aiChatVisible = true;
            }
        }
    } else {
        console.log('AI advisor card not found or no simulation ID');
    }
}

function sendAIMessage() {
    const chatInput = document.getElementById('aiChatInput');
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    console.log('sendAIMessage called, currentSimulationId:', currentSimulationId);
    
    // Add user message
    addMessage('user', message);
    chatInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send to AI - use currentSimulationId if available, otherwise let AI use global portfolio state
    const requestBody = {
        question: message
    };
    
    // Only include simulation_id if we have one and it's not the test simulation
    if (currentSimulationId && currentSimulationId !== 'test-simulation-123') {
        requestBody.simulation_id = currentSimulationId;
    }
    
    // Send to AI
    fetch('/ai_analysis', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();
        
        console.log('AI Response received:', data);
        console.log('Analysis content:', data.analysis);
        
        if (data.success) {
            addMessage('ai', data.analysis);
        } else {
            addMessage('ai', `Sorry, I encountered an error: ${data.error || 'Unknown error'}`);
        }
    })
    .catch(error => {
        hideTypingIndicator();
        addMessage('ai', `Sorry, I couldn't process your request. Please check your internet connection and try again.`);
        console.error('AI Chat Error:', error);
    });
}

function addMessage(sender, text) {
    console.log('addMessage called:', sender, text);
    const chatMessages = document.getElementById('aiChatMessages');
    if (!chatMessages) {
        console.log('chatMessages element not found');
        return;
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const time = new Date().toLocaleTimeString();
    const icon = sender === 'ai' ? 'fas fa-robot' : 'fas fa-user';
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <i class="${icon}"></i>
            <div class="message-text">${formatMessage(text)}</div>
        </div>
        <div class="message-time">${time}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatMessage(text) {
    // Convert line breaks to HTML
    text = text.replace(/\n/g, '<br>');
    
    // Format bullet points
    text = text.replace(/\n- /g, '<br>• ');
    text = text.replace(/^- /g, '• ');
    
    // Format numbered lists
    text = text.replace(/\n(\d+)\. /g, '<br>$1. ');
    text = text.replace(/^(\d+)\. /g, '$1. ');
    
    return text;
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('aiChatMessages');
    if (!chatMessages) return;
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'ai-typing';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <i class="fas fa-robot"></i>
        <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    typingDiv.style.display = 'flex';
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Override the existing updateResults function to show AI advisor and plots
const originalUpdateResults = updateResults;
updateResults = function(data) {
    console.log('updateResults override called with data:', data);
    originalUpdateResults(data);
    
    // Check for executed one-time rules and trigger evaporation
    checkForExecutedOneTimeRules(data);
    
    // Show final results, AI advisor and plots when simulation is complete
    console.log('updateResults data:', { 
        is_complete: data.is_complete, 
        error: data.error, 
        currentSimulationId,
        resultsLength: data.results ? data.results.length : 0
    });
    if (data.is_complete && !data.error && currentSimulationId) {
        console.log('Simulation complete, showing final results, AI advisor and plots...');
        setTimeout(() => {
            showFinalResults(data);
            showAIAdvisor();
            showPlotsCard();
        }, 1000); // Small delay to let results display first
    } else {
        console.log('Not showing final results because:', {
            is_complete: data.is_complete,
            has_error: !!data.error,
            has_simulation_id: !!currentSimulationId
        });
    }
};

// Portfolio Plot Functions
function showPlotsCard() {
    console.log('showPlotsCard called');
    const plotsCard = document.getElementById('plotsCard');
    console.log('plotsCard element:', plotsCard);
    if (plotsCard) {
        plotsCard.style.display = 'block';
        plotsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Load the default plot (portfolio value)
        console.log('Loading default plot...');
        loadPlot('value');
    } else {
        console.error('plotsCard element not found!');
    }
}

function loadPlot(plotType) {
    const plotContainer = document.getElementById('plotContainer');
    const plotLoading = document.getElementById('plotLoading');
    
    if (!plotContainer || !plotLoading) return;
    
    // Show loading indicator
    plotLoading.style.display = 'block';
    plotContainer.style.display = 'none';
    
    // Update button states
    document.querySelectorAll('[data-plot-type]').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-plot-type="${plotType}"]`).classList.add('active');
    
    // Determine which endpoint to use
    let plotUrl;
    if (currentSimulationId && currentSimulationId !== 'test-simulation-123') {
        plotUrl = `/plot/${currentSimulationId}/${plotType}`;
    } else {
        plotUrl = `/plot/current/${plotType}`;
    }
    
    // Fetch the plot
    fetch(plotUrl)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Display the plot
                plotContainer.innerHTML = `<img src="${data.image}" alt="${plotType} plot" class="img-fluid">`;
                plotContainer.style.display = 'block';
            } else {
                // Show error message
                plotContainer.innerHTML = `
                    <div class="text-center text-danger">
                        <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                        <p>Error loading plot: ${data.error}</p>
                        <small class="text-muted">Make sure your simulation has completed successfully.</small>
                    </div>
                `;
                plotContainer.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error loading plot:', error);
            plotContainer.innerHTML = `
                <div class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                    <p>Failed to load plot. Please try again.</p>
                </div>
            `;
            plotContainer.style.display = 'block';
        })
        .finally(() => {
            plotLoading.style.display = 'none';
        });
}


