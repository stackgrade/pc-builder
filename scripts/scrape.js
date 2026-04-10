/**
 * PC Component Price Scraper
 * Scrape Swedish retailers for component pricing
 * Run via: node scripts/scrape.js
 */

import { writeFileSync } from 'fs';
import { load } from 'cheerio';
import got from 'got';

// Swedish retailers to scrape
const RETAILERS = {
  komplett: {
    name: 'Komplett.se',
    baseUrl: 'https://www.komplett.se',
    categories: {
      cpus: '/data/tillbehor/datorkomponenter/processorer',
      gpus: '/data/tillbehor/datorkomponenter/grafikkort',
      motherboards: '/data/tillbehor/datorkomponenter/moderkort',
      ram: '/data/tillbehor/datorkomponenter/internminne',
      storage: '/data/tillbehor/datorkomponenter/lagring',
      cases: '/data/tillbehor/datorkomponenter/chassin',
      psus: '/data/tillbehor/datorkomponenter/strömförsörjning',
    }
  },
  cdon: {
    name: 'CDON.se',
    baseUrl: 'https://www.cdon.se',
    categories: {
      cpus: '/category/data/datorer/komponenter/processorer',
      gpus: '/category/data/datorer/komponenter/grafikkort',
    }
  },
  webhallen: {
    name: 'Webhallen.com',
    baseUrl: 'https://www.webhallen.com',
    categories: {
      cpus: '/sv_SE/cpu',
      gpus: '/sv_SE/grafikkort',
    }
  }
};

// Fallback mock data for development/offline
const MOCK_DATA = {
  updated: new Date().toISOString(),
  source: 'mock',
  components: {
    cpus: [
      { id: 'amd-9800x3d', name: 'AMD Ryzen 9 9800X3D', price: 5990, retailer: 'Komplett', url: '#', performance: 95, performancePerKrona: 15.9 },
      { id: 'amd-9600x', name: 'AMD Ryzen 5 9600X', price: 2890, retailer: 'Komplett', url: '#', performance: 82, performancePerKrona: 28.4 },
      { id: 'intel-285k', name: 'Intel Core Ultra 9 285K', price: 6990, retailer: 'CDON', url: '#', performance: 94, performancePerKrona: 13.4 },
      { id: 'intel-265k', name: 'Intel Core Ultra 7 265K', price: 4290, retailer: 'Webhallen', url: '#', performance: 88, performancePerKrona: 20.5 },
    ],
    gpus: [
      { id: 'rtx-5090', name: 'NVIDIA RTX 5090', price: 24990, retailer: 'Komplett', url: '#', performance: 100, performancePerKrona: 4.0 },
      { id: 'rtx-5080', name: 'NVIDIA RTX 5080', price: 12990, retailer: 'CDON', url: '#', performance: 90, performancePerKrona: 6.9 },
      { id: 'rtx-5070ti', name: 'NVIDIA RTX 5070 Ti', price: 8990, retailer: 'Komplett', url: '#', performance: 85, performancePerKrona: 9.5 },
      { id: 'rx-9070xt', name: 'AMD RX 9070 XT', price: 6990, retailer: 'Webhallen', url: '#', performance: 83, performancePerKrona: 11.9 },
      { id: 'arc-b580', name: 'Intel Arc B580', price: 2390, retailer: 'Komplett', url: '#', performance: 72, performancePerKrona: 30.1 },
    ],
    motherboards: [
      { id: 'asus-x670e', name: 'ASUS ROG X670E Hero', price: 5990, retailer: 'Komplett', url: '#' },
      { id: 'msi-b650', name: 'MSI MAG B650 Tomahawk', price: 1890, retailer: 'CDON', url: '#' },
    ],
    ram: [
      { id: 'ddr5-32-6000', name: 'G.Skill Trident DDR5 32GB 6000MHz', price: 1190, retailer: 'Komplett', url: '#' },
      { id: 'ddr5-64-6000', name: 'Kingston Fury DDR5 64GB 6000MHz', price: 2290, retailer: 'Webhallen', url: '#' },
    ],
    storage: [
      { id: 'samsung-990pro-2tb', name: 'Samsung 990 Pro 2TB', price: 1790, retailer: 'Komplett', url: '#' },
      { id: 'wd-sn850x-1tb', name: 'WD Black SN850X 1TB', price: 1190, retailer: 'CDON', url: '#' },
    ]
  }
};

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function scrapeKomplett(category, path) {
  const results = [];
  const url = RETAILERS.komplett.baseUrl + path;
  
  console.log(`Scraping Komplett: ${category}`);
  
  try {
    const response = await got(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; PCBuilderBot/1.0)',
        'Accept': 'text/html',
      },
      timeout: 15000,
    });
    
    const $ = load(response.body);
    
    // Komplett product grid selector (approximate)
    $('[data-product-item], .product-grid-item, .product-list-item').each((i, el) => {
      const name = $(el).find('h3, .product-title, .product-name').first().text().trim();
      const priceText = $(el).find('[data-price], .price, .product-price').first().text().trim();
      const link = $(el).find('a').first().attr('href');
      
      if (name && priceText) {
        const price = parseInt(priceText.replace(/[^\d]/g, ''));
        if (price > 0) {
          results.push({
            id: name.toLowerCase().replace(/[^a-z0-9]/g, '-'),
            name,
            price,
            retailer: 'Komplett',
            url: link ? RETAILERS.komplett.baseUrl + link : '#',
          });
        }
      }
    });
    
    console.log(`  Found ${results.length} items`);
  } catch (err) {
    console.log(`  Error: ${err.message}`);
  }
  
  await sleep(1000); // Rate limiting
  return results;
}

async function scrapeRetailers() {
  console.log('Starting scrape of Swedish PC component retailers...\n');
  
  const data = {
    updated: new Date().toISOString(),
    source: 'scraped',
    components: {
      cpus: [],
      gpus: [],
      motherboards: [],
      ram: [],
      storage: [],
      cases: [],
      psus: []
    }
  };
  
  // Try Komplett (largest selection)
  try {
    for (const [category, path] of Object.entries(RETAILERS.komplett.categories)) {
      const items = await scrapeKomplett(category, path);
      if (items.length > 0) {
        data.components[category] = items;
      }
    }
  } catch (err) {
    console.log(`Komplett scrape failed: ${err.message}`);
    console.log('Using mock data...\n');
    return MOCK_DATA;
  }
  
  // Check if we got any data
  const totalItems = Object.values(data.components).reduce((sum, arr) => sum + arr.length, 0);
  
  if (totalItems === 0) {
    console.log('No items scraped, using mock data...');
    return MOCK_DATA;
  }
  
  console.log(`\nScraping complete! Total items: ${totalItems}`);
  return data;
}

// Calculate performance per krona (normalized scores)
function addPerformanceScores(data) {
  // CPU benchmark scores (approximate real-world performance)
  const cpuBenchmarks = {
    'amd-9800x3d': 95, 'amd-9600x': 82, 'amd-7700x': 78,
    'intel-285k': 94, 'intel-265k': 88, 'intel-245k': 80,
  };
  
  // GPU benchmark scores (approximate)
  const gpuBenchmarks = {
    'rtx-5090': 100, 'rtx-5080': 90, 'rtx-5070ti': 85,
    'rtx-5070': 78, 'rx-9070xt': 83, 'rx-9070': 75,
    'arc-b580': 72, 'arc-b570': 65,
  };
  
  for (const cpu of data.components.cpus) {
    const normalizedName = cpu.id.replace(/(amd|intel)/g, '$1-');
    cpu.performance = cpuBenchmarks[cpu.id] || cpuBenchmarks[normalizedName] || 70;
    cpu.performancePerKrona = Math.round((cpu.performance / cpu.price) * 1000) / 10;
  }
  
  for (const gpu of data.components.gpus) {
    const normalizedName = gpu.id.replace(/(nvidia|amd|rtx|rx)/gi, '');
    gpu.performance = gpuBenchmarks[gpu.id] || gpuBenchmarks[normalizedName] || 70;
    gpu.performancePerKrona = Math.round((gpu.performance / gpu.price) * 1000) / 10;
  }
  
  return data;
}

// Main execution
async function main() {
  const data = await scrapeRetailers();
  const scoredData = addPerformanceScores(data);
  
  // Write to data file
  writeFileSync('data/prices.json', JSON.stringify(scoredData, null, 2));
  console.log('\nData written to data/prices.json');
}

main().catch(console.error);
