"""News/RSS fetcher - pre-tender project intelligence.

Unlike portal fetchers (worldbank, undp), this catches projects at the
announcement/award stage: data centers in TR/KZ, Syria reconstruction,
airports, EPC packages. Items are typed "Project News" so the channel
audience can tell them apart from live tenders.

Stdlib XML parsing only; requires `requests` (already in requirements).
"""
import hashlib
import re
import xml.etree.ElementTree as ET

import requests

SOURCE = "news"

FEEDS = [
    ("DatacenterDynamics", "https://www.datacenterdynamics.com/en/rss/"),
    ("Global Construction Review", "https://www.globalconstructionreview.com/feed/"),
    ("The Astana Times", "https://astanatimes.com/feed/"),
]

# item must match at least one sector keyword AND one geo keyword
SECTOR_KEYWORDS = [
    "data center", "data centre", "hyperscale", "colocation",
    "airport", "terminal", "runway",
    "epc", "construction", "reconstruction", "infrastructure",
    "power plant", "substation", "pipeline", "industrial",
]

GEO_COUNTRIES = {
    "Turkey": ["turkey", "türkiye", "turkiye", "ankara", "istanbul"],
    "Kazakhstan": ["kazakhstan", "astana", "almaty", "ekibastuz", "pavlodar"],
    "Syria": ["syria", "damascus", "aleppo", "latakia"],
    "Uzbekistan": ["uzbekistan", "tashkent"],
    "Azerbaijan": ["azerbaijan", "baku"],
    "Georgia": ["georgia", "tbilisi"],
    "Turkmenistan": ["turkmenistan", "ashgabat"],
    "Kyrgyzstan": ["kyrgyzstan", "bishkek"],
    "Tajikistan": ["tajikistan", "dushanbe"],
}

TIMEOUT = 30
HEADERS = {"User-Agent": "Mozilla/5.0 (TenderGram feed reader)"}

_TAG_RE = re.compile(r"<[^>]+>")


def _clean(text):
    return _TAG_RE.sub("", text or "").strip()


def _match_country(text):
    low = text.lower()
    for country, kws in GEO_COUNTRIES.items():
        if any(k in low for k in kws):
            return country
    return None


def _match_sector(text):
    low = text.lower()
    return any(k in low for k in SECTOR_KEYWORDS)


def _parse_feed(name, url):
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items = root.findall(".//item") or root.findall(".//atom:entry", ns)
    out = []
    for it in items:
        title = _clean(it.findtext("title") or it.findtext("atom:title", namespaces=ns))
        link = it.findtext("link") or ""
        if not link:  # atom: <link href="..."/>
            el = it.find("atom:link", ns)
            link = el.get("href") if el is not None else ""
        desc = _clean(it.findtext("description")
                      or it.findtext("atom:summary", namespaces=ns) or "")
        if title:
            out.append((title, link.strip(), desc))
    return out


def fetch():
    tenders = []
    for feed_name, url in FEEDS:
        try:
            entries = _parse_feed(feed_name, url)
        except Exception as e:
            print(f"  {feed_name}: feed error ({e}); skipping")
            continue
        for title, link, desc in entries:
            blob = f"{title} {desc}"
            country = _match_country(blob)
            if not country or not _match_sector(blob):
                continue
            uid_src = link or title
            tenders.append({
                "source": SOURCE,
                "source_id": hashlib.sha1(uid_src.encode("utf-8")).hexdigest()[:16],
                "title": title,
                "country": country,
                "notice_type": "Project News",
                "procurement_group": "CW",
                "procurement_method": None,
                "project_name": None,
                "reference_no": None,
                "deadline": None,
                "url": link or None,
                "raw_excerpt": (desc[:500] or None),
            })
    return tenders
