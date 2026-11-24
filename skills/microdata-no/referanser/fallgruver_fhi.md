# Fallgruver med FHI-data (Kreftregisteret og Norsk pasientregister)

Fra 2026-11 har microdata.no to datalagre fra FHI: `no.fhi.kreftregisteret` (versjon 1) og `no.fhi.npr` (versjon 1).
Kolonnen `datalager` i `metadata/variabler.csv` sier hvor variabelen ligger. Punktene er lest ut av metadataene
og ELVIS, og de viktigste er testet i microdata.no (TESTLOGG del 10, se siste punkt).

- **Enheten er ikke person.** Kreftregisteret har krefttilfelle (`KRG_TILFELLEID`), NPR har episode (`NPR_EPISODEID`)
  og prosedyre (`NPR_PROSEDYREID`). En person kan ha flere tilfeller og mange episoder. Personen står som en vanlig
  variabel: `P_PERSONIDMICRODATA` (Kreftregisteret), `SOM_EP_PERSONID` og `SOM_PROS_PERSONID` (NPR).
  Personopplysninger kobles inn i tilfellene med `merge kjonn into kreft on personid` (fra persondatasettet).
  Motsatt vei må tilfellene aggregeres med `collapse ..., by(personid)` først. Nøkkelen er samme pseudonym som hos
  SSB, og det aggregerte datasettet kan kobles inn i et persondatasett (testet, 10.4 og 10.5).
- **Hvert datalager har sin egen `require` og versjon.** `require no.fhi.kreftregisteret:1 as krg` og
  `import krg/S_TOPOGRAFIICD10 as topo`. Versjonene står i `metadata/datalagre.json`. Variablene er `FIXED` og
  importeres uten dato.
- **ICD-10-kodene er uten punktum**, med tre eller fire tegn (`C18`, `C187`). Kreftform: bruk
  `verktoy/kreftregisteret.py grupper` (nivå 1: 14 hovedgrupper, nivå 2: tresifret kode). Grupperingen er
  Kreftregisterets egen (ELVIS), ikke Klass. C77–C79 (spredning) og C97 er ikke kreftform og står uendret.
  `S_LOKICD7` er Kreftregisterets egen ICD-7 og passer ikke til grupperingen.
- **Kreftformene i Cancer in Norway er en annen gruppering enn ELVIS.** Bruk `kreftregisteret.py grupper --nivaa cin`
  når tallene skal sammenlignes med rapporten eller statistikkbanken (https://sb.kreftregisteret.no/). Den har 48
  kreftformer (tabell 2.3 i Cancer in Norway 2025). Noen avgjøres av fire tegn (C00.3–5 og C05.1–2), og noen D-koder er
  med (in situ i urinveier, godartede svulster i sentralnervesystemet og endokrine kjertler, D45–D47).
  - **Leppekreft er kodet som hud på leppe (C44.0, noen C43.0) i `S_TOPOGRAFIICD10`.** Ingen tilfeller har C00
    (2023). Leppen står i ICD-O-3-topografien `S_TOPOGRAFIICDO3`: 000–002 lepperødt, 006 munnvik. Rapporten regner
    dem som leppe. Bruk `--topografi`, ellers havner om lag 90 leppekrefter i året i C44 Hud.
  - **`S_TOPOGRAFIICDO3` er uten C** (`000`, `440`), ulikt ICD-10-variabelen (`C440`). Et utvalg med `'C00'` blir
    tomt, og `tabulate` på et tomt utvalg stopper skriptet («Tomt datasett»).
  - C48.2 (bukhinnen) er eggstokk m.m. for kvinner og bløtvev for menn. Kjønn må hentes fra SSB (`--kjonn`).
  - Basalcellekarsinom (morfologi 809x) er ikke med i rapporten, og datalageret har ingen (2023). `--morfologi`
    skiller dem ut som `basal` om de kommer med senere.
  - Pagets sykdom i bryst og papillomer i urinveier er heller ikke med i rapporten, men skilles ikke ut.
  - **Testet (versjon 1, 2026-11-23, TESTLOGG 10.11):** alle tilfeller og alle kreftformer i 2023 stemmer med Cancer in
    Norway 2025 (tabell 4.5–4.6) innenfor støyen, unntatt leppe før `--topografi`. Rapporten for 2023 (CiN 2023) har
    lavere tall for flere kreftformer: registeret er oppdatert siden.
- **TNM-verdiene gjelder ulike kreftformer.** `4c`, `4d` og `is(DCIS)` i `S_PT` brukes bare for bryst (C50), `1a1` bare
  for livmor (C55). Tabeller over TNM på tvers av kreftformer blander verdisett. Se
  `kreftregisteret.py verdier --variabel S_PT --kreftform C50`.
- **Kodelistene i microdata.no er et utvalg av ELVIS.** Alle kodene i microdata.no finnes i ELVIS, men ELVIS har flere.
  `S_STRALEBEH` har bare `1` (mottatt strålebehandling) i microdata.no, mens ELVIS også har `0` (ikke behandlet) og
  `9` (ukjent). Manglende verdi betyr «ikke registrert», ikke «ukjent» (testet, 10.3). Det samme gjelder trolig
  `S_HORMONBEH` (4 av 8 verdier, ikke testet).
- **Velg avgrensning etter hva du vil telle.** `S_TUMORATFERD` skiller benign (0), usikker (1), in situ (2) og
  ondartet (3). Bruk atferd 3 når spørsmålet gjelder ondartede svulster. For sammenligning med «All kreft» i
  *Cancer in Norway*, bruk rapportens diagnoseavgrensning med `kreftregisteret.py grupper --nivaa cin` (se over),
  ikke atferd 3. Den omfatter også utvalgte godartede svulster og in situ-tilfeller, og utelater
  basalcellekarsinomer. [FHIs definisjon](https://www.fhi.no/is/ncd/dodelighet-sykelighet/kreft/)
- **Beskrivelser og verdier står i ELVIS.** Lenken til detaljsiden står i kolonnen `ekstern_metadata` i `variabler.csv`.
  Verdiene er hentet til `metadata/fhi/kreftregisteret/verdier.csv` med `kreftregisteret.py hent`.
- **Testet (versjon 60 / FHI 1, november 2026, TESTLOGG del 10):**
  - Tre `require` i samme skript virker.
  - Personnøkkelen er samme pseudonym som hos SSB, både i Kreftregisteret og NPR (`SOM_EP_PERSONID`). Alle tilfeller
    fikk kjønn med `merge ... on personid`.
  - `collapse ... by(personid)` på krefttilfeller gir et persondatasett som kan kobles inn i SSB-personer.
  - `S_STRALEBEH` har bare `1` og manglende. Manglende betyr ikke registrert med stråling.
  - `values("2024")` på `SOM_EP_AAR` virker (9,1 millioner episoder).
  - Instant-datoene (`S_DIAGNOSEDATO`, `SOM_EP_INNDATO`) er dager siden 1970 og kan regnes med `date()`, også mot
    dødsdato fra SSB (ÅÅÅÅMMDD, regnet om).
  - `recode kreftform ('C50' = 'C50' 'Bryst')` setter merkelappen (regel til samme verdi, TESTLOGG 10.8).
  - **Dataene har koder som ikke står i kodelisten.** `S_TOPOGRAFIICD10` hadde D45 og D46 blant de ondartede, men
    kodelisten har bare D47. `kreftregisteret.py grupper` tar nå med alle kreftformene i ELVIS.
