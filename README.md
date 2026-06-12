# TenderGram

Telegram channel bot posting construction & EPC tenders for CIS, Middle East, Africa, and Turkey. Runs free on GitHub Actions.

## Live sources
- **World Bank** procurement notices (official free API)
- **UNDP** procurement notice board (public page, text-parsed)

Stubs with implementation notes: UNGM, EKAP (Turkey), Etimad (Saudi), zakupki/goszakup (CIS).

## Visual cards
Posts are image cards (region-colored banner, country, title, deadline) with a caption containing the link. Toggle with `VISUAL_CARDS` in `config.py`; falls back to plain text if Pillow is missing.

## GitHub Actions deployment
Workflow at `.github/workflows/tenders.yml` runs every 4 hours.
1. Private repo with these files.
2. Secrets (Settings > Secrets and variables > Actions): `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL`.
3. Settings > Actions > General > Workflow permissions: "Read and write permissions".
4. Actions tab > Run workflow to test.

The bot must be an administrator of the channel with "Post messages" enabled.

## Local usage
```
pip install -r requirements.txt
python main.py run --dry-run   # preview without posting
python main.py run             # fetch + post
python main.py add             # manual tender entry
python main.py stats
```

## Tuning (config.py)
`REGIONS` (countries), `SECTOR_KEYWORDS`, `SKIP_NOTICE_TYPES`, `MAX_POSTS_PER_RUN`, `VISUAL_CARDS`.

## Adding a source
Copy `fetchers/worldbank.py`, implement `fetch()` returning the same dict shape, register it in `fetchers/__init__.py`.

## Limitations
World Bank + UNDP cover donor-funded work well (Africa, CIS, parts of MEA) but not Gulf government megaprojects - those need national portals (fragile scraping, check terms) or licensed data (TendersInfo, GlobalTenders, dgMarket). UNDP parsing is screen-scraping a public page: low volume, be respectful, it may need re-tuning if the site changes.
