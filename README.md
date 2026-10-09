# TKKataloG

Offene, maschinenlesbare Metadaten zur regulären TKKG-Hörspielserie – mit
durchsuchbarer Website und statischer JSON-API, inspiriert von
[dreimetadaten](https://github.com/YourMJK/dreimetadaten).

- Website: <https://ciavland.github.io/TKKataloG/>
- API-Dokumentation: <https://ciavland.github.io/TKKataloG/api/>
- OpenAPI: <https://ciavland.github.io/TKKataloG/api/openapi.json>

Der aktuelle Import enthält die regulären Folgen 1–243, soweit sie in den
Quellen vorhanden sind. Im Mittelpunkt stehen Beschreibung, Sprechrollen und
Produktionsdaten. Jede Angabe bleibt über `sources` auf ihre Herkunft
zurückführbar.

## Daten

- `data/episodes/NNN.json`: ein gut diffbarer Datensatz pro Folge
- `data/all.json`: alle Folgen als bequem konsumierbare Gesamtausgabe
- `data/index.csv`: flacher Index für Tabellenprogramme
- `REPORT.md`: automatisch erzeugter Vollständigkeits- und Lückenbericht
- `schema/episode.schema.json`: JSON Schema der Einzelfolgen

Wichtige Felder sind `description`, `cast`, `production`, `tracks`,
`release_year`, `duration_seconds`, `editions` und `sources`. Ein fehlendes Feld
wird nicht geraten, sondern als `null` bzw. leere Liste gespeichert und im
Bericht ausgewiesen.

## API

Die API ist vollständig statisch und wird bei jedem Build aus `data/` erzeugt.
Sie braucht keinen API-Key und eignet sich für Browser, Apps und statische
Websites:

```text
GET /api/v1/episodes.json
GET /api/v1/episodes/index.json
GET /api/v1/episodes/001.json
GET /api/v1/status.json
```

Beispiel:

```js
const response = await fetch(
  "https://ciavland.github.io/TKKataloG/api/v1/episodes/001.json"
);
const episode = await response.json();
```

Für reproduzierbare Builds kann statt `main` ein Release-Tag über jsDelivr
verwendet werden:

```text
https://cdn.jsdelivr.net/gh/ciavland/TKKataloG@v1.0.0/data/all.json
```

`/api/v1/` bleibt rückwärtskompatibel. Brechende Schemaänderungen erhalten
eine neue Hauptversion.

## Aktualisieren

Python 3.9+ und Beautiful Soup werden benötigt:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
make update
make validate
make test
make build
make serve
```

`scripts/update.py` lädt die Übersichtsseite von Hörspiel-Request, bis zu 206
Archivseiten von TKKG-Site.de sowie offizielle Detailseiten für die neueren
Folgen. Antworten werden in `.cache/` gespeichert;
`--refresh` erzwingt einen neuen Abruf. Nützliche Optionen:

```sh
python3 scripts/update.py --help
python3 scripts/update.py --offline   # nur vorhandenen Cache auswerten
python3 scripts/update.py --workers 4 # schonendere Parallelität
```

Die erzeugten Dateien sind deterministisch sortiert. `make validate` prüft
Nummern, Pflichtfelder, Quellen, Dubletten und abgeleitete Ausgaben.

## Veröffentlichung

`.github/workflows/pages.yml` validiert Daten und Parser, baut Website und API
und veröffentlicht `dist/` automatisch auf GitHub Pages. Die Website selbst
ist buildloses, responsives HTML/CSS/JavaScript; es gibt keine
Laufzeit-Abhängigkeiten, kein Tracking und kein serverseitiges Backend.

## Abgrenzung

Der erste Stand behandelt die reguläre Hörspielserie. Specials, TKKG Junior,
Bücher, Filme, Coverdateien, Streaming-IDs und exakte Veröffentlichungstage
sind als nächste Ausbaustufe vorgesehen. Details stehen in `REPORT.md`.

Bitte vor Weitergabe der Daten [DATA-LICENSE.md](DATA-LICENSE.md) lesen.
