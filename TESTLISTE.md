# Testliste

Ting som ikke er prøvd i microdata.no, eller som bygger på antakelser. Kryss av og skriv inn datalagerversjon og dato når en test er gjort.
Når en test avklarer noe, flytt konklusjonen til [`fallgruver.md`](skills/microdata-no/referanser/fallgruver.md) og endre teststatus i berørte snutter.

Prioritet: **P1** kan gi feil resultat uten at det synes, **P2** kan stoppe skriptet, **P3** er kvalitetssjekk.

Det som kan sjekkes uten microdata.no, er automatisert i [`tests/`](tests/) (`python -m unittest discover -s tests`). Listen her gjelder det som bare kan avklares ved å kjøre i microdata.no.

## 1. `recode`-oppførsel (avklarer flere verktøy samtidig)

Bruk ett lite skript med `import fdb/BEFOLKNING_KOMMNR_FORMELL 2024-01-01 as kommune` og `generate x = kommune`.

| # | Hva | Hvordan | Forventet | Pri |
|---|---|---|---|---|
| 1.1 | En sluttregel i **egen** `recode`-kommando overskriver tidligere omkodinger | `recode x ('0301' = 'A')`, deretter `recode x (* = 'B')`, `tabulate x` | Alt blir `B`. Bekrefter feilen som ble rettet i `regionomkoding.py` | P1 |
| 1.2 | Sluttregel som siste regel i **samme** kommando | `recode x ('0301' = 'A') (* = 'B')` | Oslo blir `A`, resten `B` | P1 |
| 1.3 | Lange `recode`-linjer: standard (opptil ca. 600 tegn), konfliktkommandoen i `klass.py kobling` (ca. 2 200 tegn for SN2002 → SN2007) og `--ukjent` (2 800–4 700 tegn) | `python verktoy/regionomkoding.py helseregioner` og `... --ukjent`, og `python verktoy/klass.py kobling 6 --dato 2005-01-01 --tabell "SN 2007" --navn naring` på `REGSYS_NARING_SN2002` | Godtas. Ellers: finn grensen og still inn `MAKS_TEGN` i `recode_regler.py` (konfliktkommandoen kan ikke deles) | P2 |
| 1.9 | Regler i samme kommando ser ikke hverandres resultat (grunnlaget for `recode_regler.py`) | `recode x ('0301' = '1103') ('1103' = '4601')`, `tabulate x` | Oslo blir `1103`, Stavanger `4601`. Blir Oslo `4601`, er verktøyenes antakelse feil | P1 |
| 1.4 | Samme merkelapp på flere regler (merkelappen står bare på første bit) | `recode x ('0301' = 'A' 'Oslo') ('1103' = 'A')`, `tabulate x` | Begge får merkelappen `Oslo`. Ellers: sett merkelapp på alle biter | P2 |
| 1.5 | ~~Teller 10-enhetsregelen per kommando eller per regel?~~ **Avklart (versjon 59, 2026-11):** per målverdi. Én liten regel stopper hele kommandoen. Se `fallgruver.md` | | | ✓ |
| 1.6 | `generate x = y` for en strengvariabel | `generate kommune_orig = kommune` | Kopi av strengen | P2 |
| 1.7 | `recode` med verdier som ikke finnes i variabelens kodeliste | `recode x ('0101' = 'A')` på 2024-data | Feil, advarsel eller ingen virkning? Styrer om verktøyene må begrenses til kodelisten | P2 |
| 1.8 | Merkelapper med spesialtegn (æøå, `/`, `-`) i strengrecode | `recode x ('0301' = 'A' 'Oslo/Bærum')` | Godtas | P3 |

## 2. Kommuneomkoding (`verktoy/kommuneomkoding.py`)

| # | Hva | Hvordan | Forventet | Pri |
|---|---|---|---|---|
| 2.1 | Utskriften kjører uten feil | Standard (1989 til 2024) på `BEFOLKNING_KOMMNR_FORMELL 2010-01-01` | Ingen feil, ingen avvisning | P2 |
| 2.2 | Ingen gamle koder igjen | `tabulate kommune` etter omkoding | Bare kommunenumre fra 2024, de delte kommunene som finnes i årgangen (0114, 0720, 1613, 1850, 5012) og spesialkodene, som står uendret: `-1`, `-2`, `0000`, `2100`–`2131` (Svalbard), `2500`, `9999`, `xxxx` og «ukjent kommune i fylket» (`xx00`, også gamle fylker som `3000` Viken, `3800` og `5400`). Andre koder er feil | P1 |
| 2.3 | Folketall per kommune stemmer | Sammenlign 1.1.2024 med Statistikkbanken (tabell 07459), og 1.1.2010 summert til 2024-kommuner | Samme tall (innen støy) | P1 |
| 2.4 | Ålesund-reverseringen | Folketall 1.1.2023 og 1.1.2024 for 1508 Ålesund og 1580 Haram | Ørskog, Skodje og Sandøy ligger i Ålesund etter omkoding, Haram i 1580 | P1 |
| 2.5 | `--til 2026` (Indre Østfold 3118 deles i 2026) | Kjør og sjekk kommentarene | Kodene som får 3118 som «fortsettelse» er riktige. Ellers: skarpere regel | P2 |
| 2.6 | Svalbard-kodene (2111, 2112, 2115, 2121, 2131) | `tabulate` på kodene i dataene | Finnes de, må de legges til for hånd | P3 |
| 2.7 | Kode som er både kilde og mål | Håndteres nå i koden (`recode_regler.py`) og testes i `tests/`. I microdata.no avhenger det av 1.9 | Se 1.9 | P3 |

## 3. Regionomkoding (`verktoy/regionomkoding.py`)

| # | Hva | Hvordan | Forventet | Pri |
|---|---|---|---|---|
| 3.1 | Standardutskrift (uten `--ukjent`) | `helseregioner`, `okonomiske_regioner`, `politidistrikt` på 2024-data | Alle 357 kommuner får region. Ellers står bare spesialkodene fra 2.2 igjen (og gamle kommunenumre hvis dataene ikke er omkodet først). Med `--ukjent` blir alt dette `xxxx` | P1 |
| 3.7 | Regionkode lik en kommunekode (`barnevernsregioner`, kode `0300`) | Kjør uten `--ukjent` og se advarselen | Personer med kommunekode `0300` havner i regionen `0300`. Med `--ukjent` får de `xxxx` | P2 |
| 3.2 | Merkelapper beholdes | `tabulate` av regionvariabelen | Regionnavn vises, ikke bare koder | P2 |
| 3.3 | Regionene stemmer med offisielle tall | Folketall per region mot Statistikkbanken, for to-tre inndelinger | Samme tall | P2 |
| 3.4 | Helseregioner oversatt fra Kommuneinndeling 2020 | Stikkprøve: Haram (1580), Indre Østfold (3118) | Haram i Helse Midt-Norge. Indre Østfold i Helse Sør-Øst | P3 |
| 3.5 | Bo- og arbeidsmarkedsregioner (manuell fil) | Sammenlign 10 kommuner mot TØI-rapporten | Samme region | P3 |
| 3.6 | Kommuner uten rad i tabellen | Sammenlign tabellens kommuner med 2024-listen | 357 kommuner dekket i hver tabell | P3 |

## 4. Klass-verktøyet (`verktoy/klass.py`)

| # | Hva | Hvordan | Forventet | Pri |
|---|---|---|---|---|
| 4.1 | Land til verdensdel | `grupper 545 --nivaa 2 --variabel BEFOLKNING_LANDBAK3GEN --navn landbak` på `BEFOLKNING_LANDBAK3GEN` | Kjører. Sammenlign fordelingen med `landbakgrunn_region.txt` | P1 |
| 4.2 | Landkodene er strenger | Kjør uten `destring` | Fungerer. Ellers: dokumenter | P2 |
| 4.3 | Land: koder som ikke finnes i Klass | Tell hvor mange personer som har en av de 42 kodene | Få, ellers må de håndteres for hånd | P2 |
| 4.4 | STYRK-08 til hovedgruppe | `grupper 7 --nivaa 1 --variabel REGSYS_ARB_YRKE_STYRK08` | `tabulate` viser hovedgruppene 0–9 og `XXXX` | P2 |
| 4.5 | SN2007 til seksjon og divisjon | `grupper 6 --nivaa 1 --dato 2024-01-01 --variabel REGSYS_NARING_SN2007` | Seksjon A–U. De 25 kodene som mangler i Klass: hvor mange personer? | P1 |
| 4.6 | NUS til nivå | `grupper 36 --nivaa 1 --variabel NUDB_BU` | Nivå 0–9. Sammenlign med `utdanningsniva.txt` | P1 |
| 4.7 | Koblingstabell NUS til ISCED | `kobling 36 --tabell "ISCED 2011 Attainment"` | Kjører. Koder som går til flere mål utelatt og listet | P3 |
| 4.8 | Historisk `--dato` mot gjeldende kodeliste | `--dato` før 2015 med `--variabel` | Mange koder «mangler». Avgjør om `klass.py` bør bruke kodelistehistorikken | P2 |
| 4.9 | SN2002 til SN2007 med koblingstabell | `kobling 6 --dato 2005-01-01 --tabell "SN 2007" --navn naring` på `REGSYS_NARING_SN2002` | Kjører (se 1.3 for linjelengden). Koder med flere mål (262) står uendret. Sammenlign fordelingen på seksjon med `REGSYS_NARING_SN2007` for samme år | P2 |

## 5. Kodesnutter

| # | Hva | Pri |
|---|---|---|
| 5.1 | **Gjort (versjon 59, 2026-11):** alle snuttene unntatt `lavinntekt_vedvarende.txt` kjørt frittstående med `samle_snutter.py`. Neste gang: kjør (se [`kodesnutter/README.md`](skills/microdata-no/kodesnutter/README.md)), og endre status fra «testet i større skript» til «testet» | P2 |
| 5.2 | `lavinntekt_vedvarende.txt` (utkast): kjør og sammenlign med SSBs tall | P1 |
| 5.4 | ~~Færre leiere i `bolig.txt` enn i SSB tabell 14897~~ **Avklart (versjon 59, 2026-11):** statistisk koblede husholdninger har anslått eierstatus med gammel metode (51,6 % eiere mot 13–15 % etter SSBs revisjon). Se `fallgruver.md` | ✓ |
| 5.3 | Se om `landbakgrunn_region.txt` kan erstattes av `klass.py grupper 545`, og om resultatet blir likt | P3 |

## 6. Henting og vedlikehold

| # | Hva | Hvordan | Forventet | Pri |
|---|---|---|---|---|
| 6.1 | Ukentlig workflow | Kjør «Oppdater metadata» manuelt (workflow_dispatch) | Pull request åpnes bare ved faktiske endringer | P2 |
| 6.2 | Delvis feilet henting | Simulert i `tests/test_hent_variabler.py` og `tests/test_hent_manual.py`. Se første gang det skjer i workflowen | Jobben feiler, og ingen PR åpnes | P3 |
| 6.3 | Ny datalagerversjon | Første ukentlige kjøring etter at microdata.no har fått ny versjon | Alle variabler hentes på nytt, `datalager.json` viser den nye versjonen, og PR-tittelen nevner den | P2 |
| 6.4 | `hent_kommuneendringer.py`, `hent_regioninndelinger.py` | Kjør på nytt på en annen maskin | Identiske filer (bortsett fra datoer) | P3 |
| 6.5 | `python -I` på macOS/Linux | Workflowen «Tester» kjører verktøyene på Ubuntu | Grønn kjøring (utviklet på Windows) | P3 |

## 7. Agentatferd (evaluering)

Sammenlign agentens svar med og uten skillen på disse oppgavene.

| # | Oppgave | Hva som måles |
|---|---|---|
| 7.1 | Variabel som ikke dekker perioden | Sjekker `fra`/`til` før skriptet skrives |
| 7.2 | Pseudonymisert ID | Bruker ikke ID-en direkte |
| 7.3 | Gamle kommunenumre | Bruker `kommuneomkoding.py`, melder om delte kommuner |
| 7.4 | Manglende verdier | Avslutter grupperinger med `sysmiss` |
| 7.5 | Feil statistikkopsjon | Retter og forklarer |
| 7.6 | Region fra kommune | Bruker `regionomkoding.py` uten sluttregel i egen kommando |
| 7.7 | Næring/yrke til grupper | Bruker `klass.py` og setter riktig `--dato` |
| 7.8 | Usikkerhet | Skiller mellom det som er kontrollert mot kildene, det som bygger på testet snutt, og det som må kjøres |
