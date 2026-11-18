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

### Sektor finnes ikke etter 2019
- **Symptom:** `REGSYS_FRTK_SEKTOR_2014` har ingen data etter 2019-11-16, og `ARBLONN_FRTK_SEKTOR_2014`
  (jobbnivå, 2015–2026) finnes ikke fra versjon 60.
- **Årsak:** SSB stoppet personvariabelen av personvernhensyn (risiko for å avsløre opplysninger om foretak),
  og slettet jobbvariabelen i versjon 60 (november 2026, ingen erstatning).
- **Løsning:** Sektor kan bare brukes til og med 2019 (`REGSYS_FRTK_SEKTOR_2014`, 4. kvartal). Si fra til
  brukeren at nyere sektortall ikke finnes i microdata.no. `kodesnutter/sektor_lonnstakere.txt` er
  utgått. Den traff SSB tabell 13926 innenfor 0,1 % (versjon 59) og viser metoden.

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

### Datoer er tall i formatet ÅÅÅÅMMDD, ikke dager
- **Symptom:** Tid til hendelse blir rundt 20 millioner. `dod - date(2024, 1, 1)` ga 20 222 468 i stedet
  for et antall dager (versjon 60, november 2026).
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
  TESTLISTE 8.10: dødsdatoer 2023–2025 ble 19 380–20 436, og tid fra diagnose til død 0–971 dager):
  `generate dag_aar = int(dod/10000)`, `generate dag_mnd = int(dod/100) - dag_aar*100`,
  `generate dag_dag = dod - int(dod/100)*100` og `generate doddag = date(dag_aar, dag_mnd, dag_dag)`.
  Sammenligning med en dato kan gjøres direkte på tallet: `dod >= 20240101`.

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
  nå også i regresjoner og `correlate` (se «Analyse»).
- **Nedsampling:** 1–3 tilfeldige observasjoner fjernes før de fleste analyser (per undergruppe i
  volumtabeller), og 1–11 før `regress`, `ivregress` og `anova`. Samme statistikk i to kommandoer kan
  derfor avvike litt (`tabulate ..., summarize(x)` mot `barchart (mean) x`).
- **Støyen avhenger av skriptet.** Samme tabell for de samme personene gir ny støy når skriptet er endret.
  Sammenlign ikke små tall mellom kjøringer av ulike skriptversjoner.
- **`configure confidentiality v1`** øverst i skriptet gir de gamle tiltakene, til 30. april 2027 (planlagt).
  Bare for brukere akkreditert før 17. november 2026, og ikke med FHI-data eller `BEFOLKNING_GRUNNKRETS`.
  Bruk det bare for å gjenskape gamle resultater.

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
  før man aggregerer videre, slik `kodesnutter/sektor_lonnstakere.txt` gjør.

### `replace`/`recode` må endre minst 10 enheter (bare versjon 1)
- **Gjelder ikke fra versjon 2** (tiltak 6 er fjernet 17. november 2026). Ikke testet ennå (TESTLISTE 1.13).
  `--utelat` i verktøyene trengs da bare med `configure confidentiality v1`.
- **Versjon 1:** En `replace` eller `recode` som traff 1–9 enheter ble avvist. I `recode` gjaldt grensen
  **hver målverdi for seg**: «Stoppet av avsløringskontroll. Omkodingen til 9 påvirker for få enheter»
  (`(990 = 9)` for uoppgitt landbakgrunn, versjon 59). En regel som traff 0 enheter ble ikke stoppet
  (TESTLISTE 1.7). Feilmeldingen nevnte én målkode om gangen. Ta ut målkoder med `--utelat` (SN2002 →
  SN2007 gikk gjennom i tredje runde, 33 av 410 målkoder tatt ut). Kategorier som ikke var med i
  `tabulate`, kunne likevel stoppe omkodingen.

## Analyse

Kartlagt fra manualen (`metadata/manual/konfidensialitet.md`, `kommandoer_og_funksjoner/kommandoer.md` og
`eksempel/Regresjonsanalyser/`, versjon 60 med anonymiseringstiltak versjon 2, november 2026). Punktene er
**ikke kjørt** i microdata.no før det står. Det som må testes, står i TESTLISTE del 8.

### Regresjoner winsoriseres og nedsamples
- **Versjon 2:** Alle kontinuerlige variabler i en regresjon winsoriseres før estimeringen (1 % i hver ende),
  også i `correlate`. Koeffisienter for skjeve variabler (inntekt, formue) påvirkes mindre av ekstreme
  verdier, og R² blir ofte høyere. Før `regress`, `ivregress` og `anova` fjernes 1–11 tilfeldige
  observasjoner, så N og frihetsgrader varierer litt mellom kjøringer.
- **Versjon 1:** Regresjoner brukte de ikke-winsoriserte dataene, mens tabellene var winsorisert.
  Regresjoner fra før 17. november 2026 kan derfor gi andre koeffisienter.
- **Testet (versjon 60, november 2026, TESTLISTE 8.3):** lønn etter tre utdanningsgrupper. Konstantledd +
  koeffisienter avvek med 0,7 %, 0,4 % og −0,6 % fra gjennomsnittene i `tabulate ..., summarize()`. Regresjonen
  winsoriseres på hele utvalget og tabellen per gruppe, så regresjonen ble litt lavere for gruppen med de
  høyeste lønningene og litt høyere for den laveste.
- Manglende verdier utelates listevis: N i `regress y x1 x2` var lik antall uten manglende verdi i noen av
  variablene (TESTLISTE 8.1).
- Prosentiler mikroaggregeres og glattes (tiltak 10). Tellinger støylegges (±5).
- **Løsning:** Skriv i `textblock` at kontinuerlige variabler er winsorisert, både i tabeller og regresjoner.
  For å gjenskape eldre resultater: `configure confidentiality v1` (til 30. april 2027).

### Kategoriske variabler med små grupper fjernes fra regresjonen (tiltak 14)
- **Symptom:** En forklaringsvariabel (f.eks. `i.kommune`) mangler helt i resultatet, og under tabellen står
  «Leddet i.kommune er fjernet fra analysen pga. lav frekvens i minst en av gruppene.» Regresjonen kjøres
  likevel, uten variabelen (testet versjon 60, november 2026, TESTLISTE 8.4).
- **Årsak:** Har én kategori færre enn 5 observasjoner, fjernes **hele variabelen** fra analysen, ikke bare
  kategorien (tiltak 14). Interaksjoner som `i.kjonn#i.utdniv#i.fylke` gir lett små grupper. Meldingen er
  lett å overse, og resultatet ser ut som en modell uten variabelen.
- **Løsning:** Slå små kategorier sammen med nabokategorier, bruk grovere inndeling eller større
  populasjon. `tabulate` variabelen i analysepopulasjonen først: celler som vises som 0, er under 5.

### Forklaringsvariabler som er (nesten) like utfallet, fjernes (tiltak 12 og 13)
- En forklaringsvariabel som er perfekt eller nesten perfekt korrelert med utfallet, droppes. `correlate`
  viser 1 når to variabler er like for alle unntatt under 5 enheter. Skjer det, er modellen trolig feil
  spesifisert (f.eks. utfallet laget av en av forklaringsvariablene).

### En regresjon må ha minst to koeffisienter (tiltak 17)
- **Symptom:** «Regresjonsmodellen har for få forklaringsvariabler/koeffisienter. Nedre grense er to
  koeffisienter.» på `regress lonn mann` (testet versjon 60, november 2026, TESTLISTE 8.9). Skriptet stopper.
- **Årsak:** Modeller med færre enn to koeffisienter (konstantleddet telles ikke) stoppes. Det gjelder også
  når tiltak 14 har fjernet en faktorvariabel, så det bare er én forklaringsvariabel igjen. En faktorvariabel
  med tre nivåer gir to koeffisienter og er nok.
- **Løsning:** Ta med minst to forklaringsvariabler. Et gruppegjennomsnitt hentes med
  `tabulate gr, summarize(y)`, ikke med regresjon.

### Konstantleddet skjules ved små kombinasjoner av kategorier (bare versjon 1)
- Tiltak 9 er fjernet i versjon 2. I versjon 1 ble konstantleddet skjult når en kombinasjon av de
  kategoriske forklaringsvariablene hadde færre enn 5 enheter.

### Overlevelsesanalyse: populasjonen må være alle i risiko
- **Symptom:** Nesten alle har `hendelse = 1`, og overlevelseskurven faller til 0.
- **Årsak:** Manualens eksempel A lager datasettet fra `import-event` (`keep if astatus == '1'` og
  `collapse (min) START@...`). Da består populasjonen bare av personer som *fikk* hendelsen, og ingen er
  sensurert. Kurven viser tid til hendelsen blant dem som fikk den, ikke risikoen i befolkningen.
- **Løsning:** Lag populasjonen først (f.eks. bosatte 16–60 år 1.1. startåret), finn første hendelsesdato
  i et eget datasett (`import-event`, `keep`, `collapse (min) START@... by(PERSONID_1)`), og `merge` den
  inn. De uten dato får `hendelse = 0` og tiden satt til slutten av perioden. Se også
  `kodesnutter/forlop_til_person.txt`.

### Overlevelsesanalyse: død og utvandring er ikke sensurert
- **Symptom:** For lang overlevelsestid, særlig for eldre og innvandrere.
- **Årsak:** Manualen setter tiden til maksverdi for alle uten hendelse. Den som dør eller utvandrer i
  perioden, regnes da som i risiko helt til slutt. Det finnes ingen hendelsesvariabel for utvandring.
- **Løsning:** Sett sensureringstid ved død (`BEFOLKNING_DOEDS_DATO`, tallet ÅÅÅÅMMDD, se «Datoer er tall i
  formatet ÅÅÅÅMMDD») og ved første 1.1. med
  `BEFOLKNING_STATUSKODE` = `'3'` (utvandret, bare årlig). Hendelse etter sensurering skal ikke telle.
  Er hendelsen selv død, er utvandring den viktigste sensureringen. Si fra om at utvandring bare er kjent
  per 1.1.

### Overlevelsesanalyse: tolkning av `cox`
- Koeffisientene gjelder hazard (risikoen for hendelsen per tidsenhet), ikke overlevelsestiden, selv om
  manualen kaller tiden «avhengig variabel». Positiv koeffisient (hazardrate over 1) betyr høyere risiko
  og kortere tid til hendelsen.
- Med `hazard` vises ingen standardfeil. Kjør uten `hazard` for å se usikkerheten, og regn om med `exp()`.
- Tid i hele år (`int(dager/365.24)`, som i manualen) gir mange like tider. Bruk dager eller måneder i
  `cox`, år bare i grafer.

### `regress-panel-diff`: behandlingsvariabelen er etter-perioden for alle
- **Symptom:** Diff-in-diff-estimatet (ATET) blir feil eller lik null.
- **Årsak:** Manualen kaller variabel 3 «behandlingsvariabel», men den skal være 1 for **alle enheter** fra
  og med behandlingstidspunktet, også kontrollgruppen (eksempelet: `replace behandling = 1 if
  year(date@panel) >= 2020`). Settes den bare for behandlingsgruppen, er den lik interaksjonsleddet.
- **Løsning:** `gruppe` = 1 for behandlingsgruppen, `etter` = 1 for alle fra behandlingsåret. Samme
  resultat: `regress-panel y gruppe##etter ..., pooled`.
- **Testet (versjon 60, november 2026, TESTLISTE 8.5):** med `etter` = 1 for alle i 2020–2021 ga
  `regress-panel-diff` −4 159 for `gruppe ⨯ etter` og den pooled regresjonen −4 156 for interaksjonen.
  Forskjellen skyldes nedsampling (N 331 647 mot 331 649). Utskriften kaller estimatet `gruppe ⨯ etter`,
  ikke ATET.

### `ivregress`: endogen variabel til venstre for `=`, instrumentene til høyre
- **Årsak:** Teksten i manualen bytter om begrepene («instrumentvariabel på venstre side»), og eksempelsiden
  sier at IV er for multikollinearitet. Syntaksen i eksemplene er
  `ivregress y x1 x2 ( endogen = instrument1 instrument2 )`.
- **Løsning:** Skriv det slik, og forklar valget av instrument: det må påvirke `endogen`, men ikke `y` på
  annen måte. Alder som instrument for formue i lønnsregresjonen (manualens eksempel) oppfyller ikke det.
  IV er for endogenitet (utelatte variabler, omvendt kausalitet, målefeil), ikke multikollinearitet.

### `poisson` eller `negative-binomial`
- Teksten for `negative-binomial` sier «forventet verdi større enn variansen». Det er omvendt:
  overdispersjon er når variansen er større enn forventningen, og da passer `negative-binomial`. Teksten for
  `poisson` er riktig. Sjekk med `summarize` (varians = std²) og se om `alpha` i `negative-binomial` er
  tydelig større enn 0.

### Paneldata
- `import-panel` virker bare i et tomt datasett. Lag populasjonen først, og bruk
  `clone-units <populasjon> <panel>` og `use <panel>` før `import-panel`.
- Datasettet får én rad per enhet og tidspunkt. Hold populasjonen under ca. 1 million enheter (manualen).
- Akkumulerte variabler (inntekt) gir årsverdien uansett dato i året. Med `2018-01-01` får du inntekt for
  2018, men status (sivstand, bosted) per 1.1.2018. Si fra om rekkefølgen er viktig for tolkningen.
- `robust` i `regress-panel` og `regress-panel-diff` er cluster på panel-ID. `cluster()` kan ikke brukes samtidig.
- `hausman`: p < 0,05 betyr at fixed effects bør brukes.

### Standardfeil, faktorvariabler og prediksjon
- `cluster()` må være en numerisk variabel som ikke er med i modellen, og kan ikke kombineres med `robust`.
  Bruk cluster når enhetene er gruppert (f.eks. elever i skoler, personer i kommuner).
- Kategoriske variabler skrives som `i.var`. Uten `i.` tolkes en numerisk kode som kontinuerlig. Interaksjon:
  `i.a#i.b` (bare interaksjonen) eller `i.a##i.b` (hovedeffekter og interaksjon). `control(i.kommune)` tar
  med faste effekter uten å vise dem.
- `logit`/`probit` krever et utfall som er 0/1. `mfx(dydx)` gir gjennomsnittlige marginaleffekter
  (`overall`). For en 0/1-variabel er det trolig den deriverte, ikke en diskret endring fra 0 til 1:
  `mann` ga 0,1805, mens forskjellen i `margins(mann)` var 0,1864 og en derivert ga om lag 0,180 (TESTLISTE
  8.7, versjon 60). Forskjellen er liten. Trengs den diskrete effekten, bruk forskjellen i `margins()`. `or` gir oddsratio. `margins()` gir predikert verdi ved gjennomsnittet av
  forklaringsvariablene, ikke gjennomsnittet av predikerte verdier.
- `mlogit` viser koeffisientene for hver utfallskategori under hverandre uten å si hvilken kategori blokken
  gjelder (versjon 60). Første kategori er referanse, og blokkene står trolig i stigende rekkefølge. Si fra om
  det når resultatet tolkes, eller lag utfallet med få, tydelige kategorier.
- `regress-mml`: gruppevariabelen kan ikke også være forklaringsvariabel. Like variansestimater for to
  nivåer (f.eks. fylke og landsdel) betyr at nivåene fanger opp det samme. Bruk ett av dem.
- Spredningsplott finnes ikke. Bruk `hexbin` (celler med under 5 enheter vises ikke). Søyler i `histogram`
  og `barchart` med under 5 enheter vises heller ikke (tiltak 11).

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
  - **Ålesund 1507 (2020–2023) omkodes helt til 1508, også Haram.** 1.1.2023 fikk 1508 67 525 personer,
    mot 58 511 i Ålesund og 9 358 i Haram 1.1.2024 (versjon 59, november 2026). Koden kan ikke deles uten
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

### Grunnkrets (`BEFOLKNING_GRUNNKRETS`, fra versjon 60)
Kartlagt fra metadataene og SSB Klass (november 2026). Ikke kjørt i microdata.no ennå (TESTLISTE del 11).
- **Koden skifter med kommunenummeret.** Grunnkrets `15040101` (Ålesund 2019) er `15070101` i 2020–2023 og
  `15080101` fra 2024. Over 10 000 koder ble byttet i 2020 og 6 000 i 2024. Koble aldri grunnkretser fra
  ulike år direkte. Bruk `verktoy/grunnkrets.py --aar <år>`, som følger kodene gjennom Klass-endringene.
- **Små enheter:** mange grunnkretser har under 10 beboere. Tabeller på grunnkrets (og delområde) får mange
  celler med 1–4, som vises som 0. Kod rett til delområde, levekårssone, bydel eller egne områder.
  Verktøyet tar med alle grunnkretsene i hver målenhet i samme regel, også de uendrede. Det gir kortere
  skript enn å gå via gjeldende grunnkrets. (Grunnkrets kan ikke brukes med `configure confidentiality v1`,
  så 10-enhetsregelen fra versjon 1 gjelder ikke her.)
- **Delte grunnkretser:** noen grunnkretser er senere delt mellom flere delområder eller soner (334 fra
  1990, 59 fra 2019, 3 fra 2025 på grunnkretsnivå, langt færre på sone- og delområdenivå). De kan ikke
  fordeles uten adresse og står uendret (8 tegn) med `--splitt behold`.
- **Uoppgitt grunnkrets** har koden `kkkk9999` i hver kommune (360 koder i 2026) og står uendret.
- **Kodelisten har også delområdene** (6 sifre, med navn). Dataene har trolig bare 8-sifrede koder.
- **Delområde** er de seks første sifrene i *gjeldende* kode. For eldre år gir `substr(gk, 1, 6)` det gamle
  delområdet med gammelt kommunenummer. `grunnkrets.py --til delomrade` omkoder bare delområdene som har
  endrede koder, og tar resten med `substr`.
- **Levekårssoner** finnes i Klass for 66 kommuner (2026-inndelingen, ikke Oslo). Bydeler finnes for Oslo,
  Bergen, Trondheim og Stavanger, delbydeler for Oslo. Alle bygger på 2026-grunnkretsene.

## Klass

- **Velg riktig versjon med `--dato`.** `klass.py` bruker kodene som gjelder på datoen (standard i dag). SN2007-variabler
  må ha en dato før 2025-01-01, ellers får du SN2025 (Klass 6 har fire versjoner: SN 1994, SN 2002, SN 2007 og SN 2025).
  For NUS, STYRK og landkoder er det samme prinsipp: bruk en dato fra perioden dataene dekker.
- **Variablene har koder som ikke finnes i Klass.** Med `--variabel` listes slike koder i en kommentar og står uendret:
  - Landkoder: utgåtte land (Sovjetunionen 135, DDR 151), «uspesifisert»/«Resten av …» (194, 394, 594 osv.) og 989
    (uoppgitt utenlandsk statsborgerskap). Omkod dem for hånd, f.eks. til «Uoppgitt».
  - STYRK: `XXXX` (uoppgitt/ukjent).
  - SN2007: sammenfattede koder som `01.000` og `43.220`, og koder som ikke finnes i SN2007 i Klass på datoen. `grupper` plasserer
    dem via nærmeste overordnede kode (43.220 → 43.22 → F) og lister dem i en kommentar. Bare `00.000` (uoppgitt) står uendret.
    Det samme gjelder andre prefiksbaserte klassifikasjoner (STYRK, NUS), men ikke landkoder.
- **Resultatet er en kopi av kodene i Klass akkurat nå.** Klassifikasjoner endres. Oppgi hentedato i skriptet (verktøyet
  skriver den i en kommentar).
- **Koblinger med koder som har flere mål blander kodeverk.** SN2002 → SN2007 lot 42 % av sysselsatte
  (november 2006) stå med SN2002-kode. Gruppering på de første sifrene blir da feil (f.eks. «85» er helse
  i SN2002 og undervisning i SN2007).
- **Bruk `kobling --nivaa 1` (eller 2) for næring over tid.** Målene løftes til seksjon (A–U) eller
  divisjon, så koder med flere detaljerte mål blir entydige: 91 % omkodet på nivå 1 og 83 % på nivå 2
  (november 2007), mot 57 % på femsifret nivå. Omkodede og uendrede koder kan skilles på lengden (1 eller
  2 tegn mot `xx.xxx`).
- **Koblingstabeller kan være mange-til-mange.** `kobling` utelater koder som går til flere mål, og koder uten
  motpart (Klass har rader uten mål, f.eks. `46.890` i SN2025–SN2007), og lister dem i en kommentar.
- **Samme kode som kilde i én regel og mål i en annen** (vanlig mellom versjoner, f.eks. `25.300 -> 25.400` og
  `25.400 -> 25.500`): står reglene i ulike `recode`-kommandoer, omkodes verdien to ganger. Verktøyene samler
  slike regler i første kommando. Ikke del den linjen, og ikke flytt regler mellom linjene.
- **`recode` på strenger.** Koder som `'01.110'` og `'0110'` må skrives som strenger. Landkodene i `BEFOLKNING_LANDBAK3GEN` er
  strenger. Snutten `landbakgrunn_region.txt` bruker `destring` og tallintervaller. Det går også, men verktøyets
  utskrift er strenger og skal ikke kombineres med `destring`.
- **Statsløs og uoppgitt er små.** `grupper 545` gir egne målkoder for statsløs og uoppgitt (`V9`, eller `V91` og
  `V92` på nivå 2). De har under 10 bosatte og stoppet `recode` med versjon 1 av tiltakene (da: `--utelat V9`
  eller `--utelat V91,V92`). Med versjon 2 vises de som 0 i tabeller.
  Klass 545 er autoritet for verdensdel (Kypros i Europa, Bermuda og Saint-Pierre-et-Miquelon i Nord-Amerika).
  `landbakgrunn_region.txt` følger Klass og skiller i tillegg EU/EØS fra resten av Europa, som Klass ikke gjør.
- **Dataene kan ha nyere koder enn kodelisten.** `NUDB_BU` 1.7.2024 hadde NUS-koder (f.eks. 754144 Master, kunstig
  intelligens) som verken står i kodelisten i microdata.no eller i Klass 2024-01, bare i nyere Klass-versjoner. Bruk
  standarddatoen (i dag) for NUS. `grupper --variabel` tar med alle detaljkoder fra Klass på datoen.
- **Koblinger gir målnavnene fra Klass.** Er flere navn like (ISCED 2011: fem «Not further defined»), får de navnene
  over seg i hierarkiet («Bachelor’s or equivalent level – Academic – Not further defined»).
- **Landkodene i microdata er SSB-3 (Klass 91).** Verdensinndeling (545) bruker samme landkoder som blader. Gruppering
  av land (546) skiller EU/EFTA fram til 2004 fra nye EU-land etter 2004. Det er ikke dagens EU/EØS-medlemskap.

## FHI-data (Kreftregisteret og Norsk pasientregister)

Fra 2026-11 har microdata.no to datalagre fra FHI: `no.fhi.kreftregisteret` (versjon 1) og `no.fhi.npr` (versjon 1).
Kolonnen `datalager` i `metadata/variabler.csv` sier hvor variabelen ligger. Det meste her er lest ut av
metadataene og ELVIS, og er **ikke testet i microdata.no** (TESTLISTE del 10).

- **Enheten er ikke person.** Kreftregisteret har krefttilfelle (`KRG_TILFELLEID`), NPR har episode (`NPR_EPISODEID`)
  og prosedyre (`NPR_PROSEDYREID`). En person kan ha flere tilfeller og mange episoder. Personen står som en vanlig
  variabel: `P_PERSONIDMICRODATA` (Kreftregisteret), `SOM_EP_PERSONID` og `SOM_PROS_PERSONID` (NPR).
  Personopplysninger kobles inn i tilfellene med `merge kjonn into kreft on personid` (fra persondatasettet).
  Motsatt vei må tilfellene aggregeres med `collapse ..., by(personid)` først. Om resultatet kan kobles inn i et
  persondatasett, og om nøkkelen er samme pseudonym som hos SSB, er ikke testet (10.4, 10.5).
- **Hvert datalager har sin egen `require` og versjon.** `require no.fhi.kreftregisteret:1 as krg` og
  `import krg/S_TOPOGRAFIICD10 as topo`. Versjonene står i `metadata/datalagre.json`. Variablene er `FIXED` og
  importeres uten dato.
- **ICD-10-kodene er uten punktum**, med tre eller fire tegn (`C18`, `C187`). Kreftform: bruk
  `verktoy/kreftregisteret.py grupper` (nivå 1: 14 hovedgrupper, nivå 2: tresifret kode). Grupperingen er
  Kreftregisterets egen (ELVIS), ikke Klass. C77–C79 (spredning) og C97 er ikke kreftform og står uendret.
  `S_LOKICD7` er Kreftregisterets egen ICD-7 og passer ikke til grupperingen.
- **TNM-verdiene gjelder ulike kreftformer.** `4c`, `4d` og `is(DCIS)` i `S_PT` brukes bare for bryst (C50), `1a1` bare
  for livmor (C55). Tabeller over TNM på tvers av kreftformer blander verdisett. Se
  `kreftregisteret.py verdier --variabel S_PT --kreftform C50`.
- **Kodelistene i microdata.no er et utvalg av ELVIS.** Alle kodene i microdata.no finnes i ELVIS, men ELVIS har flere.
  `S_STRALEBEH` har bare `1` (mottatt strålebehandling) i microdata.no, mens ELVIS også har `0` (ikke behandlet) og
  `9` (ukjent). Manglende verdi er da trolig «ikke registrert», ikke «ukjent» (uavklart, 10.3). Det samme kan gjelde
  `S_HORMONBEH` (4 av 8 verdier).
- **Godartede svulster og forstadier er med.** `S_TUMORATFERD` skiller benign (0), usikker (1), in situ (2) og ondartet
  (3). Kreftregisterets publiserte tall for nye krefttilfeller gjelder ondartede.
- **Beskrivelser og verdier står i ELVIS.** Lenken til detaljsiden står i kolonnen `ekstern_metadata` i `variabler.csv`.
  Verdiene er hentet til `metadata/fhi/kreftregisteret/verdier.csv` med `kreftregisteret.py hent`.
- **Testet (versjon 60 / FHI 1, november 2026, TESTLISTE del 10):**
  - Tre `require` i samme skript virker. 38 889 krefttilfeller med diagnoseår 2023, 37 118 ondartede (atferd 3).
  - Personnøkkelen er samme pseudonym som hos SSB: alle tilfeller fikk kjønn med `merge ... on personid`, og
    kjønnsorganer ble 100 % ett kjønn (brystkreft 0,9 % menn). NPR (`SOM_EP_PERSONID`) kobler også: 25 % av
    kreftepisodene i 2024 gjaldt personer med krefttilfelle i 2023, mot 2 % av andre episoder.
  - `collapse ... by(personid)` på krefttilfeller gir et persondatasett som kan kobles inn i SSB-personer
    (37 872 personer, 97 % med ett tilfelle i 2023).
  - `S_STRALEBEH` har bare `1` (8 567) og manglende (30 322). Manglende betyr ikke registrert med stråling.
  - `values("2024")` på `SOM_EP_AAR` virker: 9,1 millioner episoder, 0,3 % uten hoveddiagnose.
  - Instant-datoene (`S_DIAGNOSEDATO`, `SOM_EP_INNDATO`) er dager siden 1970 og kan regnes med `date()`.
    Dødsdato fra SSB (ÅÅÅÅMMDD, regnet om) minus diagnosedato ga 0–971 dager. Andel døde innen 2025 av
    tilfellene i 2023: lunge m.m. 58 %, fordøyelse 42 %, bryst 8 %.
  - `recode kreftform ('C50' = 'C50' 'Bryst')` setter merkelappen (regel til samme verdi, TESTLISTE 10.8).
  - **Dataene har koder som ikke står i kodelisten.** `S_TOPOGRAFIICD10` hadde D45 (102) og D46 (200) blant de
    ondartede, men kodelisten har bare D47. `kreftregisteret.py grupper` tar nå med alle kreftformene i ELVIS.

## Alder

- For å treffe Statistikkbanken beregnes alder ved utgangen av året før:
  `år - 1 - int(BEFOLKNING_FOEDSELS_AAR_MND/100)`.
