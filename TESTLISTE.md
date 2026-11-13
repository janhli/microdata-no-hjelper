# Testliste

Ting som ikke er prøvd i microdata.no, eller som bygger på antakelser. Kryss av og skriv inn datalagerversjon og dato når en test er gjort.
Når en test avklarer noe, flytt konklusjonen til [`fallgruver.md`](skills/microdata-no/referanser/fallgruver.md) og endre teststatus i berørte snutter.

Prioritet: **P1** kan gi feil resultat uten at det synes, **P2** kan stoppe skriptet, **P3** er kvalitetssjekk.

Det som kan sjekkes uten microdata.no, er automatisert i [`tests/`](tests/) (`python -m unittest discover -s tests`). Listen her gjelder det som bare kan avklares ved å kjøre i microdata.no.

## 1. `recode`-oppførsel (avklarer flere verktøy samtidig)

Bruk ett lite skript med `import fdb/BEFOLKNING_KOMMNR_FORMELL 2024-01-01 as kommune` og `generate x = kommune`.

| # | Hva | Hvordan | Forventet | Pri |
|---|---|---|---|---|
| 1.1 | ~~Sluttregel i egen `recode`-kommando~~ **Avklart (versjon 59, 2026-11):** overskriver alt, også det som er omkodet før | | | ✓ |
| 1.2 | ~~Sluttregel sist i samme kommando~~ **Avklart (versjon 59, 2026-11):** Oslo A, resten B, som forventet | | | ✓ |
| 1.3 | ~~Lange `recode`-linjer~~ **Avklart (versjon 59, 2026-11):** 2 789 tegn (`--ukjent`) og 2 161 tegn (SN-kobling) godtas. SN-koblingen ble stoppet av 10-enhetsregelen (målkode 17.240), ikke av lengden. Se 1.10 | | | ✓ |
| 1.9 | ~~Regler i samme kommando ser ikke hverandres resultat~~ **Avklart (versjon 59, 2026-11):** Oslo → 1103, Stavanger → 4601, Bergen uendret. Antakelsen i `recode_regler.py` stemmer | | | ✓ |
| 1.4 | ~~Samme merkelapp på flere regler~~ **Avklart (versjon 59, 2026-11):** merkelappen på første regel gjelder også de andre med samme mål | | | ✓ |
| 1.5 | ~~Teller 10-enhetsregelen per kommando eller per regel?~~ **Avklart (versjon 59, 2026-11):** per målverdi. Én liten regel stopper hele kommandoen. Se `fallgruver.md` | | | ✓ |
| 1.6 | ~~`generate x = y` for streng~~ **Avklart (versjon 59, 2026-11):** gir en kopi | | | ✓ |
| 1.7 | ~~`recode` med koder som ikke finnes i dataene~~ **Avklart (versjon 59, 2026-11):** ingen virkning, ingen feil. Regler som treffer 0 enheter stoppes ikke | | | ✓ |
| 1.8 | ~~Spesialtegn i merkelapp~~ **Avklart (versjon 59, 2026-11):** «Oslo/Bærum – æøå» vises riktig | | | ✓ |
| 1.10 | ~~Detaljerte koblinger stoppes av 10-enhetsregelen~~ **Avklart (versjon 59, 2026-11):** `klass.py --utelat` virker. SN2002 → SN2007 gikk gjennom i runde 3, med 33 målkoder tatt ut (beregnet fra `tabulate` på kildekodene). Men 42 % av sysselsatte står igjen med SN2002-kode fordi kodene har flere mål. Se 1.11 | | | ✓ |
| 1.11 | ~~`klass.py kobling --nivaa N`~~ **Avklart (versjon 59, 2026-11):** SN2002 → SN2007 for november 2007 omkoder 91,0 % på nivå 1 (seksjon) og 82,6 % på nivå 2 (divisjon). Nivå 1 gikk gjennom uten `--utelat`, nivå 2 trengte `--utelat 30`. Fordelingen på seksjon ligner ekte SN2007 (2008), med avvik på +0,1 til −1,7 prosentpoeng, størst for N og O | | | ✓ |
| 1.12 | ~~`klass.py grupper` for koder som mangler i Klass~~ **Avklart (versjon 59, 2026-11):** `grupper` går nå opp i hierarkiet via prefiks (43.220 → 43.22 → F). `REGSYS_NARING_SN2007` for november 2008 ble gruppert fullt ut (før: 1,2 % ugruppert). Seksjon F +19 244 | | | ✓ |

## 2. Kommuneomkoding (`verktoy/kommuneomkoding.py`)

| # | Hva | Hvordan | Forventet | Pri |
|---|---|---|---|---|
| 2.1 | ~~Utskriften kjører uten feil~~ **Avklart (versjon 59, 2026-11):** kjørt på 1.1. i 1995, 2010, 2019, 2023 og 2024 uten feil eller avvisning | | | ✓ |
| 2.2 | ~~Ingen gamle koder igjen~~ **Avklart (versjon 59, 2026-11):** bare delte kommuner står igjen (1995: 0720, 1613, 1850. 2010: 0720, 1613, 1850. 2019: 1850, 5012) og 14 personer med 9999 i 1995. 2023 og 2024: alle i 2024-kommuner | | | ✓ |
| 2.3 | ~~Folketall per kommune stemmer~~ **Avklart (versjon 59, 2026-11):** alle 357 kommuner innenfor ±5 av tabell 07459, både 1.1.2024 og 1.1.2010 summert til 2024-kommuner (det er støyen) | | | ✓ |
| 2.4 | ~~Ålesund-reverseringen~~ **Avklart (versjon 59, 2026-11):** 2019-koder blir riktige (Haram 1534 → 1580, de andre → 1508). Men 1507 Ålesund (2020–2023) går helt til 1508, også Haram: 67 525 i 1508 for 2023 mot 58 511 + 9 358 i 2024. Verktøyet varsler nå om koder som selv ble delt. Se `fallgruver.md` | | | ✓ |
| 2.5 | ~~`--til 2026` (Indre Østfold 3118)~~ **Avklart (versjon 59, 2026-11):** 2026-endringen er en grensejustering (små deler til Nordre Follo og Vestby). At 0122–0125, 0138 og 3014 får 3118 er riktig. Avklart fra Klass, uten kjøring | | | ✓ |
| 2.6 | ~~Svalbard-kodene~~ **Avklart (versjon 59, 2026-11):** ingen personer har dem i 1995, 2010, 2019, 2023 eller 2024 | | | ✓ |
| 2.8 | ~~Merkelapper på omkodede koder~~ **Avklart (versjon 59, 2026-11):** `kommuneomkoding.py` gir målkodene navnet i inndelingen det omkodes til. 1.1.2010 omkodet: alle rader har navn (1108 Sandnes, 3101 Halden, 5055 Heim), samme tall som før. Koder som ikke omkodes, beholder navnet fra datoen (1826 Hattfjelldal) | | | ✓ |
| 2.7 | ~~Kode som er både kilde og mål~~ **Avklart (versjon 59, 2026-11):** håndteres i `recode_regler.py`, og 1.9 bekrefter at det virker i microdata.no | | | ✓ |

## 3. Regionomkoding (`verktoy/regionomkoding.py`)

| # | Hva | Hvordan | Forventet | Pri |
|---|---|---|---|---|
| 3.1 | ~~Standardutskrift (uten `--ukjent`)~~ **Avklart (versjon 59, 2026-11):** helseregioner, politidistrikt, barnevernsregioner og økonomiske regioner på 2024-data: alle personer fikk region, ingen koder står igjen | | | ✓ |
| 3.7 | ~~Regionkode lik en kommunekode (`0300`)~~ **Avklart (versjon 59, 2026-11):** ingen personer har kommunekode 0300 i 2024, så regionen 0300 Oslo inneholder bare Oslo. Advarselen beholdes | | | ✓ |
| 3.2 | ~~Merkelapper beholdes~~ **Avklart (versjon 59, 2026-11):** regionnavn vises for alle fire inndelinger | | | ✓ |
| 3.3 | ~~Regionene stemmer med offisielle tall~~ **Avklart (versjon 59, 2026-11):** regionene er summer av kommuner, og kommunetallene stemmer med 07459 (2.3). Helseregioner, politidistrikt og barnevern summerer til samme total | | | ✓ |
| 3.4 | ~~Helseregioner oversatt fra Kommuneinndeling 2020~~ **Avklart (versjon 59, 2026-11):** Haram og Ålesund i Midt-Norge, Indre Østfold i Sør-Øst (sjekket i tabellen) | | | ✓ |
| 3.5 | ~~Bo- og arbeidsmarkedsregioner (manuell fil)~~ **Avklart (2026-11):** alle 357 kommuner sammenlignet med regnearket `baregioner_2020.xlsx` fra regjeringen.no (omkodet 2020 → 2024, Haram i Ålesund-regionen). Samme region for alle. Avklart uten microdata.no | | | ✓ |
| 3.6 | ~~Kommuner uten rad i tabellen~~ **Avklart (versjon 59, 2026-11):** alle elleve tabeller har de samme 357 kommunene | | | ✓ |

## 4. Klass-verktøyet (`verktoy/klass.py`)

| # | Hva | Hvordan | Forventet | Pri |
|---|---|---|---|---|
| 4.1 | ~~Land til verdensdel~~ **Avklart (versjon 59, 2026-11):** `grupper 545` nivå 1 og 2 kjører på 1.1.2025. Statsløs og uoppgitt (V9, V91, V92) må tas ut med `--utelat`, ellers stoppes de av 10-enhetsregelen. Mot snutten: samme tall, unntatt Kypros (Europa i Klass, Asia i snutten, 613) og Bermuda/Saint-Pierre (Nord-Amerika i Klass) | | | ✓ |
| 4.2 | ~~Landkodene er strenger~~ **Avklart (versjon 59, 2026-11):** virker uten `destring` | | | ✓ |
| 4.3 | ~~Land: koder som ikke finnes i Klass~~ **Avklart (versjon 59, 2026-11):** ingen synlige personer med de 42 kodene (bare 656 uten landbakgrunn) | | | ✓ |
| 4.4 | ~~STYRK-08 til hovedgruppe~~ **Avklart (versjon 59, 2026-11):** 0–9 for 16.11.2024. `XXXX` forekommer ikke. Gruppe 0 (militære og uoppgitt) er 1,5 mill. | | | ✓ |
| 4.5 | ~~SN2007 til seksjon~~ **Avklart (versjon 59, 2026-11):** A–U for 16.11.2014, alt gruppert via prefiks. Uoppgitt vises som `00` (784), ikke `00.000` | | | ✓ |
| 4.6 | ~~NUS til nivå~~ **Avklart (versjon 59, 2026-11):** nivå = første siffer for alle. 8 NUS-koder (106 personer) fantes i dataene, men ikke i kodelisten eller i Klass 2024-01. `grupper` tar nå med detaljkoder fra Klass som mangler i kodelisten, og med standarddato (i dag) kommer de med. Kjørt på nytt: bare diagonalen | | | ✓ |
| 4.7 | ~~Koblingstabell NUS til ISCED~~ **Avklart (versjon 59, 2026-11):** kjører uten stopp, ingen koder med flere mål. Målnavnene var tvetydige (fem «Not further defined»). `kobling` gir nå like navn navnene over i hierarkiet | | | ✓ |
| 4.8 | ~~Historisk `--dato` mot gjeldende kodeliste~~ **Avklart (versjon 59, 2026-11):** løst med prefiks-oppslaget (1.12): NUS med dato 2010 grupperer 1 555 koder via overordnet kode, SN2007 med 2009 24 koder. Klass 545 har ingen koder i 2010 og gir tydelig feil. Avklart uten kjøring | | | ✓ |
| 4.9 | ~~SN2002 til SN2007 med koblingstabell~~ **Avklart (versjon 59, 2026-11):** se 1.10 og 1.11 | | | ✓ |

## 5. Kodesnutter

| # | Hva | Pri |
|---|---|---|
| 5.1 | ~~Kjør alle snuttene frittstående~~ **Avklart (versjon 59, 2026-11):** alle 15 er kjørt frittstående med `samle_snutter.py`, `lavinntekt_vedvarende.txt` for seg (5.2). Alle har status «testet». Resultatene står i [`kodesnutter/TESTRESULTATER.md`](skills/microdata-no/kodesnutter/TESTRESULTATER.md) | ✓ |
| 5.2 | ~~`lavinntekt_vedvarende.txt`: sammenlign med SSBs tall~~ **Avklart (versjon 59, 2026-11):** 2021–2023 mot tabell 09571. Krav om privathusholdning bare siste år traff best: 10,0 % mot 9,9 % for barn under 18, Oslo 13,6 mot 13,8, alle fylker innen 0,3 prosentpoeng. Alle tre år: 9,8 (Oslo 13,3). Uten krav: 10,1 (Oslo 13,9). Snutten bruker nå siste år. Hele befolkningen mot 04204 («studenter er utelatt»): 9,6 mot 9,5 % (2022–2024) og 9,5 mot 9,2 (2021–2023), antall personer innen 0,2 %. Kommunal median lagt til og kjørt. KPI-tallene for 2023 og 2024 var feil, og er rettet | ✓ |
| 5.4 | ~~Færre leiere i `bolig.txt` enn i SSB tabell 14897~~ **Avklart (versjon 59, 2026-11):** statistisk koblede husholdninger har anslått eierstatus med gammel metode (51,6 % eiere mot 13–15 % etter SSBs revisjon). Se `fallgruver.md` | ✓ |
| 5.3 | ~~Kan `landbakgrunn_region.txt` erstattes av `klass.py grupper 545`?~~ **Avklart (versjon 59, 2026-11):** nei. Snutten skiller EU/EØS fra resten av Europa, det gjør ikke Klass 545. Snutten følger nå Klass for verdensdel (Kypros, Bermuda, Saint-Pierre), og EU/EØS-listen er rettet (Sveits, Grønland, Færøyene, Gibraltar og småstatene var med, Kypros manglet). Kontrollert mot Klass uten avvik. Må kjøres på nytt (5.5) | ✓ |
| 5.5 | ~~Kjør `landbakgrunn_region.txt` etter endringen av EU/EØS-listen~~ **Avklart (versjon 59, 2026-11):** hver gruppe ligger innenfor sin Klass-region (Grønland og Færøyene, 4 367, er Norden i Klass og Europa utenom EU/EØS i snutten). EU/EØS 710 473 | ✓ |

## 6. Henting og vedlikehold

| # | Hva | Hvordan | Forventet | Pri |
|---|---|---|---|---|
| 6.1 | Ukentlig workflow | Kjør «Oppdater metadata» manuelt (workflow_dispatch) | Pull request åpnes bare ved faktiske endringer | P2 |
| 6.2 | Delvis feilet henting | Simulert i `tests/test_hent_variabler.py` og `tests/test_hent_manual.py`. Se første gang det skjer i workflowen | Jobben feiler, og ingen PR åpnes | P3 |
| 6.3 | Ny datalagerversjon | Første ukentlige kjøring etter at microdata.no har fått ny versjon | Alle variabler hentes på nytt, `datalager.json` viser den nye versjonen, og PR-tittelen nevner den | P2 |
| 6.4 | `hent_kommuneendringer.py`, `hent_regioninndelinger.py` | Kjør på nytt på en annen maskin | Identiske filer (bortsett fra datoer) | P3 |
| 6.5 | ~~`python -I` på macOS/Linux~~ **Avklart for Linux (2026-11):** «Tester» kjører verktøyene med `python -I` (`tests/hjelp.py`) på `ubuntu-latest`, grønt på `main` siden 2026-11-10. macOS er ikke testet | | | ✓ |

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
