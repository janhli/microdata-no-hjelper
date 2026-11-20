# Mulige feil å rapportere

Funn fra testkjøringer som ser ut som feil i microdata.no (eller i metadata/dokumentasjon), ikke bare
udokumentert atferd. Sendes til microdata@microdata.no (Kreftregisteret-punktene til Kreftregisteret).
Marker hvert punkt med dato når det er sendt, og med svaret når det kommer.

Alle funn: no.ssb.fdb:60, no.fhi.kreftregisteret:1, no.fhi.npr:1, anonymiseringstiltak versjon 2,
18. november 2026.

## Resultatvisning

### 1. Kopi av hele utskriften mangler resultater fra mange kommandoer
Når hele skriptet med resultater kopieres ut, står disse kommandoene uten resultat, selv om resultatet vises i
analyseverktøyet: `citation`, `tabulate-panel`, `regress-panel-diff`, `summarize-panel`, `probit`, `poisson`,
`negative-binomial`, `list-labels`, `variables`. `coefplot` gir tomme regresjonstabeller i kopien. (Grafene
mangler også, men det er kanskje forventet.) `logit`, `mlogit`, `regress`, `regress-panel` og `hausman` kommer med.

Eksempel:
```
probit hoy mann alder        // vises i verktøyet, mangler i kopien
logit hoy mann alder         // kommer med
```
Konsekvens: det ser ut som kommandoen ikke ga resultat, og resultater går tapt ved dokumentasjon.

### 2. `ci`: kolonnen «Median» ser ut til å være gjennomsnittet
`ci lonn` viste «Median» 674 979, mens `summarize lonn` på samme datasett ga gjennomsnitt 664 571 og median
628 777. Tallet i `ci` er hverken medianen eller det winsoriserte gjennomsnittet. Det kan være det
ikke-winsoriserte gjennomsnittet med feil kolonnenavn. Er det meningen at `ci` ikke winsoriseres?

### 3. `logit`: LR chi2 har én frihetsgrad for mye
`logit hoy mann alder` (to forklaringsvariabler) viser «LR chi2(3)». `cox dod24 tid mann alder` viser
«LR chi2(2)» for to variabler, som forventet.

### 4. `mlogit`: koeffisientblokkene har ikke navn på utfallskategorien
`mlogit utdgr mann alder` (utfall med tre kategorier) viser to blokker med `mann`, `alder`, `Konst` under
hverandre, uten å si hvilken kategori hver blokk gjelder eller hva referansekategorien er.

### 5. `regress-mml`: tabellene ser ut til å ha forskjøvne kolonner
`regress-mml lonn mann alder by fylke`:
- Testtabellen har tallene (884,09, 2983,79 ...) under «Test», 0 under «Statistikk», «chi2» under «p-verdi»
  og 1, 2, 3 under «Distribusjon».
- Gruppetabellen viser «Grupperingsvariabel 15, N grupper 681, Min 7080, Maks 3334,67, Gjennomsnitt
  2 339 040 384». 15 ser ut til å være antall grupper (fylker), og Maks er mindre enn Min.

### 6. `weibull`: tabellen ser ut til å ha forskjøvne kolonner
`weibull dod24 tid` med 177 hendelser av 50 000 viste «Hendelsesrate 3 636 401 167, Antall 0, 75% 49 995».
Første kolonne og siste kolonne er uten overskrift. (Tidsvariabelen var feil i denne kjøringen, men «Antall 0»
med 177 hendelser og antall observasjoner under «75%» ser uansett feil ut.)

### 7. Stoppet regresjon viser tomme tabeller
Når `regress lonn mann` stoppes av tiltak 17, vises tomme regresjonstabeller («F(, )») i tillegg til
feilmeldingen. Mindre viktig, men kan forveksles med et resultat.

### 8. `regress-panel-diff`: navnet på interaksjonsleddet begynner med ⨯
Leddet heter «⨯ gruppe ⨯ etter». Kosmetisk.

## Modeller

### 17. `c.x#c.x` og `c.x##c.x` utelates uten melding (funnet 19.–20. november 2026)
Et samspill mellom en variabel og seg selv tas ikke med i modellen, og ingen melding forteller det:
- `regress lonn alder c.alder#c.alder mann` gir samme modell som `regress lonn alder mann`: R² 0,0615
  og F(2, ...). Med `alder2 = alder*alder` er R² 0,0932.
- `c.alder##c.alder` gir det samme.
- `logit hoy alder c.alder#c.alder mann` gir log-likelihood −107 337, og med `alder2` −104 976.

Samspill mellom ulike variabler virker (`c.alder#c.lonn23`, `i.mann#c.alder`). Andregradsledd er vanlige,
og brukeren får en annen modell enn den hen skrev. Enten bør leddet beregnes, eller det bør komme en
feilmelding.

### 18. Winsorisering gjør gjennomsnittet av sjeldne 0/1-variabler til 0 (funnet 20. november 2026)
En 0/1-variabel der 0,53 % har verdien 1 (3 729 av 709 037), ga i `summarize` gjennomsnitt 0,
standardavvik 0 og 99-persentil 0. `tabulate bydel, summarize(x) mean` ga 0 i alle grupper. `tabulate x`
viste 3 729 med verdien 1. Andeler av sjeldne utfall (død, diagnoser) blir dermed 0 uten melding, og i
undergrupper også for utfall som er over 1 % totalt. Winsorisering gir neppe mening for variabler med to
verdier. Kan 0/1-variabler (eller variabler med få verdier) unntas?

## Metadata

### 9. `S_TOPOGRAFIICD10`: dataene har koder som ikke står i kodelisten
Blant ondartede krefttilfeller med diagnoseår 2023 hadde 102 topografi D45 og 200 D46 (`substr(topo, 1, 3)`).
Kodelisten i variabelbeskrivelsen har D47 og underkoder, men ikke D45 eller D46. Kreftregisterets
metadatabase (ELVIS) har dem som kreftformer under C81–C96.

### 10. `S_STRALEBEH`: kodelisten har bare `1`
Kodelisten i microdata.no har bare `1` (mottatt strålebehandling), og dataene har bare `1` og manglende
verdi (8 567 og 30 322 i 2023). ELVIS har også 0 (ikke behandlet), 2–5 og 9. Hvis manglende betyr «ikke
registrert med strålebehandling», bør det stå i variabelbeskrivelsen.

### 11. Datovariabler med ulikt format uten at det står i beskrivelsen
`BEFOLKNING_DOEDS_DATO` er et tall i formatet ÅÅÅÅMMDD (20240315), mens `date()` og `START@` er dager siden
1970. `dod - date(2024, 1, 1)` gir derfor rundt 20 millioner uten feilmelding. Formatet står bare i
metadataene (`format: YYYYMMDD`), ikke på variabelsiden. Ønske: en funksjon som gjør ÅÅÅÅMMDD om til dato,
eller at formatet vises tydelig. Navn som `KRIMINALITET_SIKTEDE_GJDATO1` (format ÅÅÅÅMM) gjør det verre.

## Dokumentasjon

### 12. Sammenligning med manglende verdi er ikke dokumentert
`generate h = x > 5` gir 0 når x mangler, `x != 2` gir 1, og `replace h = 1 if x > 5` endrer ikke enheter der
x mangler. Brukere som kjenner Stata (der manglende er større enn alle tall) får feil dummyer uten varsel.
Bør stå i manualen.

### 13. `negative-binomial`: overdispersjon er beskrevet omvendt
Manualen: «Negativ binomial-regresjon bør velges dersom forventet verdi for den avhengige variabelen er større
enn variansen (overdispersjon).» Overdispersjon er når variansen er større enn forventningen.

### 14. `ivregress` og overlevelsesanalyse i manualen
- `ivregress`: teksten bytter om begrepene («instrumentvariabel på venstre side»), og eksempelsiden sier at IV er
  for multikollinearitet. IV er for endogenitet.
- Overlevelsesanalyse (5.14.1, eksempel A): populasjonen lages fra `import-event` og består bare av personer som
  fikk hendelsen, så ingen er sensurert. Død og utvandring sensureres heller ikke.

### 15. `citation` er nesten ikke beskrevet
Manualen har én linje. Det bør stå at alle datalagre i `require` tas med (også de som ikke er brukt), at
datalagerversjonen ikke er med, og at resultatet ikke kommer med når utskriften kopieres (punkt 1).

## Til Kreftregisteret (ELVIS)

### 16. Skrivefeil i kreftformene (`/rest/v1/metadata/cancer-sites`)
- «Skjoldbruskkjertel og andre enodkrine kjertler» (endokrine), og «Skjoldbrukskjertel» for C73 (Skjoldbruskkjertel)
- «Mutliple myeloma and malignant plasma cell neoplasms» (Multiple)
- «Andre og upesifiserte ondartede svulster ...» (uspesifiserte), «... heamatopoietic ...» (haematopoietic)
