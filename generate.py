import datetime
import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from scraper import TZ, fetch_all, today_berlin, week_progress

BASE_DIR = Path(__file__).parent
OUT_DIR = BASE_DIR / "docs"
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
HIST_FILE = DATA_DIR / "history.json"

HISTORY_WEEKS = 26


def build_history(tabs, persist=True):
    """Merkt sich pro Woche den Bestpreis je Tab und haengt Sparkline-Daten an."""
    data = {}
    if HIST_FILE.exists():
        data = json.loads(HIST_FILE.read_text(encoding="utf-8"))

    week = today_berlin().strftime("%G-W%V")
    for t in tabs:
        arr = data.setdefault(t["id"], [])
        for e in arr:
            if e["week"] == week:
                if t["min_price"] is not None:
                    e["price"] = min(p for p in [e["price"], t["min_price"]] if p is not None)
                break
        else:
            arr.append({"week": week, "price": t["min_price"]})
        del arr[:-HISTORY_WEEKS]

    if persist:
        DATA_DIR.mkdir(exist_ok=True)
        HIST_FILE.write_text(json.dumps(data, indent=1), encoding="utf-8")

    for t in tabs:
        pts = [(e["week"], e["price"]) for e in data.get(t["id"], []) if e["price"] is not None]
        t["hist_points"] = None
        if len(pts) >= 2:
            vals = [p for _, p in pts]
            lo, hi = min(vals), max(vals)
            span = (hi - lo) or 1
            n = len(pts)
            t["hist_points"] = " ".join(
                "{:.1f},{:.1f}".format(i * 100 / (n - 1), 2 + (hi - v) / span * 24)
                for i, (_, v) in enumerate(pts)
            )
            t["hist_min"] = "{:.2f} €".format(lo).replace(".", ",")
            t["hist_max"] = "{:.2f} €".format(hi).replace(".", ",")
            t["hist_n"] = n
    return data


def main():
    tabs, (week_start, week_end) = fetch_all()
    build_history(tabs)

    env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")))
    template = env.get_template("index.html")
    html = template.render(
        tabs=tabs,
        week_start=week_start.strftime("%d.%m.%Y"),
        week_end=week_end.strftime("%d.%m.%Y"),
        week_pct=week_progress(),
        updated=datetime.datetime.now(TZ).strftime("%d.%m.%Y %H:%M"),
    )

    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "index.html").write_text(html, encoding="utf-8")

    if STATIC_DIR.exists():
        for f in STATIC_DIR.iterdir():
            shutil.copy(f, OUT_DIR / f.name)

    total = sum(len(t["offers"]) for t in tabs)
    print(f"Generated {OUT_DIR / 'index.html'} mit {total} Angebot(en) insgesamt diese Woche.")


if __name__ == "__main__":
    main()
