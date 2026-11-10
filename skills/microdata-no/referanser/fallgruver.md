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

### `merge` kjøres fra datasettet variablene ligger i
- **Symptom:** «Feil ved snitt3: Variabelen snitt3 eksisterer ikke» på `merge snitt3 vlav into barn`.
- **Årsak:** `merge` henter variablene fra det **aktive** datasettet. `create-dataset barn` gjør `barn`
  aktivt, så variablene fra forrige datasett finnes ikke der.
- **Løsning:** `use <kildedatasett>` før `merge ... into <måldatasett>`, og `use <måldatasett>` etterpå.

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

### Sektor på personnivå er stoppet etter 2019
- **Symptom:** `REGSYS_FRTK_SEKTOR_2014` har ingen data etter 2019-11-16.
- **Årsak:** SSB stoppet variabelen av personvernhensyn (risiko for å avsløre opplysninger om foretak).
- **Løsning:** For lønnstakere: bruk `ARBLONN_FRTK_SEKTOR_2014` på jobbnivå og velg sektoren med mest
  avtalt arbeidstid per person. Se `kodesnutter/sektor_lonnstakere.txt`, som treffer SSB tabell 13926
  innenfor 0,1 % for stat og kommune (4. kvartal 2025, versjon 59). Selvstendige kommer ikke med.

### `BEFOLKNING_PARITET` mangler for de siste fødselskullene
- **Symptom:** 100 % ukjent paritet for barn født i 2025 (observert november 2026).
- **Løsning:** Utled paritet av mors tidligere fødsler, eller hold det siste året utenfor.

### `BOFORHOLD_EIE_LEIE` gir færre leiere enn Statistikkbanken
- **Symptom:** 1.1.2024 gir 23,6 % leiere blant husholdninger koblet til bolig, mot 27,4 % i SSB tabell
  14897. Antall husholdninger er det samme (2 584 506 mot 2 584 517), men ca. 98 000 er selveiere i
  microdata.no og leiere i Statistikkbanken. SSB-tabellen ligger på 27–28 % leiere for hele 2015–2025.
- **Årsak (bekreftet november 2026, versjon 59):** Husholdninger som er *statistisk koblet* til bolig
  (`BOFORHOLD_KOBLNIVAA_HUSH_BOLIG = STAT`, 293 143 husholdninger) får anslått (imputert) eierstatus.
  I microdata.no er 51,6 % av dem eiere, mens bare 13–15 % har registrert eierskap i Matrikkelen,
  Grunnboken eller skattemeldingen. Med 13–15 % eiere i denne gruppen blir det 716 000–721 000 leiere,
  mot 707 784 i tabell 14897. SSB har revidert eierstatus med tidsserier bakover, mens `BOFORHOLD_*`
  i microdata.no (til 1.1.2024) bruker den gamle metoden. Direkte koblede husholdninger (DIR) har
  20,4 % leiere, så de alene er heller ikke representative.
  Kilde: [SSB, notat 2026/17](https://www.ssb.no/bygg-bolig-og-eiendom/bolig-og-boforhold/artikler/boforholdsregisteret-dokumentasjon-og-revisjon-av-eierstatus-variabel).
- **Løsning:** Sammenlign ikke eierandeler direkte med Statistikkbanken. Vis statistisk koblede
  husholdninger som egen gruppe, eller regn eierstatus for dem som usikker. Unge, aleneboende og
  husholdninger med lav inntekt er overrepresentert blant dem, så feilen er størst for de gruppene.
  Se `kodesnutter/bolig.txt`.

### Bolig og husholdning er ikke egne enheter
- Alle `BOFORHOLD_*`-variabler er boligens egenskaper lagt på hver beboer. Husholdningen finnes bare som
  nøkkelen `BEFOLKNING_HUSHNR`. Én rad per husholdning (og per bebodd bolig) får du med
  `if kontakt == '1'` (`BEFOLKNING_KONTAKT_HUSHNR`). Se `kodesnutter/husholdning.txt` og `bolig.txt`.
- `hushnr` finnes også for institusjoner og felleshusholdninger (ca. 39 000 personer). De har ikke
  husholdningsstørrelse. Ta dem ut med `drop if sysmiss(<BEFOLKNING_PERS_I_HUSHNR>)` før `collapse`, ellers
  får du «husholdninger» med 30–40 barn.

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

### Region i Statistikkbankens lønnstakertabeller er arbeidssted
- **Symptom:** Antall lønnstakere i en kommune er langt lavere enn i SSB tabell 13926 (Bergen 2025K4:
  154 082 etter bosted mot 182 619 i tabellen).
- **Årsak:** Tabellen fordeler etter arbeidsstedet for hovedarbeidsforholdet. `REGSYS_ARB_ARBKOMM` gir
  heller ikke samme tall, fordi den bare har bosatte sysselsatte 15–74 år.
- **Løsning:** Bruk `ARBLONN_ARB_ARBKOMM` for jobben der `ARBLONN_ARB_HOVEDARBEID == '1'`. Det ga
  182 609 for Bergen (testet november 2026, versjon 59).

### Manglende verdier i sammenligninger er udokumentert
- Hvordan `sysmiss` håndteres i `if`-sammenligninger er ikke dokumentert. Avslutt alltid grupperinger
  med `replace gr = 'ukjent' if sysmiss(x)`, så ingen enheter havner i feil gruppe i stillhet.

## Bindinger og løkker

### Variabelnavn fra en iterator
- **Symptom:** «Feil ved generate: Syntaksfeil» på `generate t$i = 0` inne i en `for`-løkke.
- **Årsak:** `$i` limes ikke inn i et navn. Navn settes sammen med `++`.
- **Løsning:** `let v = tid_ ++ $i` og deretter `generate $v = 0`. Bruk `let` i stedet for `++` direkte
  i kommandoen, for det virker ikke i `collapse`, `aggregate`, `recode` og `reshape-to-panel`
  (manualen, 6.2 Løkker).

### Navn som er funksjonsnavn
- **Symptom:** «Feil ved t: Kan ikke bruke funksjonen t i en binding» på `let t = t ++ $i`.
- **Årsak:** `t` er en funksjon (Students t-fordeling). Bindinger og variabler kan ikke hete det samme
  som en funksjon.
- **Løsning:** Bruk beskrivende navn, og sjekk korte navn mot `metadata/manual/kommandoer_og_funksjoner/funksjoner.md`.

## Avsløringskontroll

### Tabeller på små delgrupper stoppes
- **Symptom:** Tabellen blir ikke vist, f.eks. `tabulate far_landbak if far_kat == '4', top(15)` på
  en liten gruppe.
- **Løsning:** Grupper til få, store kategorier, og tabuler for hele datasettet uten `if`.

### `collapse`/`aggregate` med `sum` winsoriseres når `by()` er en vanlig variabel
- **Symptom:** Antall tilfeller per kommune (eller fylke, utdanningsnivå osv.) blir feil, særlig for små
  grupper, når de telles med `collapse (sum) dummy, by(kommune)`.
- **Årsak:** Anonymiseringstiltaket winsorisering slår inn når det aggregeres til en vanlig variabel. Det
  gjelder ikke når `by()` er en pseudonymisert enhet (personid, familieid, husholdningsid, jobbid).
  `count`, `median` og `percent` påvirkes ikke. (Manualen, 3.5 collapse, oppdatert i versjon 59.)
- **Løsning:** Tell med `(count)`. `count` teller alle gyldige verdier, også 0, så sett dem som ikke skal
  telles til missing først. Bruk `sum` bare til å summere verdier. Det går fint å summere per person
  før man aggregerer videre, slik `kodesnutter/sektor_lonnstakere.txt` gjør.

### `replace`/`recode` må endre minst 10 enheter
- En `replace` eller `recode` som treffer færre enn 10 enheter blir avvist. Slå sammen kategorier
  eller endre rekkefølgen på omkodingen.
- I `recode` gjelder grensen **hver målverdi for seg**, ikke kommandoen samlet. Én liten regel stopper
  hele kommandoen. Symptom: «Stoppet av avsløringskontroll. Omkodingen til 9 påvirker for få enheter»
  (`(990 = 9)` for uoppgitt landbakgrunn, versjon 59, november 2026). Slå små koder sammen med en
  større gruppe i samme regel. Er de små til sammen også (`(980 989 990 = 8)` ble også stoppet), la
  dem stå uomkodet og gi dem navn med `define-labels`.
- En regel som treffer **0** enheter stoppes ikke (TESTLISTE 1.7). Utskrift med koder som ikke finnes i
  dataene (f.eks. gamle kommunenumre fra `kommuneomkoding.py`) er derfor trygg.
- Detaljerte koblinger (f.eks. `klass.py kobling` mellom SN2002 og SN2007 på femsifret nivå) har ofte
  målkoder med 1–9 personer, og stoppes. Feilmeldingen nevner bare én målkode om gangen («Omkodingen til
  17.240 påvirker for få enheter»). Ta ut målkodene med `klass.py ... --utelat 17.240,...`. Raskest:
  `tabulate` kildevariabelen først, og ta ut alle målkoder med under 20 personer eller uten synlige
  kilder på én gang (SN2002 → SN2007 gikk gjennom i tredje runde, 33 av 410 målkoder tatt ut).
- Koblinger med koder som har flere mål blander kodeverk: SN2002 → SN2007 lot 42 % av sysselsatte
  (november 2006) stå med SN2002-kode. Gruppering på de første sifrene blir da feil (f.eks. «85» er helse
  i SN2002 og undervisning i SN2007).

## Geografi

### Kommune- og fylkesnummer endres med regionreformene
- Fylke hentes med `substr(BEFOLKNING_KOMMNR_FORMELL, 1, 2)`.
- Fylkesnumrene fra 2024 gjelder: 31 Østfold, 32 Akershus, 33 Buskerud osv. Kommuner i Viken (30xx)
  i 2020–2023 må omkodes til nummeret de fikk i 2024 (31xx/32xx/33xx) før du sammenligner over tid.
  Tilsvarende gjelder Vestfold og Telemark (38xx → 39xx/40xx) og Troms og Finnmark (54xx → 55xx/56xx).
- Bruk `python verktoy/kommuneomkoding.py` til å lage `recode` fra gamle til nyere inndeling
  (data: SSB Klass 131 i `metadata/kommuneendringer.json`). Fallgruver:
  - Delte kommuner (Varteig 0114, Stokke 0720, Snillfjord 1613 og 5012, Tysfjord 1850) kan ikke
    omkodes uten adresse. Verktøyet lar dem stå uendret, og de vises som gamle koder i tabellen.
  - Når Ålesund ble delt i 2024 (Haram ut igjen), kjedes de gamle kodene via navn. Haram 1534 blir 1580,
    og Ørskog, Skodje og Sandøy blir 1508. Verktøyet lister slike valg som «kontroller».
  - Klass dekker ikke Svalbard-kodene 2111, 2112, 2115, 2121 og 2131 (i kodelisten til
    `BEFOLKNING_KOMMNR_FORMELL`). Legg dem til for hånd hvis de skal slås sammen til 2100.
  - Klass har endringer til 2026 (bl.a. Indre Østfold). Standard er `--til 2024`.
- Regiontabellene i `metadata/regioner/` gjelder kommunenummer i 2024-inndelingen. Gamle kommunenumre
  står uendret hvis de ikke omkodes først, og blir stående som kommunekode i regionvariabelen.
  Kontroller med `tabulate`, eller bruk `--ukjent` (se neste punkt).
  - `recode (* = ...)` må stå som siste regel i samme kommando som de andre reglene. I en egen kommando
    treffer den alle verdier, også de som allerede er omkodet. Derfor lager `regionomkoding.py` ingen
    sluttregel som standard. `--ukjent` gir én lang kommando. microdata.no har godtatt 2 789 tegn
    (versjon 59, november 2026), og sluttregelen virker som forventet (TESTLISTE 1.1 og 1.2).
  - Regionene er dagens inndeling. Politidistrikt (2016), helseregioner (2007), barnevern (2004) og
    samiske valgkretser (2009) har eldre versjoner enn 2024, og tabellene viser dagens kobling.
  - Helseregionene har bare tabell mot Kommuneinndeling 2020 hos Klass. Kommunekodene er oversatt
    til 2024 med Klass' kommuneendringer (merket i `INDEX.csv`).
  - Sentralitet er en gruppering etter SSBs indeks, ikke sammenhengende regioner.
  - Bo- og arbeidsmarkedsregioner (TØI) finnes ikke i Klass og er lastet inn manuelt.
    Se `metadata/regioner/manuelt/README.md`.

## Klass

- **Velg riktig versjon med `--dato`.** `klass.py` bruker kodene som gjelder på datoen (standard i dag). SN2007-variabler
  må ha en dato før 2025-01-01, ellers får du SN2025 (Klass 6 har fire versjoner: SN 1994, SN 2002, SN 2007 og SN 2025).
  For NUS, STYRK og landkoder er det samme prinsipp: bruk en dato fra perioden dataene dekker.
- **Variablene har koder som ikke finnes i Klass.** Med `--variabel` listes slike koder i en kommentar og står uendret:
  - Landkoder: utgåtte land (Sovjetunionen 135, DDR 151), «uspesifisert»/«Resten av …» (194, 394, 594 osv.) og 989
    (uoppgitt utenlandsk statsborgerskap). Omkod dem for hånd, f.eks. til «Uoppgitt».
  - STYRK: `XXXX` (uoppgitt/ukjent).
  - SN2007: sammenfattede koder som `01.000` og `00.000`, og koder som ikke finnes i SN2007 i Klass på datoen (f.eks. `10.100`, `55.100`). Sjekk dem mot kodelisten før du omkoder dem.
- **Resultatet er en kopi av kodene i Klass akkurat nå.** Klassifikasjoner endres. Oppgi hentedato i skriptet (verktøyet
  skriver den i en kommentar).
- **Koblingstabeller kan være mange-til-mange.** `kobling` utelater koder som går til flere mål, og koder uten
  motpart (Klass har rader uten mål, f.eks. `46.890` i SN2025–SN2007), og lister dem i en kommentar.
- **Samme kode som kilde i én regel og mål i en annen** (vanlig mellom versjoner, f.eks. `25.300 -> 25.400` og
  `25.400 -> 25.500`): står reglene i ulike `recode`-kommandoer, omkodes verdien to ganger. Verktøyene samler
  slike regler i første kommando. Ikke del den linjen, og ikke flytt regler mellom linjene.
- **`recode` på strenger.** Koder som `'01.110'` og `'0110'` må skrives som strenger. Landkodene i `BEFOLKNING_LANDBAK3GEN` er
  strenger. Snutten `landbakgrunn_region.txt` bruker `destring` og tallintervaller. Det går også, men verktøyets
  utskrift er strenger og skal ikke kombineres med `destring`.
- **Landkodene i microdata er SSB-3 (Klass 91).** Verdensinndeling (545) bruker samme landkoder som blader. Gruppering
  av land (546) skiller EU/EFTA fram til 2004 fra nye EU-land etter 2004. Det er ikke dagens EU/EØS-medlemskap.

## Alder

- For å treffe Statistikkbanken beregnes alder ved utgangen av året før:
  `år - 1 - int(BEFOLKNING_FOEDSELS_AAR_MND/100)`.
