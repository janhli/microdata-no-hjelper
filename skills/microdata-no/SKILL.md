---
name: microdata-no
description: Hjelp til å skrive og feilsøke skript for microdata.no (SSB/Sikt), det Stata-lignende skriptspråket for norske registerdata. Bruk skillen når brukeren nevner microdata.no, no.ssb.fdb, variabler som BEFOLKNING_*, INNTEKT_*, REGSYS_* eller NUDB_*, eller kommandoer som import-event, create-dataset og textblock, eller limer inn feilmeldinger eller resultater fra microdata.no.
---

# microdata.no

Microdata.no har sitt eget skriptspråk, som ligner Stata. Analysemiljøet krever innlogging, så du kan
ikke kjøre skript selv. Du skriver skriptet, brukeren kjører det i microdata.no og limer inn
feilmeldinger eller resultater, og du justerer.

## Lokale kilder (bruk dem før nettet)

Alle stier er relative til denne skill-mappen. Søk med Grep, og ikke les hele filene.

| Fil | Innhold |
|---|---|
| `metadata/variabler.csv` | Én linje per variabel (`;`-separert): navn, label, temporalitet, datatype, enhet, fra, til, antall koder, emner, beskrivelse, populasjon |
| `metadata/kodelister.csv` | Gjeldende kodeliste for alle variabler: `navn;kode;kategori` |
| `metadata/variabler/<NAVN>.json` | Full metadata: kodelistehistorikk, måletidspunkter (`temporalStatusDates`, dager siden 1970-01-01) og beskrivelser per periode |
| `metadata/datalager.json` | Versjonshistorikk for `no.ssb.fdb`, med hvilke variabler som er endret i hver versjon |
| `metadata/kommuneendringer.json` | Kommuneendringer fra SSB Klass 131 siden 1989 (gammel kode, ny kode, dato, navn). Brukes av `verktoy/kommuneomkoding.py` |
| `metadata/regioner/*.csv` | Koblingstabeller fra kommune (2024) til regioninndelinger: politidistrikt, valgdistrikt, økonomiske regioner, helseregioner, familievern, barnevern, reiseliv, samiske valgkretser, sentralitet, landsdeler og bo- og arbeidsmarkedsregioner. Kolonner `kommunenr;regionkode;regionnavn`. Oversikt i `INDEX.csv`, manuelt lastede filer i `manuelt/` |
| `metadata/manual/**/*.md` | Hele manualen som Markdown. Kommandoreferansen ligger i `kommandoer_og_funksjoner/kommandoer.md` og funksjonene i `.../funksjoner.md`. |
| `referanser/fallgruver.md` | Feil som ikke står (tydelig) i manualen, med feilmelding og løsning. **Les den før du leverer et skript.** |
| `kodesnutter/` | Frittstående og kommenterte snutter med teststatus: analysemal, alder, innvandringskategori, landbakgrunn, utdanning, arbeidsstyrkestatus, samliv, lavinntekt, verdi ved hendelse, mor–barn og forløp. Oversikt i `kodesnutter/README.md`. **Ta utgangspunkt i disse før du skriver noe selv.** |

Dato for siste nedlasting står i `metadata/HENTET`. Oppdater med `python verktoy/hent_variabler.py`
(`--alle` henter alt på nytt, ca. 6 min) og `python verktoy/hent_manual.py`.
Kommuneendringene oppdateres med `python verktoy/hent_kommuneendringer.py`.

## Kommunenumre over tid

Skal data fra flere år sammenlignes på kommune, må gamle kommunenumre omkodes til én inndeling.
Ikke skriv reglene for hånd. Kjør `python verktoy/kommuneomkoding.py --fra <år> --til <år> --navn <variabel>`
og lim `recode`-linjene inn i skriptet. Verktøyet lister kommuner som er delt i flere (f.eks. Tysfjord)
og lar dem stå uendret. Si fra til brukeren om disse. Se også «Geografi» i `referanser/fallgruver.md`.

For å gruppere kommuner i regioner (helseregion, politidistrikt, økonomisk region osv.): kjør
`python verktoy/regionomkoding.py <inndeling> --fra <kommunevariabel> --til <ny variabel>`
(`--liste` viser inndelingene). Tabellene gjelder kommunenummer i 2024-inndelingen, så omkod gamle
kommunenumre først. Oppdater tabellene med `python verktoy/hent_regioninndelinger.py`.

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
| Næring (SN2007), `REGSYS_NARING_SN2007` | 6 | `grupper 6 --nivaa 1 --dato 2024-01-01 --variabel REGSYS_NARING_SN2007 --navn naring` |
| Koblingstabeller (NUS til ISCED osv.) | 36, 6, 91 | `kobling 36` lister tabellene, `kobling 36 --tabell "ISCED 2011 Attainment" --navn nus` lager recode |
| Finne en annen klassifikasjon | | `sok yrke` |

Nivåene i hierarkiene: STYRK 1–4 er ett til fire siffer. NUS 1 er utdanningsnivå (0–9), 2 er nivå og
fagfelt, 5 er 6-sifret kode. SN 1 er seksjon (A–U), 2 er divisjon (`01`), 5 er femsifret kode (`01.110`).
Verdensinndeling 1 er verdensdel, 2 er region (f.eks. Norden, Subsaharisk Afrika), 3 er gruppe (`V111`),
4 er landkoden. `koder <id> --nivaa N` viser kodene på et nivå, så du kan velge riktig nivå først.

Fallgruver står i «Klass» i `referanser/fallgruver.md`. Les dem før du leverer skriptet. Resultatene er
ikke kjørt i microdata.no før brukeren har kjørt dem.

## Arbeidsflyt

1. Avklar tema, populasjon, år og geografi med brukeren.
2. Finn kandidatvariabler i `metadata/variabler.csv`. Sjekk dekningen (`fra`/`til`), koder i
   `metadata/kodelister.csv` og eksakt syntaks i `metadata/manual/`.
3. Les `referanser/fallgruver.md` og skriv skriptet. Det skal være kommentert, og kilde-URL skal
   stå ved hver variabel: `https://microdata.no/discovery/variable/no.ssb.fdb/<versjon>/<NAVN>`.
4. Sett en `textblock` ... `endblock` (Markdown) med tittel og en kort lesehjelp foran hver
   `tabulate`, `summarize` og `regress`. Ikke legg tabeller med tittel inne i `for`-løkker. Skriv dem
   ut for hvert år, så årstallet kan stå i tittelen.
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
- `tabulate`, `summarize`, `regress`, `logit`, `barchart`, `histogram`
- `let` og `for ... end` for løkker

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
