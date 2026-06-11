
> Note: `tenders.db` ships empty and is recreated automatically on first run. `test_pipeline.py` was used during development and can be deleted.

## Running on GitHub Actions (nothing on your computer)

A workflow is included at `.github/workflows/tenders.yml` — it runs every 4 hours on GitHub's servers and commits the dedupe database back to the repo.

1. Create a **private** GitHub repository (e.g. `tendergram`).
2. Upload this entire folder to it (including the hidden `.github` folder).
3. In the repo: **Settings → Secrets and variables → Actions → New repository secret**, add:
   - `TELEGRAM_BOT_TOKEN` = your bot token from @BotFather
   - `TELEGRAM_CHANNEL` = `@your_channel` (or `-100...` numeric id)
4. **Settings → Actions → General → Workflow permissions** → select "Read and write permissions" → Save.
5. Go to the **Actions** tab → "Post tenders to Telegram" → **Run workflow** to test immediately. After that it runs every 4 hours automatically.

Notes:
- Free tier: 2,000 Actions minutes/month on private repos; each run takes well under a minute, so every-4-hours uses ~½ of nothing.
- GitHub disables cron schedules on repos with no activity for 60 days — the database commits count as activity, so this is rarely an issue; if it pauses, press "Run workflow" once.
- Keep the repo **private**: never commit your bot token, and the secrets stay out of the code by design.
