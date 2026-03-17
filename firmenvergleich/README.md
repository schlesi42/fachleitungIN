# Firmenvergleich - Mengenanalyse mit Fuzzy Matching

Dieses Projekt analysiert Firmenlisten aus drei Sparten und erstellt eine Mengenanalyse mit Schnittmengen und Venn-Diagrammen.

**NEU:** Das Tool erkennt jetzt auch ähnliche Firmennamen (z.B. "DB Station&Service AG" vs. "DB Station & Service AG") als Duplikate mit Fuzzy String Matching!

## Projektstruktur

```
firmenvergleich/
├── data/
│   └── Firmenvergleich.xlsx    # Input-Datei mit drei Spalten (Firmennamen)
├── results/                     # Output-Ordner (wird automatisch erstellt)
├── venv/                        # Virtuelle Python-Umgebung
├── requirements.txt             # Python-Dependencies
├── firmenvergleich_analyse.ipynb  # Hauptanalyseskript (Jupyter Notebook)
└── README.md                    # Diese Datei
```

## Installation

Die virtuelle Umgebung und alle Dependencies sind bereits eingerichtet.

Falls du sie neu einrichten möchtest:

```bash
cd firmenvergleich
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Verwendung

### 1. Virtuelle Umgebung aktivieren

```bash
cd firmenvergleich
source venv/bin/activate
```

### 2. Jupyter Notebook starten

```bash
jupyter notebook firmenvergleich_analyse.ipynb
```

Das Notebook öffnet sich in deinem Browser.

### 3. Notebook ausführen

Führe alle Zellen nacheinander aus (oder wähle "Run All" im Menü "Cell").

## Was das Notebook macht

1. **Daten einlesen**: Liest die Excel-Datei `data/Firmenvergleich.xlsx` ein
2. **Normalisierung**: Normalisiert Firmennamen (Leerzeichen, Groß-/Kleinschreibung)
3. **Duplikatserkennung innerhalb Sparten**: Findet ähnliche Firmennamen in jeder Sparte
4. **Cross-Matching zwischen Sparten**: Erkennt ähnliche Firmen über Sparten hinweg
5. **Mengenoperationen**: Berechnet
   - Schnittmenge aller drei Sparten
   - Schnittmengen von je zwei Sparten
   - Firmen, die nur in einer Sparte vorkommen
6. **Vergleich**: Zeigt Unterschiede zwischen exaktem und Fuzzy Matching
7. **Visualisierung**: Erstellt ein Venn-Diagramm
8. **Export**: Speichert Ergebnisse in `results/mengenanalyse_fuzzy_85.xlsx`

### Similarity Threshold

Der **Similarity Threshold** bestimmt, wie ähnlich zwei Firmennamen sein müssen, um als identisch zu gelten:
- **100%** = Exaktes Matching (alte Methode)
- **85-95%** = Empfohlen für Firmennamen mit kleinen Unterschieden
- **< 85%** = Sehr tolerant, aber mehr False Positives möglich

Du kannst den Threshold in Zelle 3 des Notebooks anpassen!

## Output

Das Notebook erstellt:
- **Venn-Diagramm**: Visuelle Darstellung der Schnittmengen
- **Detaillierte Listen**: Firmen in den verschiedenen Kategorien
- **Excel-Datei** (`results/mengenanalyse_fuzzy_85.xlsx`) mit:
  - Alle Schnittmengen und Differenzen
  - Gefundene Duplikate innerhalb der Sparten
  - Cross-Matches zwischen den Sparten (z.B. "DB Station&Service AG" ≈ "DB Station & Service")
  - Zusammenfassung mit allen Statistiken
  - Vergleich zwischen exaktem und Fuzzy Matching

## Hinweise

- Die erste Zeile der Excel-Datei wird als Überschrift verwendet
- Leere Zellen werden automatisch ignoriert
- Die Spaltennamen aus der Excel-Datei werden automatisch übernommen
- **Fuzzy Matching**: Ähnliche Firmennamen werden automatisch erkannt und gruppiert
  - Beispiel: "DB Station&Service AG" und "DB Station & Service AG" werden als identisch erkannt
  - Threshold ist auf 85% voreingestellt (anpassbar im Notebook)

## Dependencies

- **pandas**: Datenverarbeitung
- **openpyxl**: Excel-Dateien lesen/schreiben
- **matplotlib**: Plotting
- **matplotlib-venn**: Venn-Diagramme
- **rapidfuzz**: Fuzzy String Matching für ähnliche Firmennamen
- **jupyter**: Jupyter Notebook
- **notebook**: Notebook-Interface

## Beispiele für erkannte Duplikate

Das Fuzzy Matching erkennt z.B.:
- "DB Station&Service AG" ≈ "DB Station & Service AG"
- "Amazon Gera GmbH" (identisch in mehreren Sparten)
- "DACHSER SE Logistikzentrum Berlin Brandenbg" ≈ "Dachser SE-Logistikzentrum BB"
- Firmen mit unterschiedlichen Leerzeichen oder Sonderzeichen
