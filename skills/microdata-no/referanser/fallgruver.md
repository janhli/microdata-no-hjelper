# Fallgruver i microdata.no

Erfaringer fra faktiske kjøringer som ikke står, eller står utydelig, i manualen. Hver fallgruve har:
**Symptom** (gjerne den eksakte feilmeldingen), **Årsak** og **Løsning**. Nye fallgruver legges til
med pull request (se CONTRIBUTING.md). Tagg dem med datalagerversjon/dato hvis de kan bli utdatert.
Tallene fra testkjøringene står i TESTLISTE.md i repoet (numre som 8.12) og i `kodesnutter/TESTRESULTATER.md`.

Denne filen gjelder alle skript. Les i tillegg hele temafilen når skriptet bruker temaet:

| Skriptet bruker | Les |
|---|---|
| Regresjon, `correlate`, overlevelsesanalyse, paneldata eller andre statistiske analyser | `fallgruver_analyse.md` |
| Kommune, fylke, region, bydel eller grunnkrets | `fallgruver_geografi.md` |
| Næring, eller yrke, utdanning eller landbakgrunn gruppert etter Klass (`klass.py`) | `fallgruver_klass.md` |
| `no.fhi.kreftregisteret` eller `no.fhi.npr` | `fallgruver_fhi.md` |

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

### `collapse` endrer det aktive datasettet
- **Symptom:** «Feil ved kreftform: Variabelen kreftform eksisterer ikke» etter en `collapse` tidligere i skriptet.
- **Årsak:** `collapse` lager ikke et nytt datasett. Det gjør om det aktive datasettet til ett per `by()`-enhet
  med bare de aggregerte variablene. De andre variablene er borte (versjon 60, november 2026).
- **Løsning:** `clone-dataset kilde kopi` og `use kopi` før `collapse` når kilden skal brukes videre.

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

### NEET: bruk `ARBSTATUS_PERS_NEET`, ikke en egen definisjon
- SSBs NEET-variabel (15–29 år, november) traff tabell 13556 innen ±3 personer (versjon 60, 2026-11-23,
  `kodesnutter/neet.txt`). Importer den først i et tomt datasett, med alder og bosted fra `ARBSTATUS_PERS_ALDER`
  og `ARBSTATUS_PERS_KOMM_NR` (datoene er den 30.), så populasjonen og gruppene blir som hos SSB.
- Lager du NEET selv fra `ARBSTATUS_PERS_STATUS8`: bare sysselsatte (0808, 0816, 0832, 1608), ordinær utdanning
  (4008) og tiltak (3208, 3216 tiltakspenger, 3240 introduksjonsprogram, 4816) er utenfor NEET. Dagpenger (3224)
  og sykepenger (4808) er NEET. Snutten `arbeidsstyrkestatus.txt` legger dagpenger i «andre», ikke i ledig.
- Over halvparten av NEET-gruppen har ukjent status (7208).
- NEET etter registrert utdanning fra `NUDB_BU` er en tilleggsanalyse. Langt flere har uoppgitt eller ingen
  utdanning enn i tabell 12423. Snutten bruker 1. august. SSB bruker 1. oktober, imputerer
  utdanningsnivå for innvandrere med uoppgitt nivå og koder de fleste 15-åringene og en del 16-åringer som å
  ha fullført grunnskolen. Vis antallet med uoppgitt eller ingen utdanning når du bruker `NUDB_BU`, og bruk
  tabell 12423 hvis du trenger de publiserte tallene. [SSBs metodebeskrivelse](https://www.ssb.no/arbeid-og-lonn/sysselsetting/statistikk/tilknytning-til-arbeid-utdanning-og-velferdsordninger/#om-statistikken)
- Dekker bare til 2024-11-16. Brudd mellom 2014 og 2015.

### Sektor finnes ikke etter 2019
- **Symptom:** `REGSYS_FRTK_SEKTOR_2014` har ingen data etter 2019-11-16, og `ARBLONN_FRTK_SEKTOR_2014`
  (jobbnivå, 2015–2026) finnes ikke fra versjon 60.
- **Årsak:** SSB stoppet personvariabelen av personvernhensyn (risiko for å avsløre opplysninger om foretak),
  og slettet jobbvariabelen i versjon 60 (november 2026, ingen erstatning).
- **Løsning:** Sektor kan bare brukes til og med 2019 (`REGSYS_FRTK_SEKTOR_2014`, 4. kvartal). Si fra til
  brukeren at nyere sektortall ikke finnes i microdata.no.
- **Metoden som traff SSB tabell 13926 innenfor 0,1 % (versjon 59):** sektor per jobb, avtalt arbeidstid
  summert per sektor med `collapse (sum) ..., by(personid)` (personid fra `ARBEIDSFORHOLD_PERSON`), og
  sektoren med mest arbeidstid per person. Region i tabellen er arbeidssted for hovedarbeidsforholdet. Snutten
  er arkivert i `arkiv/kodesnutter/sektor_lonnstakere.txt` i repoet.

### `BEFOLKNING_PARITET` mangler for de siste fødselskullene
- **Symptom:** 100 % ukjent paritet for barn født i 2025 (observert november 2026).
- **Løsning:** Utled paritet av mors tidligere fødsler, eller hold det siste året utenfor.

### `BOFORHOLD_EIE_LEIE` gir færre leiere enn Statistikkbanken
- **Symptom:** 1.1.2024 gir 23,6 % leiere blant husholdninger koblet til bolig, mot 27,4 % i SSB tabell
  14897, selv om antall husholdninger er det samme.
- **Årsak (bekreftet november 2026, versjon 59):** Husholdninger som er *statistisk koblet* til bolig
  (`BOFORHOLD_KOBLNIVAA_HUSH_BOLIG = STAT`) får anslått (imputert) eierstatus, og for mange blir eiere.
  SSB har revidert eierstatus med tidsserier bakover, mens `BOFORHOLD_*` i microdata.no (til 1.1.2024)
  bruker den gamle metoden. Direkte koblede husholdninger (DIR) alene er heller ikke representative.
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

### Faste variabler (`FIXED`) importeres uten dato
- **Symptom:** «Denne registervariabelen tar ikke et datoargument siden den har temporalitet: 'Fast'».
- **Årsak:** Variabelen har én verdi per enhet (kolonnen `temporalitet` i `variabler.csv` er `FIXED`), f.eks.
  `BEFOLKNING_LANDBAK3GEN`, `BEFOLKNING_KJOENN`, `BEFOLKNING_FOEDSELS_AAR_MND` og alle FHI-variablene.
- **Løsning:** `import fdb/BEFOLKNING_LANDBAK3GEN as landbak`, uten dato. Sjekk `temporalitet` før du skriver
  importlinjen. Populasjonen avgrenses av variablene som har dato (f.eks. bostedskommune).
- Versjon 60, 2026-11-19.

### Importfiltre: `values()` og `values_from()` (fra juli 2026)
- `import ..., values("0301", "4601")` importerer bare enheter med disse kodene. Bruk det på den
  **første** importen i et datasett, der filteret bestemmer populasjonen. Ved senere import er det
  uklart om det filtrerer eller bare gir manglende verdier, så der brukes `keep if`.
- `import <nøkkelvariabel>, values_from(datasett)` importerer bare rader der nøkkelverdien finnes som
  enhet i datasettet. Det fungerer for variabler med keyType PERSON (`BEFOLKNING_MOR_FNR`,
  `BEFOLKNING_FAR_FNR`, `ARBEIDSFORHOLD_PERSON`). Eksempel for barn av en mødrepopulasjon:
  `import fdb/BEFOLKNING_MOR_FNR as fnr_mor, values_from(mor)`.
- Manual: `metadata/manual/brukermanual/Oppretting og endring av datasett/2.6 Filtrering av datasettutvalg.md`.

### Datoer er tall i formatet ÅÅÅÅMMDD, ikke dager
- **Symptom:** Tid til hendelse (`dod - date(2024, 1, 1)`) blir rundt 20 millioner i stedet for et antall
  dager (versjon 60, november 2026).
- **Årsak:** `BEFOLKNING_DOEDS_DATO`, `BEFOLKNING_FORSTDATO` og `INTRO_*_DATO` er tall som `20240315`
  (`format: YYYYMMDD` i `metadata/variabler/<NAVN>.json`). `date()` gir dager siden 1970-01-01. 24 variabler
  har `YYYYMM` (f.eks. `BEFOLKNING_FOEDSELS_AAR_MND`) og 4 har `YYYY`.
- **Oversikt** (`dataType` og `format` i `metadata/variabler/<NAVN>.json`, versjon 60):

  | Lagring | Eksempler | Regne med `date()` |
  |---|---|---|
  | `START@`/`STOP@` fra `import-event` | `START@astatus` | Ja, dager siden 1970 (manualens eksempler) |
  | `date@panel` fra `import-panel` | | Ja, `year(date@panel)` virker |
  | `Instant` (5) | `ARBLONN_ARB_START`/`_SLUTT`, `SOM_EP_INNDATO`/`_UTDATO`, `S_DIAGNOSEDATO` | Ja, dager siden 1970 (testet for `S_DIAGNOSEDATO` og `SOM_EP_INNDATO`, TESTLISTE 10.9) |
  | `Long` ÅÅÅÅMMDD (5) | `BEFOLKNING_DOEDS_DATO`, `BEFOLKNING_FORSTDATO`, `INTRO_*_DATO`, `INTRO_GJENNOMFORINGSFRIST` | Nei, regn om (TESTLISTE 8.10) |
  | `Long` ÅÅÅÅMM (24) | `BEFOLKNING_FOEDSELS_AAR_MND`, `ARBEIDSSOKER_DAGDATO1`, `KRIMINALITET_SIKTEDE_*DATO` | Nei, `int(x/100)` gir året |
  | ÅÅÅÅ (5) | `BOFORHOLD_BYGGEAAR`, `KJORETOY_FREG_AR`, `BARNEVERN_FODTAAR` (tekst), `SOM_EP_AAR` (tekst) | Rene årstall |

  Navnet sier lite om formatet: `KRIMINALITET_SIKTEDE_GJDATO1` er ÅÅÅÅMM.
- **Løsning:** Sjekk `format` i JSON-filen. Gjør om til dager før du regner med datoer (testet versjon 60,
  TESTLISTE 8.10):
  `generate dag_aar = int(dod/10000)`, `generate dag_mnd = int(dod/100) - dag_aar*100`,
  `generate dag_dag = dod - int(dod/100)*100` og `generate doddag = date(dag_aar, dag_mnd, dag_dag)`.
  Sammenligning med en dato kan gjøres direkte på tallet: `dod >= 20240101`.

## Tabeller og statistikk

### `median` er ikke gyldig i `tabulate ..., summarize(x)`
- Gyldige valg: `mean` (standard), `std`, `sum`, `p25`, `p50` (median), `p75`, `gini`, `iqr`.
- Standardavvik er `std`, ikke `sd` (Stata). `sd` stopper skriptet.
- Til sammenligning bruker `collapse` og `aggregate` `(median)`.

### `summarize()` i `tabulate` tar bare én variabel
- **Symptom:** «Feil ved hendelse_b): Syntaksfeil» for `tabulate gr, summarize(a b) mean`.
- **Løsning:** Én `tabulate` per variabel. For flere variabler i samme tabell: `summarize a b` med `if`
  per gruppe, eller `collapse (mean) a b, by(gr)` på en kopi av datasettet. Versjon 60, 2026-11-19.

### `Frekvens` i `tabulate gr, summarize(x) mean freq` er antall enheter
- Frekvensen er antall enheter i datasettet (f.eks. kvinner), ikke summen av x. Ta med `sum` når x
  er en telling (f.eks. antall fødsler), og forklar radene i en `textblock`.

### Region i Statistikkbankens lønnstakertabeller er arbeidssted
- **Symptom:** Antall lønnstakere etter bosted i en kommune er langt lavere enn i SSB tabell 13926.
- **Årsak:** Tabellen fordeler etter arbeidsstedet for hovedarbeidsforholdet. `REGSYS_ARB_ARBKOMM` gir
  heller ikke samme tall, fordi den bare har bosatte sysselsatte 15–74 år.
- **Løsning:** Bruk `ARBLONN_ARB_ARBKOMM` for jobben der `ARBLONN_ARB_HOVEDARBEID == '1'`. Det
  traff tabellen (testet november 2026, versjon 59).

### Sammenligninger med manglende verdi gir 0 eller 1, ikke missing
- **Symptom:** En dummy laget med `generate h = x > 5` har ingen manglende verdier, selv om `x` mangler for
  mange. Enhetene kommer med i regresjoner og tabeller med feil verdi.
- **Årsak (testet versjon 60, november 2026, TESTLISTE 8.2):** En sammenligning med manglende verdi er
  *usann*, unntatt `!=`, som er *sann* (som NaN i flyttall, ikke som i Stata):
  - `generate h = x > 5` gir **0** når `x` mangler (Stata gir 1).
  - `generate h = x != 2` gir **1** når `x` mangler.
  - `replace h = 1 if x > 5` endrer ikke enheter der `x` mangler.
- **Løsning:** Lag dummyer slik at manglende verdi blir manglende:
  `generate h = x > 5 if !sysmiss(x)` (som `generate hoy = 0 if mangler_lonn == 0` i 8.7). Avslutt alltid
  grupperinger med `replace gr = 'ukjent' if sysmiss(x)`.
- **Grupper av inntekt eller andre beløp:** start ikke med `generate gr = '1'` og la `replace ... if x >= ...`
  bestemme resten. Da havner alle med manglende beløp stille i laveste gruppe. Gi dem egen kode, ta dem ut,
  eller gjør det eksplisitt (`replace x = 0 if sysmiss(x)`) når manglende skal bety 0, og si hva som er valgt
  (agentevaluering, TESTLISTE 7.4).

### Figurtallene ligger i Vega-spesifikasjonen
- Manualen sier at figurer eksporteres som bilder uten de underliggende tallene. Det gjelder .png og .svg.
  «Åpne i Vega-editor» gir en Vega-Lite-spesifikasjon (v6) med de aggregerte, støylagte tallene i
  `data.values`, på vega.github.io/editor (versjon 60, TESTLISTE 9.1–9.3).
- **Bruk:** Brukeren limer inn spesifikasjonen, og du endrer figuren. Se `referanser/vega.md`.
- Editorens Config-fane har en mørk stil fra microdata.no (tallformat `~s` på aksene gir «NaN» for
  navn). Overstyr den i spesifikasjonen (`config`-blokken i `vega.md`). En helt tom fane gir
  «ValueExpected», skriv `{}`.

### Kopi av hele utskriften mangler noen resultater
- **Symptom:** En bruker limer inn utskriften, og noen kommandoer står uten resultat. Det ser ut som de
  ikke ga noe.
- **Årsak:** Når hele skriptet med resultater kopieres ut, mangler resultatet av en del kommandoer, selv om
  det vises i microdata.no (versjon 60, november 2026, testskriptet `utklipp.txt`):
  - Mangler: `citation`, `tabulate-panel`, `regress-panel-diff`, `summarize-panel`, `probit`, `poisson`,
    `negative-binomial`, `list-labels`, `variables`, og alle grafer (`histogram`, `barchart`, `boxplot`,
    `hexbin`, `piechart`, `kaplan-meier`). `coefplot` gir tomme regresjonstabeller.
  - Kommer med: `summarize`, `tabulate` (også `rowpct` og `summarize()`), `ci`, `correlate`, `normaltest`,
    `anova`, `regress`, `logit`, `mlogit`, `oaxaca`, `regress-mml`, `regress-panel`, `hausman`,
    `transitions-panel`, `cox`, `weibull`.
- **Løsning:** Be brukeren kopiere resultatet av kommandoen for seg, før du konkluderer med at den feilet.
  En stoppet kommando gir derimot tomme tabeller og en feilmelding («Problem på linje N: ...»).

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

### Versjon 2 av anonymiseringstiltakene (fra versjon 60, 17. november 2026)
Kilde: `metadata/manual/konfidensialitet.md` og `systemendringer.md`. Det som står i avsnittene under, ble
avklart med versjon 1, hvis ikke annet står. Endringene som påvirker skript:
- **Fjernet:** `generate`/`replace`/`recode` som treffer 1–9 enheter, stoppes ikke lenger (tiltak 6).
  Tabeller med mange små celler stoppes ikke (tiltak 5). Konstantleddet skjules ikke (tiltak 9).
- **Celler med 1–4 settes til 0** i tabeller og grafer (tiltak 11). 0 betyr «0–5», 5 betyr «5–10».
- **Minste datasett er 100 personer** (var 1000). Gjelder også datasett under personnivå (jobber):
  de må kunne knyttes til minst 100 personer.
- **Winsorisering per undergruppe** i `tabulate ..., summarize()`, `barchart, by()/over()` og med `if`, og
  nå også i regresjoner og `correlate` (se `fallgruver_analyse.md`).
- **Nedsampling:** 1–3 tilfeldige observasjoner fjernes før de fleste analyser (per undergruppe i
  volumtabeller), og 1–11 før `regress`, `ivregress` og `anova`. Samme statistikk i to kommandoer kan
  derfor avvike litt (`tabulate ..., summarize(x)` mot `barchart (mean) x`).
- **Støyen avhenger av skriptet.** Samme tabell for de samme personene gir ny støy når skriptet er endret.
  Sammenlign ikke små tall mellom kjøringer av ulike skriptversjoner.
- **`configure confidentiality v1`** øverst i skriptet gir de gamle tiltakene, til 30. april 2027 (planlagt).
  Bare for brukere akkreditert før 17. november 2026, og ikke med FHI-data eller `BEFOLKNING_GRUNNKRETS`.
  Bruk det bare for å gjenskape gamle resultater. Skriptet kjører fram til importen av grunnkrets, som
  stoppes med «Ulovlig import med valgt konfidensialitetsprofil. Kan ikke bruke variabler innenfor
  *_GRUNNKRETS» (versjon 60, TESTLISTE 11.7). FHI-data er ikke testet med v1, men stoppes trolig på samme
  måte. FHI-testene i TESTLISTE del 10 ble kjørt med v2.

### Sjeldne 0/1-variabler blir 0 i gjennomsnitt og forsvinner fra regresjoner (versjon 2)
- **Symptom:** `tabulate gruppe, summarize(x) mean` eller `summarize x` gir gjennomsnitt 0 (og standardavvik 0)
  for en 0/1-variabel, selv om `tabulate x` viser mange med verdien 1. Ingen melding.
- **Årsak:** winsoriseringen (1 % i hver ende) gjelder også 0/1-variabler. Har under 1 % verdien 1, er
  99-persentilen 0, og alle 1-erne blir 0 (testet versjon 60, 2026-11-20, TESTLISTE 11.12). Motsatt blir alle
  0-ene 1 når over 99 % har verdien 1.
- **Også i undergrupper:** winsoriseringen skjer per gruppe i `summarize()`, `by()`/`over()` og med `if`. En
  andel som er over 1 % totalt, kan bli 0 i en gruppe der den er lavere (dødelighet blant unge, sjeldne
  diagnoser i små grupper).
- **Regresjoner:** en 0/1-forklaringsvariabel der under 1 % har verdien 1, utelates fra `regress` og `logit`
  uten melding: ingen rad, og F-testen er som uten variabelen. Andeler over 1 % er med, og koeffisienten er
  som ventet. Grensen er 1 %, likt med `summarize`, også for utfallet i `logit` (TESTLISTE 8.12).
- **Kategorier i `i.`-variabler rammes ikke.** `regress lonn i.gruppe mann` og `logit` viste kategorier under
  1 %, med koeffisienter nær forskjellene i gjennomsnitt. `i.` lages trolig om til 0/1-ledd etter winsoriseringen (TESTLISTE 8.13).
- **Utfall under 1 % (eller over 99 %) gir meningsløse modeller uten feilmelding** (8.13):
  - `regress`: alle koeffisienter og standardfeil 0, R² og F «NaN».
  - `logit`: 35 iterasjoner, «Pseudo R2 Infinity» og negativ eller nær null `LR chi2`. Med utfallet over 99 %
    ser koeffisientene signifikante ut (svært høye z-verdier), men tallene er tull.
  - Kjennetegn: «NaN», «Infinity», negativ `LR chi2`, 35 iterasjoner, standardavvik 0 i `summarize`.
- **Løsning:**
  - Andeler: bruk antall i en krysstabell, `tabulate gruppe x, rowpct`. Bruk `summarize(x) mean` bare når
    andelen er godt over 1 % (og under 99 %) i hver gruppe.
  - Sjeldne forklaringsvariabler: skriv `i.x` i stedet for `x`. Raden heter da «x '1'». Testet i både
    `regress` og `logit` (8.14).
    Sjekk at alle forklaringsvariablene har en rad i resultatet.
  - Sjeldne utfall: tabuler utfallet først. Under 1 % kan ikke modelleres med `regress` eller `logit` på hele
    populasjonen. Avgrens populasjonen til en risikogruppe der utfallet er over 1 %, eller bruk tabeller med
    antall.
- **`cox` rammes ikke.** En hendelse på 0,19 % ga 0 i `summarize`, men `cox` fant hendelsene og ga rimelige
  koeffisienter. For sjeldne hendelser over tid er `cox` derfor et alternativ til `logit` (TESTLISTE 8.14). `kaplan-meier`
  og andre modeller (`poisson`, `probit`) er ikke testet.

### Tabeller på små delgrupper
- **Versjon 2:** Tabellen vises alltid. Celler med 1–4 vises som 0, så små kategorier ser tomme ut.
  Behandle 0 i en tabell som «0–5», ikke som ingen.
- **Versjon 1:** Tabeller der minst halvparten av cellene var under 5, ble ikke vist, f.eks.
  `tabulate far_landbak if far_kat == '4', top(15)` på en liten gruppe.
- **Løsning:** Grupper til få, store kategorier.

### `collapse`/`aggregate` med `sum` winsoriseres når `by()` er en vanlig variabel
- **Symptom:** Antall tilfeller per kommune (eller fylke, utdanningsnivå osv.) blir feil, særlig for små
  grupper, når de telles med `collapse (sum) dummy, by(kommune)`.
- **Årsak:** Anonymiseringstiltaket winsorisering slår inn når det aggregeres til en vanlig variabel. Det
  gjelder ikke når `by()` er en pseudonymisert enhet (personid, familieid, husholdningsid, jobbid).
  `count`, `median` og `percent` påvirkes ikke. (Manualen, 3.5 collapse, oppdatert i versjon 59.)
- **Løsning:** Tell med `(count)`. `count` teller alle gyldige verdier, også 0, så sett dem som ikke skal
  telles til missing først. Bruk `sum` bare til å summere verdier. Det går fint å summere per person
  før man aggregerer videre (`by(personid)` på jobbdata, deretter per gruppe).

### `replace`/`recode` må endre minst 10 enheter (bare versjon 1)
- **Gjelder ikke fra versjon 2** (tiltak 6 er fjernet 17. november 2026). Testet med versjon 60: `(990 = 9)`
  på landbakgrunn godtas nå (TESTLISTE 1.13).
  `--utelat` i verktøyene trengs da bare med `configure confidentiality v1`.
- **Versjon 1:** En `replace` eller `recode` som traff 1–9 enheter ble avvist. I `recode` gjaldt grensen
  **hver målverdi for seg**: «Stoppet av avsløringskontroll. Omkodingen til 9 påvirker for få enheter»
  (`(990 = 9)` for uoppgitt landbakgrunn, versjon 59). En regel som traff 0 enheter ble ikke stoppet
  (TESTLISTE 1.7). Feilmeldingen nevnte én målkode om gangen. Ta ut målkoder med `--utelat`,
  eventuelt i flere runder. Kategorier som ikke var med i
  `tabulate`, kunne likevel stoppe omkodingen.

## Alder

- For å treffe Statistikkbanken beregnes alder ved utgangen av året før:
  `år - 1 - int(BEFOLKNING_FOEDSELS_AAR_MND/100)`.
