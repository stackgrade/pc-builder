# PC Builder SE

**Svensk marknad** — Hitta bästa prestanda per krona för din nästa dator.

👉 **Live:** https://stackgrade.github.io/pc-builder/

## Vad det är

En sajt som jämför PC-komponenter och visar vilken som ger mest prestanda per krona. Priserna hämtas från svenska återförsäljare (Komplett, CDON, Webhallen, Dustin).

## Tech Stack

- **Framework:** Astro.js (static output)
- **Språk:** Svenska
- **Styling:** Vanilla CSS (dark mode)
- **Data:** JSON (scrapad via GitHub Actions)
- **Hosting:** GitHub Pages ($0)

## Arkitektur

```
src/pages/index.astro    ← UI (Astro static)
data/prices.json        ← Priser (uppdateras var 6:e timme)
.github/workflows/      ← Scraping cron job
```

## Deployment

GitHub Pages: https://stackgrade.github.io/pc-builder/

## Features (kommande)

- [ ] AI build-förslag ("Jag vill spela Cyberpunk för 15k")
- [ ] Riktiga priser från svenska återförsäljare
- [ ] Affiliate links
- [ ] Price history
- [ ] Build configurator

## Licens

MIT
