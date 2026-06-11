"""Etimad (Saudi Arabia government tenders) fetcher - STUB.

https://tenders.etimad.sa - lists Saudi government tenders publicly.
The portal has an unofficial JSON endpoint used by its own frontend
(e.g. /Tender/AllTendersForVisitorAsync) which returns paged tender data.
It is unofficial and may change or be blocked; review terms before use.
"""
SOURCE = "etimad"


def fetch() -> list[dict]:
    raise NotImplementedError("Etimad fetcher not yet implemented - see module docstring")
