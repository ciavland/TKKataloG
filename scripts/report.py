#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ranges(numbers: list[int]) -> str:
    if not numbers:
        return "–"
    groups = []
    start = previous = numbers[0]
    for number in numbers[1:]:
        if number == previous + 1:
            previous = number
            continue
        groups.append(str(start) if start == previous else f"{start}–{previous}")
        start = previous = number
    groups.append(str(start) if start == previous else f"{start}–{previous}")
    return ", ".join(groups)


def build_report(episodes: list[dict], target: Path, generated_at: str) -> None:
    fields = {
        "Titel": "title",
        "Beschreibung": "description",
        "Sprecher": "cast",
        "Produktionsdaten": "production",
        "Erscheinungsjahr": "release_year",
        "Exaktes Erscheinungsdatum": "release_date",
        "Laufzeit": "duration_seconds",
        "Trackpunkte": "tracks",
        "Ausgaben/EAN": "editions",
    }
    lines = [
        "# Datenstand und Lückenbericht",
        "",
        f"Erzeugt am {generated_at}. Der Bestand umfasst **{len(episodes)} reguläre Folgen**.",
        "",
        "## Abdeckung",
        "",
        "| Feld | vorhanden | fehlt | fehlende Folgen |",
        "|---|---:|---:|---|",
    ]
    for label, key in fields.items():
        missing = [episode["number"] for episode in episodes if not episode.get(key)]
        lines.append(f"| {label} | {len(episodes) - len(missing)} | {len(missing)} | {ranges(missing)} |")

    expected = set(range(1, max(e["number"] for e in episodes) + 1))
    absent = sorted(expected - {e["number"] for e in episodes})
    host_counts = Counter(
        source["url"].split("/", 3)[2]
        for episode in episodes
        for source in episode.get("sources", [])
    )
    lines += [
        "",
        "## Bekannte Lücken und Grenzen",
        "",
        f"- Komplett fehlende reguläre Folgen im Nummernbereich: **{ranges(absent)}**.",
        "- Produktionscredits stammen für ältere Folgen überwiegend aus dem TKKG-Site-Archiv und ab Folge 207 aus offiziellen Detailseiten. Einzelne Quellseiten enthalten trotzdem keine Credits; die betroffenen Folgen stehen in der Tabelle.",
        "- Exakte Veröffentlichungstage stammen ausschließlich aus den eingebundenen offiziellen Detailseiten (derzeit 199, 205–243). Das Archiv vermischt bei älteren Folgen Erst- und Wiederveröffentlichungen, weshalb daraus bewusst kein scheinbar exaktes Datum abgeleitet wird.",
        "- Trackpunkte fehlen für Folge 154 bereits in der Archivquelle; ab Folge 207 wurden noch keine belastbaren Kapitel-/Tracklisten importiert.",
        "- Die Beschreibungen sind Quelltexte Dritter und nicht von der MIT-Lizenz des Codes umfasst.",
        "- Specials, TKKG Junior, Bücher, Filme, Coverdateien, Kapitel-Zeitstempel, Streaming-IDs und MusicBrainz-IDs sind noch nicht modelliert/importiert.",
        "- Schreibweisen von Rollen und Personen werden quellengetreu übernommen; Pseudonyme und Alias-Normalisierung fehlen noch.",
        "- Konflikte zwischen Quellen werden noch nicht als eigene Datensätze gespeichert; bei Sprecher-, Produktions-, Track- und Ausgabelisten hat das detailliertere TKKG-Site-Archiv Vorrang.",
        "",
        "## Quellenbilanz",
        "",
    ]
    for host, count in sorted(host_counts.items()):
        lines.append(f"- `{host}`: bei {count} Folgendatensätzen referenziert")
    lines += [
        "",
        "## Sinnvolle nächste Schritte",
        "",
        "1. Die in der Tabelle genannten Folgen ohne Produktionsdaten anhand offizieller Inlays oder einer ausdrücklich nutzbaren Quelle ergänzen.",
        "2. Exakte Veröffentlichungstage und Streaming-IDs aus offiziellen Katalogen ergänzen.",
        "3. Specials und TKKG Junior in getrennten Serien erfassen.",
        "4. Personen- und Rollen-IDs samt Alias-Tabelle einführen, ohne abweichende Originalcredits zu verlieren.",
        "5. Kapitel-Zeitstempel aus legal verfügbaren Medien oder MusicBrainz-Daten ergänzen.",
        "",
        "Der Bericht wird mit `make report` bzw. bei jedem `make update` neu erzeugt.",
        "",
    ]
    target.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    bundle = json.loads((ROOT / "data" / "all.json").read_text(encoding="utf-8"))
    build_report(
        bundle["episodes"], ROOT / "REPORT.md", datetime.now(timezone.utc).date().isoformat()
    )


if __name__ == "__main__":
    main()
