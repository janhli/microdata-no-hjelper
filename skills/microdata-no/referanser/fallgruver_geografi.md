# Fallgruver med geografi

## Kommune- og fylkesnummer endres med regionreformene
- Fylke hentes med `substr(BEFOLKNING_KOMMNR_FORMELL, 1, 2)`. Navn og kontrolltall: `kodesnutter/fylke.txt`.
- Fylkesnumrene fra 2024 gjelder: 31 Østfold, 32 Akershus, 33 Buskerud osv. Kommuner i Viken (30xx)
  i 2020–2023 må omkodes til nummeret de fikk i 2024 (31xx/32xx/33xx) før du sammenligner over tid.
  Tilsvarende gjelder Vestfold og Telemark (38xx → 39xx/40xx) og Troms og Finnmark (54xx → 55xx/56xx).
- Bruk `python verktoy/kommuneomkoding.py` til å lage `recode` fra gamle til nyere inndeling
  (data: SSB Klass 131 i `metadata/kommuneendringer.json`). Fallgruver:
  - Delte kommuner (Varteig 0114, Stokke 0720, Snillfjord 1613 og 5012, Tysfjord 1850) kan ikke
    omkodes på kommunekoden alene. Verktøyet lar dem stå uendret, og de vises som gamle koder i tabellen.
    Fra 1990 fordeler `--grunnkrets <variabel>` personene etter grunnkretsen på samme dato (`BEFOLKNING_GRUNNKRETS`,
    Klass 1). Det gjelder også Ålesund/Haram 2020–2023 og kommuner valgt ved navn. Grunnkretser som selv er
    delt (f.eks. 2 i Stokke 2015, 3 i Indre Østfold 2025) og uoppgitt (`kkkk9999`) står med kommunekoden.
    Testet (versjon 60, 2026-11-23, TESTLISTE 2.9): 88–98 % havnet i kommunen de bodde i året etter delingen, og
    resten ser ut som flytting. Men de to delte grunnkretsene i Stokke har 13 % av befolkningen, så Stokke står
    fortsatt delvis igjen. Si fra om det. Koder som
    ikke finnes i kodelisten på datoen (1580 Haram i 2023), får navn med en regel til samme verdi, som
    verktøyet lager (TESTLISTE 2.10).
  - **Merkelapp på en kode som ikke fantes:** `recode kommune ('1580' = '1580' 'Haram')` gir navnet, både før
    og etter at noen har verdien (`replace` etterpå får også navnet). Testet med versjon 60, 2026-11-23.
  - Når Ålesund ble delt i 2024 (Haram ut igjen), kjedes de gamle kodene via navn. Haram 1534 blir 1580,
    og Ørskog, Skodje og Sandøy blir 1508. Verktøyet lister slike valg som «kontroller».
  - **Ålesund 1507 (2020–2023) omkodes helt til 1508, også Haram** (TESTLISTE 2.4). Koden kan ikke deles uten
    adresse. Verktøyet lister slike koder under «Koder som selv ble delt». Trenger du Haram for 2020–2023,
    bruk kommunen personen bodde i 1.1.2019 eller 1.1.2024.
  - Omkodingen er kontrollert mot SSB tabell 07459: alle kommuner innenfor ±5 (støy) for 1.1.2010 omkodet
    til 2024 og for 1.1.2024 (versjon 59). Verktøyet gir kommunene det omkoder til navnet i den nye
    inndelingen, så nye koder (1108 Sandnes, 3101 Halden) får navn også i gamle årganger. Koder som ikke
    omkodes, beholder navnet fra kodelisten på datoen (1826 Hattfjelldal, ikke Aarborte - Hattfjelldal).
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

## Grunnkrets (`BEFOLKNING_GRUNNKRETS`, fra versjon 60)
Kartlagt fra metadataene og SSB Klass (november 2026), og testet i microdata.no med versjon 60 (TESTLISTE
del 11, 2026-11-19).
- **De fire første sifrene er bostedskommunen** på samme dato (lik `BEFOLKNING_KOMMNR_FORMELL` for alle
  1.1.2026, 11.2).
- **Koden skifter med kommunenummeret.** Grunnkrets `15040101` (Ålesund 2019) er `15070101` i 2020–2023 og
  `15080101` fra 2024. Over 10 000 koder ble byttet i 2020 og 6 000 i 2024. Koble aldri grunnkretser fra
  ulike år direkte. Bruk `verktoy/grunnkrets.py --aar <år>`, som følger kodene gjennom Klass-endringene.
- **Små enheter:** mange grunnkretser har under 10 beboere. Tabeller på grunnkrets (og delområde) får mange
  celler med 1–4, som vises som 0. Kod rett til delområde, levekårssone, bydel eller egne områder.
  Verktøyet tar med alle grunnkretsene i hver målenhet i samme regel, også de uendrede. Det gir kortere
  skript enn å gå via gjeldende grunnkrets. (Grunnkrets kan ikke brukes med `configure confidentiality v1`,
  testet i 11.7, så 10-enhetsregelen fra versjon 1 gjelder ikke her.)
- **Delte grunnkretser:** noen grunnkretser er senere delt mellom flere delområder eller soner (334 fra
  1990, 59 fra 2019, 3 fra 2025 på grunnkretsnivå, langt færre på sone- og delområdenivå). De kan ikke
  fordeles uten adresse og står uendret (8 tegn) med `--splitt behold` (11.8). Si fra om dem, eller bruk `--splitt forste`.
- **Uoppgitt grunnkrets** har koden `kkkk9999` i hver kommune (360 koder i 2026) og står uendret. Det
  gjelder under 0,5 % av de bosatte (11.8).
- **Kodelisten har også delområdene** (6 sifre, med navn). Dataene har bare 8-sifrede koder (11.1).
- **Delområde** er de seks første sifrene i *gjeldende* kode. For eldre år gir `substr(gk, 1, 6)` det gamle
  delområdet med gammelt kommunenummer. `grunnkrets.py --til delomrade` omkoder bare delområdene som har
  endrede koder, og tar resten med `substr`.
- **Levekårssoner** finnes i Klass for 66 kommuner (2026-inndelingen, ikke Oslo). Bydeler finnes for Oslo,
  Bergen, Trondheim og Stavanger, delbydeler for Oslo. Alle bygger på 2026-grunnkretsene.
- **`BEFOLKNING_BYDEL` gir de samme bydelene som `grunnkrets.py --til bydel`** (TESTLISTE 11.9).
  Uoppgitt er `kkkk99` i `BEFOLKNING_BYDEL` og `kkkk9999` fra grunnkrets, og noen få personer har grunnkrets, men
  manglende `BEFOLKNING_BYDEL`.
- **Grunnkrets kan brukes med alle personvariabler og med FHI-data** under versjon 2 (lønn etter delområde,
  krefttilfeller koblet til bosatte med grunnkrets, 11.10–11.11). Delområder laget med `substr` har ikke navn.
- **Lange skript går.** Hele landet fra 2015 til delområde (160 kB, over 300 `recode`-linjer) ble godtatt
  (11.6), og alle 2015-kodene i dataene ble omkodet til delområder som finnes i 2026 (11.8). Begrens med
  `--kommune` når analysen bare gjelder noen kommuner, så blir skriptet lettere å lese.
