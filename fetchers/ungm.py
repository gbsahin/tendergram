"""UNGM (UN Global Marketplace) fetcher - STUB.

https://www.ungm.org publishes UN agency tenders (UNDP, UNOPS etc.) including
construction in MEA/CIS. No official public API; the site exposes a JSON search
endpoint (POST https://www.ungm.org/Public/Notice/Search) that requires session
cookies and respectful throttling. Check robots.txt and terms before enabling.

Implement fetch() returning the same normalized dict shape as worldbank.py,
then add this module to fetchers.ACTIVE.
"""
SOURCE = "ungm"


def fetch() -> list[dict]:
    raise NotImplementedError("UNGM fetcher not yet implemented - see module docstring")
