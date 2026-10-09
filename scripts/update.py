#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tkkgmeta.scrapers import (
    OFFICIAL_URL,
    REQUEST_URL,
    SITE_URL,
    merge_episode,
    parse_official,
    parse_request,
    parse_tkkg_site,
)

CACHE = ROOT / ".cache"
USER_AGENT = "tkkgmeta/0.1 (+https://github.com/; public metadata research)"
OFFICIAL_EPISODES = {
    199: "verfolgungsjagd-vor-mitternacht",
    205: "teuflische-kaffeefahrt",
    206: "achtung-ufo-kult",
    207: "doppelte-entfuhrung",
    208: "geheimnis-im-tresor",
    209: "drohbriefe-von-unbekannt",
    210: "raubzug-im-casino",
    211: "geiselnahme-im-villenviertel",
    212: "tyrannei-kommando-eins",
    213: "das-unheimliche-dorf",
    214: "diamantenrausch-auf-der-a9",
    215: "verbrechen-im-moorsteiner-wald",
    216: "das-geheimnis-im-jagdschloss-1",
    217: "todliche-klarinette-1",
    218: "schutzgeld-fur-damonen-1",
    219: "terror-frei-haus-1",
    220: "attentat-am-gamsengrat-1",
    221: "beim-raubzug-helfen-ahnungslose",
    222: "roter-drache-222",
    223: "betruger-super-sauber",
    224: "bilderdiebe-haben-kein-gesicht",
    225: "tanz-mit-der-giftschlange",
    226: "der-tater-unter-uns",
    227: "zwei-fur-zwolf",
    228: "das-geld-das-niemand-wollte",
    229: "auf-den-schwingen-des-totenvogels",
    230: "die-tesla-verschworung",
    231: "knackis-streicheln-mit-der-faust",
    232: "drohnenaugen-in-der-nacht",
    233: "rauberwald",
    234: "im-auftrag-des-bosen",
    235: "ein-gruselfest-fur-ein-vermogen",
    236: "schatten-aus-der-unterwelt",
    237: "k-i-kriminelle-illusion",
    238: "nur-tote-schlafen-langer",
    239: "vollgas-ins-verderben",
    240: "das-verschollene-zepter-von-gizeh",
    241: "das-ratsel-der-gruselvilla",
    242: "verbrechen-live-im-radio",
    243: "die-fahrte-des-hehlers",
}


def fetch(url: str, target: Path, refresh: bool, offline: bool) -> str:
    if target.exists() and not refresh:
        return target.read_text(encoding="utf-8", errors="replace")
    if offline:
        raise FileNotFoundError(f"Nicht im Cache: {target}")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = response.read()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    return payload.decode("utf-8", errors="replace")


def archive_page(number: int, refresh: bool, offline: bool) -> tuple[int, str | None, str | None]:
    try:
        html = fetch(
            SITE_URL.format(number=number),
            CACHE / "tkkg-site" / f"{number:03d}.html",
            refresh,
            offline,
        )
        return number, html, None
    except (OSError, urllib.error.URLError) as error:
        return number, None, str(error)


def write_outputs(episodes: list[dict], generated_at: str) -> None:
    episode_dir = ROOT / "data" / "episodes"
    episode_dir.mkdir(parents=True, exist_ok=True)
    expected = set()
    for episode in episodes:
        path = episode_dir / f"{episode['number']:03d}.json"
        expected.add(path.name)
        path.write_text(json.dumps(episode, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for stale in episode_dir.glob("*.json"):
        if stale.name not in expected:
            stale.unlink()

    bundle = {
        "meta": {"generated_at": generated_at, "episode_count": len(episodes)},
        "episodes": episodes,
    }
    (ROOT / "data" / "all.json").write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (ROOT / "data" / "index.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["number", "title", "release_year", "duration_seconds", "cast_count", "track_count"]
        )
        for episode in episodes:
            writer.writerow(
                [
                    episode["number"],
                    episode["title"],
                    episode["release_year"],
                    episode["duration_seconds"],
                    len(episode["cast"]),
                    len(episode["tracks"]),
                ]
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="TKKG-Metadaten aus öffentlichen Quellen aktualisieren")
    parser.add_argument("--refresh", action="store_true", help="vorhandenen HTTP-Cache neu laden")
    parser.add_argument("--offline", action="store_true", help="keine Netzaufrufe ausführen")
    parser.add_argument("--workers", type=int, default=6, help="parallele Archivabrufe (Standard: 6)")
    parser.add_argument("--archive-max", type=int, default=206, help="höchste TKKG-Site-Archivfolge")
    args = parser.parse_args()
    if args.refresh and args.offline:
        parser.error("--refresh und --offline schließen sich aus")

    today = datetime.now(timezone.utc).date().isoformat()
    overview = fetch(REQUEST_URL, CACHE / "hoerspiel-request" / "tkkg.html", args.refresh, args.offline)
    episodes = parse_request(overview, today)
    print(f"Hörspiel-Request: {len(episodes)} reguläre Folgen")

    for number, slug in OFFICIAL_EPISODES.items():
        official_html = fetch(
            OFFICIAL_URL.format(slug=slug),
            CACHE / "tkkg.de" / f"{number:03d}.html",
            args.refresh,
            args.offline,
        )
        official = parse_official(official_html, number, slug, today)
        # Keep the usually more exhaustive Hörspiel-Request cast, but prefer
        # official scalar values and use official production data as fallback.
        episodes[number] = merge_episode(official, episodes.get(number, {"number": number}))
    print(f"Offizielle Ergänzungen: {len(OFFICIAL_EPISODES)}")

    archive_results = {}
    failures = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        jobs = {
            executor.submit(archive_page, number, args.refresh, args.offline): number
            for number in range(1, args.archive_max + 1)
        }
        for index, future in enumerate(as_completed(jobs), 1):
            number, html, error = future.result()
            if html:
                archive_results[number] = parse_tkkg_site(html, number, today)
            else:
                failures.append((number, error))
            if index % 25 == 0:
                print(f"TKKG-Site: {index}/{args.archive_max} verarbeitet")
            if not args.offline:
                time.sleep(0.01)

    all_numbers = sorted(set(episodes) | set(archive_results))
    merged = [
        merge_episode(episodes.get(number, {"number": number}), archive_results.get(number, {"number": number}))
        for number in all_numbers
    ]
    write_outputs(merged, today)
    print(f"Geschrieben: {len(merged)} Folgen; Archivfehler: {len(failures)}")
    for number, error in failures[:10]:
        print(f"  Folge {number:03d}: {error}")

    from scripts.report import build_report

    build_report(merged, ROOT / "REPORT.md", today)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
