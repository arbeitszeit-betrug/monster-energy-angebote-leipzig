import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from scraper import fetch_offers

BASE_DIR = Path(__file__).parent
OUT_DIR = BASE_DIR / "docs"


def main():
    offers, week_start, week_end, next_offer = fetch_offers()

    env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")))
    template = env.get_template("index.html")
    html = template.render(
        offers=offers,
        next_offer=next_offer,
        week_start=week_start.strftime("%d.%m.%Y"),
        week_end=week_end.strftime("%d.%m.%Y"),
        updated=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
    )

    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"Generated {OUT_DIR / 'index.html'} mit {len(offers)} Angebot(en) diese Woche.")


if __name__ == "__main__":
    main()
