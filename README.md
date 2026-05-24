# TradingView Financial Scraper + Institutional Multi-Agent AI Investment System (v6.0)

A real-time financial data scraper and **institutional-grade multi-agent AI investment engine** built with **Playwright**, **BeautifulSoup**, and a state-of-the-art **11-Layer Intelligence Pipeline**.

This system doesn't just scrape data; it applies advanced quantitative finance models, market microstructure analysis, and a committee of AI agents to synthesize definitive, actionable investment decisions.

---

## 🚀 What's New in v6.0

- **Universal AI Backend:** Abstraction layer for **NVIDIA LLaMA 3.3-70B** (Primary), **OpenAI GPT-4o** (Fallback), and **Local Ollama** (Privacy/Offline).
- **Performance Backtester:** Real-time tracking of AI trade accuracy by comparing past "CIO Decisions" against current market prices.
- **Signal Confluence Validator:** A new layer that cross-references Technical signals (RSI/MACD) with Microstructure data (OFI/Microprice) to filter out "fake" moves.
- **Enhanced Memory:** Episodic and semantic memory now tracks entry prices and reflection outcomes for continuous self-improvement.

---

## 🏛 The 11-Layer Intelligence Pipeline

1.  **Market Data Layer:** Concurrent fetching of Stocks, Crypto, Forex, Commodities, and News.
2.  **Microstructure Engine:** Order Flow Imbalance (OFI), Microprice, and Queue Position modeling.
3.  **Feature Extraction:** Cross-asset correlations, momentum vectors, and volatility regimes.
4.  **Regime Detection:** Hidden Markov Model (HMM) + Bayesian switching for Bull/Bear/Panic states.
5.  **Stochastic Math:** Monte Carlo, GBM, and Black-Scholes for probability-weighted price targets.
6.  **Portfolio Optimization:** Markowitz Efficient Frontier, Risk Parity, and Kelly Criterion sizing.
7.  **Information Theory:** Entropy and KL Divergence for regime-shift detection and "Surprise" scores.
8.  **World Model:** Economic digital twin tracking Central Bank policy and Geopolitical risks.
9.  **Market Simulation:** Multi-agent Nash Equilibrium modeling (Retail vs. Institutional flows).
10. **Autonomous Research:** AI Scientist detects anomalies and validates hypotheses statistically.
11. **Multi-Agent AI (CIO):** A committee of Specialized Agents (Fundamental, Technical, Sentiment, News) debated by a CIO for final execution.

---

## 🛠 Project Structure

| File | Role |
| :--- | :--- |
| `scraper.py` | Main orchestrator and entry point. |
| `ai_client.py` | **[NEW]** Universal AI client with multi-provider fallback logic. |
| `backtest.py` | **[NEW]** Performance tracking module for historical AI recommendations. |
| `validation.py` | **[NEW]** Signal confluence validator (Micro + Tech alignment). |
| `ai_analyst.py` | Highest-level multi-agent pipeline using LLaMA 3.3-70B. |
| `microstructure.py`| HFT-style order flow and liquidity analysis. |
| `regime.py` | Bayesian and HMM-based market state detection. |
| `memory.py` | AI reasoning storage for continuous learning. |
| `world_model.py` | Macro-economic and geopolitical risk engine. |

---

## 📥 Installation & Setup

1. **Clone & Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

2. **Set Environment Variables:**
   ```bash
   # Optional: System will fallback to local Ollama if keys are missing
   export NVIDIA_API_KEY="your_nvapi_key"
   export OPENAI_API_KEY="your_openai_key"
   ```

3. **Run the System:**
   ```bash
   python scraper.py
   ```

---

## 📊 Outputs

- **Console:** Real-time interactive dashboard with color-coded tables and AI summaries.
- **`output.json`:** Comprehensive data dump of the entire 11-layer run.
- **`memory.json`:** Long-term storage for AI learning and backtesting.
- **CSV Exports:** Time-stamped files for external analysis.

---

## ⚠️ Disclaimer

This project is for **educational and research purposes only**. It is not financial advice. The models and AI outputs are probabilistic and should be verified. Trading involves risk. Review [TradingView's Terms of Service](https://www.tradingview.com/policies/) before commercial use.
