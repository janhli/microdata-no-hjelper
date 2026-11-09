<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Jobb-%20og%20inntektsanalyser/Koble%20sammen%20data%20om%20arbeidsforhold%20p%C3%A5%20persondatasett%20-%20numeriske%20opplysninger -->

# Koble sammen data om arbeidsforhold på persondatasett - numeriske opplysninger

Skriptet under viser hvordan man kan jobbe med jobbdata fra A-ordningen. Dette ble gjennomgått i vårt temakurs som ble kjørt to ganger i 2022.

Dette konkrete eksempelet demonstrerer hvordan man kobler data med arbeidsforhold som enhetstype sammen med et annet datasett med person som enhetstype. Dette er nyttig når man vil lage jobbstatistikk på personnivå.

Data fra den såkalte A-ordningen med prefikset `ARBLONN_ARB_` har arbeidsforhold som enhetstype (altså opptil flere records per person). For å kunne koble slike data sammen med vanlige persondatasett, må en først bruke kommandoen `collapse` til å summere opplysningene knyttet til hvert enkelt arbeidsforhold per individ. Datasettet får da person som enhetstype (en record per person), og kan dermed kobles sammen med persondatasettet sysselsatte.

Variabelen `ARBEIDSFORHOLD_PERSON` brukes til å lenke/aggregere fra jobb til personnivå (variabelen inneholder personidentifikatoren tilknyttet det aktuelle arbeidsforholdet/jobben).

Fremgangsmåten under passer fint på numeriske jobbopplysninger som f.eks. arbeidstid og stillingsprosent. Dersom man vil koble på kategoriske jobbopplysninger, anbefales løsningen i eksempelet Koble sammen data om arbeidsforhold på persondatasett - kategoriske opplysninger.

```
 require no.ssb.fdb:30 as db

// Lager datasett for sysselsatte (persondata)
create-dataset sysselsatte
import db/ARBLONN_PERS_KJOENN 2021-07-16 as kjønn
import db/ARBLONN_PERS_ALDER 2021-07-16 as alder

// Lager datasett for arbeidsforhold (jobbdata)
create-dataset arbeidsforhold
import db/ARBLONN_ARB_ARBEIDSTID 2021-07-16 as arbtid
import db/ARBLONN_ARB_STILLINGSPST 2021-07-16 as stillingspst
import db/ARBEIDSFORHOLD_PERSON as personid

// Aggregerer fra jobbdata- til persondatanivå ved å summere arbeidstid og stillingsprosent per person.
// Kobler deretter jobbopplysningene på persondatasettet sysselsatte
collapse (sum) arbtid stillingspst, by(personid)
merge arbtid stillingspst into sysselsatte

// Lager jobbstatistikk
use sysselsatte

summarize arbtid stillingspst
tabulate kjønn, summarize(arbtid)
tabulate kjønn, summarize(stillingspst)

generate aldersgr = 1
replace aldersgr = 2 if alder > 25
replace aldersgr = 3 if alder > 40
replace aldersgr = 4 if alder > 60
define-labels alderslabel 1 '0-25' 2 '26-40' 3 '41-60' 4 '61->'
assign-labels aldersgr alderslabel
tabulate aldersgr kjønn, summarize(arbtid)
tabulate aldersgr kjønn, summarize(stillingspst)

```
