# PensionUnlock
### The Intelligent Portfolio Architect for Unit-Linked Insurance
**Track:** Concierge Agents

![Project Type](https://img.shields.io/badge/Project-AI%20Agent-blue) ![Stack](https://img.shields.io/badge/Tech-Google%20Gemini%20%7C%20ADK%20%7C%20Python-green) ![Status](https://img.shields.io/badge/Status-Prototype_Complete-success)

> 🎓 **Capstone Project Submission:** This agent is an experimental prototype developed for the **Google Agents Intensive - Capstone Project**. It demonstrates advanced ADK patterns and is intended for educational purposes. Financial advice is **not** intended for real-world decisions; please consult a professional for real-world decisions.

## ⚡ Executive Summary
**PensionUnlock** is a specialized "Concierge Agent" designed to solve the "Walled Garden" problem in unit-linked insurance policies. 

Many policyholders are restricted to a confusing list of 30-50 specific funds hidden in PDF documents. **PensionUnlock** uses a highly instructed **Gemini 2.5 Flash** agent to act as a financial expert. It autonomously researches real-time market data via Google Search, analyzes risk metrics, and mathematically constructs an optimized portfolio based on the user's risk profile.

> **Value Proposition:** Transforms a complex 10-hour financial analysis task into a 2-minute autonomous operation, potentially saving users tens of thousands of euros in fees and lost compound interest.

---


### ✅ 1. Applied Course Concepts (3+ Features)
This project implements the following ADK and Agent concepts:
* **Agent Deployment:** The project is architected for production.
 It includes the `.agent_engine_config.json` and `requirements.txt` configuration to enable seamless deployment to Google Cloud Run via the Agent Engine, ensuring the agent is not just a local script but a scalable web service.
* **Agent Powered by LLM:** Leverages **Gemini 2.5 Flash** for its superior long-context reasoning and instruction following capabilities.
* **Built-in Tools (Google Search):** The agent is not limited to training data; it uses the `Google Search` tool to fetch *live* financial data (Volatility, 1Y Performance, Expense Ratios) from the web.
* **Observability & Logging:** Implements a custom logging solution (writing to `logger.log`) to trace agent decision-making and tool inputs/outputs for debugging and evaluation.
* **Context Engineering (Phased Reasoning):** Instead of a fragile chain of weak agents, this project uses a sophisticated "Phased System Instruction" that forces the single agent to act sequentially (Discovery $\rightarrow$ Extraction $\rightarrow$ Research $\rightarrow$ Logic).

---

## 🚩 Problem Statement (The "Why")
Millions of policyholders are locked into **Unit-Linked Insurance Plans** (e.g., German *Riester*, *Rürup*) with sub-optimal performance.

1.  **The "Walled Garden" Constraint:** Users cannot buy *any* asset; they are restricted to a closed, variable list of funds specific to their contract.
2.  **The Data Gap:** These lists are trapped in messy text, making manual analysis impossible for laypeople.
3.  **The Impact:** Users unknowingly remain in high-fee active funds (2.5%+ TER) when low-cost ETFs are available within their contract options.

---

## 🏗️ System Architecture (The "How")

**Single "Super-Agent" Architecture** to reduce latency and improve reasoning consistency.

### The "PolicyPilot" Agent
The agent (`PolicyPilot`) utilizes a **Chain-of-Thought (CoT)** architecture defined in its system instruction. It operates in four strict phases:

1.  **Phase 1: Discovery & Extraction**
    * Ingests user input (messy text or lists).
    * Identifies ISINs (International Securities Identification Numbers) using regex-like pattern matching.
2.  **Phase 2: Live Market Research (The Loop)**
    * Iterates through extracted ISINs.
    * **TOOL USE:** Triggers `Google Search` to find current Fact Sheets.
    * Extracts critical metrics: *Volatility (Risk)*, *1-Year Return*, and *Total Expense Ratio (TER)*.
3.  **Phase 3: Quantitative Logic**
    * Applies a "Core-Satellite" strategy rule set.
    * Filters out funds with fees > 2.5%.
    * Selects winners based on Sharpe Ratio (Risk-Adjusted Return).
4.  **Phase 4: Synthesis**
    * Generates a structured markdown table and a persuasive, empathetic recommendation for the user.

---

## 🛠️ Technical Implementation

### Tech Stack
* **LLM:** Google Gemini 2.5 Flash
* **Framework:** Google Gen AI SDK (ADK)
* **Tools:** Google Search Tool
* **Language:** Python 3.10+

### Key Technical Highlight: Hallucination Control
Financial advice requires accuracy. To prevent the LLM from "hallucinating" numbers:
1.  **Grounding:** The agent is forced to use the Search Tool to find data, rather than relying on internal training knowledge.
2.  **Strict Schema:** The system prompt requires specific metrics (Volatility, Fees) to be found before a recommendation is made.

---

## ☁️ Deployment Instructions
*This agent is configured for the Google Agent Engine runtime.*

1.  **Clone the Repo:**
    ```bash
    git clone [https://github.com/IngoScholzSolutions/pension-unlock.git](https://github.com/IngoScholzSolutions/pension-unlock.git)
    cd pension-unlock
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set API Keys:**
    ```bash
    # Create a .env file or export directly
    export GOOGLE_API_KEY="your_gemini_key"
    ```
4.  **Run the Agent (Local Web Interface in debugging mode):**
    ```bash
    adk web --log_level DEBUG
    ```
    *Select "PolicyPilot" from the interface.*

---

## 🔍 Observability
We have implemented file-based logging to trace the agent's "thought process."
* Check `logger.log` to see the raw ISIN extraction and the specific queries sent to Google Search.
* Check `web.log` for server-side interactions.

---

## 🚀 Future Roadmap
* **Stateful Fund Registry & Pre-Scoring:** Move beyond simple list processing to a granular tracking system. This will maintain a state object for *each* extracted fund to ensure 100% data completeness (fetching missing volatility/fee data individually) and apply a pre-calculated "Quality Score." The final Advisor Agent will then reason over this clean, pre-rated dataset rather than raw search results.
* **Long-Term Persistence (Memory Bank):** Implement a database (SQLite) to persistently store the "Fund Registry" objects. This enables **"Scenario Replay"**, allowing users to change their risk profile later (e.g., "What if I switch to Conservative?") and receive an instant re-calculation without re-triggering the expensive data extraction and search loop.
* **PDF OCR Tool:** Re-integrate a dedicated PDF parser for handling scanned documents.
* **Python Math Sandbox:** Give the agent a calculator tool to perform exact Mean-Variance Optimization rather than heuristic ranking.