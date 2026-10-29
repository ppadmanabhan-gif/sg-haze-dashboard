# Singapore haze dashboard

A small website showing Singapore's latest 24-hour PSI for each region, plus the past week.

- Data: National Environment Agency (NEA), via data.gov.sg
- `scripts/fetch_psi.py` fetches the latest readings
- `.github/workflows/update-data.yml` runs it every hour with GitHub Actions
- `docs/index.html` is the website, published with GitHub Pages
