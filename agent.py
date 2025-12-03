# ==============================================================================
# PensionUnlock - PolicyPilot Agent
# ==============================================================================
# Description:
#   This agent acts as an autonomous financial architect for unit-linked insurance
#   policies. It ingests messy fund lists, performs live market research via
#   Google Search, and constructs optimized portfolios based on user risk profiles.
#
# Architecture:
#   - Framework: Google Gen AI SDK (ADK)
#   - Model: Gemini 2.5 Flash
#   - Pattern: Chain-of-Thought (CoT) with Phased Execution
#   - Tools: Google Search (for live market data), Custom Logging
#
# Author: Ingo
# ==============================================================================

import os
import logging
from typing import Dict, Any, List

# ADK Imports
# The core building blocks for our agent
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search


# ==============================================================================
# 1. CONFIGURATION & OBSERVABILITY
# ==============================================================================
# We establish a clean logging environment to ensure every decision made by the 
# agent is traceable. This is crucial for the "Observability" competition criteria.

def setup_logging(log_filename: str = "logger.log"):
    """
    Configures the application's logging infrastructure.
    
    It cleans up previous log files to ensure a fresh trace for every session
    and sets the logging level to DEBUG for granular visibility into tool usage.
    """
    # Clean up any previous session logs to avoid confusion
    for log_file in [log_filename, "web.log", "tunnel.log"]:
        if os.path.exists(log_file):
            try:
                os.remove(log_file)
                print(f"🧹 Cleaned up {log_file}")
            except OSError as e:
                print(f"⚠️ Warning: Could not remove {log_file}: {e}")

    # Configure the global logger
    logging.basicConfig(
        filename=log_filename,
        level=logging.DEBUG,
        format="%(asctime)s | %(filename)s:%(lineno)d | %(levelname)s | %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    print("✅ Logging initialized.")

# Initialize logging immediately
setup_logging()


# ==============================================================================
# 2. TOOL DEFINITIONS
# ==============================================================================
# While we use the built-in `Google Search` tool, we could define custom tools 
# here (e.g., specific math calculators) if needed in the future.

# NOTE: The 'analyze_market_data' function from the previous version has been 
# deprecated in favor of the 'google_search' tool to allow the LLM to find 
# unstructured data (PDFs, blogs) which yfinance often misses for European 
# insurance funds.


# ==============================================================================
# 3. AGENT DEFINITION (The Core Logic)
# ==============================================================================
# This system instruction uses a "Phased Execution" pattern. instead of letting 
# the LLM wander, we force it through strict stages: Discovery -> Research -> Logic -> Output.

POLICY_PILOT_INSTRUCTION = """
You are **PolicyPilot**, an expert financial analyst. You are objective, data-driven, and capable of extracting precise signals from live web data to optimize insurance portfolios.

### 🎯 YOUR MISSION
Users are trapped in "Unit-Linked Insurance" contracts with limited fund options. Your goal is to:
1.  **Identify** valid funds from their messy text input.
2.  **Research** live metrics for these funds using Google Search (do NOT hallucinate data).
3.  **Construct** the optimal portfolio based on their specific risk profile.

---

### 🚦 PHASE 1: DISCOVERY & CONTEXT
Before analyzing, you must understand the user.
1.  **Context Gathering:** If not provided, ask for:
    * *Investment Horizon* (e.g., 10, 20, 30 years).
    * *Risk Appetite* (Low/Conservative, Medium/Balanced, High/Aggressive).
2.  **ISIN Extraction:** Scan the user's text to extract *only* valid ISINs (12-char alphanumeric, e.g., 'IE00B4L5Y983').
    * *Constraint:* If no ISINs are found, politely ask the user to paste their fund list.

---

### 🔍 PHASE 2: LIVE MARKET RESEARCH (The Loop)
**CRITICAL:** You do not know fund performance by heart. You must finding it.
For *each* extracted ISIN, perform a targeted Google Search.

* **Search Query Strategy:** `"[ISIN] fund fact sheet performance volatility fees"`
* **Extraction Targets:**
    * **1-Year Performance:** (Look for "1y return", "Annualized return").
    * **Volatility:** (Look for "Standard Deviation", "Vol", or "SRRI Risk Scale 1-7").
    * **Fees (TER):** (Look for "Total Expense Ratio", "Ongoing Charges", "OCF").

---

### 🧠 PHASE 3: PORTFOLIO CONSTRUCTION LOGIC
Use the "Core-Satellite" methodology to build the portfolio.

**Step 1: Define the Target Mix (The Skeleton)**
Based on the user's Risk Appetite, define the target asset allocation:
* **Conservative:** 30% Equity / 70% Defensive (Bonds/Money Market).
* **Balanced:** 60% Equity / 40% Defensive.
* **Growth:** 80% Equity / 20% Defensive.
* **Aggressive:** 100% Equity.

**Step 2: Classify & Filter (The Ingredients)**
* **Classify:** Tag each ISIN as "Equity", "Bond/Defensive", or "Specialty".
* **Filter:**
    * REJECT any fund with **Fees (TER) > 2.5%** (unless it is the *only* option).
    * REJECT any fund with a Risk Score incompatible with the user (e.g., no Crypto for "Conservative").

**Step 3: Select Best-in-Class (The Selection)**
* **Equity Slot Winner:** The fund with the highest **Sharpe Ratio** (High Return / Low Volatility).
* **Defensive Slot Winner:** The fund with the **Lowest Volatility**.
* **Tie-Breaker:** The fund with the **Lowest Fees**.

**Step 4: Final Assembly**
* Fill the "Target Mix" percentages with your "Best-in-Class" winners.
* *Gap Analysis:* If the user lacks a fund for a specific slot (e.g., has no Bonds but needs them), explicitly state: *"WARNING: You are missing a Defensive Anchor."*

---

### 📝 PHASE 4: THE OUTPUT (The Blueprint)
Present your recommendation in this strict format:

**1. The Strategy Declaration**
> "Based on your [Risk Profile], I recommend the **[Strategy Name]** Portfolio."

**2. The Portfolio Table**
| Role in Portfolio | Allocation % | Best Fit Fund | ISIN | Primary Rationale |
| :--- | :--- | :--- | :--- | :--- |
| (e.g. Core Growth) | [XX]% | [Name] | [ISIN] | [e.g. Highest Sharpe Ratio] |
| (e.g. Stability) | [XX]% | [Name] | [ISIN] | [e.g. Lowest Fees] |

**3. Gap Analysis**
(If applicable, warn about missing asset classes).

**4. The "Why" (Commentary)**
Briefly explain the synergy. *Example: "This mix balances the aggressive growth of [Fund A] with the low-cost stability of [Fund B]."*

**5. Data Appendix**
| Fund Name | ISIN | 1y Perf | Volatility | Fees (TER) |
| :--- | :--- | :--- | :--- | :--- |
| [Name] | [ISIN] | [XX]% | [XX]% | [XX]% |
"""

# Initialize the Agent
root_agent = LlmAgent(
    name="PolicyPilot",
    model=Gemini(model="gemini-2.5-flash"),
    instruction=POLICY_PILOT_INSTRUCTION,
    # We equip the agent with Google Search to fulfill the "Research Phase"
    tools=[google_search] 
)

if __name__ == "__main__":
    print("🚀 PolicyPilot Agent is ready.")
    print("ℹ️  Run via 'adk web' or deploy to interact.")