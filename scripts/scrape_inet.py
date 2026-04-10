#!/usr/bin/env python3
"""
PC Builder SE — Scrape real prices from Inet.se
Runs via GitHub Actions on schedule.
Output: data/prices.json

Categories:
- CPU: /kategori/52/processor-cpu
- GPU: /kategori/164/grafikkort-gpu  
- RAM: /kategori/42/internminne-ram
- SSD: /kategori/591/harddisk-ssd
- Motherboard: /kategori/45/moderkort
- Case: /kategori/48/datorlada-chassi
- PSU: /kategori/595/nataggregat-psu
"""

import json, re, time, urllib.request, urllib.error
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "sv-SE,sv;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

CATEGORIES = {
    "cpus": {"url": "https://www.inet.se/kategori/52/processor-cpu", "id": "cpu"},
    "gpus": {"url": "https://www.inet.se/kategori/164/grafikkort-gpu", "id": "gpu"},
    "ram": {"url": "https://www.inet.se/kategori/42/internminne-ram", "id": "ram"},
    "storage": {"url": "https://www.inet.se/kategori/591/harddisk-ssd", "id": "storage"},
    "motherboards": {"url": "https://www.inet.se/kategori/45/moderkort", "id": "motherboard"},
    "cases": {"url": "https://www.inet.se/kategori/48/datorlada-chassi", "id": "case"},
    "psus": {"url": "https://www.inet.se/kategori/595/nataggregat-psu", "id": "psu"},
}

def fetch(url, retries=2):
    """Fetch URL with retries"""
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read()
                # Handle gzip
                if resp.info().get("Content-Encoding") == "gzip":
                    import gzip
                    content = gzip.decompress(content)
                return content.decode("utf-8", errors="ignore")
        except Exception as e:
            if attempt < retries:
                time.sleep(2 ** attempt)
            else:
                print(f"  FAILED: {url} — {e}")
                return ""

def parse_price(text):
    """Extract price number from text like '4 990 kr'"""
    text = text.replace("\xa0", " ").replace("\u202f", " ").replace("\u2009", " ")
    m = re.search(r"([\d\s]+)\s*kr", text)
    if m:
        return int(re.sub(r"\s+", "", m.group(1)))
    m = re.search(r"([\d]+)", text.replace(" ", ""))
    if m:
        return int(m.group(1))
    return 0

def parse_product_card(html, category):
    """Extract product data from an Inet product card HTML"""
    # Try to find product name
    name_match = re.search(r'class="[^"]*product[^"]*name[^"]*">([^<]+)<', html)
    if not name_match:
        name_match = re.search(r'"name":\s*"([^"]+)"', html)
    if not name_match:
        name_match = re.search(r'<h[23][^>]*>([^<]+)<', html)
    
    # Try to find price
    price_match = re.search(r'class="[^"]*price[^"]*">([^<]+)<', html)
    if not price_match:
        price_match = re.search(r'"price":\s*(\d+)', html)
    if not price_match:
        price_match = re.search(r'(\d[\d\s]+)\s*kr', html)
    
    # Try to find product URL
    url_match = re.search(r'href="(/produkt/\d+[^"]+)"', html)
    
    name = name_match.group(1).strip() if name_match else ""
    price = parse_price(price_match.group(1)) if price_match else 0
    product_url = "https://www.inet.se" + url_match.group(1) if url_match else ""
    
    if not name or not price:
        return None
    
    return {
        "name": name,
        "price": price,
        "retailer": "Inet",
        "url": product_url,
        "category": category,
    }

def scrape_category(key, cat_info, max_pages=3):
    """Scrape a category page for products"""
    base_url = cat_info["url"]
    cat_id = cat_info["id"]
    products = []
    
    print(f"Scraping {key}: {base_url}")
    
    for page in range(1, max_pages + 1):
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}?page={page}"
        
        html = fetch(url)
        if not html:
            break
        
        # Find product items — Inet uses various HTML patterns
        # Try to find product links first
        product_urls = re.findall(r'href="(/produkt/\d+[^"]*)"', html)
        product_urls = list(dict.fromkeys(product_urls))  # dedupe, preserve order
        
        if not product_urls:
            # Try JSON data embedded in page
            json_matches = re.findall(r'"products":\s*\[([^\]]+(?:\[[^\]]+\][^\]]*)*)\]', html)
            if json_matches:
                print(f"  Page {page}: Found JSON products (not parsing inline)")
            else:
                if page > 1:
                    break
        
        # Fetch each product page for price (Inet has client-side rendering)
        # Instead, try to extract prices from listing page
        # Look for price patterns near product names
        price_patterns = re.findall(
            r'(?:price|Price|pris| Pris)["\s:]*([^"<\n,]+?)(?:\s*kr|\s*SEK|\s*\:)',
            html, re.IGNORECASE
        )
        
        # Try to find all product blocks with their prices
        # Pattern: product name followed by price within reasonable distance
        blocks = re.split(r'<article|<div[^>]*class="[^"]*product', html)
        
        for block in blocks[1:50]:  # limit blocks processed
            product = parse_product_card(block, cat_id)
            if product and product["price"] > 0:
                products.append(product)
        
        # Limit products per category
        if len(products) >= 50:
            break
        
        if len(product_urls) == 0:
            break
        
        time.sleep(0.5)  # polite delay
    
    print(f"  Found {len(products)} products")
    return products[:50]  # cap at 50 per category

def main():
    print(f"=== PC Builder SE Scraper === {datetime.now().isoformat()}")
    
    all_components = []
    
    for key, cat_info in CATEGORIES.items():
        products = scrape_category(key, cat_info, max_pages=2)
        all_components.extend(products)
        time.sleep(1)  # delay between categories
    
    result = {
        "updated": datetime.now().isoformat(),
        "components": all_components,
    }
    
    # Save to data/prices.json
    output_path = "data/prices.json"
    with open(output_path, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal products: {len(all_components)}")
    print(f"Saved to {output_path}")
    
    # Summary
    cats = {}
    for p in all_components:
        cats[p["category"]] = cats.get(p["category"], 0) + 1
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")

if __name__ == "__main__":
    main()
