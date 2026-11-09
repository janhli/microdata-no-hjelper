<!-- Kilde: https://microdata.no/manual/eksempel/Regresjonsanalyser/Bruk%20av%20instrumentvariabel%20i%20regresjonsanalyse -->

# Bruk av instrumentvariabel i regresjonsanalyse

Kommandoen `ivregress` kan brukes til å spesifisere instrumentvariabler. Dette er aktuelt dersom en har en hypotese om at det eksisterer multikollinearitet (korrelasjon mellom minst to av de uavhengige variablene). En definerer instrumentvariabler inne i parentesuttrykket. I eksempelet nedenfor brukes instrumentvariabelen formuehøy, og instrumentet alder. Men en kan bruke som mange instrumenter en ønsker. F.eks. om en tror at også bosted (= Oslo) påvirker formuehøy, kan en bruke parentesuttrykket `(formuehøy = alder oslo)`. Men i prinsippet behandler `ivregress` alle uavhengige variabler som instrumenter, bortsett fra instrumentvariabelen.

```
 require no.ssb.fdb:33 as db

create-dataset ivanalyse
import db/INNTEKT_WLONN 2021-12-31 as lønn
import db/BEFOLKNING_FOEDSELS_AAR_MND as faarmnd

generate alder = 2020 - int(faarmnd /100)
keep if inrange(alder,18,60)

import db/BEFOLKNING_KJOENN as kjønn
generate mann = kjønn == '1'

import db/INNTEKT_BRUTTOFORM 2020-12-31 as formue
generate formuehøy = formue > 1500000

// Foretar først vanlig lineær regresjon
regress lønn alder mann formuehøy

// Mistenker en sammenheng mellom alder og formue. Bruker derfor en modell med instrumentvariabel (formuehøy)
ivregress lønn mann (formuehøy = alder)

// I tillegg til å sammenlikne output fra regresjonene, sjekkes det for multikollinearitet og normalfordelte restledd
correlate formuehøy alder
regress-predict lønn alder mann formuehøy, residuals(res1)
ivregress-predict lønn mann (formuehøy = alder), residuals(res2)

histogram res1
histogram res2

```
