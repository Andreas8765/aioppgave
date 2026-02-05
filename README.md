# VLC Oppdaterings-Sjekker

Et program som overvåker VLC Media Player for nye oppdateringer og lagrer historikk i SQLite.

## Funktioner

- Sjekker automatisk for nye VLC-versjoner
- Lagrer oppdateringshistorikk i lokal SQLite-database
- Sender varsel når ny versjon er tilgjengelig
- Enkel CLI-grensesnitt

## Installasjon

```bash
pip install -r requirements.txt
```

## Bruk

```bash
python main.py
```

Eller for å sjekke omgående:

```bash
python main.py --check
```

## Konfigurering

Databasefilen opprett automatisk ved første kjøring i samme mappe som programmet.

## Lisens

MIT License - Se LICENSE-fil for detaljer.
