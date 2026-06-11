"""zakupki.gov.ru (Russia) / goszakup.gov.kz (Kazakhstan) fetchers - STUB.

Russia: zakupki.gov.ru offers official open data (ftp.zakupki.gov.ru, XML dumps)
under 44-FZ/223-FZ. Free but high-volume; needs XML parsing pipeline.
Kazakhstan: goszakup.gov.kz has an official REST API (token required, free reg).
Uzbekistan/Azerbaijan have their own portals (xarid.uzex.uz, etender.gov.az).

Implement per-country fetch() functions returning normalized dicts.
"""
SOURCE = "zakupki"


def fetch() -> list[dict]:
    raise NotImplementedError("CIS national portal fetchers not yet implemented")
