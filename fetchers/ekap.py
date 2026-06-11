"""EKAP (Turkey public procurement platform) fetcher - STUB.

https://ekap.kik.gov.tr - Turkey's official e-procurement platform.
No public API. Tender announcements are searchable on the site; scraping
requires handling ASP.NET viewstate/session and is against some usage terms.
A legally cleaner route: Kamu Ihale Bulteni (public tender bulletin) or licensed
data resellers (e.g. ihale.gov.tr bulletins, private aggregators).

Implement fetch() returning normalized dicts (see worldbank.py), then register
in fetchers.ACTIVE.
"""
SOURCE = "ekap"


def fetch() -> list[dict]:
    raise NotImplementedError("EKAP fetcher not yet implemented - see module docstring")
