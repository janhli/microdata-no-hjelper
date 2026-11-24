# Fallgruver i statistiske analyser

Les også «Avsløringskontroll» i `fallgruver.md`, særlig om sjeldne 0/1-variabler.

Kartlagt fra manualen (`metadata/manual/konfidensialitet.md`, `kommandoer_og_funksjoner/kommandoer.md` og
`eksempel/Regresjonsanalyser/`, versjon 60 med anonymiseringstiltak versjon 2, november 2026). Punkter med
«testet» og et TESTLISTE-nummer er kjørt i microdata.no (del 8). De andre bygger bare på manualen.

## Regresjoner winsoriseres og nedsamples
- Alle kontinuerlige variabler i en regresjon winsoriseres før estimeringen (1 % i hver ende),
  også i `correlate`. Koeffisienter for skjeve variabler (inntekt, formue) påvirkes mindre av ekstreme
  verdier, og R² blir ofte høyere. Før `regress`, `ivregress` og `anova` fjernes 1–11 tilfeldige
  observasjoner, så N og frihetsgrader varierer litt mellom kjøringer.
- Regresjonen winsoriseres på hele utvalget og `tabulate ..., summarize()` per gruppe, så konstantledd +
  koeffisienter avviker litt (under 1 %) fra gjennomsnittene i tabellen: lavere for gruppen med de høyeste
  verdiene og høyere for den laveste (testet versjon 60, november 2026, TESTLISTE 8.3).
- Manglende verdier utelates listevis: N i `regress y x1 x2` var lik antall uten manglende verdi i noen av
  variablene (TESTLISTE 8.1).
- Prosentiler mikroaggregeres og glattes (tiltak 10). Tellinger støylegges (±5).
- **Løsning:** Skriv i `textblock` at kontinuerlige variabler er winsorisert, både i tabeller og regresjoner.
  For å gjenskape resultater fra før 17. november 2026: se «Versjon 1 av anonymiseringstiltakene» i `fallgruver.md`.

## Kategoriske variabler med små grupper fjernes fra regresjonen (tiltak 14)
- **Symptom:** En forklaringsvariabel (f.eks. `i.kommune`) mangler helt i resultatet, og under tabellen står
  «Leddet i.kommune er fjernet fra analysen pga. lav frekvens i minst en av gruppene.» Regresjonen kjøres
  likevel, uten variabelen (testet versjon 60, november 2026, TESTLISTE 8.4).
- **Årsak:** Har én kategori færre enn 5 observasjoner, fjernes **hele variabelen** fra analysen, ikke bare
  kategorien (tiltak 14). Interaksjoner som `i.kjonn#i.utdniv#i.fylke` gir lett små grupper. Meldingen er
  lett å overse, og resultatet ser ut som en modell uten variabelen.
- **Løsning:** Slå små kategorier sammen med nabokategorier, bruk grovere inndeling eller større
  populasjon. `tabulate` variabelen i analysepopulasjonen først: celler som vises som 0, er under 5.

## Forklaringsvariabler som er (nesten) like utfallet, fjernes (tiltak 12 og 13)
- En forklaringsvariabel som er perfekt eller nesten perfekt korrelert med utfallet, droppes. `correlate`
  viser 1 når to variabler er like for alle unntatt under 5 enheter. Skjer det, er modellen trolig feil
  spesifisert (f.eks. utfallet laget av en av forklaringsvariablene).

## En regresjon må ha minst to koeffisienter (tiltak 17)
- **Symptom:** «Regresjonsmodellen har for få forklaringsvariabler/koeffisienter. Nedre grense er to
  koeffisienter.» på `regress lonn mann` (testet versjon 60, november 2026, TESTLISTE 8.9). Skriptet stopper.
- **Årsak:** Modeller med færre enn to koeffisienter (konstantleddet telles ikke) stoppes. Det gjelder også
  når tiltak 14 har fjernet en faktorvariabel, så det bare er én forklaringsvariabel igjen. En faktorvariabel
  med tre nivåer gir to koeffisienter og er nok.
- **Løsning:** Ta med minst to forklaringsvariabler. Et gruppegjennomsnitt hentes med
  `tabulate gr, summarize(y)`, ikke med regresjon.

## Overlevelsesanalyse: populasjonen må være alle i risiko
- **Symptom:** Nesten alle har `hendelse = 1`, og overlevelseskurven faller til 0.
- **Årsak:** Manualens eksempel A lager datasettet fra `import-event` (`keep if astatus == '1'` og
  `collapse (min) START@...`). Da består populasjonen bare av personer som *fikk* hendelsen, og ingen er
  sensurert. Kurven viser tid til hendelsen blant dem som fikk den, ikke risikoen i befolkningen.
- **Løsning:** Lag populasjonen først (f.eks. bosatte 16–60 år 1.1. startåret), finn første hendelsesdato
  i et eget datasett (`import-event`, `keep`, `collapse (min) START@... by(PERSONID_1)`), og `merge` den
  inn. De uten dato får `hendelse = 0` og tiden satt til slutten av perioden. Se også
  `kodesnutter/forlop_til_person.txt`.

## Overlevelsesanalyse: død og utvandring er ikke sensurert
- **Symptom:** For lang overlevelsestid, særlig for eldre og innvandrere.
- **Årsak:** Manualen setter tiden til maksverdi for alle uten hendelse. Den som dør eller utvandrer i
  perioden, regnes da som i risiko helt til slutt. Det finnes ingen hendelsesvariabel for utvandring.
- **Løsning:** Sett sensureringstid ved død (`BEFOLKNING_DOEDS_DATO`, tallet ÅÅÅÅMMDD, se «Datoer er tall i
  formatet ÅÅÅÅMMDD» i `fallgruver.md`) og ved første 1.1. med
  `BEFOLKNING_STATUSKODE` = `'3'` (utvandret, bare årlig). Hendelse etter sensurering skal ikke telle.
  Er hendelsen selv død, er utvandring den viktigste sensureringen. Si fra om at utvandring bare er kjent
  per 1.1.
- **Størrelse (testet versjon 60, TESTLISTE 8.6):** for bosatte 70+, fulgt i ti år, ble `cox`-koeffisienten
  for innvandrer 3 standardfeil feil uten sensurering, fordi flere innvandrere utvandrer og få av dem får
  dødsdato. For hele gruppen utgjorde det lite. Sensurer alltid når grupper med mye utvandring sammenlignes.

## Overlevelsesanalyse: tolkning av `cox`
- Koeffisientene gjelder hazard (risikoen for hendelsen per tidsenhet), ikke overlevelsestiden, selv om
  manualen kaller tiden «avhengig variabel». Positiv koeffisient (hazardrate over 1) betyr høyere risiko
  og kortere tid til hendelsen.
- Med `hazard` vises ingen standardfeil. Kjør uten `hazard` for å se usikkerheten, og regn om med `exp()`.
- Tid i hele år (`int(dager/365.24)`, som i manualen) gir mange like tider. Bruk dager eller måneder i
  `cox`, år bare i grafer.

## `regress-panel-diff`: behandlingsvariabelen er etter-perioden for alle
- **Symptom:** Diff-in-diff-estimatet (ATET) blir feil eller lik null.
- **Årsak:** Manualen kaller variabel 3 «behandlingsvariabel», men den skal være 1 for **alle enheter** fra
  og med behandlingstidspunktet, også kontrollgruppen (eksempelet: `replace behandling = 1 if
  year(date@panel) >= 2020`). Settes den bare for behandlingsgruppen, er den lik interaksjonsleddet.
- **Løsning:** `gruppe` = 1 for behandlingsgruppen, `etter` = 1 for alle fra behandlingsåret. Samme
  resultat: `regress-panel y gruppe##etter ..., pooled`.
- **Testet (versjon 60, november 2026, TESTLISTE 8.5):** med `etter` = 1 for alle ga `regress-panel-diff` og
  den pooled regresjonen samme estimat, bortsett fra nedsampling. Utskriften kaller estimatet
  `gruppe ⨯ etter`, ikke ATET.

## `ivregress`: endogen variabel til venstre for `=`, instrumentene til høyre
- **Årsak:** Teksten i manualen bytter om begrepene («instrumentvariabel på venstre side»), og eksempelsiden
  sier at IV er for multikollinearitet. Syntaksen i eksemplene er
  `ivregress y x1 x2 ( endogen = instrument1 instrument2 )`.
- **Løsning:** Skriv det slik, og forklar valget av instrument: det må påvirke `endogen`, men ikke `y` på
  annen måte. Alder som instrument for formue i lønnsregresjonen (manualens eksempel) oppfyller ikke det.
  IV er for endogenitet (utelatte variabler, omvendt kausalitet, målefeil), ikke multikollinearitet.

## `poisson` eller `negative-binomial`
- Teksten for `negative-binomial` sier «forventet verdi større enn variansen». Det er omvendt:
  overdispersjon er når variansen er større enn forventningen, og da passer `negative-binomial`. Teksten for
  `poisson` er riktig. Sjekk med `summarize` (varians = std²) og se om `alpha` i `negative-binomial` er
  tydelig større enn 0.

## Paneldata
- `import-panel` virker bare i et tomt datasett. Lag populasjonen først, og bruk
  `clone-units <populasjon> <panel>` og `use <panel>` før `import-panel`.
- Datasettet får én rad per enhet og tidspunkt. Hold populasjonen under ca. 1 million enheter (manualen).
- Akkumulerte variabler (inntekt) gir årsverdien uansett dato i året. Med `2018-01-01` får du inntekt for
  2018, men status (sivstand, bosted) per 1.1.2018. Si fra om rekkefølgen er viktig for tolkningen.
- `robust` i `regress-panel` og `regress-panel-diff` er cluster på panel-ID. `cluster()` kan ikke brukes samtidig.
- `hausman`: p < 0,05 betyr at fixed effects bør brukes. Utskriften har fe, re og forskjellene. Tom
  standardfeil for noen ledd (negativ variansforskjell) er normalt. Les chi2 og p nederst.
- **Testet (versjon 60, november 2026, `kodesnutter/paneldata.txt`):** `import-panel` med en fast variabel
  (kjønn) og datoer virker, `year(date@panel)` gir året, og `i.aar` virker i `regress-panel` og `hausman`
  (første år er referanse). `transitions-panel` viser kodene uten navn. `tabulate-panel x, colpct` virker med én
  variabel, med årene som kolonner. Uten fe blandes effekten
  med faste forskjeller mellom personer, og forskjellen kan være stor.

## Standardfeil, faktorvariabler og prediksjon
- `cluster()` må være en numerisk variabel som ikke er med i modellen, og kan ikke kombineres med `robust`.
  Bruk cluster når enhetene er gruppert (f.eks. elever i skoler, personer i kommuner).
- Kategoriske variabler skrives som `i.var`. Uten `i.` tolkes en numerisk kode som kontinuerlig. Interaksjon:
  `i.a#i.b` (bare interaksjonen) eller `i.a##i.b` (hovedeffekter og interaksjon). `control(i.kommune)` tar
  med faste effekter uten å vise dem.
- **`i.` virker på tekstvariabler, og `destring` trengs ikke** (versjon 60, 2026-11-23, TESTLISTE 8.15).
  `i.kjonn` (`BEFOLKNING_KJOENN`), `i.fylke` (`substr` av kommunenummeret) og `i.invkat` (bokstavene A–G)
  ga én rad per kategori unntatt den laveste, i `regress` og `logit`, og `i.kjonn##i.invkat` ga
  hovedeffekter og samspill («kjonn 'Kvinne' ⨯ invkat 'Innvandrere'»). `i.fylke` ga de samme
  koeffisientene som etter `destring`. Variabler med kodeliste vises bare med navnet («invkat
  'Innvandrere'», uten koden), og variabler uten kodeliste med verdien («fylke '11'»).
  - Referansen er den laveste verdien. Fylkesnumrene har ledende null ('03'), så rekkefølgen var den samme
    som for tall. Tekst uten ledende null ('3', '11') er ikke testet. Som tekst kommer '11' trolig før
    '3', så se etter hvilken kategori som mangler i tabellen.
- **Testet med `logit` (versjon 60, november 2026, `kodesnutter/logistisk_regresjon.txt`):** laveste kode er
  referanse, og kategoriene vises med navn. `cluster()` virker med `or` og `mfx()`, og gir
  langt lavere z-verdier. `mfx(dydx)` skriver først koeffisientene, så marginaleffektene under «dydx av syss».
  `logit-predict` godtar `i.`-ledd.
- **`c.x#c.x` og `c.x##c.x` (andregradsledd) utelates fra modellen uten melding**, både i `regress` og
  `logit` (versjon 60, 2026-11-20, TESTLISTE 8.11).
  - Resultatet har ingen rad for leddet og er samme modell som uten. Koeffisienten for alder blir helt annerledes
    enn med andregradsleddet.
  - **Løsning:** lag andregradsledd som egen variabel: `generate alder2 = alder * alder`.
  - **Samspill mellom ulike variabler virker:** `c.alder#c.lonn23` (vises som «alder ⨯ lonn23») og
    `i.mann#c.alder` (vises som «mann '1' ⨯ alder»), i både `regress` og `logit`. Koeffisientene skiller
    seg noen prosent fra en variabel laget med `generate`, trolig fordi den genererte produktvariabelen
    winsoriseres for seg.
  - Sjekk at alle ledd du skrev, har en rad i tabellen. I `regress` er F-testens frihetsgrader lik antall
    ledd som faktisk er med. `LR chi2` i `logit` har alltid én frihetsgrad mer enn de synlige leddene, så
    der sier frihetsgradene ikke om et ledd er med.
- **Kontroller prediksjoner mot noe som ikke er i modellen.** En logit med `i.gruppe` treffer andelen per
  gruppe nøyaktig, så den sammenligningen sier ingenting.
- `logit`/`probit` krever et utfall som er 0/1. `mfx(dydx)` gir gjennomsnittlige marginaleffekter
  (`overall`). For en 0/1-variabel er det trolig den deriverte, ikke en diskret endring fra 0 til 1
  (TESTLISTE 8.7, versjon 60). Forskjellen er liten. Trengs den diskrete effekten, bruk forskjellen i
  `margins()`. `or` gir oddsratio. `margins()` gir predikert verdi ved gjennomsnittet av
  forklaringsvariablene, ikke gjennomsnittet av predikerte verdier.
- `mlogit` viser koeffisientene for hver utfallskategori under hverandre uten å si hvilken kategori blokken
  gjelder (versjon 60). Første kategori er referanse, og blokkene står trolig i stigende rekkefølge. Si fra om
  det når resultatet tolkes, eller lag utfallet med få, tydelige kategorier.
- `regress-mml`: gruppevariabelen kan ikke også være forklaringsvariabel. Like variansestimater for to
  nivåer (f.eks. fylke og landsdel) betyr at nivåene fanger opp det samme. Bruk ett av dem.
- Spredningsplott finnes ikke. Bruk `hexbin` (celler med under 5 enheter vises ikke). Søyler i `histogram`
  og `barchart` med under 5 enheter vises heller ikke (tiltak 11).
