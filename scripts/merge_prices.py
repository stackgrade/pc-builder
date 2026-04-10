#!/usr/bin/env python3
"""
Merge scraped real prices with mock metadata structure.
Keeps all metadata (socket, performance, etc.) from mock,
updates only prices from scraped data.
"""

import json
from datetime import datetime, timezone

# Load scraped data
with open('/home/larry/pc-builder/data/prices_scraped.json', 'r') as f:
    scraped = json.load(f)

# Load existing full data (with metadata)
with open('/home/larry/pc-builder/data/prices.json', 'r') as f:
    existing = json.load(f)

def normalize_name(name):
    """Normalize product name for matching"""
    return name.lower().replace('®', '').replace('™', '').replace('-', ' ').replace("'", '')

def find_best_match(scraped_name, mock_products):
    """Find best matching product in mock by normalized name"""
    scraped_norm = normalize_name(scraped_name)
    
    best_match = None
    best_score = 0
    
    for mock in mock_products:
        mock_norm = normalize_name(mock['name'])
        
        # Check key terms
        scraped_words = set(scraped_norm.split())
        mock_words = set(mock_norm.split())
        
        # Remove common words
        common = {'cpu', 'processor', 'graphics', 'card', 'nvidia', 'geforce', 'amd', 'radeon', 'ssd', 'nvme', 'moderkort'}
        scraped_words -= common
        mock_words -= common
        
        # Count matching significant words
        overlap = len(scraped_words & mock_words)
        score = overlap / max(len(scraped_words), len(mock_words), 1)
        
        # Boost score for partial matches at start of string
        if mock_norm.startswith(scraped_norm[:20]):
            score += 0.3
        
        if score > best_score and score > 0.3:
            best_score = score
            best_match = mock
    
    return best_match, best_score

def merge_category(category, scraped_products, mock_products):
    """Merge scraped prices into mock products"""
    merged = []
    
    for mock in mock_products:
        # Try to find matching scraped product
        match, score = find_best_match(mock['name'], scraped_products)
        
        if match:
            # Update price from scraped
            new_entry = mock.copy()
            new_entry['price'] = match['price']
            new_entry['id'] = match['id']
            new_entry['url'] = match['url']
            new_entry['retailer'] = 'Komplett'
            merged.append(new_entry)
        else:
            # Keep mock data as-is
            merged.append(mock)
    
    return merged

# Merge each category
categories = ['cpus', 'gpus', 'motherboards', 'ram', 'storage', 'cases', 'psus']

for cat in categories:
    if cat in scraped['components'] and cat in existing['components']:
        scraped_products = scraped['components'][cat]
        mock_products = existing['components'][cat]
        
        existing['components'][cat] = merge_category(cat, scraped_products, mock_products)

# Update metadata
existing['updated'] = datetime.now(timezone.utc).isoformat()
existing['source'] = 'komplett.se (merged with metadata)'

# Save
with open('/home/larry/pc-builder/data/prices.json', 'w', encoding='utf-8') as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)

print("✅ Merged scraped prices with mock metadata")
print(f"   Updated: {existing['updated']}")

# Show summary
for cat in categories:
    products = existing['components'].get(cat, [])
    if products:
        print(f"   {cat}: {len(products)} products")