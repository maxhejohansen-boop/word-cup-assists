import os
import requests
import re

SIMMER_API_KEY = os.environ.get('SIMMER_API_KEY')
TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')
BACKEND_URL = 'https://api.simmer.markets'
SIMMER_HEADERS = {'Authorization': 'Bearer ' + str(SIMMER_API_KEY)}
DRY_RUN = True
BANKROLL = 1000
THRESHOLD = 0.08

PLAYERS = [
    {'name': 'Bruno Fernandes', 'team': 'Portugal', 'market_id': '199324fc-27a0-4f89-ac1e-d38d41a76293'},
    {'name': 'Michael Olise', 'team': 'France', 'market_id': '7bfd3117-bc46-4d24-b41e-1086ed631b8f'},
    {'name': 'Lamine Yamal', 'team': 'Spain', 'market_id': '6d2174d0-1ca0-41f0-9a38-b6ed254f9917'},
    {'name': 'Luis Diaz', 'team': 'Colombia', 'market_id': '7ae6f9d3-803f-4a69-b8ea-d5230183729e'},
]

def tavily_search(query, domains=None):
    body = {'api_key': TAVILY_API_KEY, 'query': query, 'max_results': 5}
    if domains:
        body['include_domains'] = domains
    r = requests.post('https://api.tavily.com/search', json=body)
    results = r.json().get('results', [])
    return ' '.join([x.get('content', '') + ' ' + x.get('title', '') for x in results])

def find_number(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None

def get_expected_price(player):
    name = player['name']
    team = player['team']

    print('  Searching FBref for club stats...')
    club = tavily_search(name + ' 2024-2025 stats assists key passes fbref', ['fbref.com'])

    print('  Searching for World Cup assists...')
    wc = tavily_search(name + ' World Cup 2026 assists goal contributions', ['fbref.com', 'bbc.co.uk', 'espn.com', 'skysports.com'])

    print('  Searching for team attacking style...')
    style = tavily_search(team + ' World Cup 2026 attacking chances created goals', ['fbref.com', 'espn.com'])

    combined = club + ' ' + wc + ' ' + style

    assists = find_number(combined, [
        r'(\d+\.?\d*)\s*assists',
        r'Ast[:\s]+(\d+\.?\d*)',
        r'assists[:\s]+(\d+\.?\d*)',
    ])
    key_passes = find_number(combined, [
        r'(\d+\.?\d*)\s*key passes',
        r'KP[:\s]+(\d+\.?\d*)',
        r'key passes[:\s]+(\d+\.?\d*)',
    ])
    print('  Assists: ' + str(assists) + ' | Key passes: ' + str(key_passes))

    score = 0.10
    if assists:
        score += min((float(assists) / 50) * 0.12, 0.12)
    if key_passes:
        score += min(float(key_passes) * 0.004, 0.06)
    if 'assist' in wc.lower():
        score += 0.02
    if any(w in style.lower() for w in ['possession', 'attack', 'creative', 'chance', 'goal']):
        score += 0.02

    return min(score, 0.45)

def get_market_price(market_id):
    r = requests.get(BACKEND_URL + '/api/sdk/markets/' + market_id, headers=SIMMER_HEADERS)
    return r.json()['market']['current_price']

print('=== World Cup Assist Value Trading Signal ===')
print('--- DRY-RUN MODE ---')
print()

for player in PLAYERS:
    print('Processing: ' + player['name'] + ' (' + player['team'] + ')')
    expected = get_expected_price(player)
    price = get_market_price(player['market_id'])
    discount = (expected - price) / expected if expected > 0 else 0
    print('  Market: ' + str(round(price,3)) + ' | Expected: ' + str(round(expected,3)) + ' | Discount: ' + str(round(discount*100,1)) + '%')
    if discount >= THRESHOLD:
        print('  BUY SIGNAL! Stake: $' + str(BANKROLL * 0.01) + ' (DRY RUN)')
    else:
        print('  No signal.')
    print()
