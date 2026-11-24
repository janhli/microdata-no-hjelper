---
name: microdata-no
description: Hjelp til å skrive og feilsøke skript for microdata.no (SSB/Sikt), det Stata-lignende skriptspråket for norske registerdata. Bruk skillen når brukeren nevner microdata.no, no.ssb.fdb, variabler som BEFOLKNING_*, INNTEKT_*, REGSYS_* eller NUDB_*, eller kommandoer som import-event, create-dataset og textblock, eller limer inn feilmeldinger eller resultater fra microdata.no. Også for FHI-datalagrene i microdata.no (no.fhi.kreftregisteret, no.fhi.npr), grunnkrets og bydel i microdata.no (BEFOLKNING_GRUNNKRETS, BEFOLKNING_BYDEL) og for å endre figurer fra microdata.no i Vega-editoren.
---

# microdata.no

Microdata.no har sitt eget skriptspråk, som ligner Stata. Analysemiljøet krever innlogging, så du kan
ikke kjøre skript selv. Du skriver skriptet, brukeren kjører det i microdata.no og limer inn
feilmeldinger eller resultater, og du justerer.

## Lokale kilder (bruk dem før nettet)

Alle stier er relative til denne skill-mappen. I `metadata/` søker du (grep, rg eller agentens søkeverktøy) i stedet for å
lese hele filene. `referanser/fallgruver.md` leser du i sin helhet før du leverer et skript, og hver temafil
(`referanser/fallgruver_*.md`) når skriptet bruker temaet.

| Fil | Innhold |
|---|---|
| `metadata/variabler.csv` | Én linje per variabel (`;`-separert): navn, label, temporalitet, datatype, enhet, fra, til, antall koder, emner, beskrivelse, populasjon, datalager, ekstern_metadata (lenker i beskrivelsen, f.eks. til Kreftregisterets metadatabase ELVIS) |
| `metadata/kodelister.csv` | Gjeldende kodeliste for alle variabler: `navn;kode;kategori` |
| `metadata/variabler/<NAVN>.json` | Full metadata: kodelistehistorikk, måletidspunkter (`temporalStatusDates`, dager siden 1970-01-01) og beskrivelser per periode |
| `metadata/datalager.json` | Versjonshistorikk for `no.ssb.fdb`, med hvilke variabler som er endret i hver versjon |
| `metadata/datalagre.json` | Alle datalagrene med navn og versjon: `no.ssb.fdb` (SSB) og fra 2026-11 `no.fhi.kreftregisteret` og `no.fhi.npr` (FHI). Kolonnen `datalager` i `variabler.csv` sier hvor variabelen ligger. |
| `metadata/kommuneendringer.json` | Kommuneendringer fra SSB Klass 131 siden 1989 (gammel kode, ny kode, dato, navn). Brukes av `verktoy/kommuneomkoding.py` |
| `metadata/grunnkrets/` | Grunnkrets (SSB Klass 1): `endringer.csv` (alle kodeendringer siden 1990) og `inndelinger.csv` (grunnkrets → levekårssone, bydel og delbydel i Oslo, gjeldende inndeling). Brukes av `verktoy/grunnkrets.py` |
| `metadata/regioner/*.csv` | Koblingstabeller fra kommune (2024) til regioninndelinger: politidistrikt, valgdistrikt, økonomiske regioner, helseregioner, familievern, barnevern, reiseliv, samiske valgkretser, sentralitet, landsdeler og bo- og arbeidsmarkedsregioner. Kolonner `kommunenr;regionkode;regionnavn`. Oversikt i `INDEX.csv`, manuelt lastede filer i `manuelt/` |
| `metadata/manual/**/*.md` | Hele manualen som Markdown. Kommandoreferansen ligger i `kommandoer_og_funksjoner/kommandoer.md` og funksjonene i `.../funksjoner.md`. |
| `referanser/fallgruver.md` | Feil som ikke står (tydelig) i manualen, med feilmelding og løsning. Gjelder alle skript. **Les hele før du leverer et skript.** |
| `referanser/fallgruver_analyse.md` | Fallgruver i regresjon, `correlate`, overlevelsesanalyse og paneldata. **Les når skriptet har en statistisk analyse.** |
| `referanser/fallgruver_geografi.md` | Kommune, fylke, region, bydel og grunnkrets. **Les når skriptet bruker geografi.** |
| `referanser/fallgruver_klass.md` | Koder og koblinger fra Klass, og næring (finnes bare til 2019). **Les når skriptet bruker `klass.py` eller næring.** |
| `referanser/fallgruver_fhi.md` | Kreftregisteret og NPR. **Les når skriptet bruker `no.fhi.*`.** |
| `referanser/vega.md` | Endre figurer fra microdata.no i Vega-editoren: brukeren limer inn Vega-Lite-spesifikasjonen (med tallene), du endrer etiketter, rekkefølge, farger, titler og tallformat. Les den når brukeren vil ha en penere eller tilpasset figur |
| `kodesnutter/` | Frittstående og kommenterte snutter med teststatus: analysemal, fylke med navn, alder, innvandringskategori, landbakgrunn, utdanning, arbeidsstyrkestatus, NEET, samliv, husholdning, bolig, lavinntekt, verdi ved hendelse, mor–barn, forløp, overlevelsesanalyse, logistisk regresjon og paneldata. Oversikt i `kodesnutter/README.md`. **Ta utgangspunkt i disse før du skriver noe selv.** |

Dato for siste nedlasting står i `metadata/HENTET`. Oppdater med `python verktoy/hent_variabler.py`
(`--alle` henter alt på nytt, ca. 6 min) og `python verktoy/hent_manual.py`.
Begge skriptene kontrollerer uttrekket før de skriver, og avsluttes med feilkode uten å endre filer hvis noe
mangler. `--tving` skriver likevel.
Kommuneendringene oppdateres med `python verktoy/hent_kommuneendringer.py`. Grunnkretsene oppdateres med `python verktoy/hent_grunnkrets.py`.

## Konfidensialitet

Fra 17. november 2026 (versjon 60) gjelder **versjon 2 av anonymiseringstiltakene**: celler med 1–4 vises som
0, minste datasett er 100 personer, tellinger har støy, og gjennomsnitt og regresjoner er winsorisert. Unngå svært
finfordelte tabeller og små populasjoner. Resultatene kan avvike litt fra SSBs offisielle statistikk. Hva tiltakene gjør med skript og analyser,
og når `configure confidentiality v1` kan brukes, står i «Avsløringskontroll» i `referanser/fallgruver.md`.

## Kommunenumre over tid

Skal data fra flere år sammenlignes på kommune, må gamle kommunenumre omkodes til én inndeling.
Ikke skriv reglene for hånd. Kjør `python verktoy/kommuneomkoding.py --fra <år> --til <år> --navn <variabel>`
og lim `recode`-linjene inn i skriptet. Velg et målår som er likt eller senere enn kildeåret. Kommunene får
navnet fra Klass, med samisk og kvensk navn der kommunen har det (Hábmer - Hamarøy). `--norske-navn` gir
bare det norske navnet. Verktøyet lister kommuner som er delt i flere (f.eks. Tysfjord)
og lar dem stå uendret. Si fra til brukeren om disse, og om «koder som selv ble delt». Fra 1990 kan personene i
delte kommuner fordeles etter grunnkrets: importer `BEFOLKNING_GRUNNKRETS` på samme dato som kommunen og legg
til `--grunnkrets <variabel>`. Se `referanser/fallgruver_geografi.md`.

For å gruppere kommuner i regioner (helseregion, politidistrikt, økonomisk region osv.): kjør
`python verktoy/regionomkoding.py <inndeling> --fra <kommunevariabel> --til <ny variabel>`
(`--liste` viser inndelingene). Tabellene gjelder kommunenummer i 2024-inndelingen, så omkod gamle
kommunenumre først. Oppdater tabellene med `python verktoy/hent_regioninndelinger.py`.

## Grunnkrets, delområde, levekårssone og bydel

`BEFOLKNING_GRUNNKRETS` (fra versjon 60, november 2026) er grunnkretsen personen bor i per 1.1. fra 1990.
Alt som finnes på person, kan tabuleres og brukes i modeller etter grunnkrets og områdene under. Grensen er små
celler, ikke hvilke variabler som kan brukes.

**Bydeler:** bruk først den ferdige `BEFOLKNING_BYDEL` (Oslo, Bergen, Trondheim, Stavanger, fra 1990, eldre år
omkodet til gjeldende bydeler, Klass 103). `grunnkrets.py --til bydel` trengs når bydelene skal følge
gjeldende grunnkretser eksakt.

Koden er kommune (4) + delområde (2) + grunnkrets (2) og skifter når kommunen skifter nummer. Bruk
`python verktoy/grunnkrets.py --til <inndeling> --aar <år> --var <variabel> [--kommune 4601,5001]`:

| `--til` | Gir |
|---|---|
| `delomrade` | Delområde (6 sifre), hele landet |
| `lks` | Levekårssoner fra Klass (10 sifre, 66 kommuner) |
| `bydel` | Bydeler i Oslo, Bergen, Trondheim og Stavanger (6 sifre). Se `BEFOLKNING_BYDEL` over |
| `delbydel` | Delbydeler i Oslo (4 sifre) |
| `FIL.csv` | Egne områder, kolonnene `grunnkrets;kode;navn` med gjeldende grunnkretskoder |

`--aar` er året dataene er hentet for. Kod rett til målet, ikke via enkeltgrunnkretser. Si fra til brukeren om
grunnkretser som er delt mellom enheter (står i kommentaren), og at verdier med 8 tegn ikke er omkodet. Se
«Grunnkrets» i `referanser/fallgruver_geografi.md`.

## Klass: slå opp i stedet for å skrive reglene for hånd

SSBs klassifikasjoner (https://www.ssb.no/klass) gir grupperinger og koblinger mellom koder. Bruk
`verktoy/klass.py` til å lage `recode`-linjer, i stedet for å gjette eller skrive hundrevis av regler selv.
Verktøyet krever nettilgang. Er den ikke der, si fra til brukeren og bruk det som ligger i `metadata/`.

| Behov | Klass-ID | Kommando |
|---|---|---|
| Yrke (STYRK-08), `*_YRKE_STYRK08` | 7 | `grupper 7 --nivaa 1 --variabel REGSYS_ARB_YRKE_STYRK08 --navn yrke` |
| Utdanning (NUS), `NUDB_BU`, `NUDB_KURS_NUS` | 36 | `grupper 36 --nivaa 1 --variabel NUDB_BU --navn nus` |
| Landkode til verdensdel, `BEFOLKNING_LANDBAK3GEN`, `*_FODELAND` | 545 (verdensinndeling) | `grupper 545 --nivaa 2 --variabel BEFOLKNING_LANDBAK3GEN --navn landbak` |
| Land til EU/EFTA, Norden osv. | 546 (gruppering av land) | `grupper 546 --nivaa 2 --variabel ...` |
| Næring (SN2007), `REGSYS_NARING_SN2007` (2008–2014), `REGSYS_VIRK_NACE1_SN07` (2015–2019) | 6 | `grupper 6 --nivaa 1 --dato 2019-11-16 --variabel REGSYS_VIRK_NACE1_SN07 --navn naring`. Finnes ikke etter november 2019: si det til brukeren |
| Koblingstabeller (NUS til ISCED osv.) | 36, 6, 91 | `kobling 36` lister tabellene, `kobling 36 --tabell "ISCED 2011 Attainment" --navn nus` lager recode |
| Næring over tid (SN2002 til SN2007) | 6 | `kobling 6 --dato 2005-01-01 --tabell "SN 2007" --nivaa 1 --navn naring` (seksjon). Bruk alltid `--nivaa` |
| Finne en annen klassifikasjon | | `sok yrke` |

Nivåene i hierarkiene: STYRK 1–4 er ett til fire siffer. NUS 1 er utdanningsnivå (0–9), 2 er nivå og
fagfelt, 5 er 6-sifret kode. SN 1 er seksjon (A–U), 2 er divisjon (`01`), 5 er femsifret kode (`01.110`).
Verdensinndeling 1 er verdensdel, 2 er region (f.eks. Norden, Subsaharisk Afrika), 3 er gruppe (`V111`),
4 er landkoden. `koder <id> --nivaa N` viser kodene på et nivå, så du kan velge riktig nivå først.

Fallgruver står i `referanser/fallgruver_klass.md`. Les dem før du leverer skriptet. Resultatene er
ikke kjørt i microdata.no før brukeren har kjørt dem.

## FHI-data: Kreftregisteret og Norsk pasientregister

Microdata.no har fra 2026-11 også `no.fhi.kreftregisteret` og `no.fhi.npr` (versjon 1, se `metadata/datalagre.json`).
Enhetene er krefttilfelle, episode og prosedyre, ikke person. Les `referanser/fallgruver_fhi.md` før du skriver skriptet.

| Behov | Kommando |
|---|---|
| ICD-10 til kreftform (14 hovedgrupper) | `python verktoy/kreftregisteret.py grupper --variabel S_TOPOGRAFIICD10 --nivaa 1 --var topo` |
| Tresifret kreftform med navn (C18 Tykktarm) | `... grupper --variabel S_TOPOGRAFIICD10 --nivaa 2 --navn kreft3 --var topo` |
| Kreftformene i Cancer in Norway (48, f.eks. C19-20 Endetarm), for å sammenligne med publiserte tall | `... grupper --variabel S_TOPOGRAFIICD10 --nivaa cin --var topo --kjonn kjonn --topografi topo3` (`topo3` = `S_TOPOGRAFIICDO3`, for leppekreft) |
| Diagnoser i NPR, resten som «annet» | `... grupper --variabel SOM_EP_HOVEDTILSTAND1 --nivaa 1 --var diag --ukjent` |
| Hvilke verdier gjelder for en kreftform (TNM) | `... verdier --variabel S_PT --kreftform C50` |
| Oppdatere kreftformer og verdier fra ELVIS | `... hent` |

Kodelistene står i `metadata/kodelister.csv`, beskrivelsene i Kreftregisterets metadatabase (lenken står i
`ekstern_metadata` i `variabler.csv`). Gi brukeren lenken i stedet for å gjette hva en kode betyr.

## Statistiske analyser: velg kommando etter utfallet

Syntaks og opsjoner står i `metadata/manual/kommandoer_og_funksjoner/kommandoer.md` (avsnittene
«Regresjon», «Statistikk» og «Overlevelsesanalyse»), og eksempler i `metadata/manual/eksempel/Regresjonsanalyser/`.
Eksemplene bruker gamle datalagerversjoner (23–45), så sjekk variabelnavnene.

| Problem | Kommando | Merk |
|---|---|---|
| Kontinuerlig utfall (lønn, inntekt) | `regress` | `robust` eller `cluster()`. Diagnostikk med `ov vif het_bp` |
| Ja/nei-utfall | `logit` / `probit` | Utfallet må være 0/1. `mfx(dydx)` for marginaleffekter, `or` for oddsratio. Snutt: `kodesnutter/logistisk_regresjon.txt` |
| Utfall med flere kategorier uten rekkefølge | `mlogit` | |
| Antall (sykemeldinger, fødsler) | `poisson`, `negative-binomial` ved overdispersjon | `exposure()` for rater, `irr` |
| Forskjell mellom to grupper, forklart og uforklart | `oaxaca ... by gruppe` | |
| Samme enheter over tid | `import-panel` + `regress-panel` (`fe`/`re`), `hausman` | Bare i tomt datasett. Ta med årseffekter (`i.aar`). Snutt: `kodesnutter/paneldata.txt`. Manualen: `Paneldata-analyse.md` |
| Effekt av et tiltak før/etter, med kontrollgruppe | `regress-panel-diff` | Variabel 3 er etter-perioden for alle. Eksempel: `Diff-in-diff-analyse.md` |
| Terskel i en kontinuerlig variabel | `rdd` (`cutoff()`, `fuzzy()`) | Eksempel: `RDD-analyse.md` |
| Endogen forklaringsvariabel | `ivregress y x ( endogen = instrument )` | Instrumentet til høyre for `=` |
| Personer i grupper (skoler, kommuner) | `regress-mml ... by gruppe` | Eksempel: `Flernivåanalyse.md` |
| Tid til hendelse | `kaplan-meier`, `cox`, `weibull` | Populasjonen er alle i risiko, med sensurering. Snutt: `kodesnutter/overlevelse.txt`. Manualen: `Hvordan tilrettelegge data for overlevelsesanalyse.md` (eksempel A har ingen sensurerte) |
| Predikerte verdier og residualer | `*-predict`, `margins()` | |
| Sammenheng mellom to numeriske variabler | `correlate`, `hexbin` | Ingen spredningsplott. `correlate` utelater manglende verdier listevis, `pairwise` parvis |
| Konfidensintervall for et gjennomsnitt | `ci` | `level()` |
| Forskjell i gjennomsnitt mellom grupper | `anova` (ANCOVA med en metrisk kovariat) | Forklaringsvariablene er faktorer. `posthoc` gir Tukey HSD |
| Er variabelen normalfordelt? | `normaltest` | Skjevhet, kurtose, Jarque-Bera, Shapiro-Wilk |
| Overganger mellom kategorier over tid | `transitions-panel` | På paneldata. Overganger til og fra missing er utelatt |

Les `referanser/fallgruver_analyse.md`, og «Sjeldne 0/1-variabler» i `referanser/fallgruver.md`, før du leverer en
analyse. **0/1-variabler der under 1 % har verdien 1, gir feil resultat uten feilmelding**, og flere av manualens
eksempler har feil (overlevelsesanalyse, diff-in-diff, `ivregress`). Velg modell etter utfallet og designet,
og si fra om forutsetningene (f.eks. parallelle trender i diff-in-diff, instrumentets gyldighet).

## Arbeidsflyt

1. Avklar tema, populasjon, år og geografi med brukeren.
2. Finn kandidatvariabler i `metadata/variabler.csv`. Sjekk dekningen (`fra`/`til`), koder i
   `metadata/kodelister.csv` og eksakt syntaks i `metadata/manual/`.
3. Les hele `referanser/fallgruver.md` og temafilene skriptet trenger, og skriv skriptet. Kommenter koden og oppgi kilde-URL ved hver variabel med
   `https://microdata.no/discovery/variable/<datalager>/<versjon>/<NAVN>`. Bruk kolonnen `datalager` i
   `metadata/variabler.csv` og hovedversjonen fra `require` for det datalageret.
   Kommentarblokken øverst i hvert skript du skriver, skal ha denne linjen ordrett:
   `// Laget med hjelp fra en KI-agent (microdata-no-hjelper). Kontroller variabler, populasjon og resultater selv: du er ansvarlig for skriptet.`
   Si det samme kort til brukeren når du leverer skriptet: du er et hjelpemiddel, og brukeren må
   kontrollere og står ansvarlig for skriptet og resultatene.
4. Sett en `textblock` ... `endblock` (Markdown) med tittel og en kort lesehjelp foran hver
   `tabulate`, `summarize` og `regress`. Ikke legg tabeller med tittel inne i `for`-løkker. Skriv dem
   ut for hvert år, så årstallet kan stå i tittelen. Avslutt skriptet med `citation`.
5. Kjør `python verktoy/sjekk_skript.py <fil>` før du leverer (`-` leser skriptet fra stdin). Den finner
   variabler som ikke finnes, datoer utenfor dekningen, pseudonymer i uttrykk, `median`/`sd`, `c.x#c.x`,
   funksjonsnavn som navn og manglende ansvarslinje eller `citation`. Rett alle feil. Advarslene er ting du
   må vurdere og eventuelt si fra om. Til slutt skriver den ut hvilke temafiler
   skriptet trenger: les dem du ikke har lest, og rett skriptet. Sjekken erstatter ikke fallgruvefilene.
6. Brukeren kjører skriptet og melder tilbake. Rett feilen, og finnes den ikke allerede i
   fallgruvefilene, foreslå at brukeren bidrar med den (se CONTRIBUTING.md i repoet).

## Datalagerversjon

Skriv én `require <datalager>:<versjon> as <alias>` øverst i skriptet per datalager du bruker. For SSB bruker
du `require no.ssb.fdb:<versjon> as fdb`. Siste hovedversjon for hvert lager står i `metadata/datalagre.json`
(for eksempel `1` fra `1.0.0.0`). SSBs versjonshistorikk ligger i `metadata/datalager.json`.
Analysemiljøet kan ligge en versjon bak metadatasidene. **Spør
brukeren hvilken versjon de har tilgang til** hvis det er usikkert. Eldre eksempelskript bruker ofte
gamle versjoner, og da må du sjekke at variabelnavnene fortsatt finnes i `variabler.csv`.

## Språket kort fortalt

- `require no.ssb.fdb:<v> as fdb` kobler til datalageret
- `create-dataset navn` / `use navn`
- `import fdb/VARIABEL 2024-01-01 as alias` henter en tverrsnittsverdi på en dato
- `import-event`, `import-panel` henter hendelser og paneldata
- `generate`, `replace`, `recode`, `destring`, `drop`, `keep`
- `collapse`, `aggregate`, `merge ... into ... on ...`
- `tabulate`, `summarize`, `regress`, `logit`, `barchart`, `histogram` (figurene kan endres i Vega-editoren, se `referanser/vega.md`)
- `let` og `for ... end` for løkker
- `citation` nederst i skriptet gir én linje med datalager og dato, men uten versjon og variabler, så oppgi
  `require`-versjonen selv. Alle datalagre i `require` listes, også ubrukte: ta bare med dem du bruker. Resultater skal ha microdata.no som kilde ved publisering
  (https://www.microdata.no/dokumentasjon/kildehenvisning/)

### Vaner fra Stata som ikke virker

| Stata | microdata.no | Se |
|---|---|---|
| `x == .`, `x != .`, `generate x = .` | `sysmiss(x)` og `!sysmiss(x)`. `.` som manglende verdi står ikke i manualen | `sysmiss` i manualens funksjoner |
| `x > 5` er sann når `x` mangler | Usann (0). Bare `!=` er sann. Skriv `generate h = x > 5 if !sysmiss(x)` | «Sammenligninger med manglende verdi» |
| `summarize(x) median` eller `sd` i `tabulate` | `p50` og `std`. `sd` stopper skriptet. `collapse (median)` virker | «Tabeller og statistikk» |
| `c.x#c.x` for andregradsledd | Utelates uten melding. Lag `generate x2 = x * x` | «Standardfeil, faktorvariabler og prediksjon» |
| `i.` krever tall | `i.` virker på tekstvariabler. `destring` trengs ikke | samme |
| `foreach` og `forvalues` med `` `i' `` | `for aar in 2022 : 2024` ... `end`, verdien er `$aar`. Navn: `let v = navn_ ++ $aar`, så `$v` | «Bindinger og løkker» |
| `merge 1:1 id using fil` | `merge a b into <måldatasett> on <nøkkel>`, kjørt fra datasettet `a` og `b` ligger i | «`merge` kjøres fra datasettet variablene ligger i» |
| Ett datasett i minnet | Flere datasett (`create-dataset`, `use`, `clone-dataset`). `collapse` gjør om det aktive | «`collapse` endrer det aktive datasettet» |
| `vce(cluster id)` | `cluster(id)` med en numerisk variabel som ikke er i modellen. Kan ikke kombineres med `robust` | «Standardfeil, faktorvariabler og prediksjon» |
| Datoer som dager | Mange datovariabler er tall som `20240315`. `date(år, mnd, dag)` gir dager siden 1970 | «Datoer er tall i formatet ÅÅÅÅMMDD» |

Avsnittene står i `referanser/fallgruver.md`, unntatt «Standardfeil, faktorvariabler og prediksjon», som står i
`referanser/fallgruver_analyse.md`.

## Nettkilder (hvis lokale filer ikke strekker til)

| Hva | URL |
|---|---|
| Variabelliste | `https://microdata.no/discovery/variables?pageIndex={N}` (nullbasert, 20 per side, `&sortBy=LABEL&sortType=ASC`) |
| Variabeldetaljer | `https://microdata.no/discovery/variable/<datalager>/<versjon>/<NAVN>` |
| Manual | `https://microdata.no/manual/` (med avsluttende `/`) |

`https://microdata.no/discovery/` rendres med JavaScript og kommer tom tilbake.
`https://microdata.no/variable/...` (uten `/discovery/`) gir 404.

Flere eksempler (ikke kvalitetssikret, kan bruke eldre syntaks eller variabler): https://github.com/JOSliper/Microdata-skript.
Bruk dem bare som idékilde når `kodesnutter/` ikke dekker behovet. De bruker gamle
datalagerversjoner og har kjente feil.
