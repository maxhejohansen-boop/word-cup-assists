---
name: world-cup-assist-value-trading
description: "World Cup Assist Value trading signal: buy players when Simmer assist price is 8% below form-based value."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
categories: [mlops]
tags: [trading, assist, world cup, simmer, signal]
---

# World Cup Assist Value Trading Skill

This skill implements a signal-based trading strategy for World Cup assist markets on Simmer. It searches for recent club form stats (chances created, key passes, assists) for five target players, computes a form-based assist value, compares it to the current Simmer market price, and triggers a dry-run buy when the market price is at least 8% below the form-based value.

## Players Monitored
- Bruno Fernandes (Manchester United)
- Michael Olise (Crystal Palace / Bayern Munich)
- Rayan Cherki (Lyon)
- Lamine Yamal (Barcelona)
- Luis Diaz (Liverpool)

## Signal Logic
1. **Form Stats Retrieval**: For each player, search the web for recent club form over the last 5 matches, focusing on:
   - Chances created
   - Key passes
   - Assists
2. **Form-Based Value Calculation**: Assign weights to each stat (e.g., assists weight 0.5, key passes 0.3, chances created 0.2) and compute a normalized score. Convert this score to an expected assist market price using a scaling factor derived from historical data (skill author should adjust based on backtesting).
3. **Market Price Fetch**: Search Simmer (or general web) for the current assist market price for each player on Simmer.
4. **Comparison**: If Simmer price ≤ (form-based value × 0.92) (i.e., at least 8% below), generate a buy signal.
5. **Trade Execution**: In dry-run mode, log the intended trade (player, amount, expected value, market price). In live mode, would place a 1% bankroll trade via Simmer API.
6. **Hold to Match Resolution**: Maintain the position until the relevant World Cup match concludes (skill should note to check match schedule and exit after match end).

## Dry-Run Mode
The skill starts in dry-run mode, meaning no actual trades are placed. Instead, it outputs detailed logs of signals that would have been triggered.

### Baseline Data Requirement
Before running or reporting a dry-run, check `baselines.json` for structured player baselines. Do not silently rely on placeholder/capped dummy values from web snippets. If recent last-5-match data cannot be fetched reliably, run the signal against the season baselines and clearly label it as baseline-driven. `baselines.json` should include raw totals, appearances, derived per-game values, and source URLs so the numbers are auditable.

## Implementation Steps (for the agent when invoking this skill)

### 1. Search for Recent Form Stats
For each player, execute a web search query like:
```
"Bruno Fernandes" last 5 matches chances created key passes assists
```
Extract numerical values from the results (may require visiting specific sports stats sites like FBref, Premier League, Ligue 1, La Liga, Bundesliga, etc.).

### 2. Compute Form-Based Value
Example calculation (adjust weights as needed):
```
form_score = (assists * 0.5) + (key_passes * 0.3) + (chances_created * 0.2)
expected_price = form_score * scaling_factor
```
Where `scaling_factor` maps form score to market price (e.g., if average form score of 2.0 corresponds to average assist price of $10, scaling_factor = 5).

### 3. Fetch Simmer Assist Price
Search for:
```
Simmer assist price Bruno Fernandes
```
or visit Simmer market page and extract the current price.

### 4. Generate Signal
If `simmer_price <= expected_price * 0.92`, output:
```
[SIGNAL] BUY Bruno Fernandes: Expected ${expected_price:.2f}, Simmer ${simmer_price:.2f} (discount {discount_pct:.1f}%)
```

### 5. Trade Sizing
Use 1% of allocated bankroll per trade. In dry-run, compute and log the stake amount.

### 6. Hold Until Match Resolution
After entering a trade, monitor the World Cup fixture list for the player's national team. Exit the trade after the match concludes (or when the market settles).

## Notes
- The skill assumes the agent has access to web search and can parse HTML/text for numeric stats.
- For production use, replace dry-run logs with actual Simmer API calls for price fetching and order placement.
- Consider adding error handling for missing data or price fetch failures.
- Backtest the weighting and scaling factor on historical data before live deployment.

## Example Invocation
When the agent loads this skill, it should run the signal generation process once (or be scheduled via cron to run periodically, e.g., every 6 hours).

```
# To run manually (if skill exposes an entrypoint):
# The skill itself does not define a CLI; it is intended to be invoked via the agent's reasoning loop.
# Example: delegate_task with goal "Run world-cup-assist-value-trading skill".
```

## Linked Files
- `references/player_baselines.md` - Baseline stats for all monitored players
- `references/2024_25_baseline_refresh.md` - Auditable 2024/25 baseline refresh notes, source strategy, and pitfalls
- `references/2025_26_baseline_refresh.md` - Auditable 2025/26 baseline refresh notes, source strategy, current values, and pitfalls
- `references/world_cup_2026_fixtures.md` - World Cup 2026 match schedule
- `references/research_notes.md` - Methodology, limitations, and improvement notes
- `scripts/signal.py` - Executable signal generation script (dry-run mode)
