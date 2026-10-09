from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from bs4 import BeautifulSoup, Tag


REQUEST_URL = "https://www.hoerspiel-request.de/tkkg.shtml"
SITE_URL = (
    "https://www.tkkg-site.de/de/hoeren/hoerspiele/serie/"
    "folge-{number:03d}/inhalt.html"
)
OFFICIAL_URL = "https://www.tkkg.de/produkte/details/{slug}"


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def duration_seconds(value: str | None) -> int | None:
    if not value:
        return None
    try:
        parts = [int(part) for part in value.split(":")]
    except ValueError:
        return None
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return None


def empty_episode(number: int) -> dict[str, Any]:
    return {
        "number": number,
        "title": None,
        "description": None,
        "release_year": None,
        "release_date": None,
        "duration_seconds": None,
        "cast": [],
        "production": [],
        "tracks": [],
        "editions": [],
        "sources": [],
    }


def source(url: str, retrieved_at: str, fields: list[str]) -> dict[str, Any]:
    return {"url": url, "retrieved_at": retrieved_at, "fields": sorted(fields)}


def parse_request(html: str, retrieved_at: str | None = None) -> dict[int, dict[str, Any]]:
    retrieved_at = retrieved_at or datetime.now(timezone.utc).date().isoformat()
    soup = BeautifulSoup(html, "html.parser")
    episodes: dict[int, dict[str, Any]] = {}
    for node in soup.select("div.folge[id]"):
        match = re.fullmatch(r"f(\d{1,3})", node.get("id", ""))
        if not match:
            continue
        number = int(match.group(1))
        episode = empty_episode(number)
        image = node.find("img", alt=re.compile(r"^Cover:"))
        if image:
            episode["title"] = clean(image.get("alt", "").removeprefix("Cover:"))

        strong = node.find("strong")
        strong_text = clean(strong.get_text(" ", strip=True)) if strong else ""
        metadata = re.search(
            r"\((\d+)\)\s*(.*?)\s+Erschienen:\s*(\d{4}).*?Dauer:\s*([0-9:]+)",
            strong_text,
        )
        if metadata:
            if not episode["title"]:
                episode["title"] = clean(metadata.group(2))
            episode["release_year"] = int(metadata.group(3))
            episode["duration_seconds"] = duration_seconds(metadata.group(4))

        description = node.find("em")
        if description:
            episode["description"] = clean(description.get_text(" ", strip=True))

        for row in node.select("table.sprecher_folge tr"):
            cells = row.find_all("td")
            if len(cells) != 2:
                continue
            role, person = (clean(cell.get_text(" ", strip=True)) for cell in cells)
            if role.lower() == "rolle" or not role or not person:
                continue
            episode["cast"].append({"role": role, "person": person})

        fields = [
            key
            for key in ("title", "description", "release_year", "duration_seconds", "cast")
            if episode[key]
        ]
        episode["sources"].append(source(f"{REQUEST_URL}#f{number}", retrieved_at, fields))
        episodes[number] = episode
    return episodes


def _heading(soup: BeautifulSoup, name: str) -> Tag | None:
    return soup.find(lambda tag: isinstance(tag, Tag) and tag.name == "h3" and clean(tag.get_text()) == name)


def _pairs_from_dl(dl: Tag | None) -> list[dict[str, str]]:
    if not dl:
        return []
    result = []
    for term in dl.find_all("dt"):
        value = term.find_next_sibling("dd")
        if value:
            result.append(
                {
                    "role": clean(term.get_text(" ", strip=True)).removesuffix(":"),
                    "person": clean(value.get_text(" ", strip=True)),
                }
            )
    return result


def _production_from_paragraph(paragraph: Tag | None) -> list[dict[str, str]]:
    if not paragraph:
        return []
    values: list[dict[str, str]] = []
    credit: str | None = None
    parts: list[str] = []

    def flush() -> None:
        nonlocal credit, parts
        value = clean(" ".join(parts))
        if credit:
            values.append({"credit": credit, "value": value})
        elif value and ":" in value:
            inferred_credit, inferred_value = value.split(":", 1)
            values.append({"credit": clean(inferred_credit), "value": clean(inferred_value)})
        elif value:
            values.append({"credit": "Weitere Angabe", "value": value})
        credit, parts = None, []

    for child in paragraph.children:
        if isinstance(child, Tag) and child.name == "strong":
            flush()
            strong_text = clean(child.get_text(" ", strip=True))
            if strong_text.endswith(":"):
                credit = strong_text.removesuffix(":")
            elif strong_text:
                values.append({"credit": "Weitere Angabe", "value": strong_text})
        elif isinstance(child, Tag) and child.name == "br":
            flush()
        else:
            text = child.get_text(" ", strip=True) if isinstance(child, Tag) else str(child)
            if clean(text):
                parts.append(clean(text))
    flush()
    return values


def parse_tkkg_site(
    html: str, number: int, retrieved_at: str | None = None
) -> dict[str, Any]:
    retrieved_at = retrieved_at or datetime.now(timezone.utc).date().isoformat()
    soup = BeautifulSoup(html, "html.parser")
    result = empty_episode(number)
    title = soup.find("h1")
    if title:
        title_text = clean(title.get_text(" ", strip=True))
        result["title"] = re.sub(r"^Folge\s+\d+:\s*", "", title_text)

    description_heading = _heading(soup, "Klappentext")
    if description_heading:
        paragraph = description_heading.find_next_sibling("p")
        if paragraph:
            result["description"] = clean(paragraph.get_text(" ", strip=True))

    track_heading = _heading(soup, "Trackpunkte")
    if track_heading:
        items = []
        for sibling in track_heading.find_next_siblings():
            if isinstance(sibling, Tag) and sibling.name == "h3":
                break
            if isinstance(sibling, Tag):
                items.extend(sibling.find_all("li"))
        result["tracks"] = [
            {"position": index, "title": clean(item.get_text(" ", strip=True))}
            for index, item in enumerate(items, 1)
        ]

    cast_heading = _heading(soup, "Sprecher")
    if cast_heading:
        result["cast"] = _pairs_from_dl(cast_heading.find_next_sibling("dl"))

    production_heading = _heading(soup, "Produktion")
    if production_heading:
        result["production"] = _production_from_paragraph(
            production_heading.find_next_sibling("p")
        )

    labels = soup.select_one(".bookInfo .infotext")
    values = soup.select_one(".bookInfo .infoContent")
    if labels and values:
        label_lines = [clean(x) for x in labels.get_text("\n").splitlines() if clean(x)]
        value_lines = [clean(x) for x in values.get_text("\n").splitlines() if clean(x)]
        edition = {label.removesuffix(":"): value for label, value in zip(label_lines, value_lines)}
        if edition:
            result["editions"] = [edition]

    fields = [
        key
        for key in ("title", "description", "cast", "production", "tracks", "editions")
        if result[key]
    ]
    result["sources"] = [source(SITE_URL.format(number=number), retrieved_at, fields)]
    return result


def parse_official(
    html: str, number: int, slug: str, retrieved_at: str | None = None
) -> dict[str, Any]:
    retrieved_at = retrieved_at or datetime.now(timezone.utc).date().isoformat()
    soup = BeautifulSoup(html, "html.parser")
    result = empty_episode(number)
    main = soup.find("main") or soup
    title = main.find("h1")
    if title:
        result["title"] = clean(title.get_text(" ", strip=True))

    date_match = re.search(r"Veröffentlichkeitsdatum:\s*(\d{2})\.(\d{2})\.(\d{4})", main.get_text(" "))
    if date_match:
        result["release_date"] = f"{date_match.group(3)}-{date_match.group(2)}-{date_match.group(1)}"
        result["release_year"] = int(date_match.group(3))

    content_heading = _heading(main, "Inhalt")
    if content_heading:
        paragraph = content_heading.find_next_sibling("p")
        if paragraph:
            result["description"] = clean(paragraph.get_text(" ", strip=True))

    cast_heading = _heading(main, "Sprecher")
    if cast_heading:
        paragraph = cast_heading.find_next_sibling("p")
        if paragraph:
            for line in paragraph.get_text("\n", strip=True).splitlines():
                line = clean(line)
                if "-" not in line or line.lower().startswith("und "):
                    continue
                role, person = line.split("-", 1)
                if clean(role) and clean(person):
                    result["cast"].append({"role": clean(role), "person": clean(person)})

    details_heading = _heading(main, "Details")
    if details_heading:
        result["production"] = _production_from_paragraph(
            details_heading.find_next_sibling("p")
        )

    fields = [
        key
        for key in ("title", "description", "release_year", "release_date", "cast", "production")
        if result[key]
    ]
    result["sources"] = [source(OFFICIAL_URL.format(slug=slug), retrieved_at, fields)]
    return result


def merge_episode(primary: dict[str, Any], archive: dict[str, Any]) -> dict[str, Any]:
    merged = empty_episode(primary["number"])
    scalar_keys = ("title", "description", "release_year", "release_date", "duration_seconds")
    for key in scalar_keys:
        merged[key] = primary.get(key) or archive.get(key)
    for key in ("cast", "production", "tracks", "editions"):
        merged[key] = archive.get(key) or primary.get(key) or []
    merged["sources"] = (primary.get("sources") or []) + (archive.get("sources") or [])
    return merged
