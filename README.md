# 📊 MacroStress Analyzer

**MacroStress Analyzer** is an interactive Streamlit dashboard that helps you explore how financial markets and sectors respond to historical macroeconomic shocks. Visualize the impact of events like rate hikes, inflation spikes, and pandemics on sector ETFs, simulate custom portfolios, and analyze sector resilience — all in one place.

---

## 🚀 Features

- **Macro Shock Scenarios:**
  - Rate Hike Cycle (2015–2018)
  - COVID Crash (Feb–Mar 2020)
  - Inflation Spike (2021–2022)
  - Bank Failures (Mar 2023)

- **Market Data Visualization:**
  - S&P 500 ETF (SPY)
  - Fed Funds Rate
  - CPI Inflation (YoY %)
  - Yield Curve Spread (10Y – 3M) with recession warning

- **Portfolio Simulation:**
  - Allocate across SPY, XLK, XLF, XLE, XLV
  - Visualize portfolio growth over time
  - Analyze return, volatility, drawdown

- **Sector Heatmap:**
  - View sector returns across shocks
  - Color-coded performance
  - Average performance row

- **Insights & Fun Facts:**
  - Tips, trivia, and context for each macro event

---

## 🛠️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/kritikapandey05/macrostress-analyser.git
cd macrostress-analyser
```
### 2. (Optional) Create a virtual environment
```bash
python -m venv venv
```
On Windows:
```bash
venv\Scripts\activate
```
On Mac/Linux:
```bash
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Add your FRED API key

- Sign up at https://fred.stlouisfed.org/ for a free API key.
- Copy your 32-character key.
- Paste it in `app.py`:

FRED_API_KEY = "your-32-char-fred-api-key"

### 5. Run the app
```bash
streamlit run app.py
```
---

## 📁 Folder Structure
```
macrostress-analyzer/
│
├── app.py # Main dashboard
├── utils/
│ └── data_fetch.py # Functions to load FRED/YFinance data
├── requirements.txt
└── README.md
```
---

## 👥 Target Audience

- Students applying to finance, quant, or trading roles (e.g., Morgan Stanley, JPMorgan, Goldman Sachs)
- Aspiring macro analysts or researchers
- Curious learners exploring macro + markets

---

## 📈 Data Sources

- **FRED API:** Fed Funds Rate, CPI, Yield Curves
- **Yahoo Finance (via yfinance):** ETF price data

---

## 🧮 How the Calculations Work

### 1. ETF Price Normalization

We use daily adjusted close prices for each ETF (e.g., SPY, XLK, etc.) fetched from Yahoo Finance via yfinance.

To normalize ETF prices over a macro period:
```
normalized_price = (price_series / price_series.iloc) * 100
```
This sets the starting value to 100 so you can easily compare relative growth or decline.

---

### 2. Portfolio Value Calculation

Users input percentage weights for selected ETFs. The weighted portfolio is calculated as follows:
```
alloc = np.array([weights[etf] / 100 for etf in selected])
df_norm["Portfolio"] = df_norm[selected].dot(alloc)
```
Here, `df_norm` contains normalized prices for selected ETFs and `.dot()` performs a matrix multiplication of ETF prices with the weights.

---

### 3. Return, Volatility, and Max Drawdown

- **Total Return (%):**
```
total_return = normalized_portfolio.iloc[-1] - 100
```
- **Volatility (Annualized):**
```
volatility = daily_returns.std() * (252 ** 0.5)
```
- **Max Drawdown (%):**
```
drawdown = (portfolio / portfolio.cummax() - 1).min() * 100
```
---

### 4. CPI Inflation YoY %

We use CPI Index from FRED and calculate year-over-year percentage change:
```
cpi_yoy = (cpi.pct_change(12) * 100).dropna()
```
---

### 5. Yield Curve Spread

We fetch GS10 (10Y Treasury) and DTB3 (3M Treasury) from FRED and compute the spread:
```
yield_spread = gs10 - dtb3
```
If the spread goes below 0, it’s called a yield curve inversion, which historically precedes U.S. recessions. The app shows a warning when this happens.

---

### 6. Sector Heatmap Across Shocks

We calculate percent return per ETF per macro scenario:
```
sector_return = (end_price / start_price - 1) * 100
```
Applied to each ETF (e.g., XLK, XLF, etc.), mapped to sectors and plotted with a heatmap. Includes an "Average" row across scenarios.

---

## 🗂️ ETF Key

| ETF  | Sector                |
|------|-----------------------|
| SPY  | S&P 500 (broad market)|
| XLK  | Technology            |
| XLF  | Financials            |
| XLE  | Energy                |
| XLV  | Healthcare            |

---

## ✨ Extensions

- Include more sector ETFs (e.g., XLY, XLU)
- Generate reports or export PDF dashboards
- Use LLMs to generate narratives

---

## 👩‍💻 Author

Kritika P.  
Thank you !
---
