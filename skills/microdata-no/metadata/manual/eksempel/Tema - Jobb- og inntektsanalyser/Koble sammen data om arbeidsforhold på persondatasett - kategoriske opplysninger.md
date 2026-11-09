<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Jobb-%20og%20inntektsanalyser/Koble%20sammen%20data%20om%20arbeidsforhold%20p%C3%A5%20persondatasett%20-%20kategoriske%20opplysninger -->

# Koble sammen data om arbeidsforhold på persondatasett - kategoriske opplysninger

Skriptet under viser hvordan man kan jobbe med jobbdata fra A-ordningen. Dette ble gjennomgått i vårt temakurs som ble kjørt to ganger i 2022.

Dette konkrete eksempelet demonstrerer hvordan man kobler data med arbeidsforhold som enhetstype sammen med et annet datasett med person som enhetstype. Dette er nyttig når man vil lage jobbstatistikk på personnivå.

Data fra den såkalte A-ordningen med prefikset `ARBLONN_ARB_` har arbeidsforhold som enhetstype (altså opptil flere records per person). For å kunne koble slike data sammen med vanlige persondatasett, må en først bruke kommandoen `collapse` til å summere opplysningene knyttet til hvert enkelt arbeidsforhold per individ. Datasettet får da person som enhetstype (en record per person), og kan dermed kobles sammen med persondatasettet.

Variabelen `ARBEIDSFORHOLD_PERSON` brukes til å lenke/aggregere fra jobb til personnivå (variabelen inneholder personidentifikatoren tilknyttet det aktuelle arbeidsforholdet/jobben).

Fremgangsmåten under passer fint på kategoriske jobbopplysninger som f.eks. heltid/deltid. Dersom man vil koble på numeriske jobbopplysninger som f.eks. arbeidstid og stillingsprosent, anbefales løsningen i eksempelet Koble sammen data om arbeidsforhold på persondatasett - numeriske opplysninger.

Som skriptet under viser, er det mulig å kombinere kategoriske og numeriske opplysninger når man bruker denne aktuelle fremgangsmåten.

```
 require no.ssb.fdb:30 as db

create-dataset vestland
import db/ARBLONN_PERS_KOMMNR 2021-07-31 as bosted
keep if substr(bosted,1,2) == '46'
import db/ARBLONN_PERS_KJOENN 2021-07-16 as kjønn

create-dataset heltid
import db/ARBLONN_ARB_H3LDELTID 2021-07-16 as heldel
import db/ARBLONN_ARB_ARBEIDSTID 2021-07-16 as arbtid
import db/ARBEIDSFORHOLD_PERSON as personid
tabulate heldel
keep if heldel == '1'
destring heldel
collapse(sum) heldel arbtid, by(personid)
rename heldel hel
rename arbtid arbtid_hel
merge hel arbtid_hel into vestland

create-dataset deltid
import db/ARBLONN_ARB_H3LDELTID 2021-07-16 as heldel
import db/ARBLONN_ARB_ARBEIDSTID 2021-07-16 as arbtid
import db/ARBEIDSFORHOLD_PERSON as personid
keep if heldel == '2'
destring heldel
replace heldel = heldel/2
collapse(sum) heldel arbtid, by(personid)
rename heldel del
rename arbtid arbtid_del
merge del arbtid_del into vestland

use vestland
tabulate hel
tabulate del
tabulate del kjønn, rowpct freq
tabulate del, summarize(arbtid_del)
tabulate kjønn, summarize(arbtid_del)
tabulate kjønn, summarize(arbtid_hel)

```
