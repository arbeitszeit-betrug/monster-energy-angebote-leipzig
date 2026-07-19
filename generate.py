import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from scraper import fetch_all, week_progress

BASE_DIR = Path(__file__).parent
OUT_DIR = BASE_DIR / "docs"


def main():
    tabs, (week_start, week_end) = fetch_all()

    env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")))
    template = env.get_template("index.html")
    html = template.render(
        tabs=tabs,
        week_start=week_start.strftime("%d.%m.%Y"),
        week_end=week_end.strftime("%d.%m.%Y"),
        week_pct=week_progress(),
        updated=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
    )

    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "index.html").write_text(html, encoding="utf-8")
    total = sum(len(t["offers"]) for t in tabs)
    print(f"Generated {OUT_DIR / 'index.html'} mit {total} Angebot(en) insgesamt diese Woche.")


if __name__ == "__main__":
    main()
