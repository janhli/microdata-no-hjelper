<!-- Kilde: https://microdata.no/manual/eksempel/Regresjonsanalyser/Logistisk%20regresjonsanalyse -->

# Logistisk regresjonsanalyse

Logistiske regresjonsanalyser (logit/probit) brukes til å estimere hvilken effekt et sett med forklaringsvariabler har på sannsynligheten for et gitt utfall gitt ved en dikotom responsvariabel (jobb/ikke-jobb, tiltak/ikke-tiltak etc). Gjennom opsjoner kan en tilpasse outputen (ikke vise fastleddet, endre på signifikansnivået m.m.).

Eksempelet under demonstrerer en logit-analyse. Alternativt kan også probit brukes. Multinomiske analyser (flere enn 2 utfall) kan også gjøres ved hjelp av kommandoen `mlogit`.

```
 // Kobler til databank
require no.ssb.fdb:33 as db

// Starter med å lage en populasjon
create-dataset demografidata
import db/BEFOLKNING_FOEDSELS_AAR_MND as faarmnd
import db/BEFOLKNING_STATUSKODE 2020-01-01 as regstat
generate alder = 2020 - int(faarmnd / 100)
keep if regstat == '1' & inrange(alder,16,66)

// Importerer relevante analysevariabler
import db/BEFOLKNING_KJOENN as kjønn
import db/SIVSTANDFDT_SIVSTAND 2020-01-01 as sivstand
import db/INNTEKT_BRUTTOFORM 2020-01-01 as formue
import db/INNTEKT_WYRKINNT 2021-01-01 as innt21

// Lager en avhengig variabel med to utfall (dummyvariabel): Høy inntekt vs. lav inntekt
generate høyinnt = innt21 > 800000

// Tilrettelegger de uavhengige variablene slik at de passer med den statistiske modellen
// (innebærer at de fleste variabler gjøres som til dummy’er)
generate mann = kjønn == '1'
generate gift = sivstand == '2'
generate formuehøy = formue > 1500000

// Kjører selve logit-analysen der den avhengige variabelen (må være dummy) listes først
logit høyinnt mann gift alder formuehøy

```
