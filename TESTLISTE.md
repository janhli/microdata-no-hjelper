# Testliste

Ting som ikke er prøvd i microdata.no, eller som bygger på antakelser. Kryss av og skriv inn datalagerversjon og dato når en test er gjort.
Når en test avklarer noe, flytt konklusjonen til [`fallgruver.md`](skills/microdata-no/referanser/fallgruver.md) og endre teststatus i berørte snutter.

Prioritet: **P1** kan gi feil resultat uten at det synes, **P2** kan stoppe skriptet, **P3** er kvalitetssjekk.

Det som kan sjekkes uten microdata.no, er automatisert i [`tests/`](tests/) (`python -m unittest discover -s tests`). Listen her gjelder det som bare kan avklares ved å kjøre i microdata.no.

## 1. `recode`-oppførsel (avklarer flere verktøy samtidig)

Bruk ett lite skript med `import fdb/BEFOLKNING_KOMMNR_FORMELL 2024-01-01 as kommune` og `generate x = kommune`.

Punktene er avklart med versjon 1 av anonymiseringstiltakene. 1.5 og 1.10 (og 4.1 om `V9`) gjaldt regelen om
minst 10 enheter (tiltak 6), som er fjernet i versjon 2 (17. november 2026). Bekreftet i 1.13.

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
| 1.13 | ~~`recode` som treffer 1–9 enheter (versjon 2)~~ **Avklart (versjon 60, 2026-11-19):** `recode lb ('990' = '9')` på `BEFOLKNING_LANDBAK3GEN` godtas, uten «påvirker for få enheter». Kategori 9 vises ikke i tabellen (totalen er 3 høyere enn `000`). `--utelat` trengs bare med `configure confidentiality v1` | | | ✓ |

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
| 2.9 | ~~`--grunnkrets`: delte kommuner fordelt etter grunnkrets~~ **Avklart (versjon 60, 2026-11-23):** virker. Bosatte året før delingen fordelt med verktøyet, mot faktisk kommune året etter: Stokke 2016 → Tønsberg 93 % og Sandefjord 96 % riktig, Tysfjord og Snillfjord 88–98 %, Ålesund 2023 → Haram 8 940 av 9 252 (97 %). Resten ser ut som flytting. Hele landet 2015 → 2024 ble godtatt. Gjenstår: de to delte grunnkretsene i Stokke har 13 % av befolkningen (1 534, delt likt på Tønsberg og Sandefjord), Snillfjord 31, Tysfjord 11. 1580 fikk ikke navn fra 2023 (se 2.10). Skript: [`del2_9_grunnkrets_kommune.txt`](.claude/skills/vedlikehold/testskript/del2_9_grunnkrets_kommune.txt) | | | ✓ |
| 2.10 | ~~Navn på koder som ikke fantes i kodelisten~~ **Avklart (versjon 60, 2026-11-23):** `recode kommune ('1580' = '1580' 'Haram')` ga «1580 - Haram» både etter og før `replace` (før: ingen hadde verdien ennå). `kommuneomkoding.py --grunnkrets` lager regelen. C00 Leppe med `kreftregisteret.py --topografi`: 90 (rapporten 89), C44 3 061 (3 063). Skript: [`del2_10_navn_nye_koder.txt`](.claude/skills/vedlikehold/testskript/del2_10_navn_nye_koder.txt) | | | ✓ |

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
| 5.6 | ~~Kjør snuttene på nytt med versjon 60~~ **Avklart (versjon 60, 2026-11-19):** alle 14 kjørt uten feil (`testskript/del5_6_snutter.txt` og `del5_6_lavinntekt_vedvarende.txt`), med de samme tallene som versjon 59 innen støyen. Kommunal median i `lavinntekt_vedvarende.txt` er nå kontrollert mot FHI (nøkkeltall 403): fylkene innen 0,25 prosentpoeng, storbyene opptil 0,5 over. Statuslinjer og `require` er oppdatert. `sektor_lonnstakere.txt` er utgått og beholdes som dokumentasjon | ✓ |
| 5.5 | ~~Kjør `landbakgrunn_region.txt` etter endringen av EU/EØS-listen~~ **Avklart (versjon 59, 2026-11):** hver gruppe ligger innenfor sin Klass-region (Grønland og Færøyene, 4 367, er Norden i Klass og Europa utenom EU/EØS i snutten). EU/EØS 710 473 | ✓ |
| 5.7 | ~~Vedvarende lavinntekt, kommunal median: storbyene over FHI 403~~ **Avklart (versjon 60, 2026-11-23):** grensen i snutten er riktig: for alle aldre treffer den FHI innen 0,2 prosentpoeng (Oslo 14,5 mot 14,4, landet 9,6 mot 9,6), også 18–24 år. Median over husholdninger, studenthusholdninger i medianen, privathusholdning alle tre år og bosted 1.1.2024 bommer eller endrer ingenting. Avviket for barn i storbyene (opptil 0,5) ligger i tellingen av barn. 75+ ligger 0,5–1,4 over (trolig institusjonsbeboere, ikke undersøkt). Fasit hentet fra FHIs åpne API (nokkel/Table/403). Se `kodesnutter/TESTRESULTATER.md`. Skript: `del5_7_…`, `del5_7b_…`, `del5_7c_lavinntekt_aldre.txt` | | | ✓ |
| 5.8 | ~~Kjør `neet.txt` (ny snutt)~~ **Avklart (versjon 60, 2026-11-23):** 102 977 NEET mot SSB 102 976. Ledige, AAP/uføre og «andre» innen ±3, alder, kjønn, alle fylker og innvandrere/resten innen 0,1 prosentpoeng. Dagpenger og sykepenger er NEET, tiltakspenger og introduksjonsprogram ikke. Utdanningsnivå fra `NUDB_BU` treffer ikke 12423: 104 911 med uoppgitt utdanning mot 7 417 hos SSB, som har fordelt dem på nivåene (de fleste på grunnskole). Se `kodesnutter/TESTRESULTATER.md` | ✓ |

## 6. Henting og vedlikehold

| # | Hva | Hvordan | Forventet | Pri |
|---|---|---|---|---|
| 6.1 | ~~Ukentlig workflow~~ **Avklart (2026-11-17):** manuell kjøring etter rettelsene ga «Ingen endringer» og ingen PR (27 min). To feil ble funnet underveis og rettet: CSV-ene ble skrevet med `\r\n` og så endret ut for `git status` (PR med bare ny dato), og FHI-variablene i listen ga 404 under `no.ssb.fdb` og fikk jobben til å gå ut på tid. Andre datalagre hoppes nå over (#11) | | | ✓ |
| 6.2 | Delvis feilet henting | Simulert i `tests/test_hent_variabler.py` og `tests/test_hent_manual.py`. Se første gang det skjer i workflowen | Jobben feiler, og ingen PR åpnes | P3 |
| 6.3 | ~~Ny datalagerversjon~~ **Avklart (versjon 60, 2026-11-18):** den ukentlige kjøringen lagde PR #12 «Oppdater metadata fra microdata.no (versjon 60, 2026-11-18)». Alle 730 variablene i `no.ssb.fdb` ble hentet på nytt (oppdatert dekning), `BEFOLKNING_GRUNNKRETS` kom til og `ARBLONN_FRTK_SEKTOR_2014` ble fjernet. `datalager.json` og `VERSJON` viser 60. De 42 FHI-variablene sto uendret, fordi versjonen av deres datalagre ikke var ny | | | ✓ |
| 6.4 | ~~`hent_kommuneendringer.py`, `hent_regioninndelinger.py` på nytt~~ **Avklart (2026-11-20):** kjørt på nytt (Windows, 11 dager etter forrige henting). Eneste endring var hentedatoen i `kommuneendringer.json` og `regioner/HENTET`. Alle 11 regiontabellene ble like (357 kommuner hver), og datoendringene ble ikke committet | | | ✓ |
| 6.5 | ~~`python -I` på macOS/Linux~~ **Avklart for Linux (2026-11):** «Tester» kjører verktøyene med `python -I` (`tests/hjelp.py`) på `ubuntu-latest`, grønt på `main` siden 2026-11-10. macOS er ikke testet | | | ✓ |

## 7. Agentatferd (evaluering)

Sammenlign agentens svar med og uten skillen på disse oppgavene. Oppgavetekster og kriterier ligger i
[`evals/`](evals/README.md) (én mappe per oppgave, 2026-11-20).

**Runde 1 (2026-11-20, 7.1–7.13 og 7.15–7.18, én kjøring hver):** med skill 50/53 (94 %), uten 34/53 (64 %), aldri
dårligere med skill. Størst forskjell på verktøy, metadata (dekning, versjon) og fallgruver som bare står i skillen
(7.1, 7.4, 7.7, 7.15). Ingen forskjell på generell metode (7.11–7.13). Hull funnet og rettet: inntektsgrupper med
manglende beløp, `sd` i stedet for `std`, næring finnes ikke etter 2019 (oppgave 7.7 skrevet om). `i.` på
tekstvariabler virker (8.15). Detaljer: [`evals/resultater/runde1.md`](evals/resultater/runde1.md).

**7.14 (2026-11-23):** Codex og Copilot CLI fant skillen via `~/.agents/skills` og lastet den på oppgaven. Codex oppfylte kriteriene på 7.3 og 7.7 (ett delvis), Copilot fikk 4/4 og 2/3 (skrev om `klass.py`-reglene for hånd). Cursor er ikke kjørt. Detaljer: [`evals/resultater/7_14_andre_agenter.md`](evals/resultater/7_14_andre_agenter.md).

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
| 7.9 | Ja/nei-utfall | Velger `logit`/`probit`, lager utfallet som 0/1 med eksplisitt håndtering av `sysmiss`, og bruker `mfx(dydx)` eller `or` når effekten skal tolkes |
| 7.10 | Faktorvariabler og standardfeil | Bruker `i.` for kategorier, `cluster()` når enhetene er gruppert (ikke sammen med `robust`), og forklarer valget |
| 7.11 | Tid til hendelse | Lager populasjonen av alle i risiko, sensurerer ved død og utvandring, og tolker `cox` som hazard |
| 7.12 | Diff-in-diff | Lager etter-dummyen for alle enheter, ikke bare behandlingsgruppen, og nevner forutsetningen om parallelle trender |
| 7.13 | Instrumentvariabel | Skriver `( endogen = instrument )` riktig vei og drøfter om instrumentet er gyldig |
| 7.14 | Andre agenter (Copilot, Codex, Cursor) | Skillen lenket til `~/.agents/skills/microdata-no` som i README: finnes med `/skills`, lastes ved en microdata.no-oppgave, finner `variabler.csv` og `fallgruver.md`, og kjører `verktoy/klass.py`. Oppgave 7.3 og 7.7 gir samme type svar som i Claude |
| 7.15 | Sjeldent utfall (død i 2025, 25–66 år) | Advarer om at `logit` gir meningsløse tall under 1 %, foreslår `cox` eller avgrensning, viser andelen med antall |
| 7.16 | Andregradsledd | Lager `alder2` med `generate`, ikke `c.alder#c.alder` |
| 7.17 | Sjelden gruppe som forklaringsvariabel (Eritrea) | Ser at gruppen er under 1 %, bruker `i.x` |
| 7.18 | Bydel | Bruker `BEFOLKNING_BYDEL`, ikke omkoding fra grunnkrets |

## 8. Analyse (fra manualen, ikke kjørt)

Antakelser i «Analyse» i [`fallgruver.md`](skills/microdata-no/referanser/fallgruver.md). Kan samles i ett skript
på en populasjon over 100 000 (f.eks. bosatte 30–60 år). Skriptet for 8.1–8.5 og 8.7–8.9 ligger i
[`.claude/skills/vedlikehold/testskript/del8_analyse.txt`](.claude/skills/vedlikehold/testskript/del8_analyse.txt) (kjørt 2026-11-18, versjon 60).

| # | Hva | Hvordan | Forventet | Pri |
|---|---|---|---|---|
| 8.1 | ~~Manglende verdier i regresjoner~~ **Avklart (versjon 60, 2026-11-18):** listevis. N i `regress lonn mann utd1` var 1 888 890, lik antallet uten manglende lønn og utdanning | | | ✓ |
| 8.2 | ~~Dummy fra sammenligning med `sysmiss`~~ **Avklart (versjon 60, 2026-11-18):** `x > 5` gir 0, `x != 2` gir 1, og `replace ... if x > 5` endrer ingenting når x mangler. Ikke som Stata. Se `fallgruver.md` | | | ✓ |
| 8.3 | ~~Regresjoner winsoriseres (versjon 2)~~ **Avklart (versjon 60, 2026-11-18):** regresjonen avvek under 1 % fra gruppegjennomsnittene i tabellen (winsorisert på hele utvalget) | | | ✓ |
| 8.4 | ~~Kategorisk variabel med grupper under 5 fjernes (tiltak 14)~~ **Avklart (versjon 60, 2026-11-18):** hele `i.kommune` fjernet, med melding under tabellen, og regresjonen kjørt med resten (N 16 976 av 20 000). Se `fallgruver.md` | | | ✓ |
| 8.5 | ~~`regress-panel-diff` mot `regress-panel ... gruppe##etter, pooled`~~ **Avklart (versjon 60, 2026-11-18):** −4 159 mot −4 156 (forskjellen er nedsampling). Variabel 3 er etter-perioden for alle. Se `fallgruver.md` | | | ✓ |
| 8.6 | ~~Sensurering i overlevelsesanalyse~~ **Avklart (versjon 60, 2026-11-19):** bosatte 70+ 1.1.2016 (575 859), fulgt til 1.1.2026. 4,6 % av innvandrerne og 0,1 % av de andre utvandret. Av dem som utvandret, hadde 11 % av innvandrerne og 28 % av de andre en dødsdato i perioden. Sensurering ga 277 færre dødsfall, og snittiden for innvandrere sank fra 2 890 til 2 802 dager (andre: −2 dager). `cox`-koeffisienten for innvandrer gikk fra −0,242 til −0,209 (3 standardfeil). Se `fallgruver.md`. Skript: `testskript/del8_6_sensurering.txt` | | | ✓ |
| 8.7 | ~~`mfx(dydx)` for en 0/1-variabel~~ **Avklart (versjon 60, 2026-11-18):** gir den deriverte, ikke diskret endring. Se `fallgruver.md` | | | ✓ |
| 8.10 | ~~Dato i ÅÅÅÅMMDD til dager~~ **Avklart (2026-11-18):** `int()` og `date()` virker: dødsdato 19 380–20 436, tid fra diagnose til død 0–971 dager, ingen negative | | | ✓ |
| 8.9 | ~~Minst to koeffisienter (tiltak 17)~~ **Avklart (versjon 60, 2026-11-18):** stoppes med «Regresjonsmodellen har for få forklaringsvariabler/koeffisienter. Nedre grense er to koeffisienter.» | | | ✓ |
| 8.11 | ~~Vises `c.x#c.x` i resultatet?~~ **Avklart (versjon 60, 2026-11-19):** nei, og leddet er heller ikke med i modellen. Med `c.alder#c.alder` var log-likelihood −1 456 133 og koeffisienten for alder negativ. Med `alder2 = alder*alder` var log-likelihood −1 430 816, med positiv alder og negativ `alder2`. Ingen melding. `LR chi2` har én df mer enn synlige ledd i begge. Se `fallgruver.md`. **Kjørt videre 2026-11-20** (`testskript/del8_11_interaksjoner.txt`, utvalg 200 000): det samme skjer i `regress` (R² 0,0615 mot 0,0932 med `alder2`) og med `c.alder##c.alder`. `c.alder#c.lonn23` og `i.mann#c.alder` virker i både `regress` og `logit`. Med i `feilrapporter.md` (nr. 17) | | | ✓ |
| 8.12 | ~~Winsoriseres sjeldne 0/1-variabler i regresjoner?~~ **Avklart (versjon 60, 2026-11-20):** ja. Av 405 000 personer: `d02` (0,22 %) og `d08` (0,85 %) ga gjennomsnitt 0 i `summarize` og ble utelatt fra `regress` og `logit` uten melding (`F(1, ...)`, bare `mann`). `d24` (2,47 %) og `topp` (1,26 %) var med: `d24` +23 (forskjell i gjennomsnitt +21), `topp` +1 245. `logit topp lonn23 mann` (utfall 1,26 %) virket. Se `fallgruver.md` og `feilrapporter.md` nr. 18. Skript: `testskript/del8_12_sjeldne_dummyer.txt` | | | ✓ |
| 8.13 | ~~Kategorier under 1 % i `i.`-variabler, og utfall under 1 %~~ **Avklart (versjon 60, 2026-11-20):** `i.gruppe` med kategorier på 0,2, 0,85 og 1,6 % ga rader for alle tre i `regress` (`F(4, ...)`) og `logit`, med koeffisienter nær forskjellene i gjennomsnitt. Utfall 0,34 % (lønn over 3 mill.): `regress` ga 0 og NaN, `logit` 35 iterasjoner og «Pseudo R2 Infinity». Utfall over 99 %: `logit` ga negativ LR chi2 og z = −145, uten feilmelding. Se `fallgruver.md`. Skript: `testskript/del8_13_sjeldne_kategorier.txt` | | | ✓ |
| 8.14 | ~~`i.x` på en sjelden 0/1-variabel, og sjelden hendelse i `cox`~~ **Avklart (versjon 60, 2026-11-20):** `d08` (0,86 %) ble utelatt, men `i.d08` ga raden «d08 '1'» med +27 (forskjell +25) og `F(2, ...)`, også i `logit`. `cox` med død i 2025 for 25–66-åringer (948, 0,19 %): `summarize` ga 0, men `cox` fant 947 hendelser med alder +0,086 og mann +0,48, som kontrollen (8,7 % døde, +0,105 og +0,39). Hendelsen i `cox` winsoriseres ikke. Skript: `testskript/del8_14_ix_og_cox.txt` | | | ✓ |
| 8.15 | ~~`i.` på en tekstvariabel~~ **Avklart (versjon 60, 2026-11-23):** virker. `i.kjonn`, `i.fylke` (`substr`) og `i.invkat` (bokstaver) ga én rad per kategori unntatt den laveste, i `regress` og `logit`, og `i.kjonn##i.invkat` ga samspill. `i.fylke` ga de samme koeffisientene som etter `destring` (Rogaland +0,38, Innlandet −126,6). Med kodeliste vises bare navnet («kjonn 'Kvinne'»). Tekst uten ledende null er ikke testet. Se `fallgruver.md`. Skript: `testskript/del8_15_i_tekst.txt` | | | ✓ |
| 8.8 | ~~`citation` (kildehenvisning, #9)~~ **Avklart (versjon 60, 2026-11-18):** «Analysen er gjennomført i microdata.no med datagrunnlag fra: SSB (registerdata). Data analysert: 2026-11-18». Med tre `require` (del 10): «FHI (Kreftregisteret), FHI (Norsk pasientregister) og SSB (registerdata)», også NPR før noe var importert derfra. Ingen versjon eller variabler. Kommer ikke med når hele utskriften kopieres | | | ✓ |

## 9. Eksport av figurer (Vega), issue #3

Manualen nevner Vega-editoren bare i [`1.6 Eksport av resultater`](skills/microdata-no/metadata/manual/brukermanual/Om%20brukergrensesnittet/1.6%20Eksport%20av%20resultater.md), uten kodeeksempler. Ingen kjøring trengs utover én figur.

| # | Hva | Hvordan | Forventet | Pri |
|---|---|---|---|---|
| 9.1 | ~~Vega eller Vega-Lite?~~ **Avklart (versjon 60, 2026-11-19):** Vega-Lite v6 (`$schema` …/vega-lite/v6.json), fra `barchart (count) fylke` | | | ✓ |
| 9.2 | ~~Ligger dataene i spesifikasjonen?~~ **Avklart (2026-11-19):** ja, de aggregerte tallene står i `data.values` (`title` = kategori, `value` = tall, `category`/`cat_order` som lister). Manualens «får ikke de underliggende tallene» gjelder bare .png/.svg. Se `referanser/vega.md` | | | ✓ |
| 9.3 | ~~Hvilken editor?~~ **Avklart (2026-11-19):** vega.github.io/editor, utenfor microdata.no | | | ✓ |
| 9.4 | ~~`tabulate ..., flatten`~~ **Avklart (versjon 60, 2026-11-19):** eksporten er semikolon + mellomrom, overskriftene «kode - navn», med raden og kolonnen Total og alle desimaler. `flatten` endrer ingenting for to dimensjoner. Stablet prosentfigur med farge etter gruppe laget fra eksporten (`fold`) tegnes riktig, også med Config-fanen urørt. Helt tom Config-fane gir «ValueExpected». Står i `vega.md` | | | ✓ |
| 9.5 | ~~Endringene i `referanser/vega.md`~~ **Avklart (2026-11-19):** fylkesnavn (`lookup`), sortering, liggende søyler, tittel/kilde og norsk tallformat (`config.locale`) virker. Microdata.no legger en mørk stil i editorens Config-fane (`axisX`/`axisY`/`legend` med format `~s`, `labelAngle` 45, IBM Plex Sans, mørk bakgrunn). Den ga «NaN» for navn på y-aksen og blandede fonter. Agenten overstyrer stilen eksplisitt i spesifikasjonen (fanen kan stå urørt, 9.4). Står i `vega.md` | | | ✓ |

## 10. FHI-datalagrene (Kreftregisteret og NPR), issue #11

Avklart. Resultatene står i «FHI-data» i [`fallgruver.md`](skills/microdata-no/referanser/fallgruver.md). Skriptet ligger i
[`.claude/skills/vedlikehold/testskript/del10_fhi.txt`](.claude/skills/vedlikehold/testskript/del10_fhi.txt) (kjørt 2026-11-18),
med 8.8 (`citation`) for flere kilder.

| # | Hva | Hvordan | Forventet | Pri |
|---|---|---|---|---|
| 10.1 | ~~Tre `require`, import fra Kreftregisteret~~ **Avklart (2026-11-18):** 38 889 tilfeller i 2023, 37 118 ondartede | | | ✓ |
| 10.2 | ~~Kreftform fra `kreftregisteret.py grupper`~~ **Avklart (2026-11-18):** ingen stopp, fordelingen rimelig (fordøyelse 7 999, melanom/hud 6 128, prostata m.m. 5 669, bryst 4 121, lunge m.m. 3 588). D45 og D46 sto igjen fordi de mangler i kodelisten; verktøyet tar dem nå med | | | ✓ |
| 10.3 | ~~Manglende verdi i `S_STRALEBEH`~~ **Avklart (2026-11-18):** bare `1` og manglende: manglende = ikke registrert | | | ✓ |
| 10.4 | ~~Personnøkkelen er samme pseudonym som hos SSB~~ **Avklart (2026-11-18):** alle fikk kjønn, kjønnsorganer 100 % ett kjønn | | | ✓ |
| 10.5 | ~~`collapse ... by(personid)` kobles inn i persondatasett~~ **Avklart (2026-11-18):** virker, 37 872 personer | | | ✓ |
| 10.6 | ~~NPR-episoder, filtrert med `values()`~~ **Avklart (2026-11-18):** 9,1 millioner episoder, 12 % med kreftdiagnose | | | ✓ |
| 10.7 | ~~Samme person i NPR og Kreftregisteret~~ **Avklart (2026-11-18):** 25 % av kreftepisodene mot 2 % av andre har krefttilfelle i 2023 | | | ✓ |
| 10.9 | ~~Datoer av typen Instant~~ **Avklart (2026-11-18):** dager siden 1970. `S_DIAGNOSEDATO` 19 361–19 713 (2023), `year()` gir 2023 for alle. `SOM_EP_INNDATO`: 2024 for alle unntatt 7 391 (2023) | | | ✓ |
| 10.8 | ~~`recode` til samme verdi for å sette merkelapp~~ **Avklart (2026-11-18):** `('C50' = 'C50' 'Bryst')` godtas, og C50 vises som «C50 - Bryst» | | | ✓ |
| 10.11 | ~~Kreftformer som i Cancer in Norway (#13)~~ **Avklart (versjon 1, 2026-11-23):** 38 887 tilfeller i 2023 mot 38 889 i Cancer in Norway 2025 (tabell 4.5–4.6). Alle kreftformer innenfor støyen, unntatt leppe: ingen C00 i ICD-10, leppekreft er C44.0. ICD-O-3-topografien (uten C) har 91 i lepperødt og munnvik mot 89 i rapporten, og `--topografi` flytter dem. Ingen basalcellekarsinomer. C48.2 med `--kjonn` virker (eggstokk bare kvinner). Skript: `del10_11_cancer_in_norway.txt` og `del10_11b_leppe.txt`. C00 Leppe med `--topografi` testet i 2.10 | | | ✓ |

## 11. Grunnkrets (`BEFOLKNING_GRUNNKRETS`, versjon 60)

Antakelser i «Grunnkrets» i [`fallgruver.md`](skills/microdata-no/referanser/fallgruver.md). Skriptet ligger i
[`.claude/skills/vedlikehold/testskript/del11_grunnkrets.txt`](.claude/skills/vedlikehold/testskript/del11_grunnkrets.txt) (kjørt 2026-11-19,
versjon 60), med recode-linjer fra `verktoy/grunnkrets.py`. 11.1–11.6 er avklart.

| # | Hva | Hvordan | Forventet | Pri |
|---|---|---|---|---|
| 11.1 | ~~Kodeformat i dataene~~ **Avklart (2026-11-19):** bare 8 tegn 1.1.2026 (5,63 mill.). 9 508 uoppgitt (`kkkk9999`, 0,17 %) | | | ✓ |
| 11.2 | ~~De fire første sifrene er bostedskommunen~~ **Avklart (2026-11-19):** like `BEFOLKNING_KOMMNR_FORMELL` for alle 1.1.2026, ingen avvik | | | ✓ |
| 11.3 | ~~Levekårssoner, gjeldende år~~ **Avklart (2026-11-19):** ingen stopp. 63 soner i Bergen med 1 598–7 650 personer. Bare uoppgitt (433) står med 8 tegn | | | ✓ |
| 11.4 | ~~Gamle koder følges gjennom kommunereformen~~ **Avklart (2026-11-19):** 2019 (1201) til delområde 2026 (4601): alle 20 delområder, 8 tegn bare for uoppgitt (`12019999`, ca. 615) | | | ✓ |
| 11.5 | ~~Bydel fra eldre år~~ **Avklart (2026-11-19):** 2019 til bydel i Oslo: 15 bydeler pluss Sentrum (1 386) og Marka (1 637). Bare uoppgitt (`03019999`, 2 398) står igjen | | | ✓ |
| 11.6 | ~~Lang recode for hele landet~~ **Avklart (2026-11-19):** 2015 til delområde (160 kB, over 300 `recode`-linjer) godtas. 5 144 078 med 6 tegn og 21 719 (0,4 %) med 8 tegn. Se 11.8 | | | ✓ |
| 11.7 | ~~`configure confidentiality v1` med grunnkrets~~ **Avklart (versjon 60, 2026-11-19):** `configure` godtas, og skriptet kjører til `import` av grunnkrets: «Ulovlig import med valgt konfidensialitetsprofil. Kan ikke bruke variabler innenfor *_GRUNNKRETS». Sjekken skjer ved hver import, ikke på forhånd. Skript: `testskript/del11_7_confidentiality_v1.txt` | | | ✓ |
| 11.8 | ~~Hva er de 21 719 med 8 tegn i 11.6?~~ **Avklart (versjon 60, 2026-11-19):** 19 069 uoppgitt (0,37 % i 2015, mot 0,17 % i 2026) og 2 657 i de 14 delte grunnkretsene, ingen andre. Alle delområdene med 6 tegn har et kommunenummer som finnes i 2026, så omkodingen av 2015 er fullstendig. Skript: `testskript/del11_8_atte_tegn.txt` | | | ✓ |
| 11.9 | ~~`BEFOLKNING_BYDEL` mot `grunnkrets.py --til bydel`~~ **Avklart (versjon 60, 2026-11-20):** 1 381 558 av 1 384 643 (99,8 %) fikk samme kode. Avvikene er 2 880 uoppgitt (`030199` mot `03019999` osv., samme personer) og 193 (0,01 %) med grunnkrets i en bydel, men manglende `BEFOLKNING_BYDEL`. Alle bydeler, også Sentrum, Marka, Finnøy og Rennesøy, innen ±15. Skript: `testskript/del11_9_bydel_fhi.txt` | | | ✓ |
| 11.10 | ~~Grunnkrets sammen med andre personvariabler~~ **Avklart (2026-11-20):** lønn etter delområde i Trondheim (105 883 personer 25–66 år, 26 delområder pluss uoppgitt) med `tabulate ..., summarize()` og `regress lonn alder i.delomrnum` kjørte uten feil. Delområdene fra `substr` har ikke navn (bare koden) | | | ✓ |
| 11.11 | ~~FHI-data og grunnkrets i samme skript (versjon 2)~~ **Avklart (2026-11-20):** krefttilfeller 2023 samlet per person og koblet til bosatte i Oslo med grunnkrets og bydel: ingen stopp. 3 729 av 709 037 (0,53 %) har et krefttilfelle. (Første kjøring stoppet på `merge` fordi `use kreft` manglet, den kjente fallgruven.) | | | ✓ |
| 11.12 | ~~Gjennomsnitt 0 for `kreft23`~~ **Avklart (versjon 60, 2026-11-20):** `summarize kreft23` ga gjennomsnitt 0, standardavvik 0 og 99-persentil 0 for 709 033 personer, mens `tabulate kreft23` viste 3 729 med 1 (0,53 %). Winsoriseringen gjør alle 1-erne til 0 når under 1 % har verdien 1. Se «Gjennomsnitt av sjeldne 0/1-variabler» i `fallgruver.md` og `feilrapporter.md` nr. 18. Uavklart: 0/1-forklaringsvariabler i regresjoner | | | ✓ |
