# Datenstand und Lückenbericht

Erzeugt am 2026-10-09. Der Bestand umfasst **243 reguläre Folgen**.

## Abdeckung

| Feld | vorhanden | fehlt | fehlende Folgen |
|---|---:|---:|---|
| Titel | 243 | 0 | – |
| Beschreibung | 243 | 0 | – |
| Sprecher | 243 | 0 | – |
| Produktionsdaten | 238 | 5 | 206, 216–217, 219, 237 |
| Erscheinungsjahr | 243 | 0 | – |
| Exaktes Erscheinungsdatum | 40 | 203 | 1–198, 200–204 |
| Laufzeit | 242 | 1 | 213 |
| Trackpunkte | 205 | 38 | 154, 207–243 |
| Ausgaben/EAN | 206 | 37 | 207–243 |

## Bekannte Lücken und Grenzen

- Komplett fehlende reguläre Folgen im Nummernbereich: **–**.
- Produktionscredits stammen für ältere Folgen überwiegend aus dem TKKG-Site-Archiv und ab Folge 207 aus offiziellen Detailseiten. Einzelne Quellseiten enthalten trotzdem keine Credits; die betroffenen Folgen stehen in der Tabelle.
- Exakte Veröffentlichungstage stammen ausschließlich aus den eingebundenen offiziellen Detailseiten (derzeit 199, 205–243). Das Archiv vermischt bei älteren Folgen Erst- und Wiederveröffentlichungen, weshalb daraus bewusst kein scheinbar exaktes Datum abgeleitet wird.
- Trackpunkte fehlen für Folge 154 bereits in der Archivquelle; ab Folge 207 wurden noch keine belastbaren Kapitel-/Tracklisten importiert.
- Die Beschreibungen sind Quelltexte Dritter und nicht von der MIT-Lizenz des Codes umfasst.
- Specials, TKKG Junior, Bücher, Filme, Coverdateien, Kapitel-Zeitstempel, Streaming-IDs und MusicBrainz-IDs sind noch nicht modelliert/importiert.
- Schreibweisen von Rollen und Personen werden quellengetreu übernommen; Pseudonyme und Alias-Normalisierung fehlen noch.
- Konflikte zwischen Quellen werden noch nicht als eigene Datensätze gespeichert; bei Sprecher-, Produktions-, Track- und Ausgabelisten hat das detailliertere TKKG-Site-Archiv Vorrang.

## Quellenbilanz

- `www.hoerspiel-request.de`: bei 242 Folgendatensätzen referenziert
- `www.tkkg-site.de`: bei 206 Folgendatensätzen referenziert
- `www.tkkg.de`: bei 40 Folgendatensätzen referenziert

## Sinnvolle nächste Schritte

1. Die in der Tabelle genannten Folgen ohne Produktionsdaten anhand offizieller Inlays oder einer ausdrücklich nutzbaren Quelle ergänzen.
2. Exakte Veröffentlichungstage und Streaming-IDs aus offiziellen Katalogen ergänzen.
3. Specials und TKKG Junior in getrennten Serien erfassen.
4. Personen- und Rollen-IDs samt Alias-Tabelle einführen, ohne abweichende Originalcredits zu verlieren.
5. Kapitel-Zeitstempel aus legal verfügbaren Medien oder MusicBrainz-Daten ergänzen.

Der Bericht wird mit `make report` bzw. bei jedem `make update` neu erzeugt.
