<!-- Kilde: https://microdata.no/manual/systemendringer -->

# Systemendringer som kan påvirke resultater

Reproduserbare resultater har vært sentralt i utviklingen av microdata.no. [Innebygget dataversjonering](https://www.microdata.no/wp-content/uploads/2022/02/FAIR_Data_Versioning_in_Microdata.pdf) er blant virkemidlene for å oppnå dette. Omfattende testbatterier som sørger for at oppdateringer av underliggende biblioteker og komponenter ikke gir endringer i analyseresultater er et annet viktig tiltak.

I visse tilfeller er det imidlertid ikke mulig å unngå endringer som påvirker resultater/analyser. Endringer i konfidensialiseringsmekanismene er én type systemendring som kan føre til at nye kjøringer av eldre skript gir litt andre resultater enn før.

Vi dokumenterer her systemendringer som gir endrede resultater.

## 2026-11-17

### Større endringer i ny hovedoppgradering av tjenesten

I forbindelse med [den større utvidelsen av microdata.no](https://www.microdata.no/omfattende-oppgradering-av-microdata-no/) er det utviklet en versjon 2 av anonymiseringstiltakene.

Muligheten til å analysere helsedata og mer detaljerte geografiske inndelinger i microdata.no kommer etter grundige vurderinger og langvarig samarbeid mellom statistikere og systemutviklere om personvernløsningene i tjenesten.

Hvis vi sammenligner versjon 2 med versjon 1, er det følgende endringer som er blitt gjort:

Tiltak 4, 7 og 10 er uforandret. Noen tiltak er fjernet (5, 6, 8, 9), andre er justert (1, 2, 3), og noen nye tiltak (11-17) er kommet til.

Alle tiltakene er beskrevet i kapittelet om konfidensialitet i brukermanualen. Tiltak som har blitt fjernet eller justert er markert spesielt.

#### **Overgangsordning for eksisterende brukere**

For eksisterende brukere vil det være mulig å bytte tilbake til versjon 1 av anonymiseringstiltakene via en egen kommando `configure confidentiality v1` som skrives inn øverst i skriptet. Denne kommandoen aktiviserer versjon 1 av anonymiseringstiltakene i det aktuelle skriptet. Dette er kun mulig for skript som ikke benytter data fra FHI eller grunnkretsvariabel fra SSB, noe som sjekkes automatisk.

Brukere med akkrediteringer som er nyere enn lanseringsdatoen, og som derfor ikke har noen resultater som kan ha blitt endret har naturlig nok ikke mulighet til å ta i bruk overgangsordningen. Dette sjekkes også automatisk.

Overgangsordningen gjør det mulig for forskere og analytikere å kjøre tidligere skript og få samme resultater som før.

Vi gjør også oppmerksom på [den nye funksjonaliteten for å generere signerte og verifiserbare analyseresultater](https://www.microdata.no/signerte-og-verifiserbare-analyseresultater/); i analyseverktøyet har du nå ha mulighet til å generere signerte, daterte og kryptografisk verifiserbare PDF-dokumenter av dine analyseresultater.

Overgangsordningen avsluttes etter planen 30. april 2027. Datoen vil bl.a. avhenge av tilbakemeldinger og andre erfaringer med versjon 2 av anonymiseringstiltakene.

#### **Vi ønsker innspill og tilbakemeldinger**

Det er en krevende balansegang å utvikle gode anonymiseringstiltak som samtidig ikke reduserer nytteverdien i dataene for mye. Arbeidet med de nye tiltakene har hatt som målsetning å treffe en god balanse her.

Tross grundig forarbeid kan det likevel være rom for forbedringer i virkemåten til anonymiseringstiltakene. Dialog med brukere om dette blir ekstra viktig i tiden fremover. Sikt og SSB vil sammen med FHI behandle innspill og tilbakemeldinger raskt og forsøke å imøtekomme behov som dukker opp. Tilbakemeldingene sendes til microdata@microdata.no.

#### **Bakgrunn for disse endringene**

Microdata.no er utviklet for å gjøre det mulig å få tilgang til å analysere registerdata uten å måtte gå gjennom en tidkrevende søknadsprosess for å få data utlevert. En slik forenkling betinger at sikkerheten og konfidensialiteten til dataene er bedre ivaretatt enn ved utlevering. Det er derfor et eksplisitt krav til microdata.no om at brukerne ikke skal kunne se data direkte eller på annen måte være i stand til å avsløre informasjon om enkeltpersoner.

Det betyr at alle analyser blir satt opp ut fra beskrivelser av dataene, såkalte metadata. Utførelsen av analysene foregår inne i systemet og brukerne får bare se statistiske resultater, som blir gjort anonyme av mekanismer i plattformen.

Hva betyr dette konkret?

I analyseverktøyet skriver brukeren selv analyseprogrammer formulert i et eget programmeringsspråk utviklet for registerdataanalyse i microdata.no. I dette programmeringsspråket beskriver brukeren hvilke data som trengs, hvordan de skal struktureres og avgrenses, og hvordan de skal analyseres. Registerdata er data som ikke er designet for analyse (i motsetning til f.eks. utvalgsundersøkelser). Bearbeiding av data og populasjoner er derfor helt nødvendig for å kunne jobbe analytisk med registerdata. Hvordan dette har påvirket arkitekturvalg i microdata.no kan du lese mer om i [dette notatet](https://www.microdata.no/wp-content/uploads/2022/06/Key-Architecture-Choices-in-Microdata.pdf).

Analyseprogrammene som brukerne har skrevet sendes inn i tjenesten, hvor de oversettes til prosedyrer inne i systemet som setter i gang selve databehandlingen og analysene brukeren har bedt om. Statistiske resultater går igjennom automatiserte anonymiseringstiltak før de sendes tilbake til analyseverktøyet hvor brukeren kan se dem.

Anonymiseringstiltakene skjuler eller modifiserer de statistiske resultatene sammenlignet med de resultatene man ville fått uten anonymiseringstiltak. Tiltakene er utformet med en målsetning om at analyseresultatene skal være mest mulig korrekte og presise, men samtidig slik at de ivaretar personvernet. Hvilke tiltak som benyttes avhenger av hvilke typer data og hvilke analyseteknikker som er benyttet. De fleste anonymiseringstiltakene (1-7) har vært stabile siden første lansering av microdata.no i 2018, og noen nye (8-10) har kommet til i tjenestens levetid.

Disse 10 tiltakene kan betraktes som versjon 1 av anonymiseringstiltakene.

I det langvarige forarbeidet før utvidelsen av microdata.no denne datoen, har Sikt og SSB oppdatert personvernvurderingen av microdata.no. FHI har bl.a. på grunnlag av denne og gjennom sitt eget testprogram gjort en helhetlig risikovurdering av tjenesten inkludert deres egen personvernkonsekvensvurdering. Disse risikovurderingene omfatter også de alminnelige sikkerhetstiltakene i og rundt tjenesten for å hindre uautorisert tilgang eller bruk.

Denne versjon 2 av anonymiseringstiltakene er et resultat av dette forarbeidet.

## 2025-10-01

### Kaplan-meier-grafer vises ikke lenger

Kaplan-Meier-grafer fremstiller faktiske endringer i overlevelsesrater (og ikke estimerte). Det har i enkelte situasjoner vist seg å være vanskelig å beskytte personvernet optimalt uten å støylegge endringene i overlevelsesratene som tegnes i grafen. Men det har også vist seg vanskelig å støylegge disse endringene uten å introdusere for stor usikkerhet mtp tolkning av Kaplan-Meier-grafene, fordi støyleggingen har en kumulativ effekt over tidsperioden.

Vi har derfor valgt å fjerne den grafiske fremstillingen for kommandoen `kaplan-meier`. De mindre detaljerte hovedtallene under grafen beholdes og kan brukes som før.

For kommandoen `weibull` baserer de genererte overlevelsesgrafene seg på estimerte/predikerte overlevelsesrater (med utgangspunkt i de faktiske observasjoner), og personvernutfordringene er vesentlig mindre. Om det viktigste for deg er å lage grafiske fremstillinger av overlevelsesrater, anbefaler vi derfor å benytte kommandoen `weibull`. Merk at hovedtallene hentes ut fra den estimerte grafen, og at tallene derfor har en viss unøyaktighet i forhold til det `kaplan-meier` rapporterer. Om korrekte tall er det viktigste, anbefaler vi å bruke `kaplan-meier` som fortsatt produserer en tabell. De to kommandoene kan også kombineres. Men da må det tas forbehold om at weibull-grafene er basert på estimater, og ikke de observerte endringene.

## 2025-04-23

### Endring: Persentiler beregnes på en ny måte

Persentil-resultater fra kommandoene `summarize`, `tabulate, summarize()`, `boxplot`, `collapse` og `aggregate` er endret etter innføring av tiltak 10 (mikroaggregering + glatting av persentiler).

## 2025-04-04

### Endring: Histogram har ny implementasjon

Kommandoen `histogram` er endret og har nå bl.a. samme støylegging som tabuleringer og vanlige søylediagrammer.

## 2024-08-19

### Endring: Barchart (søylediagram) er strammet opp og utvidet

Kommandoen `barchart` har frem til denne datoen hatt en del logiske problemer og inkonsistent virkemåte.

Dette er det nå ryddet opp i. For visse eldre skript som inkluderte `barchart` kan endringen medføre endret output eller feilmelding.

Det vil i de fleste slike tilfeller være kurant å justere kommandoen noe, og få bedre og mer forståelige søylediagrammer.

## 2024-06-18

### Endring: Winsorisering ved collapse til ikke-pseudonymisert variabel

Dersom mål-enhetstypen til `collapse()` (angitt i `by()`-leddet) er en enhetstype gitt ved en vanlig ikke-pseudonymisert variabel, f.eks. kommune, fylke, næringstype, eller utdanningsnivå, vil beregninger gjort gjennom `collapse()` være gjenstand for samme winsorisering som for deskriptiv statistikk utført på standard pseudonymiserte enhetstyper som f.eks. personid og familieid.

Mer informasjon om winsorisering [her](https://microdata.no/manual/konfidensialitet#tiltak-2-winsorisering).
