import datetime

from flask import Flask, render_template

from scraper import fetch_all, week_progress

app = Flask(__name__)

_cache = {"data": None, "fetched_at": None}
CACHE_MINUTES = 30


def get_data():
    now = datetime.datetime.now()
    if (
        _cache["data"] is None
        or _cache["fetched_at"] is None
        or now - _cache["fetched_at"] > datetime.timedelta(minutes=CACHE_MINUTES)
    ):
        _cache["data"] = fetch_all()
        _cache["fetched_at"] = now
    return _cache["data"]


@app.route("/")
def index():
    tabs, (week_start, week_end) = get_data()
    return render_template(
        "index.html",
        tabs=tabs,
        week_start=week_start.strftime("%d.%m.%Y"),
        week_end=week_end.strftime("%d.%m.%Y"),
        week_pct=week_progress(),
        updated=_cache["fetched_at"].strftime("%d.%m.%Y %H:%M"),
    )


@app.route("/refresh")
def refresh():
    _cache["data"] = None
    return index()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
