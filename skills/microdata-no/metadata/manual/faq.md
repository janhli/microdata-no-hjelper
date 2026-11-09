<!-- Kilde: https://microdata.no/manual/faq -->

# Ofte stilte spørsmål

### Hva er microdata.no?

microdata.no er utviklet for å gi umiddelbar, søknadsfri og online tilgang til skarpe, detaljerte registerdata som du kan bruke til statistikk, forskning og analyse.

Norge har mange gode kilder til registerdata, og norsk lov åpner for at de kan avidentifiseres og brukes til å utarbeide statistiske resultater og analyser, herunder forskning. For å få tradisjonell tilgang til slike mikrodata fra register må du gjennom en omfattende søknadsprosess. I tillegg er det tid- og kostnadskrevende å tilrettelegge dataene.

microdata.no er et viktig supplement og en komplementær løsning for de som bestiller tilgang til mikrodata fra SSB. Tjenesten gir øyeblikkelig tilgang og lar brukeren selv tilrettelegge registerdata uten å søke. Analysen av dataene kan foregå i microdata.no, eller de kan eksporteres til et sikkert analyserom etter søknad på tradisjonell måte.

### Hva slags data er tilgjengelige i microdata.no?

Microdata.no gir tilgang til et bredt utvalg av registerdata innenfor områder som demografi, utdanning, inntekt, arbeidsledighet, sysselsetting, trygd, boforhold, og andre sosioøkonomiske forhold. I tillegg til persondata, tilbys også data om kjøretøy, trafikkulykker, strømforbruk m.m. Alle data kan aggregeres til høyere nivå som f.eks. husholdning/familie, bydel, kommune, fylke, landsdel, eller ulike typer befolkningsgrupperinger.

 [Se hele variabeloversikten her.](https://microdata.no/discovery?language=no)

### Hvem kan få tilgang til microdata.no?

Tilgangen til opplysninger etter statistikklovens § 14, defineres av § 1 i Forskrift til statistikkloven som sier at (1) Tilgang til opplysninger etter statistikklovens §14 kan gis til forskningsinstitusjoner for forskningsformål og til følgende organer for utarbeiding av statistiske resultater og analyser[...].

Ansatte og master-, og PhD-studenter ved godkjente forskningsinstitusjoner (i henhold til forskningsrådets og Eurostats liste over godkjente forskningsinstitusjoner) kan få tilgang til microdata.no. Tilgangen forutsetter at institusjonen har en avtale om bruke av tjenesten.

 [Mer informasjon om tilgang finner du her.](https://www.microdata.no/bli-bruker/)

### Hva kan resultatene utarbeidet i microdata.no brukes til?

Tilgangen til tilgjengelige data/opplysninger er definert i §14 i Statistikkloven som sier at (1) Statistisk sentralbyrå kan gi tilgang til opplysninger for utarbeiding av statistiske resultater og analyser, herunder forskning, når det ikke medfører uforholdsmessig ulempe for andre interesser.

Den ansatte/studenten har ikke anledning til å benytte resultater og analyser til andre formål enn hva som er oppgitt i §14, og som er i tråd med arbeidsgivers eller studiestedets retningslinjer for den ansattes/studentens bruk.

### Hvordan går jeg frem for å få tilgang til microdata.no?

For å få tilgang til microdata.no, må du kontakte din kontaktperson ved institusjonen/arbeidsplassen din. Det er institusjonen, studiestedet eller arbeidsgiveren som ber om tilgang og melder inn brukerne. Tilgang er tilgjengelig for ansatte og studenter ved norske universiteter og høyskoler, godkjente forskningsinstitusjoner, offentlige etater og konsulentselskaper som jobber på oppdrag for offentlig sektor.

 [Mer informasjon om tilgang finner du her.](https://www.microdata.no/bli-bruker/)

### Har dere funksjonalitet X?

For å sjekke om microdata.no støtter en spesifikk funksjonalitet, som regresjon eller andre analysemetoder, kan du søke i brukermanualen. Bruk søkefunksjonen øverst til høyre til å finne relevante kommandoer eller beskrivelser ved å skrive inn stikkord som "regresjon", "analyse", eller andre nøkkelord knyttet til det du leter etter. Dette vil gi deg en oversikt over tilgjengelige funksjoner. Du kan også søke etter spesifikke kommandoer eller funksjoner i søkefeltet, f.eks. "regress" eller "logit".

 [Du kan utforske mer i brukermanualen.](https://microdata.no/manual/kommandoer_og_funksjoner)

### Er det mulig å eksportere data til andre programmer?

Det er ikke mulig å eksportere rådata fra microdata.no til eksterne programmer, men det er mulig å eksportere analyseresultater. Microdata.no er laget for å gi brukere tilgang til å analysere registerdata på en sikker måte uten å utlevere rådata. Analyser utføres innenfor verktøyet, som tilbyr et bredt spekter av funksjoner og kommandoer for ulike analysebehov.

 Mer informasjon om eksport av analyseresultater finner du i brukermanualen.

### Hvordan kan jeg eksportere analyseresultater som en fil?

Du kan kopiere analyseresultater og bruke dem i andre programmer ved å klikke på kopieringsknappen øverst til venstre i analyseresultatet. For å få dataene som en CSV-fil, velg "Semikolonseparerte verdier" før du kopierer. Deretter kan du lime inn dataene i et tekstredigeringsprogram og lagre dem som en CSV-fil.

### Hvorfor avviker statistikken jeg lager i microdata.no fra SSBs offisielle tall?

Statistikk laget i microdata.no kan avvike fra SSBs offisielle tall av flere grunner. Ulike datakilder kan gi forskjellige resultater, så det er viktig å sørge for at dataene sammenlignes fra samme kilde. Måletidspunkt kan også variere; mens noen statistikker er basert på årlige, kvartalsvise eller månedlige tall, bruker andre spesifikke datoer, som 1. januar eller 16. november. Avgrensninger i populasjonen, som aldersgrupper eller bosattstatus, kan også skape forskjeller. I tillegg foretar SSB ofte ekstra behandling og "rensing" av data som ikke nødvendigvis gjøres i microdata.no. Til slutt kan personvernmekanismer, som støylegging og sensurering av ekstreme verdier, påvirke resultatene og gi avvik i gjennomsnitt og andre statistiske beregninger.

 For mer informasjon om avvik, se her.

### Hvorfor kan jeg ikke kombinere ulike enhetstyper i et datasett?

Det er ikke mulig å kombinere ulike enhetstyper i samme datasett direkte fordi variablene i et datasett må ha samme enhetstype, som vanligvis er personer identifisert ved PERSONID_1. Når du importerer variabler kobles dataene automatisk sammen, og systemet forventer at alle variablene har samme enhetstype.

For å analysere data på andre enhetsnivåer, som kommune- eller hendelsesnivå, må disse dataene først bearbeides før de kan kobles mot et persondatasett. Data på lavere enhetsnivå enn person, som hendelser eller kurs, må aggregeres opp til personnivå ved hjelp av kommandoen collapse(). Data på samme eller høyere enhetsnivå, som kommune, kan kobles direkte ved å bruke en felles variabel som koblingsnøkkel i merge-kommandoen.

 Du kan lese mer om dette i brukermanualen.

### Hvorfor stemmer ikke tallene mine når jeg summerer opp tabeller og andre beregninger?

Siden microdata.no består av registerdata, er det viktig å sikre at enkeltpersoner ikke kan identifiseres. Derfor er det implementert flere personverntiltak, inkludert støylegging. Tallene kan avvike når du summerer opp tabeller eller gjør beregninger fordi dataene er støylagt for å ivareta personvernet. Dette betyr at antall enheter kan justeres litt, og summer av numeriske variabler er justert tilsvarende for å opprettholde korrekte gjennomsnitt.

 Du kan lese mer om støylegging og de andre tiltakene for konfidensialitet her.

### Hvorfor blir jeg stoppet av avsløringskontrollen på grunn av for få måldataenheter?

Grunnen til at det skjer er fordi det ikke er tillatt å definere undersøkelsespopulasjoner med færre enn 1000 personer i microdata.no. Hvis du forsøker å opprette en populasjon som faller under denne grensen, vil du få en melding som stopper operasjonen for å ivareta personvernet.

### Kan jeg bruke andre programmeringsspråk i microdata.no?

Nei, microdata.no støtter ikke bruk av andre programmeringsspråk. Verktøyet har en egen syntaks som ligner på det som brukes i andre analyseverktøy.

 Du finner mange eksempler på hvordan syntaksen brukes i brukermanualen.

### Hvordan oppgi microdata.no som kilde når jeg publiserer mine resultater?

 [Les mer om det her.](https://www.microdata.no/dokumentasjon/kildehenvisning/)

### Hva er begrensningene for datamengden ved bruk av kommandoen import-panel?

Import-panel har ganske strenge begrensinger på datamengden (observasjoner x variabler x måletidspunkter). Det skal derfor ikke mye til før kjøringen stopper opp eller man får feilmelding. Dersom man arbeider med større populasjoner, er det heller anbefalt å bruke reshape-to-panel. Denne kommandoen endrer strukturen på datasettet til et paneldatasett, og er mer fleksibel enn import-panel er. [Les mer om import-panel her.](https://microdata.no/manual/brukermanual/Oppretting%20og%20endring%20av%20datasett/2.9.1%20Restrukturere%20fra%20tverrsnittsdata%20til%20paneldata/)

### Hva er hensikten med å bruke outer_join-opsjonen ved import av variabler i microdata.no?

Når du importerer variabler, benyttes metoden "left join". Dette innebærer at enhetene som har gyldig verdi for den første importerte variabelen blir inkludert ved import av flere variabler. Dersom man bruker outer_join-opsjonen ved import, sikrer man at alle enheter med gyldige verdier for den nye variabelen blir inkludert i datasettet, selv om de ikke har gyldig verdi for den første variabelen. [Les mer om outer_join her.](https://microdata.no/manual/kommandoer_og_funksjoner/kommandoer#import)

### Er det mulig å opprette et datasett i ett skript og deretter arbeide videre med det i et annet skript?

Nei, datasett og variabler definert i ett skript er ikke tilgjengelig fra andre skript. Dersom man skal jobbe med samme variabler og populasjon, anbefaler vi å bruke samme skript. Man kan også kopiere kommandoene fra et skript til et annet.

### Jeg ønsker tilgang til en variabel som ikke er tilgjengelig i deres database. Er dette mulig å legge til?

Ja, dette kan i utgangspunktet tilbys dersom variabelen er en del av det øvrige statistikkgrunnlaget til SSB og tilgjengelig for publisering i microdata.no. SSB gjør vurderinger rundt dette i hvert enkelt tilfelle, så vi kan ikke garantere at alle ønsker blir oppfylt. Det er verdt å merke at det vil ta litt tid før man eventuelt får en ny variabel på plass i databasen.

### Er det mulig å koble på egne opplysninger i microdata.no?

Ja, det er mulig å koble på egne opplysninger ved hjelp av vår automatiserte løsning for opplasting av omkodinger via en semikolon-separert CSV-fil. Filen må inneholde fire kolonner: fra-kode, fra-label, til-kode og til-label. Du laster opp filen ved å bruke opplastingsknappen nederst til venstre i analyseverktøyet. Systemet genererer da automatisk et langt recode-uttrykk som omkoder verdiene dine.

Du må selv endre variabelnavnet fra det generiske "variabel" til ønsket navn i det genererte uttrykket. Merk at den opprinnelige variabelen blir overskrevet ved omkoding. Hvis du ønsker å beholde originalen, kan du lage en kopi med et nytt navn ved å bruke kommandoen clone-variables. [Du kan lese mer om hvordan dette gjøres her.](https://microdata.no/manual/brukermanual/Tilrettelegging%20av%20variabler/3.2.1%20Automatisk%20omkoding%20ved%20hjelp%20av%20opplasting%20av%20skilletegnseparerte%20filer/)

### Hvordan påvirker ressursbruk kjøringen av skript i microdata.no?

Lange skript og store datamengder kan føre til økt ressursbruk og gjøre at kjøringen av skriptene tar lengre tid. For å få en mer effektiv analyse anbefaler vi å begrense datamengdene du jobber med. Det kan du gjøre ved å for eksempel redusere størrelsen på populasjonen, antall variabler eller antall måletidspunkter. Man kan selv velge hvilke av disse du kan begrense uten at det går på bekostning av analysens kvalitet. Det er også smart å slette datasett og hjelpevariabler du ikke lenger trenger etter hvert som datasettet du skal analysere er laget ferdig. Slike oppryddinger kan gjøre en forskjell, spesielt ved komplekse analyser.

### Hva gjør jeg når jeg får feilmeldingen om at datasettet er større enn grensen på 1 milliard celler?

For å løse dette bør du prøve å redusere datamengden. Det kan enten gjøres ved å begrense antall variabler og måletidspunkter, avgrense populasjonen eller redusere tidsperioden du analyserer. Ofte er det for eksempel nok å ta med noen få måletidspunkter før og etter en reform, eller å se på bestemte aldersgrupper, geografiske områder eller yrkesgrupper fremfor hele befolkningen. Variabler som ikke brukes direkte i analysen bør fjernes. Dersom det passer med prosjektets formål, kan du også bruke kommandoen `sample` til å trekke et tilfeldig utvalg.

### Jeg får feilmelding når jeg forsøker å bruke nøkkelvariabler i en analyse eller kommando. Hvorfor skjer dette?

Dette skjer fordi variabelen er en pseudonymisert identifikatorvariabel. Av personvernhensyn er det ikke tillatt å bruke slike variabler i analyser eller andre logiske operasjoner. De kan kun brukes i et begrenset omfang, nærmere bestemt som `by`-variabler i `collapse` og `aggregate`, samt som `on`-variabler i `merge`. Formålet er å hindre at pseudonymiserte verdier eksponeres direkte.

### Tilbyr dere veiledning eller gjennomgang av skript for brukere som ønsker å kvalitetssikre skript og/eller metode i analyser i microdata.no?

Vi bistår gjerne med hjelp til koding av skript knyttet til analyser i microdata.no. Vi forventer at brukere på forhånd har satt seg inn i brukermanualen og tilgjengelige ressurser på nettsidene våre, og har forsøkt å sette opp et eget analyseskript. Med dette som utgangspunkt kan vi hjelpe med å nøste opp i feil, forklare hva som skjer ved bruk av ulike koder, samt se over skript og eventuelt foreslå forbedringer. Spørsmål om metodevalg ligger utenfor vårt mandat og er brukerens ansvar.
