---
name: microdata-no
description: Hjelp til å skrive og feilsøke skript for microdata.no (SSB/Sikt), det Stata-lignende skriptspråket for norske registerdata. Bruk skillen når brukeren nevner microdata.no, no.ssb.fdb, variabler som BEFOLKNING_*, INNTEKT_*, REGSYS_* eller NUDB_*, eller kommandoer som import-event, create-dataset og textblock, eller limer inn feilmeldinger eller resultater fra microdata.no.
---

# microdata.no

Microdata.no har sitt eget skriptspråk, som ligner Stata. Analysemiljøet krever innlogging, så du kan
ikke kjøre skript selv. Du skriver skriptet, brukeren kjører det i microdata.no og limer inn
feilmeldinger eller resultater, og du justerer.

## Lokale kilder (bruk dem før nettet)

Alle stier er relative til denne skill-mappen. Søk i filene (grep, rg eller agentens søkeverktøy), og ikke les hele filene.

| Fil | Innhold |
|---|---|
| `metadata/variabler.csv` | Én linje per variabel (`;`-separert): navn, label, temporalitet, datatype, enhet, fra, til, antall koder, emner, beskrivelse, populasjon, datalager, ekstern_metadata (lenker i beskrivelsen, f.eks. til Kreftregisterets metadatabase ELVIS) |
| `metadata/kodelister.csv` | Gjeldende kodeliste for alle variabler: `navn;kode;kategori` |
| `metadata/variabler/<NAVN>.json` | Full metadata: kodelistehistorikk, måletidspunkter (`temporalStatusDates`, dager siden 1970-01-01) og beskrivelser per periode |
| `metadata/datalager.json` | Versjonshistorikk for `no.ssb.fdb`, med hvilke variabler som er endret i hver versjon |
| `metadata/datalagre.json` | Alle datalagrene med navn og versjon: `no.ssb.fdb` (SSB) og fra 2026-11 `no.fhi.kreftregisteret` og `no.fhi.npr` (FHI). Kolonnen `datalager` i `variabler.csv` sier hvor variabelen ligger. FHI-dataene er testet i microdata.no (TESTLISTE del 10, se «FHI-data» i `fallgruver.md`) |
| `metadata/kommuneendringer.json` | Kommuneendringer fra SSB Klass 131 siden 1989 (gammel kode, ny kode, dato, navn). Brukes av `verktoy/kommuneomkoding.py` |
| `metadata/grunnkrets/` | Grunnkrets (SSB Klass 1): `endringer.csv` (alle kodeendringer siden 1990) og `inndelinger.csv` (grunnkrets → levekårssone, bydel og delbydel i Oslo, gjeldende inndeling). Brukes av `verktoy/grunnkrets.py` |
| `metadata/regioner/*.csv` | Koblingstabeller fra kommune (2024) til regioninndelinger: politidistrikt, valgdistrikt, økonomiske regioner, helseregioner, familievern, barnevern, reiseliv, samiske valgkretser, sentralitet, landsdeler og bo- og arbeidsmarkedsregioner. Kolonner `kommunenr;regionkode;regionnavn`. Oversikt i `INDEX.csv`, manuelt lastede filer i `manuelt/` |
| `metadata/manual/**/*.md` | Hele manualen som Markdown. Kommandoreferansen ligger i `kommandoer_og_funksjoner/kommandoer.md` og funksjonene i `.../funksjoner.md`. |
| `referanser/fallgruver.md` | Feil som ikke står (tydelig) i manualen, med feilmelding og løsning. **Les den før du leverer et skript.** |
| `referanser/vega.md` | Endre figurer fra microdata.no i Vega-editoren: brukeren limer inn Vega-Lite-spesifikasjonen (med tallene), du endrer etiketter, rekkefølge, farger, titler og tallformat. Les den når brukeren vil ha en penere eller tilpasset figur |
| `kodesnutter/` | Frittstående og kommenterte snutter med teststatus: analysemal, alder, innvandringskategori, landbakgrunn, utdanning, arbeidsstyrkestatus, sektor for lønnstakere (utgått i versjon 60), samliv, husholdning, bolig, lavinntekt, verdi ved hendelse, mor–barn, forløp, overlevelsesanalyse og logistisk regresjon. Oversikt i `kodesnutter/README.md`. **Ta utgangspunkt i disse før du skriver noe selv.** |

Dato for siste nedlasting står i `metadata/HENTET`. Oppdater med `python verktoy/hent_variabler.py`
(`--alle` henter alt på nytt, ca. 6 min) og `python verktoy/hent_manual.py`.
Begge skriptene kontrollerer uttrekket før de skriver, og avsluttes med feilkode uten å endre filer hvis noe
mangler. `--tving` skriver likevel.
Kommuneendringene oppdateres med `python verktoy/hent_kommuneendringer.py`. Grunnkretsene oppdateres med `python verktoy/hent_grunnkrets.py`.

## Kommunenumre over tid

Skal data fra flere år sammenlignes på kommune, må gamle kommunenumre omkodes til én inndeling.
Ikke skriv reglene for hånd. Kjør `python verktoy/kommuneomkoding.py --fra <år> --til <år> --navn <variabel>`
og lim `recode`-linjene inn i skriptet. Kommunene får navnet fra Klass, med samisk og kvensk navn der
kommunen har det (Hábmer - Hamarøy). `--norske-navn` gir bare det norske navnet. Verktøyet lister kommuner som er delt i flere (f.eks. Tysfjord)
og lar dem stå uendret. Si fra til brukeren om disse, og om «koder som selv ble delt» (Ålesund 1507 i
2020–2023 omkodes til 1508, også Haram). Se også «Geografi» i `referanser/fallgruver.md`.

For å gruppere kommuner i regioner (helseregion, politidistrikt, økonomisk region osv.): kjør
`python verktoy/regionomkoding.py <inndeling> --fra <kommunevariabel> --til <ny variabel>`
(`--liste` viser inndelingene). Tabellene gjelder kommunenummer i 2024-inndelingen, så omkod gamle
kommunenumre først. Oppdater tabellene med `python verktoy/hent_regioninndelinger.py`.

## Grunnkrets, delområde, levekårssone og bydel

`BEFOLKNING_GRUNNKRETS` (fra versjon 60, november 2026) er grunnkretsen personen bor i per 1.1., 1990–2026.
Koden er kommune (4) + delområde (2) + grunnkrets (2) og skifter når kommunen skifter nummer. Bruk
`python verktoy/grunnkrets.py --til <inndeling> --aar <år> --var <variabel> [--kommune 4601,5001]`:

| `--til` | Gir |
|---|---|
| `delomrade` | Delområde (6 sifre), hele landet |
| `lks` | Levekårssoner fra Klass (10 sifre, 66 kommuner) |
| `bydel` | Bydeler i Oslo, Bergen, Trondheim og Stavanger (6 sifre) |
| `delbydel` | Delbydeler i Oslo (4 sifre) |
| `FIL.csv` | Egne områder, kolonnene `grunnkrets;kode;navn` med gjeldende grunnkretskoder |

`--aar` er året dataene er hentet for. Verktøyet følger gamle koder gjennom endringene til gjeldende
inndeling og koder rett til målet. Ikke omkod til enkeltgrunnkretser først (lange skript, og tabeller på
grunnkrets får mange celler under 5). Si fra til brukeren om grunnkretser som er delt mellom enheter (står i
kommentaren), og at verdier med 8 tegn ikke er omkodet. Se «Grunnkrets» i `referanser/fallgruver.md`.

## Klass: slå opp i stedet for å skrive reglene for hånd

SSBs klassifikasjoner (https://www.ssb.no/klass) gir grupperinger og koblinger mellom koder. Bruk
`verktoy/klass.py` til å lage `recode`-linjer, i stedet for å gjette eller skrive hundrevis av regler selv.
Verktøyet krever nettilgang. Er den ikke der, si fra til brukeren og bruk det som ligger i `metadata/`.

| Behov | Klass-ID | Kommando |
|---|---|---|
| Yrke (STYRK-08), `*_YRKE_STYRK08` | 7 | `grupper 7 --nivaa 1 --variabel REGSYS_ARB_YRKE_STYRK08 --navn yrke` |
| Utdanning (NUS), `NUDB_BU`, `NUDB_KURS_NUS` | 36 | `grupper 36 --nivaa 1 --variabel NUDB_BU --navn nus` |
| Landkode til verdensdel, `BEFOLKNING_LANDBAK3GEN`, `*_FODELAND` | 545 (verdensinndeling) | `grupper 545 --nivaa 2 --variabel BEFOLKNING_LANDBAK3GEN --navn landbak`. Statsløs og uoppgitt er under 10 personer og vises som 0. Med `configure confidentiality v1`: legg til `--utelat V91,V92` (nivå 1: `--utelat V9`) |
| Land til EU/EFTA, Norden osv. | 546 (gruppering av land) | `grupper 546 --nivaa 2 --variabel ...` |
| Næring (SN2007), `REGSYS_NARING_SN2007` | 6 | `grupper 6 --nivaa 1 --dato 2024-01-01 --variabel REGSYS_NARING_SN2007 --navn naring` |
| Koblingstabeller (NUS til ISCED osv.) | 36, 6, 91 | `kobling 36` lister tabellene, `kobling 36 --tabell "ISCED 2011 Attainment" --navn nus` lager recode |
| Næring over tid (SN2002 til SN2007) | 6 | `kobling 6 --dato 2005-01-01 --tabell "SN 2007" --nivaa 1 --navn naring` (seksjon, 91 % omkodet). Uten `--nivaa` står 42 % uendret |
| Finne en annen klassifikasjon | | `sok yrke` |

Nivåene i hierarkiene: STYRK 1–4 er ett til fire siffer. NUS 1 er utdanningsnivå (0–9), 2 er nivå og
fagfelt, 5 er 6-sifret kode. SN 1 er seksjon (A–U), 2 er divisjon (`01`), 5 er femsifret kode (`01.110`).
Verdensinndeling 1 er verdensdel, 2 er region (f.eks. Norden, Subsaharisk Afrika), 3 er gruppe (`V111`),
4 er landkoden. `koder <id> --nivaa N` viser kodene på et nivå, så du kan velge riktig nivå først.

Fallgruver står i «Klass» i `referanser/fallgruver.md`. Les dem før du leverer skriptet. Resultatene er
ikke kjørt i microdata.no før brukeren har kjørt dem.

## FHI-data: Kreftregisteret og Norsk pasientregister

Microdata.no har fra 2026-11 også `no.fhi.kreftregisteret` og `no.fhi.npr` (versjon 1, se `metadata/datalagre.json`).
Hvert datalager trenger sin egen `require`. Enhetene er krefttilfelle, episode og prosedyre, ikke person. Les
«FHI-data» i `referanser/fallgruver.md` før du skriver skriptet. Ingenting av dette er testet i microdata.no ennå.

| Behov | Kommando |
|---|---|
| ICD-10 til kreftform (14 hovedgrupper) | `python verktoy/kreftregisteret.py grupper --variabel S_TOPOGRAFIICD10 --nivaa 1 --var topo` |
| Tresifret kreftform med navn (C18 Tykktarm) | `... grupper --variabel S_TOPOGRAFIICD10 --nivaa 2 --navn kreft3 --var topo` |
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
| Samme enheter over tid | `import-panel` + `regress-panel` (`fe`/`re`), `hausman` | Bare i tomt datasett. Eksempel: `Paneldata-analyse.md` |
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

Les «Analyse» i `referanser/fallgruver.md` før du leverer en analyse. Der står konfidensialitetstiltakene som
påvirker analyser (winsorisering også i regresjoner, kategorier med under 5 observasjoner som fjernes, minst to
koeffisienter) og feil i
manualens eksempler (overlevelsesanalyse, diff-in-diff, `ivregress`). Velg modell etter utfallet og designet,
og si fra om forutsetningene (f.eks. parallelle trender i diff-in-diff, instrumentets gyldighet).

## Arbeidsflyt

1. Avklar tema, populasjon, år og geografi med brukeren.
2. Finn kandidatvariabler i `metadata/variabler.csv`. Sjekk dekningen (`fra`/`til`), koder i
   `metadata/kodelister.csv` og eksakt syntaks i `metadata/manual/`.
3. Les `referanser/fallgruver.md` og skriv skriptet. Det skal være kommentert, og kilde-URL skal
   stå ved hver variabel: `https://microdata.no/discovery/variable/no.ssb.fdb/<versjon>/<NAVN>`.
4. Sett en `textblock` ... `endblock` (Markdown) med tittel og en kort lesehjelp foran hver
   `tabulate`, `summarize` og `regress`. Ikke legg tabeller med tittel inne i `for`-løkker. Skriv dem
   ut for hvert år, så årstallet kan stå i tittelen. Avslutt skriptet med `citation`.
5. Brukeren kjører skriptet og melder tilbake. Rett feilen, og finnes den ikke allerede i
   `fallgruver.md`, foreslå at brukeren bidrar med den (se CONTRIBUTING.md i repoet).

## Datalagerversjon

Skriv `require no.ssb.fdb:<versjon> as fdb` øverst i skriptet. Siste versjon står i
`metadata/datalager.json`, men analysemiljøet kan ligge en versjon bak metadatasidene. **Spør
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
- `citation` nederst i skriptet gir én linje: «Analysen er gjennomført i microdata.no med datagrunnlag fra:
  SSB (registerdata). Data analysert: 2026-11-18» (versjon 60). Uten datalagerversjon og variabler, så oppgi
  `require`-versjonen selv. Med flere datalagre listes alle som står i `require`, også dem som ikke er brukt i
  `import` («FHI (Kreftregisteret), FHI (Norsk pasientregister) og SSB (registerdata)»). Ta bare med
  `require` for lagrene du bruker. Resultater skal ha microdata.no som kilde ved publisering
  (https://www.microdata.no/dokumentasjon/kildehenvisning/)

## Nettkilder (hvis lokale filer ikke strekker til)

| Hva | URL |
|---|---|
| Variabelliste | `https://microdata.no/discovery/variables?pageIndex={N}` (nullbasert, 20 per side, `&sortBy=LABEL&sortType=ASC`) |
| Variabeldetaljer | `https://microdata.no/discovery/variable/no.ssb.fdb/<versjon>/<NAVN>` |
| Manual | `https://microdata.no/manual/` (med avsluttende `/`) |

`https://microdata.no/discovery/` rendres med JavaScript og kommer tom tilbake.
`https://microdata.no/variable/...` (uten `/discovery/`) gir 404.

Flere eksempler (eldre og ikke kvalitetssikret): https://github.com/JOSliper/Microdata-skript.
Bruk dem bare som idékilde når `kodesnutter/` ikke dekker behovet. De bruker gamle
datalagerversjoner og har kjente feil.

## Konfidensialitet

Microdata.no undertrykker små celler og legger på støy. Unngå svært finfordelte tabeller og små
populasjoner. Resultatene kan avvike litt fra SSBs offisielle statistikk. Se også avsnittet om
avsløringskontroll i `referanser/fallgruver.md`.

Fra 17. november 2026 (versjon 60) gjelder **versjon 2 av anonymiseringstiltakene**: celler med 1–4 vises som
0, tabeller stoppes ikke, `replace`/`recode` på 1–9 enheter er tillatt, minste datasett er 100 personer,
regresjoner winsoriseres og nedsamples, og støyen endres når skriptet endres. Mye i `fallgruver.md` og
`TESTLISTE.md` ble avklart med versjon 1, og er merket slik. `configure confidentiality v1` gir de gamle
tiltakene (til 30. april 2027, ikke med FHI-data eller grunnkrets).
