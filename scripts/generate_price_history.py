#!/usr/bin/env python3
"""Generate synthetic price history data from current prices.json"""
import json, os, random
from datetime import datetime, timedelta

random.seed(42)

# Load current prices
with open('data/prices.json') as f:
    current = json.load(f)

# Pick top components per category (by name)
top_components = {}
for cat, items in current['components'].items():
    if not items:
        continue
    # Pick the top 3-5 most notable items per category
    sorted_items = sorted(items, key=lambda x: x.get('price', 0), reverse=True)
    # Take a diverse mix
    selected = sorted_items[:3] + sorted_items[-2:]  # Top 3 + cheapest 2
    # Deduplicate by name
    seen = set()
    unique = []
    for c in selected:
        if c['name'] not in seen:
            seen.add(c['name'])
            unique.append(c)
    top_components[cat] = unique[:5]

# Generate weekly snapshots going back 12 weeks
snapshots = []
today = datetime.now()
for week in range(12, -1, -1):
    date = today - timedelta(weeks=week)
    date_str = date.strftime('%Y-%m-%d')
    
    # Base price on current + random variation that increases going back in time
    # More recent weeks are closer to current price
    variation_factor = (12 - week) / 12  # 0 = 12 weeks ago (most variation), 1 = now (least)
    
    entries = []
    for cat, comps in top_components.items():
        for comp in comps:
            base_price = comp['price']
            # Add some noise - more variation going back in time
            max_var = base_price * (0.15 * (1 - variation_factor * 0.7))
            hist_price = base_price + random.uniform(-max_var, max_var)
            # Ensure positive price
            hist_price = max(int(round(hist_price)), int(base_price * 0.7))
            entries.append({
                'name': comp['name'],
                'category': cat,
                'price': hist_price
            })
    
    snapshots.append({
        'date': date_str,
        'entries': entries
    })

output = {
    'updated': today.isoformat(),
    'generated_from': 'prices.json snapshot',
    'snapshots': snapshots
}

os.makedirs('data', exist_ok=True)
with open('data/price_history.json', 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"✅ Generated {len(snapshots)} weekly snapshots ({len(top_components)} categories, {sum(len(v) for v in top_components.values())} components)")
print(f"   Saved to data/price_history.json")
