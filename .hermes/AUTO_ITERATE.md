# 🏗️ PC Builder SE — Autonomous Build Backlog

## 📦 Project
- **Name:** pc-builder
- **Stack:** Astro v6 + UnoCSS + GitHub Pages
- **Live:** https://stackgrade.github.io/pc-builder
- **Repo:** github.com/stackgrade/pc-builder (main branch → GH Pages auto-deploy)
- **Build:** `npm run build` → static dist/ → pushed to main triggers deploy workflow

## 🏁 COMPLETED
- ✅ initial-codebase-deploy — Full Astro + UnoCSS project live on GH Pages
- ✅ budget-tier-selector — 4 budget tiers (7k/10k/15k/20k) with interactive switching
- ✅ build-optimization-engine — Brute-force optimal PC algorithm per budget
- ✅ component-database — 45+ components (CPU/GPU/RAM/Storage/MB/PSU/Case) scraped from Komplett.se
- ✅ price-scraping-github-actions — Daily automated scraping via GitHub Actions
- ✅ glass-morphism-design — Dark theme with glass effects, animations, performance bars
- ✅ client-side-budget-switching — URL-based budget switching with pushState + popstate

## 📋 PENDING — Ordered by priority

### 🔴 HIGH

- [x] **mobile-first-layout** — Ensure 320px responsive baseline. Fixed viewport meta (initial-scale=1.0), hero heading responsive sizing, overflow-x-hidden prevention, touch targets ≥44px on tier buttons, grid min-width:0 safety, CSS overrides for sub-375px/639px. ✅ Sprint 75

- [x] **dark-mode-persistence** — CSS custom properties for light/dark theme, `prefers-color-scheme` listener + localStorage persistence, 🌙/☀️ toggle button in fixed top-right nav. CSS variables replace all hardcoded background/text/border colors. Light theme overrides for readable mode. ✅ Sprint 76

- [x] **seo-meta-tags** — Full Open Graph (og:title, og:description, og:image, og:url, og:type, og:site_name, og:locale), Twitter Card (summary_large_image), canonical URL. Created og-image.svg. Layout.astro supports per-page overrides via Props (description, image, type, canonical, twitterCard). ✅ Sprint 77

### 🟡 MEDIUM

- [ ] **component-browser** — Add individual component browsing tab/section showing all CPUs, GPUs, RAM sticks sorted by performance per krona with retailer links. Useful for users who want to see all options, not just the optimal build.

- [ ] **price-history-chart** — Track price history from GitHub Actions scrape data. Add a simple chart showing price trends for popular components. Use a lightweight chart approach (CSS/SVG bars or canvas).

- [ ] **loading-and-empty-states** — Handle empty data (no components/price data available) gracefully. Currently assumes data always exists. Add skeleton loaders and informative empty state messages.

### 🟢 LOW

- [ ] **custom-404-page** — Create branded 404 page with search box and link back to main tool. Follow the existing glass-morphism design pattern.

- [ ] **build-configurator** — Allow manual component selection within budget constraints. Let users swap individual parts (CPU, GPU, etc.) and see updated total price and performance score. Interactive client-side logic.

- [ ] **ai-build-suggestion-banner** — "Beskriv ditt användningsområde" banner that helps users pick the right budget tier based on their use case (gaming, workstation, budget, etc.).

- [ ] **retailer-affiliate-links** — Format Komplett.se URLs with affiliate tracking parameters. Add rel="sponsored" to outbound links for SEO compliance.

- [ ] **service-worker-caching** — Basic offline support by caching the static assets and latest price data. Register a service worker that enables repeat visits even without network.

## 📊 Stats
- build_count: 23
- pages: 1 (index.astro)
- deploy: GitHub Pages (push to main → auto-deploy via workflow)
- pending: 10 items
