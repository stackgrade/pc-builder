# PC Builder SE

Hitta bästa prestanda per krona för din nästa dator. Jämför priser från svenska återförsäljare.

## Tech Stack

- **Framework:** Astro.js (static output)
- **Styling:** Vanilla CSS (dark mode)
- **Data:** JSON via GitHub Actions cron
- **Hosting:** Free (GitHub Pages / Vercel / Cloudflare Pages)
- **Scraping:** Node.js + Cheerio (via GitHub Actions)

## Arkitektur

```
.github/workflows/scrape.yml
├── Körs var 6:e timme
├── Scrape:ar svenska återförsäljare
├── Sparar till data/prices.json
└── Committar om priserna ändrats

src/pages/index.astro
├── Läser data/prices.json
├── Sorterar efter bästa pris/krona
└── Renderar statisk HTML
```

## Kom igång

```bash
# Installera
npm install

# Utveckling
npm run dev

# Bygga
npm run build

# Testa scraper (utan att spara)
npm run scrape

# Förhandsgranska
npm run preview
```

## Deployment

### Cloudflare Pages (rekommenderad - gratis)

1. Pusha till GitHub
2. Koppla till Cloudflare Pages
3. Byggkommando: `npm run build`
4. Output-katalog: `dist`

### Vercel (gratis)

1. `npm i -g vercel`
2. `vercel`

### GitHub Pages

1. `npm run build`
2. Deploya `dist/` mappen

## Framtida features

- [ ] AI-powered build recommendations ("Jag vill spela Cyberpunk för 15k")
- [ ] Price alerts (notify when GPU drops below X kr)
- [ ] Affiliate links till återförsäljare
- [ ] Real scraping från Komplett, CDON, Webhallen, Dustin
- [ ] Price history charts
- [ ] Build simulator / configurator

## Licens

MIT
