# Fallgruver i microdata.no

Erfaringer fra faktiske kjøringer som ikke står, eller står utydelig, i manualen. Hver fallgruve har:
**Symptom** (gjerne den eksakte feilmeldingen), **Årsak** og **Løsning**. Nye fallgruver legges til
med pull request (se CONTRIBUTING.md). Tagg dem med datalagerversjon/dato hvis de kan bli utdatert.

## Variabler og ID-er

### Pseudonymiserte ID-variabler kan ikke brukes i uttrykk
- **Symptom:** «Ulovlig bruk av pseudonymvariabel», f.eks. ved `drop if sysmiss(fnr_mor)`.
- **Årsak:** ID-variabler i formatet RandomUInt48 (`BEFOLKNING_MOR_FNR`, `*_FNR`,
  `ARBEIDSFORHOLD_PERSON` osv.) kan **bare** brukes i `by()` i `collapse`/`aggregate`, i `on` i
  `merge` og i `values_from()`.
- **Løsning:** Filtrer på en annen variabel, eller koble først og filtrer på resultatet. Se
  `metadata/manual/faq.md`.

### Datasett og variabler kan ikke ha samme navn
- **Symptom:** «Navnet er allerede brukt som et datasett».
- **Årsak:** f.eks. `create-dataset intro` etterfulgt av `import ... as intro`.
- **Løsning:** Gi datasett et eget navnemønster, f.eks. `introdata`.

### Statsborgerskap finnes ikke for hele befolkningen
- `ARBLONN_PERS_STATSBORGERSKAP` gjelder bare arbeidsforhold i a-ordningen. For hele befolkningen
  brukes `BEFOLKNING_LANDBAK3GEN`, `BEFOLKNING_FODELAND` og `BEFOLKNING_INVKAT`.

### Variabler som er avsluttet eller erstattet
- `REGSYS_YRKSTAT` gjelder bare til og med 2014. Fra 2015 brukes `REGSYS_ARB_ARBMARK_STATUS`, eller
  `ARBSTATUS_PERS_STATUS8` for prioritert status for alle bosatte 15+ (4. kvartal).
- Sjekk alltid `fra`/`til` i `metadata/variabler.csv` før du bruker en variabel fra et eldre skript.

### `BEFOLKNING_PARITET` mangler for de siste fødselskullene
- **Symptom:** 100 % ukjent paritet for barn født i 2025 (observert november 2026).
- **Løsning:** Utled paritet av mors tidligere fødsler, eller hold det siste året utenfor.

## Datoer og import

### Datoer ved import må ligge innenfor dekningen
- Sjekk `fra` og `til` i `metadata/variabler.csv`. Månedlige FDT-variabler (`*FDT_*`) slutter som
  regel den første i måneden, f.eks. 2024-12-01, ikke 2024-12-31.
- Forløpsvariabler som `NUDB_BU` har en siste dato som kan ligge langt bak inneværende år.

### Importfiltre: `values()` og `values_from()` (fra juli 2026)
- `import ..., values("0301", "4601")` importerer bare enheter med disse kodene. Bruk det på den
  **første** importen i et datasett, der filteret bestemmer populasjonen. Ved senere import er det
  uklart om det filtrerer eller bare gir manglende verdier, så der brukes `keep if`.
- `import <nøkkelvariabel>, values_from(datasett)` importerer bare rader der nøkkelverdien finnes som
  enhet i datasettet. Det fungerer for variabler med keyType PERSON (`BEFOLKNING_MOR_FNR`,
  `BEFOLKNING_FAR_FNR`, `ARBEIDSFORHOLD_PERSON`). Eksempel for barn av en mødrepopulasjon:
  `import fdb/BEFOLKNING_MOR_FNR as fnr_mor, values_from(mor)`.
- Manual: `metadata/manual/brukermanual/Oppretting og endring av datasett/2.6 Filtrering av datasettutvalg.md`.

## Tabeller og statistikk

### `median` er ikke gyldig i `tabulate ..., summarize(x)`
- Gyldige valg: `mean` (standard), `std`, `sum`, `p25`, `p50` (median), `p75`, `gini`, `iqr`.
- Til sammenligning bruker `collapse` og `aggregate` `(median)`.

### `Frekvens` i `tabulate gr, summarize(x) mean freq` er antall enheter
- Frekvensen er antall enheter i datasettet (f.eks. kvinner), ikke summen av x. Ta med `sum` når x
  er en telling (f.eks. antall fødsler), og forklar radene i en `textblock`.

### Manglende verdier i sammenligninger er udokumentert
- Hvordan `sysmiss` håndteres i `if`-sammenligninger er ikke dokumentert. Avslutt alltid grupperinger
  med `replace gr = 'ukjent' if sysmiss(x)`, så ingen enheter havner i feil gruppe i stillhet.

## Avsløringskontroll

### Tabeller på små delgrupper stoppes
- **Symptom:** Tabellen blir ikke vist, f.eks. `tabulate far_landbak if far_kat == '4', top(15)` på
  en liten gruppe.
- **Løsning:** Grupper til få, store kategorier, og tabuler for hele datasettet uten `if`.

### `replace`/`recode` må endre minst 10 enheter
- En `replace` eller `recode` som treffer færre enn 10 enheter blir avvist. Slå sammen kategorier
  eller endre rekkefølgen på omkodingen.

## Geografi

### Kommune- og fylkesnummer endres med regionreformene
- Fylke hentes med `substr(BEFOLKNING_KOMMNR_FORMELL, 1, 2)`.
- Fylkesnumrene fra 2024 gjelder: 31 Østfold, 32 Akershus, 33 Buskerud osv. Kommuner i Viken (30xx)
  i 2020–2023 må omkodes til nummeret de fikk i 2024 (31xx/32xx/33xx) før du sammenligner over tid.
  Tilsvarende gjelder Vestfold og Telemark (38xx → 39xx/40xx) og Troms og Finnmark (54xx → 55xx/56xx).

## Alder

- For å treffe Statistikkbanken beregnes alder ved utgangen av året før:
  `år - 1 - int(BEFOLKNING_FOEDSELS_AAR_MND/100)`.
