import datetime
import re

import requests
from bs4 import BeautifulSoup

URL = "https://www.marktguru.de/bl/monster-energy/leipzig"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}

# Angebote, deren Beschreibungstext ein eigenständiges Wort "APP" enthaelt
# (z.B. "MIT LIDL PLUS APP", "Kaufland App"), sind App-exklusiv und fliegen raus.
APP_ONLY_RE = re.compile(r"\bAPP\b", re.IGNORECASE)
DATE_RE = re.compile(r"(\d{2})\.(\d{2})\.\s*-\s*(\d{2})\.(\d{2})\.")


def _parse_dates(text, today):
    m = DATE_RE.search(text)
    if not m:
        return None, None
    d1, mo1, d2, mo2 = (int(x) for x in m.groups())
    year = today.year
    start = datetime.date(year, mo1, d1)
    end = datetime.date(year, mo2, d2)
    if end < start:
        end = end.replace(year=year + 1)
    # Jahreswechsel: Datum liegt eigentlich weit in der Vergangenheit -> naechstes Jahr
    if start < today - datetime.timedelta(days=200):
        start = start.replace(year=start.year + 1)
        end = end.replace(year=end.year + 1)
    return start, end


def week_range(today):
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return monday, sunday


def fetch_offers():
    resp = requests.get(URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    today = datetime.date.today()
    week_start, week_end = week_range(today)

    offers = []
    upcoming = []
    for li in soup.select("ul.offer-list > li.offer-list-item"):
        if "expired" in li.get("class", []):
            continue

        valid_el = li.select_one("dd.valid")
        start, end = _parse_dates(valid_el.get_text(strip=True) if valid_el else "", today)
        if not start or not end:
            continue
        if end < week_start:
            continue  # bereits abgelaufen

        info_el = li.select_one("div.info")
        info_text = info_el.get_text(" ", strip=True) if info_el else ""
        if APP_ONLY_RE.search(info_text):
            continue  # App-exklusives Angebot ausschliessen

        price_el = li.select_one("dd.price span.price")
        retailer_el = li.select_one("dd.retailer-name a")
        address_el = li.select_one("dd.retailer-address address")
        product_el = li.select_one("div.header h3")

        entry = {
            "product": product_el.get_text(strip=True) if product_el else "Monster Energy",
            "price": price_el.get_text(strip=True) if price_el else "?",
            "retailer": retailer_el.get_text(strip=True) if retailer_el else "Unbekannt",
            "address": address_el.get_text(strip=True) if address_el else "",
            "valid_from": start.strftime("%d.%m."),
            "valid_to": end.strftime("%d.%m."),
            "info": info_text,
        }

        if start > week_end:
            upcoming.append((start, entry))
        else:
            offers.append(entry)

    offers.sort(key=lambda o: (o["retailer"], o["price"]))
    upcoming.sort(key=lambda pair: pair[0])
    next_offer = upcoming[0][1] if upcoming else None
    return offers, week_start, week_end, next_offer
