#!/usr/bin/env python3
"""
PC Builder SE - Price Scraper v2 for Komplett.se
Fixed: Better price extraction and product filtering
"""

from curl_cffi import requests
import re
import json
import time
from datetime import datetime, timezone

CATEGORIES = {
    'cpus': {
        'queries': ['amd+ryzen+9800x3d', 'amd+ryzen+9950x3d', 'amd+ryzen+9900x',
                   'amd+ryzen+9600x', 'amd+ryzen+7700x', 'intel+core+ultra+9+285k',
                   'intel+core+ultra+7+265k', 'amd+ryzen+5600x'],
        'must_contain': ['ryzen', 'core ultra', 'athlon', 'processor'],
        'must_not': ['laptop', 'bärbar', 'bagg', 'chassi', 'kylare', 'fläkt', 'verktyg', 'paste', 'stationär', 'dator'],
    },
    'gpus': {
        'queries': ['nvidia+geforce+rtx+5080', 'nvidia+geforce+rtx+5070+ti', 'nvidia+geforce+rtx+5070',
                   'amd+radeon+rx+9070+xt', 'amd+radeon+rx+9070', 'nvidia+geforce+rtx+4060'],
        'must_contain': ['rtx', 'geforce', 'radeon', 'rx', 'arc', 'grafikkort'],
        'must_not': ['laptop', 'bärbar', 'chassi', 'fläkt', 'kabel', 'adapter', 'bra'],
    },
    'motherboards': {
        'queries': ['amd+x670e', 'amd+b650', 'amd+b550', 'intel+z890', 'intel+b860'],
        'must_contain': ['moderkort', 'x670', 'b650', 'b550', 'z890', 'b860'],
        'must_not': ['laptop', 'bärbar', 'chassi', 'processor', 'ryzen'],
    },
    'ram': {
        'queries': ['ddr5+32gb+6000', 'ddr5+64gb', 'ddr4+32gb+3600', 'ddr5+32gb+6400'],
        'must_contain': ['ddr5', 'ddr4', '16gb', '32gb', '64gb', 'minne', 'memory'],
        'must_not': ['laptop', 'bärbar', 'sodimm', 'chassi', 'ssd'],
    },
    'storage': {
        'queries': ['samsung+990+pro+2tb', 'wd+sn850x+2tb', 'crucial+p3+plus+2tb', 'ssd+2tb+nvme'],
        'must_contain': ['nvme', 'ssd', '2tb', '1tb'],
        'must_not': ['extern', 'usb', 'hårddisk', 'hdd', 'chassi', 'kabel'],
    },
    'cases': {
        'queries': ['chassi+atx+svart', 'datorkabinett+atx', 'fractal+define+chassi', 
                   'lian+li+pc+chassi', 'coolermaster+chassi', 'chassi+rgb'],
        'must_contain': ['chassi', 'kabinett', 'case', 'define', 'o11', 'pop air'],
        'must_not': ['laptop', 'bärbar', 'fläkt endast', 'psu', 'moderkort', 'grafikkort'],
    },
    'psus': {
        'queries': ['corsair+rm1000x', 'corsair+rm850x', 'seasonic+focus+750', 'be+quiet+650w'],
        'must_contain': ['psu', 'aggregat', 'w ', 'rm', 'seasonic', 'corsair'],
        'must_not': ['laptop', 'bärbar', 'chassi', 'fläkt', 'kabel', 'moderkort'],
    },
}

def get_product_info(pid):
    """Fetch product name and price from product page"""
    try:
        r = requests.get(f'https://www.komplett.se/product/{pid}/', 
                        impersonate='chrome', timeout=15)
        html = r.text
        
        # Extract name from multiple sources
        name = None
        
        # Try JSON-LD
        ld_match = re.search(r'"name"\s*:\s*"([^"]+)"', html)
        if ld_match:
            n = ld_match.group(1)
            if len(n) > 5 and 'komplett' not in n.lower():
                name = n
        
        # Fallback: title tag
        if not name:
            title_match = re.search(r'<title>([^<]+)</title>', html)
            if title_match:
                name = title_match.group(1).split('|')[0].strip()
        
        # Extract prices
        # Look for the main product price - it's usually in a specific pattern
        # Komplett uses priceRange or direct price field
        
        all_prices = re.findall(r'"price"\s*:\s*(\d+)', html)
        prices = sorted(set(int(p) for p in all_prices if 500 < int(p) < 100000))
        
        # The main product price is usually the HIGHEST in the 500-50000 range
        # (other prices are accessories, shipping, etc.)
        if len(prices) >= 3:
            price = prices[-2]  # Second highest tends to be the main product
        elif prices:
            price = prices[-1]
        else:
            return None, None
        
        return name, price
        
    except Exception as e:
        return None, None

def scrape_category_standalone(query, max_results=8):
    """
    Scrape a SPECIFIC search query - no filtering, just exact matches
    Returns products that match the GPU/CPU type exactly
    """
    results = []
    
    try:
        r = requests.get(f'https://www.komplett.se/search?q={query}', 
                        impersonate='chrome', timeout=20)
        html = r.text
        
        # Get product IDs from search results
        product_ids = re.findall(r'/product/(\d+)/', html)
        
        seen = set()
        for pid in product_ids:
            if pid in seen:
                continue
            seen.add(pid)
            
            name, price = get_product_info(pid)
            
            if name and price and price > 1000:
                # Validate: product name should contain some terms from query
                query_terms = query.replace('+', ' ').lower().split()
                name_lower = name.lower()
                
                # Check if at least one significant term matches
                match = any(term in name_lower for term in query_terms if len(term) > 3)
                
                if match or price > 5000:  # High price = likely actual component
                    results.append({
                        'id': pid,
                        'name': name,
                        'price': price,
                        'retailer': 'Komplett',
                        'url': f'https://www.komplett.se/product/{pid}/'
                    })
            
            time.sleep(0.25)
            
            if len(results) >= max_results:
                break
                
    except Exception as e:
        print(f"    Error: {e}")
    
    return results

def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting Komplett scrape v2...")
    
    all_data = {
        'updated': datetime.now(timezone.utc).isoformat(),
        'source': 'komplett.se',
        'components': {}
    }
    
    for category, config in CATEGORIES.items():
        print(f"\n--- {category.upper()} ---")
        all_products = {}
        
        for query in config['queries']:
            print(f"  Query: {query.replace('+', ' ')}")
            results = scrape_category_standalone(query, max_results=6)
            print(f"    -> {len(results)} valid products")
            
            for p in results:
                # Dedupe by name
                key = p['name'][:40]
                if key not in all_products or p['price'] < all_products[key]['price']:
                    all_products[key] = p
        
        # Convert to list and sort by price
        product_list = sorted(all_products.values(), key=lambda x: x['price'])
        
        # Take top 8 per category
        all_data['components'][category] = product_list[:8]
        
        for p in product_list[:5]:
            print(f"    {p['price']:>6} kr | {p['name'][:55]}")
        
        time.sleep(1.5)
    
    # Save
    output_path = '/home/larry/pc-builder/data/prices.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    total = sum(len(v) for v in all_data['components'].values())
    print(f"\n✅ Saved {total} products to {output_path}")

if __name__ == '__main__':
    main()