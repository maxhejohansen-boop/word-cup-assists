import os
import requests
import re

SIMMER_API_KEY = os.environ.get("SIMMER_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
BACKEND_URL = "https://api.simmer.markets"
SIMMER_HEADERS = {"Authorization": "Bearer " + str(SIMMER_API_KEY)}
DRY_RUN = True
BANKROLL = 1000
THRESHOLD = 0.08

def get_all_players():
    r = requests.get(BACKEND_URL + "/api/sdk/markets?q=assists&limit=50&offset=0", headers=SIMMER_HEADERS)
    data = r.json()
    players = [m for m in data["markets"] if m.get("event_name") == "World Cup: Most Assists"]
    return [{"name": p["outcome_name"], "market_id": p["id"], "price": p["current_price"]} for p in players]

def tavily_search(query):
    r = requests.post("https://api.tavily.com/search", json={"api_key": TAVILY_API_KEY, "query": query, "max_results": 3, "include_domains": ["fbref.com", "whoscored.com", "espn.com"]})
    results = r.json().get("results", [])
    return " ".join([x.get("content", "") + " " + x.get("title", "") for x in results])

def find_number(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None

def get_expected_price(name):
    club = tavily_search(name + " 2024-2025 season assists statistics fbref")
    wc = tavily_search(name + " World Cup 2026 assists goal contributions")
    combined = club + " " + wc
    assists = find_number(combined, [r"(\d+\.?\d*)\s*assists", r"Ast[:\s]+(\d+\.?\d*)"])
    score = 0.08
    if assists:
        score += min(float(assists) / 50 * 0.12, 0.12)
    if "assist" in wc.lower():
        score += 0.02
    return min(score, 0.45)

players = get_all_players()
print("Found " + str(len(players)) + " players")
signals = []
for player in players:
    name = player["name"]
    price = player["price"]
    expected = get_expected_price(name)
    discount = (expected - price) / expected if expected > 0 else 0
    if price >= 0.02 and discount >= THRESHOLD:
        signals.append({"name": name, "price": price, "expected": expected, "discount": discount})

signals.sort(key=lambda x: x["discount"], reverse=True)
print("BUY SIGNALS:")
for s in signals:
    print(s["name"] + " | Market: " + str(round(s["price"],3)) + " | Expected: " + str(round(s["expected"],3)) + " | Discount: " + str(round(s["discount"]*100,1)) + "%")
