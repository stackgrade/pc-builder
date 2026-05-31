# PC Builder SE — Svensk PC-komponent-sajt

## Projekttyp
Astro + UnoCSS sajt som jämför PC-komponentpriser från svenska retailers. Live: stackgrade.github.io/pc-builder

## Arkitektur
- **Framework:** Astro + UnoCSS
- **Scraping:** `scrape_komplett_v2.py` (curl_cffi)
- **Hosting:** GitHub Pages
- **CI/CD:** GitHub Actions (daglig scraping kl 06:00 UTC)

## Datakällor (products)
- CPUs, GPUs, Motherboards, RAM, Storage, PSUs, Cases
- 45+ produkter scraped hittills
- **Cases fortfarande tomma** — behöver bättre queries

## MCP-användning

| Verktyg | När |
|---------|-----|
| **GitHub** | Pusha priser, hantera GitHub Actions, merga PRs, kolla issues |
| **Context7** | Astro-dokumentation, UnoCSS-referens, curl_cffi |
| **Playwright** | Scrapa produktsidor som curl_cffi inte klarar, testa sajten |
| **Filesystem** | All kod-redigering i src/, scripts/, data/ |

## Arbetsflöde
1. `scrape_komplett_v2.py` scraperar produkter dagligen
2. GitHub Actions committar om priser ändras
3. Astro bygger statisk site till `dist/`
4. GitHub Pages deployar

## Viktigt
- **INGEN AI-CHAT** — istället: dynamisk value-optimering
- Fokus: pris/krona för varje komponent
- Uppdatera prices i `data/` mappen
- GitHub Actions kör `scrape.yml` varje dag 06:00 UTC

## Filer att hålla koll på
- `src/` — Astro-komponenter
- `scripts/scrape_komplett_v2.py` — scraping-script
- `data/` — produktrelatorad data
- `.github/workflows/scrape.yml` — daglig automation
