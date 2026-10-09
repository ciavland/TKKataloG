# tkkgmeta

Offene, maschinenlesbare Metadaten zur regulären TKKG-Hörspielserie –
inspiriert von [dreimetadaten](https://github.com/YourMJK/dreimetadaten).

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

## Aktualisieren

Python 3.9+ und Beautiful Soup werden benötigt:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
make update
make validate
make test
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

## Abgrenzung

Der erste Stand behandelt die reguläre Hörspielserie. Specials, TKKG Junior,
Bücher, Filme, Coverdateien, Streaming-IDs und exakte Veröffentlichungstage
sind als nächste Ausbaustufe vorgesehen. Details stehen in `REPORT.md`.

Bitte vor Weitergabe der Daten [DATA-LICENSE.md](DATA-LICENSE.md) lesen.
