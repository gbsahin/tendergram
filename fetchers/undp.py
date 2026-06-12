"""UNDP procurement notices fetcher.

Scrapes https://procurement-notices.undp.org/ (public notice board, no login).
Parsing is text-based (strip tags, scan label/value pairs) so it survives
minor markup changes. Covers UNDP offices worldwide incl. Iraq, Yemen,
Central Asia, Turkiye, and most of Africa.
"""
import re
import urllib.request

SOURCE = "undp"
BASE = "https://procurement-notices.undp.org/"

SCRIPT_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.S | re.I)
HTML_RE = re.compile(r"<[^>]+>")
LINK_RE = re.compile(r"view_(?:notice|negotiation)\.cfm\?(?:notice_id|nego_id)=\d+", re.I)
LABELS = ("Title", "Ref No", "UNDP Office/Country", "Process", "Deadline", "Posted")


def _get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 tendergram/0.2"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch() -> list[dict]:
    raw = _get(BASE)
    return parse(raw)


def parse(raw: str) -> list[dict]:
    # Ordered, de-duplicated notice links (a row may contain several anchors
    # pointing to the same notice).
    links, seen = [], set()
    for href in LINK_RE.findall(raw):
        if href not in seen:
            seen.add(href)
            links.append(href)

    text = SCRIPT_RE.sub(" ", raw)
    text = HTML_RE.sub("\n", text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    records, current, key = [], None, None
    for line in lines:
        if line == "Title":
            if current and current.get("Title"):
                records.append(current)
            current, key = {}, "Title"
            continue
        if current is None:
            continue
        if line in LABELS:
            key = line
            continue
        if key:
            current[key] = (current.get(key, "") + " " + line).strip()
    if current and current.get("Title"):
        records.append(current)

    out = []
    for i, r in enumerate(records):
        office = r.get("UNDP Office/Country", "")
        country = office.split("/")[-1].strip().title() if "/" in office else office.title()
        url = BASE + links[i] if i < len(links) else BASE
        out.append({
            "source": SOURCE,
            "source_id": r.get("Ref No") or r.get("Title", "")[:80],
            "title": r.get("Title", "Untitled")[:300],
            "country": _normalize_country(country),
            "notice_type": r.get("Process") or "Procurement Notice",
            "procurement_group": None,
            "procurement_method": r.get("Process"),
            "project_name": None,
            "reference_no": r.get("Ref No"),
            "deadline": _normalize_date(r.get("Deadline", "")),
            "url": url,
            "raw_excerpt": None,
        })
    return out


def _normalize_country(c: str) -> str:
    aliases = {
        "Tuerkiye": "Turkiye", "Turkey": "Turkiye", "Türkiye": "Turkiye",
        "Syria": "Syrian Arab Republic", "Iran": "Iran, Islamic Republic of",
        "Russia": "Russian Federation", "Kyrgyzstan": "Kyrgyz Republic",
        "Drc": "Congo, Democratic Republic of", "Ivory Coast": "Cote d'Ivoire",
        "Palestine": "West Bank and Gaza",
        "Egypt": "Egypt", "Tanzania (United Republic Of)": "Tanzania",
    }
    return aliases.get(c, c)


def _normalize_date(d: str):
    m = re.search(r"(\d{1,2})-([A-Za-z]{3})-(\d{2})", d)
    if not m:
        return None
    months = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05",
              "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10",
              "Nov": "11", "Dec": "12"}
    mon = months.get(m.group(2).title())
    if not mon:
        return None
    return f"20{m.group(3)}-{mon}-{int(m.group(1)):02d}"
