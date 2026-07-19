import datetime

from flask import Flask, render_template

from scraper import fetch_offers

app = Flask(__name__)

_cache = {"data": None, "fetched_at": None}
CACHE_MINUTES = 30


def get_offers():
    now = datetime.datetime.now()
    if (
        _cache["data"] is None
        or _cache["fetched_at"] is None
        or now - _cache["fetched_at"] > datetime.timedelta(minutes=CACHE_MINUTES)
    ):
        _cache["data"] = fetch_offers()
        _cache["fetched_at"] = now
    return _cache["data"]


@app.route("/")
def index():
    offers, week_start, week_end, next_offer = get_offers()
    return render_template(
        "index.html",
        offers=offers,
        next_offer=next_offer,
        week_start=week_start.strftime("%d.%m.%Y"),
        week_end=week_end.strftime("%d.%m.%Y"),
        updated=_cache["fetched_at"].strftime("%d.%m.%Y %H:%M"),
    )


@app.route("/refresh")
def refresh():
    _cache["data"] = None
    return index()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
