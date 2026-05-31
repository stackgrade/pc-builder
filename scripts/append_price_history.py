#!/usr/bin/env python3
"""Append today's price snapshot to data/price_history.json

Run after scraping to track price history over time.
Creates price_history.json if it doesn't exist.
"""
import json, os
from datetime import datetime

PRICES_FILE = 'data/prices.json'
HISTORY_FILE = 'data/price_history.json'

def main():
    # Check if prices.json exists and has data
    if not os.path.exists(PRICES_FILE):
        print(f"⚠️  {PRICES_FILE} not found — nothing to append")
        return

    with open(PRICES_FILE) as f:
        prices = json.load(f)

    components = prices.get('components', {})
    if not components:
        print(f"⚠️  No components found in {PRICES_FILE}")
        return

    today = datetime.now().strftime('%Y-%m-%d')

    # Build entries from all current components
    entries = []
    for cat, items in components.items():
        for item in items:
            entries.append({
                'name': item['name'],
                'category': cat,
                'price': item['price']
            })

    # Load or create history
    history = {'snapshots': []}
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                history = json.load(f)
        except (json.JSONDecodeError, KeyError):
            pass

    # Check if today already has a snapshot
    existing_dates = {s['date'] for s in history.get('snapshots', [])}
    if today in existing_dates:
        print(f"⚠️  Snapshot for {today} already exists — updating in-place")
        for i, s in enumerate(history['snapshots']):
            if s['date'] == today:
                history['snapshots'][i]['entries'] = entries
                break
    else:
        history['snapshots'].append({
            'date': today,
            'entries': entries
        })

    history['updated'] = datetime.now().isoformat()

    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    print(f"✅ Appended {len(entries)} price entries for {today}")
    print(f"   Total snapshots: {len(history['snapshots'])}")

if __name__ == '__main__':
    main()
