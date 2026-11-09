<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Jobb-%20og%20inntektsanalyser/Koble%20persondata%20p%C3%A5%20jobbdatasett -->

# Koble persondata på jobbdatasett

Skriptet nedenfor viser hvordan man kan jobbe med jobbdata fra A-ordningen. Dette ble gjennomgått i vårt temakurs som ble kjørt to ganger i 2022.

Dette konkrete eksempelet demonstrerer hvordan man kobler persondata sammen med jobbdata. Dette er nyttig når man vil lage jobbstatistikk der arbeidsforhold/jobb benyttes som analyseenhet.

Variabelen `ARBEIDSFORHOLD_PERSON` brukes til å lenke personopplysningene på riktig arbeidsforhold/jobb (variabelen inneholder personidentifikatoren tilknyttet det aktuelle arbeidsforholdet/jobben).

Om du heller vil gjøre det motsatt og lenke jobbopplysninger på et persondatasett (bruke person som analyseenhet), kan du bruke fremgangsmåten som demonstreres i eksempelet Koble sammen data om arbeidsforhold på persondatasett - numeriske opplysninger eller Koble sammen data om arbeidsforhold på persondatasett - kategoriske opplysninger.

```
 require no.ssb.fdb:30 as db

create-dataset jobber
import db/ARBLONN_ARB_YRKE_STYRK08 2021-07-16 as yrke
import db/ARBLONN_ARB_ARBEIDSTID 2021-07-16 as arbeidstid
import db/ARBLONN_LONN_EKV_IALT 2021-06-30 as mndlønn_heltidsekv
import db/ARBEIDSFORHOLD_PERSON as personid

create-dataset personer
import db/ARBLONN_PERS_KJOENN 2021-07-16 as kjønn
merge kjønn into jobber on personid

use jobber
tabulate yrke kjønn, summarize(mndlønn_heltidsekv)
tabulate yrke kjønn, summarize(arbeidstid)

```
