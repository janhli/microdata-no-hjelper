# Utkast: e-post til microdata.no

**Til:** microdata@microdata.no
**Emne:** Mulige feil i analyseverktøyet og metadata (versjon 60, anonymiseringstiltak versjon 2)

---

Hei,

Vi har testet analyseverktøyet systematisk etter overgangen til versjon 2 av anonymiseringstiltakene, og har
funnet noen ting som ser ut som feil, eller som kan gi brukere feil resultater uten at de merker det. Alle
funn er fra no.ssb.fdb:60, no.fhi.kreftregisteret:1 og no.fhi.npr:1 med anonymiseringstiltak versjon 2,
18.–20. november 2026. Vi har skriptene og kan sende dem hvis det er nyttig.

De to første punktene er de viktigste, fordi de gir en annen analyse enn brukeren skrev, uten melding.

## Modeller og winsorisering

**1. Sjeldne 0/1-variabler blir konstante etter winsoriseringen**

En 0/1-variabel der under 1 % har verdien 1, blir 0 for alle etter winsoriseringen (1 % i hver ende):

- `summarize x` med 0,53 % enere (3 729 av 709 037 i `tabulate x`) ga gjennomsnitt 0, standardavvik 0 og
  99-persentil 0. `tabulate gruppe, summarize(x) mean` ga 0 i alle grupper.
- Som forklaringsvariabel i `regress` og `logit` utelates den uten melding. I et utvalg på 405 000 ble
  variabler med 0,22 % og 0,85 % enere utelatt (bare `F(1, ...)` for den andre variabelen), mens 1,26 % og
  2,47 % var med.
- Som utfall blir modellen meningsløs, uten feilmelding. Med 0,34 % enere ga `regress` bare 0 og «NaN», og
  `logit` «Pseudo R2 Infinity» etter 35 iterasjoner. Med utfallet snudd (over 99 % enere) ga `logit` negativ
  LR chi2 og koeffisienter med z = −145, som ser ut som et gyldig resultat.

Behandlingen er ulik mellom kommandoene. Kategorier i `i.`-variabler på 0,2 % ble ikke berørt (`i.x` på den
samme 0/1-variabelen ga riktig koeffisient), og heller ikke hendelsen i `cox` (0,19 % døde ga rimelige
koeffisienter).

Andeler av sjeldne utfall (død, diagnoser) er vanlige i analyser, og i undergrupper kan også utfall som er
over 1 % totalt, falle under grensen. Kan variabler med to verdier (eller få verdier) unntas fra
winsoriseringen? Eller kan det i det minste komme en melding når en variabel blir konstant?

**2. `c.x#c.x` og `c.x##c.x` utelates uten melding**

Et samspill mellom en variabel og seg selv tas ikke med i modellen:

- `regress lonn alder c.alder#c.alder mann` gir samme modell som `regress lonn alder mann` (R² 0,0615 og
  `F(2, ...)`). Med `alder2 = alder*alder` er R² 0,0932.
- `c.alder##c.alder` gir det samme.
- `logit hoy alder c.alder#c.alder mann` gir log-likelihood −107 337, og med `alder2` −104 976.

Samspill mellom ulike variabler virker (`c.alder#c.lonn23`, `i.mann#c.alder`). Andregradsledd er vanlige, så
enten bør leddet beregnes, eller det bør komme en feilmelding.

**3. `logit`: LR chi2 har én frihetsgrad for mye**

`logit hoy mann alder` (to forklaringsvariabler) viser «LR chi2(3)». `cox dod24 tid mann alder` viser
«LR chi2(2)», som forventet.

**4. `ci`: kolonnen «Median» ser ut til å være et gjennomsnitt**

`ci lonn` viste «Median» 674 979, mens `summarize lonn` på samme datasett ga gjennomsnitt 664 571 og median
628 777. Tallet kan være det ikke-winsoriserte gjennomsnittet med feil kolonnenavn. Er det meningen at `ci`
ikke winsoriseres?

## Resultatvisning

**5. Kopi av hele utskriften mangler resultater fra mange kommandoer**

Når hele skriptet med resultater kopieres, står disse kommandoene uten resultat, selv om resultatet vises i
verktøyet: `citation`, `tabulate-panel`, `regress-panel-diff`, `summarize-panel`, `probit`, `poisson`,
`negative-binomial`, `list-labels` og `variables`. `coefplot` gir tomme regresjonstabeller i kopien.
`logit`, `mlogit`, `regress`, `regress-panel` og `hausman` kommer med. Det ser da ut som om kommandoen ikke
ga resultat, og resultater går tapt når analysen dokumenteres.

**6. `mlogit`: koeffisientblokkene har ikke navn på utfallskategorien**

`mlogit utdgr mann alder` (utfall med tre kategorier) viser to blokker med `mann`, `alder` og `Konst`, uten å
si hvilken kategori hver blokk gjelder, eller hva referansekategorien er.

**7. `regress-mml`: tabellene ser ut til å ha forskjøvne kolonner**

`regress-mml lonn mann alder by fylke`:
- Testtabellen har tallene (884,09, 2983,79 ...) under «Test», 0 under «Statistikk», «chi2» under
  «p-verdi» og 1, 2, 3 under «Distribusjon».
- Gruppetabellen viser «Grupperingsvariabel 15, N grupper 681, Min 7080, Maks 3334,67, Gjennomsnitt
  2 339 040 384». 15 ser ut til å være antall grupper, og Maks er mindre enn Min.

**8. `weibull`: tabellen ser ut til å ha forskjøvne kolonner**

`weibull dod24 tid` med 177 hendelser av 50 000 viste «Hendelsesrate 3 636 401 167, Antall 0, 75% 49 995».
Første og siste kolonne er uten overskrift. Tidsvariabelen var feil i denne kjøringen, men «Antall 0» med
177 hendelser, og antall observasjoner under «75%», ser uansett feil ut.

**9. Stoppet regresjon viser tomme tabeller**

Når `regress lonn mann` stoppes av tiltak 17, vises tomme regresjonstabeller («F(, )») i tillegg til
feilmeldingen. De kan forveksles med et resultat.

**10. `regress-panel-diff`: navnet på interaksjonsleddet begynner med ⨯**

Leddet heter «⨯ gruppe ⨯ etter». Kosmetisk.

## Metadata

**11. Datovariabler med ulikt format**

`BEFOLKNING_DOEDS_DATO` er et tall i formatet ÅÅÅÅMMDD (20240315), mens `date()` og `START@` gir dager
siden 1970. `dod - date(2024, 1, 1)` gir derfor rundt 20 millioner, uten feilmelding. Formatet står i
metadataene (`format: YYYYMMDD`), men ikke på variabelsiden. Det ville hjelpe med en funksjon som gjør
ÅÅÅÅMMDD om til dato, eller at formatet vises tydelig. `KRIMINALITET_SIKTEDE_GJDATO1` (ÅÅÅÅMM) har samme
problem.

**12. `S_TOPOGRAFIICD10`: dataene har koder som ikke står i kodelisten**

Blant ondartede krefttilfeller med diagnoseår 2023 hadde 102 topografi D45 og 200 D46. Kodelisten har D47 og
underkoder, men ikke D45 eller D46. Kreftregisterets metadatabase (ELVIS) har dem som kreftformer under
C81–C96.

**13. `S_STRALEBEH`: kodelisten har bare `1`**

Kodelisten har bare `1` (mottatt strålebehandling), og dataene har bare `1` og manglende verdi (8 567 og
30 322 i 2023). ELVIS har også 0 (ikke behandlet), 2–5 og 9. Hvis manglende betyr «ikke registrert med
strålebehandling», bør det stå i variabelbeskrivelsen.

## Dokumentasjon

**14. Sammenligning med manglende verdi er ikke dokumentert**

`generate h = x > 5` gir 0 når x mangler, `x != 2` gir 1, og `replace h = 1 if x > 5` endrer ikke enheter
der x mangler. Brukere som kjenner Stata, der manglende er større enn alle tall, får andre dummyer enn de
venter, uten varsel. Dette bør stå i manualen.

**15. `negative-binomial`: overdispersjon er beskrevet omvendt**

Manualen sier: «Negativ binomial-regresjon bør velges dersom forventet verdi for den avhengige variabelen
er større enn variansen (overdispersjon).» Overdispersjon er når variansen er større enn forventningen.

**16. `ivregress` og overlevelsesanalyse i manualen**

- `ivregress`: teksten bytter om begrepene («instrumentvariabel på venstre side»), og eksempelsiden sier at
  IV er for multikollinearitet. IV er for endogenitet.
- Overlevelsesanalyse (5.14.1, eksempel A): populasjonen lages med `import-event` og består bare av personer
  som fikk hendelsen, så ingen er sensurert. Død og utvandring sensureres heller ikke. Uten sensurering ved
  utvandring fikk innvandrere 70+ i vår test en hazardrate for død på 0,785 i stedet for 0,811.

**17. `citation` er nesten ikke beskrevet**

Manualen har én linje. Det bør stå at alle datalagre i `require` tas med (også de som ikke brukes), at
datalagerversjonen ikke er med, og at resultatet ikke kommer med når utskriften kopieres (punkt 5).

---

Takk for et svært nyttig verktøy. Si gjerne fra hvis noe av dette er tilsiktet, eller hvis dere vil ha
skriptene.

Vennlig hilsen
[Navn]

---

# Utkast: e-post til Kreftregisteret (skrivefeil i ELVIS)

**Til:** [adressen for ELVIS / metadata hos Kreftregisteret]
**Emne:** Skrivefeil i kreftformene i ELVIS (`/rest/v1/metadata/cancer-sites`)

Hei,

Vi har funnet noen skrivefeil i navnene på kreftformene i ELVIS (`/rest/v1/metadata/cancer-sites`):

- «Skjoldbruskkjertel og andre enodkrine kjertler» (endokrine), og «Skjoldbrukskjertel» for C73
  (Skjoldbruskkjertel)
- «Mutliple myeloma and malignant plasma cell neoplasms» (Multiple)
- «Andre og upesifiserte ondartede svulster ...» (uspesifiserte), og «... heamatopoietic ...»
  (haematopoietic)

Vennlig hilsen
[Navn]
