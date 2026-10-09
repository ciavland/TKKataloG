import unittest

from tkkgmeta.scrapers import (
    duration_seconds,
    merge_episode,
    parse_official,
    parse_request,
    parse_tkkg_site,
)


class ScraperTests(unittest.TestCase):
    def test_duration(self):
        self.assertEqual(duration_seconds("41:04"), 2464)
        self.assertEqual(duration_seconds("1:04:14"), 3854)

    def test_request_parser(self):
        html = '''<div class="folge" id="f7"><img alt="Cover: Rätsel um die alte Villa">
        <table class="sprecher_folge"><tr><td>Rolle</td><td>Sprecher/in</td></tr>
        <tr><td>Tim</td><td>Sascha Draeger</td></tr></table>
        <strong>TKKG (7) Rätsel um die alte Villa Erschienen: 1982 Dauer: 42:03</strong>
        <em>Eine Beschreibung.</em></div>'''
        episode = parse_request(html, "2026-01-01")[7]
        self.assertEqual(episode["title"], "Rätsel um die alte Villa")
        self.assertEqual(episode["release_year"], 1982)
        self.assertEqual(episode["cast"][0]["person"], "Sascha Draeger")

    def test_archive_parser_and_merge(self):
        html = '''<h1>Folge 007: Rätsel um die alte Villa</h1>
        <h3>Klappentext</h3><p>Archivbeschreibung.</p>
        <h3>Trackpunkte</h3><ol><li>Beginn</li></ol>
        <h3>Sprecher</h3><dl><dt>Tim:</dt><dd>Sascha Draeger</dd></dl>
        <h3>Produktion</h3><p><strong>Regie:</strong> Heikedine Körting<br>Eine Produktion</p>'''
        archive = parse_tkkg_site(html, 7, "2026-01-01")
        primary = {"number": 7, "title": "Titel", "description": "Primär", "cast": [], "sources": []}
        merged = merge_episode(primary, archive)
        self.assertEqual(merged["description"], "Primär")
        self.assertEqual(merged["tracks"][0]["title"], "Beginn")
        self.assertTrue(merged["production"])
        self.assertEqual(merged["production"][0], {"credit": "Regie", "value": "Heikedine Körting"})

    def test_official_parser(self):
        html = '''<main><h1>Das unheimliche Dorf</h1><p>Veröffentlichkeitsdatum: 06.12.2019</p>
        <h3>Inhalt</h3><p>Sommer, Sonne, Ferien!</p>
        <h3>Sprecher</h3><p>Tim - Sascha Draeger<br>Karl - Tobias Diakow</p>
        <h3>Details</h3><p><strong>Buch:</strong> Martin Hofstetter<br>
        <strong>Produktion und Regie:</strong> Heikedine Körting</p></main>'''
        episode = parse_official(html, 213, "das-unheimliche-dorf", "2026-01-01")
        self.assertEqual(episode["release_date"], "2019-12-06")
        self.assertEqual(len(episode["cast"]), 2)
        self.assertEqual(episode["production"][0]["credit"], "Buch")


if __name__ == "__main__":
    unittest.main()
