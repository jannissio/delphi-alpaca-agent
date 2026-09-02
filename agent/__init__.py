"""Delphi: an evidence-based 0DTE options agent for Alpaca paper trading.

Division of labour (research/STATE_OF_THE_ART.md section 8.2):
  * the LLM emits categories only (regime, event flag, strategy family, veto, journal text);
  * deterministic code owns prices, Greeks, strikes, sizing, gates and orders;
  * LLM authority is monotone-decreasing in risk: it can block or shrink, never enlarge.
"""

__version__ = "0.1.0"
