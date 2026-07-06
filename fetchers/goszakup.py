"""Kazakhstan public procurement (goszakup.gov.kz) fetcher.

Uses the official OWS REST API v3. Requires a (free) API token:
register at https://goszakup.gov.kz -> personal cabinet -> API access,
then set env var GOSZAKUP_TOKEN (add it to GitHub Actions secrets and
pass it in the workflow env). Without a token the fetcher skips quietly.

Filters announcements client-side by construction/EPC keywords (RU).
"""
import os
import re

import requests

SOURCE = "goszakup"

API_URL = "https://ows.goszakup.gov.kz/v3/trd-buy"
ANNOUNCE_URL = "https://goszakup.gov.kz/ru/announce/index/{id}"
TIMEOUT = 30
PAGES = 3          # 3 x 50 = last 150 announcements per run
PAGE_SIZE = 50

# RU keywords: construction, reconstruction, EPC-ish scopes
KEYWORDS_RU = [
    "строительств", "реконструкц", "возведени", "монтаж",
    "проектирован", "капитальн", "инфраструктур",
    "аэропорт", "центр обработки данных", "цод", "дата-центр",
]
_KW_RE = re.compile("|".join(KEYWORDS_RU), re.IGNORECASE)


def _token():
    return os.environ.get("GOSZAKUP_TOKEN", "").strip()


def fetch():
    token = _token()
    if not token:
        print("  goszakup: GOSZAKUP_TOKEN not set; skipping (see module docstring)")
        return []
    headers = {"Authorization": f"Bearer {token}",
               "Content-Type": "application/json"}
    tenders = []
    next_page = None
    for _ in range(PAGES):
        params = {"limit": PAGE_SIZE}
        if next_page:
            params["search_after"] = next_page
        r = requests.get(API_URL, headers=headers, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        items = data.get("items", [])
        if not items:
            break
        for it in items:
            name = it.get("name_ru") or it.get("name_kz") or ""
            if not _KW_RE.search(name):
                continue
            buy_id = it.get("id")
            tenders.append({
                "source": SOURCE,
                "source_id": str(buy_id),
                "title": name.strip(),
                "country": "Kazakhstan",
                "notice_type": "Invitation for Bids",
                "procurement_group": "CW",
                "procurement_method": (it.get("ref_trade_methods_id_name")
                                       or it.get("method_name_ru")),
                "project_name": None,
                "reference_no": it.get("number_anno"),
                "deadline": (it.get("end_date") or "")[:10] or None,
                "url": ANNOUNCE_URL.format(id=buy_id),
                "raw_excerpt": None,
            })
        next_page = data.get("next_page")
        if not next_page:
            break
    return tenders
