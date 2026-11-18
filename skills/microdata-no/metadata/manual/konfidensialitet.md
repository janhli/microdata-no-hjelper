<!-- Kilde: https://microdata.no/manual/konfidensialitet -->

# Konfidensialitet

## Bakgrunn

Lov om offisiell statistikk og Statistisk sentralbyrå (LOV-2019-06-21-32) § 14 (tilgang til opplysninger for statistiske resultater og analyser) ledd (5) sier at «Taushetsplikten etter § 8 gjelder tilsvarende for den som får tilgang til opplysninger». Slike data kan kun utleveres til forskere i godkjente forskningsinstitusjoner og til offentlige myndigheter. Det stilles derfor strenge krav for tilgang til mikrodata, og søknad om tilgang til mikrodata for forskning er en lang prosess. Kriteriene for å søke om tilgang til registerdata for forskning kan du finne på [SSBs sider om data til forskning](http://www.ssb.no/omssb/tjenester-og-verktoy/data-til-forskning).

Microdata.no er utviklet for å gjøre det mulig å få tilgang til mikrodata fra registre uten å måtte gå gjennom den omstendelige søknadsprosessen det er for å få data utlevert. Men det er en betingelse for en slik forenkling at sikkerheten og konfidensialiteten til mikrodataene er like godt ivaretatt som ved utlevering, helst bedre. Det har derfor fra begynnelsen vært et eksplisitt krav at brukerne ikke skal kunne se mikrodata eller på annen måte være i stand til å avsløre informasjon om enkeltpersoner. Når SSB publiserer offisiell statistikk er det aggre­ger­te data. Likevel må SSB passe på ved ulike typer tiltak at det ikke er mulig å føre infor­ma­sjon tilbake til enkelt­personer eller andre typer statistiske enheter som statistikken dreier seg om.

De resultatene som microdata.no produserer for sine brukere, tabeller eller analyser, er i likhet med SSBs statistikk aggregerte data. Men uten begrensninger vil en bruker av microdata.no lett kunne produsere tabeller og andre typer statistiske resultater som SSB ikke ville kunne publisere. For å forhindre at det skjer er det innført flere typer tiltak som skal begrense mulig­hetene for å kunne avsløre informasjon som skal være konfidensiell.

Dette vedlegget vil beskrive de tiltakene som er implementert for å ivareta konfidensialitet i microdata.no. Tiltakene er basert på scenarier for hvordan konfidensialitet i microdata.no kan angripes eller utilsiktet komme i fare. Disse scenariene vil ikke bli beskrevet. Det vil bli lagt vekt på det som er nødvendig for at brukeren skal kunne forstå tiltakene og forholde seg til de statistiske resultatene på riktig måte.

De tiltakene som er beskrevet nedenfor er de som er implementert så langt. Det vil kunne komme flere tiltak etter hvert eller også justeringer av de tiltakene som er beskrevet nedenfor. Dette vedlegget vil bli oppdatert når det kommer endringer.

## Tiltak 1: Minste populasjonsstørrelse

Det er ikke tillatt å opprette et datasett med populasjon under 100 personer. Om dette skjer, vises en feilmelding og brukeren blir stoppet fra å gå videre. Tidligere (tiltaksversjon 1) var grensen satt til 1000.

Eksempel der man prøver å definere en populasjon som utgjør 40 individer:

Denne operasjonen vil imidlertid gå gjennom, siden antall enheter er over grensen på 100:

Grenseverdien gjelder også datasett hvor persondata er disaggregert, dvs. man har et datasett med nivå under person (jobb, studier/kurs, kjøretøy, trafikkulykke m.m.). Så selv om man har et jobbdatasett med over 100 unike sub-person enheter, f.eks. jobber, vil du fremdeles bli stoppet dersom disse kun kan knyttes til under 100 individer.

Ved aggregerte datasett, dvs. data med nivå over person (familie, husholdning, kommune m.m.), er det tillatt med et antall enheter under 100 så lenge de kan knyttes til over 100 unike individer. Systemet holder løpende orden på hvor mange N som bidrar fra ulike enhetstyper i situasjoner hvor aggregering eller disaggregering fører til datasett med innhold om flere enhetstyper.

En nedre grense for datasettpopulasjoner på 100 vurderes som svært lite inngripende for analytisk nytteverdi ettersom grensen gjelder for det totale datasettet, og ikke undergrupper man har behov for å analysere. Man kan med andre ord lage statistikk på grupper mindre enn 100 så lenge den totale datasettpopulasjonen er større enn 100.

## Tiltak 2: Winsorisering

Winsorisering er en teknikk som ofte brukes i analyser for å hindre at ekstreme observa­sjon­er skal få for stor innvirkning på analyseresultatene. Teknikken anvendes på alle numer­iske variabler og består i å kutte av fordelingen i begge ender ved bestemte prosentiler. Vi benyt­ter 2% winsorisering som betyr at de 1% høyeste verdiene settes til 99-prosentilen (nedre grenseverdi) og de 1% laveste verdiene settes til 1-prosentilen (øvre grenseverdi). Dette skjer kun ved visning av statistiske resultater, med utgangspunkt i den aktuelle populasjon som statistikken beregnes ut i fra.

Siden fordelingene til mange numeriske statistiske variabler er skjevfordelte, typisk med lange haler i øvre ende (eks. inntekter og formuer), vil winsorisering påvirke gjennomsnitt og standardavvik til en viss grad. Disse målene vil typisk bli estimert for lave. På den andre siden vil medianer, kvartiler og andre prosentiler ikke bli påvirket av winsorisering.

Winsorisering påvirker alle deskriptive statistikker og grafiske visninger for å hindre at de mest ekstreme verdiene blir avslørt.

Eksempler på hhv. histogram og deskriptiv summarize-statistikk med winsorisering:

I histogrammet over ser man at de ytterste søylene i hver ende er mye høyere enn nabosøylene. Dette kommer av at hhv. verdiene over/under er satt til den aktuelle grenseverdien, og disse søylene representerer dermed alle enheter med denne grenseverdien eller høyere/lavere. Grenseverdiene oppgis under kolonneheadingene 1% og 99% i summarize-statistikken over.

Under vises samme summarize-statistikk uten winsorisering. Merk at 1- og 99-percentilene her er hhv. mye lavere/høyere enn de oppgitte winsoriserte verdiene over (summarize uten anonymiseringsfilteret påskrudd viser de sanne minimums- og maksimumsverdier i stedet for grenseverdier for 1- og 99-percentiler). Merk også at de sanne verdiene for gjennomsnitt og standardavvik under er noe høyere enn i tilfellet over:

### Subpopulasjonswinsorisering Utvidelse

I deskriptive analyser som bryter tall ned på undergrupper, gjennomføres nå også winsoriseringen for hver undergruppe (subpopulasjonswinsorisering). Dette er en utvidelse av tiltaket i forhold til tidligere (tiltaksversjon 1).

I deskriptive analyser er det hovedsaklig to måter å dele inn i undergrupper på:

1. Ved bruk av if-kriterium for selve analysen (f.eks. tabellen eller grafen viser kun kvinner)
1. Ved bruk av analysekommandoer med innebygd inndeling (f.eks. `tabulate, summarize()` og `barchart, by()/over()`)

Tidligere var det slik at inndelinger gjort med metode 1 førte til winsorisering av det filtrerte datasettet, mens det ikke ble gjort gruppevis winsorisering ved metode 2. Dette er nå harmonisert ved at winsorisering utføres i begge tilfeller.

Eksempel på volumtabell med subpopulasjonswinsorisering:

Den samme volumtabellen uten subpopulasjonswinsorisering (merk at de sanne gjennomsnittsverdiene er litt høyere enn de winsoriserte verdiene for alle utdanningskategorier):

### Winsorisering ved aggregering av data

Aggregering kan i microdata.no gjøres gjennom kommandoene `collapse()` og `aggregate()`.

Om man bruker commandoen `collapse()` til å aggregere et datasett opp til et nivå hvor deskriptiv statistikk winsoriseres, kjøres selve collapse-aggregeringen uten winsorisering. Aggregering fra arbeidsforhold (jobber) til personnivå eller fra person- til familienivå er eksempler på aggregeringer som gjøres uten winsorisering. Bruk av `collapse()` hvor `by()`-leddet angir en pseudonymisert variabel winsoriseres altså ikke i selve aggregeringssteget.

Men dersom målenhetstypen til `collapse()` angitt i `by()`-leddet er en enhetstype gitt ved en vanlig ikke-pseudonymisert variabel, f.eks. kommune, fylke, næringstype, eller utdanningsnivå, vil beregninger gjort gjennom `collapse()` bli gjenstand for winsorisering. Grunnen til dette er at disse enhetstypene ikke vil bli winsorisert ved generering av deskriptiv statistikk. Derfor må altså winsoriseringen gjøres i forbindelse med selve aggregeringen.

### Winsorisering ved regresjonsanalyser og korrelasjonsberegninger Utvidelse

Selv om ekstremverdier ikke vises direkte i regresjonsanalyser, vil de likevel gi utslag på/påvirke koeffisientestimeringen. Derfor er det nå også innført winsorisering på regresjonsanalyser: Alle kontinuerlige variabler som inngår i en regresjonsmodell blir gjenstand for winsorisering før selve estimeringen.

Eksempel på OLS-regresjon som kjøres uten winsorisering:

Samme regresjonsestimering med winsorisering:

Legg merke til at R2 og Justert R2 i eksempelet over får betydelig høyere verdi når regresjonen kjøres med winsorisering (0.236 vs. 0.119). Når man winsoriserer de kontinuerlige variablene lønn og bruttoformue, fjernes «outliers» (ekstremverdier), noe som tar vekk «støy» som ødelegger mønsteret man prøver å tilpasse en regresjonslinje til. Estimeringen som kjøres med winsorisering forklarer altså mer av den totale variansen.

Winsorisering vil også utføres på analysedatasettet forut for beregninger av korrelasjonsmål, jfr. kommandoen `correlate`.

### Winsoriseringens effekt på resultater

Winsorisering fører til at rapporterte gjennomsnitts- og standardavvikverdier blir noe lavere enn de sanne verdier. Dette kommer imidlertid an på hvordan frekvensfordelingen er. Ved fordelinger som likner på normalfordeling, eller som har korte venstre- og høyrehaler, vil avvikene fra sanne verdier være lave (slike fordelinger har få ekstremverdier som blir sensurert gjennom dette tiltaket).

Også regresjoner blir påvirket av dette tiltaket dersom man har innslag av kontinuerlige variabler med fordelingsskjevhet (lange høyre- og/eller ventrahaler). Men på den andre siden vil tiltaket også ha ønskede effekter: Man fjerner i praksis ekstremverdier («outliers»). Dette er vanligvis uønskede datapunkter når man vil kjøre regresjonsanalyser, siden de ødelegger mønsteret når man skal tilpasse en regresjonslinje til alle datapunktene. Det samme gjelder korrelasjonsmål (kommandoen `correlate`): Ved å fjerne outliers, vil man se bort fra variasjon som skyldes ekstremverdier, noe som vil kunne bidra til høyere korrelasjonsverdi.

## Tiltak 3: Frekvensstøy Justering

Alle opptellinger av antall enheter i et datasett som vises i forbindelse med diverse operasjoner, eller statistiske opptellinger som vises gjennom blant andre kommandoene `tabulate` eller `summarize` blir støylagt med en tilfeldig støy i intervallet -5 til 5. Av ekstra personhensyn støylegges imidlertid ingen tall til verdiene 1-4. Altså vises bare de støylagte verdiene 0 (missing), eller 5 og oppover.

Merk at marginalverdier i en frekvenstabell støylegges uavhengig. Derfor er det ikke så ofte at summen av de indre cellene stemmer over ens med kolonne- eller rekketotalen.

Individene som inngår i en frekvensopptelling avgjør hvordan støyen blir, så dersom samme gruppe individer (f.eks. i en tabellcelle) telles flere ganger i samme type statistikk, skal støyen i utgangspunktet bli den samme.

Merk at selve skriptet også brukes som en ekstra komponent i støyberegningen: Dersom man lager samme frekvensopptelling for de samme individene, men i et annet/endret skript, så vil dette gi et annet støymønster innen samme intervall.

Summer over numeriske statistikk­vari­abler knyttet til enhetene i en tabellcelle, for eksempel inntekter, er justert propor­sjonalt med støylegg­ingen slik at gjennomsnittstall blir upåvirket. Der hvor støyleggingen resulterer i at antall enheter bak summen blir 0, blir summen satt til 0, og gjennomsnittet som da blir 0/0 blir satt til NaN.

### Justeringer av tiltaket (introdusert gjennom tiltaksversjon 2)

-

Skriptet som kjøres blir selv en faktor i kilden for oppslag/beregning av støy, ikke bare individene som inngår i en frekvens. Derfor vil støymønsteret endre seg dersom man kjører samme frekvensopptelling for de samme individer, men i et nytt eller endret skript.

-

Marginaler støylegges med uavhengig støykilde og vil få nytt støymønster selv om individene det summeres over er de samme som i indre celler

-

De sanne verdiene 1-4 støylegges nå automatisk til 0 (som i microdata.no vises på samme måte som missing vises). Tidligere kunne slike verdier bli støylagt til enten 0 eller 5-9. Denne endringen regnes som et eget tiltak, dvs. tiltak 11.

Frekvensstøy har fra start av vært et viktig tiltak i microdata.no. Oppslag i en stor støytabell ble tidligere gjort på bakgrunn av nøkler basert på populasjonen i datasett og i celler.

De nye tiltakene under frekvensstøy introduserer andre støykilder enn bare populasjonsstørrelsen, og da vil støyen ikke bli den samme for to ulike skript selv om analysepopulasjonen er den samme.

### Hvordan tolke de støylagte tallene

Alle frekvenstall som blant annet vises i en frekvenstabell, jfr. kommandoen tabulate, er uavhengig støylagt med en tilfeldig støykomponent som varierer mellom -5 og +5. Og støykomponenten vil være forskjellig fra tall til tall.

Når du f.eks. ser tallet 10, så vil det sanne tallet være ett av tallene mellom 5 og 15. Tallet 11 kan være ett av tallene mellom 6 og 16 etc.

Men for de mindre tallene gjøres det tilpasninger i støyalgoritmen for å unngå negative tall eller visning av tallene 1-4:

- Tallet 0 i en frekvenstabell (altså missingverdi eller tom celle) betyr at det sanne tallet egentlig er ett av tallene 0-5
- Tallene 1-4 vises ikke grunnet personvernhensyn
- Ser du tallet 5, vil det sanne tallet være ett av tallene mellom 5 og 10 (0 støylegges ikke til et positivt tall)
- Ser du tallet 6, vil det sanne tallet være ett av tallene mellom 5 og 11
- Ser du tallet 7, vil det sanne tallet være ett av tallene mellom 5 og 12
- Ser du tallet 8, vil det sanne tallet være ett av tallene mellom 5 og 13
- Ser du tallet 9, vil det sanne tallet være ett av tallene mellom 5 og 14

Grunnet personvernhensyn, vises altså bare tallene 0 (vises likt som missing), og 5 over oppover. Se også tiltak 11.

### Effekt av frekvensstøy på resultater

For store tall (over 100) vil usikkerheten introdusert av støyfilteret på +/-5 være minimal relativt sett. Den sanne verdien 100 vil kunne bli støylagt til en verdi i intervallet 95-105, altså +/- 5%. Støylagt verdi for den sanne verdien 1000 vil tilsvarende kunne bli et tall i intervallet 995-1005, altså +/- 0.5%. Om man derimot analyserer tabeller med gjennomgående små tall, vil frekvensstøyen kunne redusere nytteverdien såpass mye at man i enkelte tilfeller bør være forsiktig med å konkludere basert på tallene man ser.

## Tiltak 4: Grafiske plott. Hexbinplott

Det er vanlig å bruke spredningsplott for å etablere et visuelt bilde av data eller også vise sammenheng mellom numeriske variabler. Slike plott kan være veldig avslørende, spesielt hvis det er få observasjoner i forhold til det grafiske området og for de punktene i plottet som ligger utenfor hovedmassen av punkter. Hvis du for en enhet/person i populasjonen kjenner verdien på en av de variablene som spenner ut plottet, er det ofte mulig å lese av verdien til den andre variabelen med for stor nøyaktighet.

For å hindre at dette kan skje, foretas en anonymisering av slike plott i microdata.no. For dette formålet er det blitt valgt å fokusere på en teknikk som kalles hexbin-plott. I et hexbin-plott deles det grafiske området inn i regulære sekskanter som fargelegges med sterkere intensitet etter hvor mange observasjoner som befinner seg i hver av dem.

Sekskanter hvor antall observasjoner er under fem vises uten fargelegging.

Eksempel på et hexbin-plott i microdata.no:

Dersom man ikke klarer seg uten ekte spredningsplott, vil dette tiltaket kunne gi redusert nytteverdi. Men selv med fargelagte arealer som metode å aggregere slike plots, vil man likevel kunne se et klart mønster og danne seg et inntrykk av hvordan sammenhengen mellom de to variablene man måler mot hverandre er.

## Tiltak 5: Skjuling av tabeller med for mange lave verdier Utgått

Utgått - ikke lenger aktivt i tiltaksversjon 2

Erstattet av Tiltak 11: Undertrykking av lave frekvenser.

Historisk beskrivelse (slik tiltaket virket da det var aktivt)

Tabeller som lages ved kommandoen `tabulate` vil i noen tilfeller kunne inneholde mange celler med lave verdier for antallet enheter. Dette kan være problematisk ettersom det gjør det lettere å indirekte identifisere individer ved å studere kombinasjoner av verdier for de kategoriske variablene som utgjør en tabell. Et annet problem med slike tabeller er at støyleggingen beskrevet under «Tiltak 3» gir en relativt høy usikkerhet for de aktuelle celleverdiene (den prosentvise støyen blir relativt stor ved små tall), slik at den statistiske nytteverdien av tabellen blir lav.

I microdata.no opereres det med en grenseverdi på 50%, dvs. tabeller der mer enn 50% av cellene inneholder frekvensverdier lavere enn 5, vil bli stoppet. I tillegg vil det vises en feilmelding om dette.

Det er mulig å unngå problemet med tabeller som stoppes pga. for mange lave verdier: Ved å lage grovere inndelinger for de kategoriske variablene som utgjør tabellen, eller ved å øke størrelsen på tabellpopulasjonen, vil en kunne øke antallet enheter i hver celle og dermed komme under 50%-grensen slik at tabellen blir godkjent og vises.

## Tiltak 6: Ikke tillatt med endringer som påvirker færre enn 10 enheter Utgått

Utgått - ikke lenger aktivt i tiltaksversjon 2

Historisk beskrivelse (slik tiltaket virket da det var aktivt)

Det er ikke tillatt å gjøre endringer i et datasett som påvirker færre enn 10 enheter, gjennom bruk av kommandoene `generate`, `replace` eller `recode()`. Om dette inntreffer, vil man få en feilmelding og kjøringen vil stoppe.

Det er heller ikke tillatt å gjøre endringer som påvirker alle enheter bortsett fra et antall færre enn 10.

Eksempler:

Et viktig unntak er at man kan gjøre endringer som påvirker alle eller ingen enheter.

Eksempler (koden 9999 finnes ikke i datasettet):

(Merk at antallet missingverdier som rapporteres er ulikt antall enheter i eksempelet over. Dette skyldes støyleggingen av frekvensverdier, jfr. tiltak 3. I praksis vil variabelen `test` bare inneholde missingverdier.)

Ved bruk av `recode`, så gjelder regelen for hvert av omkodingsleddene i uttrykket (man ser på hver av kodene det kodes til, og hvert av leddene må kode om minst 10 observasjoner).

Eksempel:

## Tiltak 7: Ikke tillatt med deskriptiv statistikk for populasjoner som utgjør færre enn 10

Deskriptiv statistikk gjennom kommandoene `summarize`, eller `summarize` i kombinasjon med `tabulate` (volumtabeller), kan ikke kjøres på populasjoner som utgjør færre enn 10.

Tiltaket kontrollerer at det er minst 10 gyldige verdier i en variabel for at deskriptiv statistikk (gjennomsnitt, standardavvik, etc) skal kunne vises. Grensen var tidligere 9, mens den nå er 10.

Eksempel på deskriptiv statistikk som sensureres (kun antall enheter vises):

Annet eksempel der antall enheter kommer over grensen på 10:

Eksempel på volumtabell som viser gjennomsnittlig lønn fordelt på kjønn, dersom lønn er større enn 30 mill. Her fjernes verdien for kvinner ettersom disse utgjør under 10 enheter for denne aktuelle statistikken. Verdien for menn vises siden de kommer over grensen:

Deskriptiv statistikk knyttet til gjennomsnitt, standardavvik m.m. for grupper av individer under 10 vil ikke være spesielt representativ for generelle populasjoner, og vil derfor ha begrenset allmenngyldig nytteverdi.

## Tiltak 8: Median- og prosentilverdier vises kun med tresifret nøyaktighet Utgått

Utgått - ikke lenger aktivt fra 23. april 2025

Erstattet av Tiltak 10: Mikroaggregering og glatting før beregning av persentiler.

Historisk beskrivelse (slik tiltaket virket da det var aktivt)

Median- og prosentilverdier viser faktiske verdier som kan knyttes til enkeltpersoner (eller andre enheter). Derfor vises slike verdier kun med tresifret nøyaktighet, og påvirker visningen av tall ved bruk av kommandoene `summarize`, `summarize` i kombinasjon med `tabulate`, og grafer der slike tall inngår.

Eksempler:

## Tiltak 9: Konstantledd skjules fra regresjonsresultat dersom analysepopulasjonen har for unike kombinasjoner av kategoriske verdier Utgått

Utgått - ikke lenger aktivt i tiltaksversjon 2

Historisk beskrivelse (slik tiltaket virket da det var aktivt)

For å styrke konfidensialiteten ved regresjonsanalyser, er det en begrensning knyttet til analyser på datasett med for høy grad av unikhet. Hvis kombinasjoner av kategoriske variabelverdier i analysen utgjør veldig små grupper, vil konstantledd-estimatene bli skjult fra regresjonsresultatene. Analysen påvirkes ikke siden konstantleddet inngår i estimeringen.

Det er prinsippet for k-anonymity som benyttes på det underliggende analysedatasettet, definert av populasjonen og settet av forklaringsvariabler for den aktuelle analysen, der grenseverdien er satt til 5. Skjuling av konstantledd skjer altså for regresjoner som kjøres på datasett med færre enn 5 enheter med samme kombinasjon av variabelverdier.

Merk at kontinuerlige variabler inngår ikke ved vurderinger av unikhet, kun kategoriske variabler.

I tilfeller der tiltak 9 slår inn, og man ønsker å se konstantleddet, er det noen grep man kan foreta for å gjøre datasettet mindre unikt (slik at antallet unike kombinasjoner kommer over 5):

- Øke populasjonsstørrelsen
- Bruke grovere inndeling av kategorier
- Begrense antallet kategoriske forklaringsvariabler

## Tiltak 10: Mikroaggregering og glatting før beregning av persentiler

Ved beregning av persentiler (inkl. median) gjennomføres det en mikroaggregering av sorterte verdier i grupper av størrelse med 5 i hver gruppe. Alle verdiene i samme gruppe blir erstattet med gjennomsnittsverdien i gruppen. Deretter glattes verdiene med sentrert glidende gjennomsnitt med periode på 5.

Dette tiltaket gjør utslag i alle statistikker som viser persentilverdier. De mest aktuelle er `summarize` og `histogram`.

Eksempel på deskriptiv statistikk med mikroaggregering og glatting:

Samme statistikk uten dette tiltaket. Merk at verdiene for de indre persentilene 25%, 50% og 75% endrer seg minimalt. De store avvikene for 1- og 99-percentilene skyldes først og fremst winsoriseringen beskrevet i avsnittet knyttet til tiltak 2 (det er egentlig min- og maks-verdier som vises når anonymiseringsfilteret er avskrudd):

I de fleste tilfeller vil mikroaggregerte og glattede prosentilverdier ha svært lave avvik fra sanne verdier, og vi anser derfor dette som et tiltak som har begrenset innvirkning på analyseresultater. Ved svært lave populasjonsstørrelser vil man imidlertid kunne få et visst avvik fra sanne verdier.

## Tiltak 11: Undertrykking av lave frekvenser Nytt

Sanne frekvenstall under 5 blir satt til 0 (missing). Dette gjelder også for histogramsøyler som representerer enhetsgrupper med sann frekvensverdi under 5, samt andre former for grafisk fremstilling av frekvenser (barchart, piechart, m.fl.).

Merk at frekvenstall som er støylagt til verdier under 5 også settes til 0 (missing), jfr. tiltak 3.

Tiltaket vil kunne ha en viss innvirkning på nytteverdien dersom man jobber med tabeller med mange små frekvenstall. En fordel er at tabellen vil vises uansett, dvs. alle cellene med verdier fra og med 5. Tidligere (tiltaksversjon 1) ble man stoppet fra å lage tabeller der minst halvparten av cellene hadde verdier under 5 (tiltak 5). Merk at man står også fritt til å lage grovere inndelinger av de kategoriske variablene, slik at man unngår celler med verdier under 5.

## Tiltak 12: Svært høy korrelasjon settes til 1 Nytt

Korrelasjonsmål settes til 1 for variabler som er identiske eller nesten identiske. Det vil si at dersom det er perfekt korrelasjon mellom to variabler målt over alle i en gitt populasjon bortsett fra en liten gruppe på under 5 enheter, så oppgis likevel korrelasjonsverdien til 1.

Dette tiltaket vil ha svært begrenset effekt på nytteverdien ettersom slike ekstremt høye korrelasjonsverdier (nær 1) forekommer svært sjeldent i kvantitative persondataanalyser. Som oftest måler man verdier langt lavere enn dette. Ved korrelasjonsverdier som nærmer seg 1, er den gjenværende variansen så minimal at vi i praksis står overfor begrepsmessig overlapp. Å skille mellom en korrelasjon på 0.9999 og 1.0 gir ingen ytterligere analytisk innsikt, da variablene i praksis er å betrakte som substitutter for hverandre.

## Tiltak 13: Fjerning av tilnærmet perfekt korrelerte forklaringsvariabler Nytt

I regresjonsanalyser vil forklaringsvariabler som er perfekt eller nesten perfekt korrelert med den avhengige variabelen droppes fra analysen.

Dette tiltaket vil av samme grunn som for tiltak 12 ha svært begrenset effekt på forskningsmessig nytteverdi ettersom det er uhyre sjeldent å oppleve nesten perfekt korrelasjon mellom to variabler. Og dersom det skulle oppstå (nesten) perfekt korrelasjon mellom en forklaringsvariabel og en avhengig variabel i en regresjonsanalyse, så kan dette mest sannsynlig forklares med dårlig design av regresjonsmodell.

## Tiltak 14: Fjerning av små grupper i regresjonsanalyse Nytt

Kategoriske variabler med enkeltgrupper som kan knyttes til færre enn 5 observasjoner fjernes helt fra regresjonsanalysen.

Tiltaket gir bedre harmonisering med undertrykking av lave frekvenser i frekvenstabeller (tiltak 11), der frekvenser under 5 i enkeltceller settes til 0 (missing).

Ønsker man å beholde alle variablene i modellen, kan man gjøre populasjonen større (hvis mulig) eller inndelingene litt grovere eller slå sammen de små kategoriene med nabokategorier.

## Tiltak 15: Automatisk nedsampling Nytt

Tiltaket foretar et tilfeldig uttrekk fra analysepopulasjonen før analysen gjennomføres. Prosessen fjerner et varierende antall (1-3) observasjoner fra analysedatasettet.

Tiltaket gjennomføres på alle statistiske analyser hvor resultatene er sensitive for små populasjonsendringer, dvs de fleste analyser og grafer utenom rene opptellinger (frekvenstabeller). I deskriptive analyser brutt ned på undergrupper, som f.eks. volumtabeller (`tabulate, summarize()`), gjennomføres det en nedsampling for hver undergruppe.

De 1-3 tilfeldige observasjoner som fjernes fra analysepopulasjoner er et såpass lavt antall at dette ikke bør ha noen merkbar effekt på analyseresultatene.

I volumtabeller (`tabulate` med `summarize` som opsjon) vil effekten kunne være mer til stede dersom man har en tabell der det forekommer mange celler med lave underliggende frekvenser. Dette vil kunne bidra til større usikkerhet rundt den deskriptive statistikken (for eksempel gjennomsnitt).

For volumtabeller der de fleste celler har en viss underliggende frekvensstørrelse, vil ikke dette tiltaket være spesielt merkbart. Merk at dette tiltaket vil gi litt variasjoner i deskriptiv statistikk der man normalt ville forvente 100% identiske resultat. For eksempel dersom man kjører en grafisk fremstilling (`barchart(mean) lønn, over(sivilstand)`) av resultat som vises i en volumtabell (`tabulate sivilstand, summarize(lønn)`). Siden det varierer fra analyse til analyse hvilke og hvor mange records som fjernes fra analysen, så vil man dermed se små avvik. Men de relative avvikene blir mindre jo større delpopulasjonen er for de aktuelle kategoriene (for hver sivilstandskategori).

## Tiltak 16: Utvidet nedsampling for analyser som rapporterer frihetsgrader Nytt

For regresjonsanalyser o.l. som viser antall frihetsgrader, kjøres det en litt utvidet sampling enn for øvrige analyser. Vanligvis fjernes det 1-3 tilfeldige observasjoner fra et analysedatasett før en analyse kjøres, jfr. tiltak 15. Men for akkurat denne typen analyser utvides intervallet til 1-11 fordi tallet på frihetsgrader gjør det så enkelt å avlede N. Blant aktuelle analyser som benytter dette tiltaket finner vi regresjonsanalysene regress og ivregress, samt anova.

Å fjerne et tilfeldig antall records mellom 1 og 11 fra analysepopulasjoner for denne typen analyser der frihetsgrader rapporteres, vil ikke ha nevneverdig effekt på forskningsmessig nytteverdi. I de fleste tilfeller jobber man med populasjoner på flere tusen enheter (og ofte over 1 mill.) i microdata.no, og da utgjør dette en svært liten andel. Dersom man imidlertid er avhengig av å rapportere frihetsgrader i forbindelse med en analyse, vil dette tiltaket kunne bidra med en viss usikkerhet rundt dette.

## Tiltak 17: Minste tillatte antall koeffisienter i regresjonsanalyser Nytt

Tiltaket stopper kjøringer av regresjonsmodeller som har under to koeffisienter. Antallet koeffisienter samsvarer ofte med antallet forklaringsvariabler, men i tilfeller med faktorvariabler (kategoriske variabler med flere enn to kategorier) og interaksjonsledd blir ikke dette nødvendigvis tilfelle. Derfor er det antallet koeffisienter, og ikke antall forklaringsvariabler, som kontrolleres når tiltaket vurderer om man er over grensen på to. Konstantleddet telles ikke med.

Eksempel der man prøver å kjøre en lineær regresjonsmodell med et binært utfall (fulltidsjobb (1) vs. deltid/ingen jobb (0)) og kun én dummyvariabel som forklaringsvariabel (mann (1) vs kvinne (0)). Antallet koeffisienter er her én:

I eksempelet under legges det til en ekstra dummyvariabel: innvandrer. Antallet koeffisienter blir da to og kjøringen kan gjennomføres:
