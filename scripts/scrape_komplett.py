#!/usr/bin/env python3
"""
PC Builder SE - Price Scraper for Komplett.se
Uses curl_cffi to scrape real prices for PC components.
"""

from curl_cffi import requests
import re
import json
import time
from datetime import datetime, timezone

CATEGORIES = {
    'cpus': {
        'search_queries': ['amd ryzen 9800x3d', 'amd ryzen 9950x3d', 'amd ryzen 9600x', 
                          'amd ryzen 7700x', 'intel core ultra 9 285k', 'intel core ultra 7 265k',
                          'amd ryzen 5600x'],
        'name_filter': ['ryzen', 'core ultra', 'athlon'],
        'name_exclude': ['laptop', 'bärbar', 'stationär', 'integrerad', 'bundled'],
    },
    'gpus': {
        'search_queries': ['nvidia rtx 5080', 'nvidia rtx 5070 ti', 'nvidia rtx 5070',
                          'amd rx 9070 xt', 'amd rx 9070', 'nvidia rtx 4060'],
        'name_filter': ['rtx', 'geforce', 'radeon', 'rx ', 'arc'],
        'name_exclude': ['laptop', 'bärbar', 'extern', 'egpu'],
    },
    'motherboards': {
        'search_queries': ['amd x670e', 'amd b650', 'amd b550', 'intel z890', 'intel b860'],
        'name_filter': ['x670', 'b650', 'b550', 'z890', 'b860', 'moderkort'],
        'name_exclude': ['laptop', 'bärbar'],
    },
    'ram': {
        'search_queries': ['ddr5 32gb 6000', 'ddr5 64gb', 'ddr4 32gb 3600', 'ddr5 32gb 6400'],
        'name_filter': ['ddr5', 'ddr4', '16gb', '32gb', '64gb', 'minne'],
        'name_exclude': ['laptop', 'bärbar', 'so-dimm'],
    },
    'storage': {
        'search_queries': ['samsung 990 pro 2tb', 'wd sn850x', 'crucial p3 plus 2tb'],
        'name_filter': ['nvme', 'ssd', '2tb', '1tb'],
        'name_exclude': ['extern', 'usb', 'hårddisk'],
    },
    'cases': {
        'search_queries': ['fractal define 7', 'lian li o11', 'fractal pop air', 'coolermaster q300l'],
        'name_filter': ['chassi', 'case', 'kabinett'],
        'name_exclude': ['laptop', 'bärbar'],
    },
    'psus': {
        'search_queries': ['corsair rm1000x', 'corsair rm850x', 'seasonic focus 750', 'be quiet 650'],
        'name_filter': ['w', ' PSU', 'aggregat', 'rm', 'focus', 'seasonic'],
        'name_exclude': ['laptop', 'bärbar', 'extern'],
    },
}

def get_product_price(pid):
    """Fetch price for a product ID"""
    for attempt in range(2):
        try:
            r = requests.get(f'https://www.komplett.se/product/{pid}/', 
                            impersonate='chrome', timeout=15)
            # Extract all prices from JSON
            price_matches = re.findall(r'"price"\s*:\s*(\d+)', r.text)
            prices = sorted(set(int(p) for p in price_matches if 200 < int(p) < 100000))
            
            if prices:
                # Return median price (filter out extremes)
                return prices[len(prices)//2] if len(prices) > 2 else prices[-1]
            return None
        except Exception as e:
            if attempt == 0:
                time.sleep(1)
                continue
            return None
    return None

def get_product_name(pid):
    """Fetch product name from page"""
    for attempt in range(2):
        try:
            r = requests.get(f'https://www.komplett.se/product/{pid}/', 
                            impersonate='chrome', timeout=15)
            # Try JSON-LD first
            name_match = re.findall(r'"name"\s*:\s*"([^"]+)"', r.text)
            for n in name_match:
                if len(n) > 10 and 'komplett' not in n.lower() and 'related' not in n.lower():
                    return n
            return None
        except:
            if attempt == 0:
                time.sleep(0.5)
                continue
            return None

def search_komplett(query, max_results=15):
    """Search Komplett and return product IDs with prices"""
    results = []
    
    try:
        r = requests.get(f'https://www.komplett.se/search?q={query}', 
                        impersonate='chrome', timeout=20)
        html = r.text
        
        # Extract product IDs from search results
        product_ids = re.findall(r'/product/(\d+)/', html)
        
        seen = set()
        for pid in product_ids:
            if pid in seen:
                continue
            seen.add(pid)
            
            # Skip generic/non-product pages (check URL path)
            idx = html.find(f'/product/{pid}/')
            if idx > 0:
                url_end = html.find('"', idx)
                path = html[idx:url_end]
                # Skip if path contains certain keywords
                skip_words = ['category', 'search', 'campaign', 'brand', 'filter']
                if any(w in path.lower() for w in skip_words):
                    continue
            
            price = get_product_price(pid)
            name = get_product_name(pid)
            
            if price:
                results.append({
                    'id': pid,
                    'name': name or f'Product {pid}',
                    'price': price,
                    'retailer': 'Komplett',
                    'url': f'https://www.komplett.se/product/{pid}/'
                })
                
            time.sleep(0.3)  # Rate limiting
            
            if len(results) >= max_results:
                break
                
    except Exception as e:
        print(f"Search error for '{query}': {e}")
    
    return results

def scrape_all_categories():
    """Main scraping function"""
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting Komplett price scrape...")
    
    all_data = {
        'updated': datetime.now(timezone.utc).isoformat(),
        'source': 'komplett.se',
        'components': {}
    }
    
    for category, config in CATEGORIES.items():
        print(f"\n--- Scraping {category.upper()} ---")
        all_products = []
        seen_ids = set()
        
        for query in config['search_queries']:
            print(f"  Searching: {query}...", end=' ')
            results = search_komplett(query, max_results=10)
            print(f"found {len(results)} products")
            
            for product in results:
                # Apply category-specific filters
                name_lower = product['name'].lower()
                
                # Filter by category keywords
                if not any(f in name_lower for f in config['name_filter']):
                    continue
                # Exclude unwanted products
                if any(ex in name_lower for ex in config['name_exclude']):
                    continue
                    
                if product['id'] not in seen_ids:
                    seen_ids.add(product['id'])
                    all_products.append(product)
                    
            time.sleep(1)
        
        # Deduplicate by ID
        unique_products = []
        seen_prices = {}
        for p in all_products:
            key = p['name'][:30]  # Dedupe by similar names
            if key not in seen_prices or p['price'] < seen_prices[key]:
                seen_prices[key] = p['price']
                unique_products.append(p)
        
        # Take top 10 cheapest per category (realistic selection)
        unique_products.sort(key=lambda x: x['price'])
        all_data['components'][category] = unique_products[:10]
        
        for p in unique_products[:5]:
            print(f"    {p['name'][:50]}... = {p['price']} kr")
        
        time.sleep(2)  # Be nice between categories
    
    return all_data

if __name__ == '__main__':
    data = scrape_all_categories()
    
    output_path = '/home/larry/pc-builder/data/prices.json'
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved to {output_path}")
    print(f"   Total products: {sum(len(v) for v in data['components'].values())}")