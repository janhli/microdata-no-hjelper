<!-- Kilde: https://microdata.no/manual/eksempel/Regresjonsanalyser/Line%C3%A6r%20regresjonsanalyse -->

# Lineær regresjonsanalyse

Lineære regresjonsanalyser (OLS) brukes til å estimere marginaleffekter/ koeffisientverdier for et sett med forklaringsvariabler, der utfalls-/responsvariabelen er metrisk. Gjennom opsjoner kan en tilpasse outputen (ikke vise fastleddet, endre på signifikansnivået, vise modelldiagnostikk, vise robuste etimater, benytte cluster-estimering m.m.).

```
 // Kobler til databank
require no.ssb.fdb:33 as db

//Starter med å lage populasjon
create-dataset demografidata
import db/BEFOLKNING_FOEDSELS_AAR_MND as faarmnd
import db/BEFOLKNING_STATUSKODE 2020-01-01 as regstat
generate alder = 2020 - int(faarmnd / 100)
keep if regstat == '1' & inrange(alder,16,66)

// Importerer relevante variabler for analysen
import db/BEFOLKNING_KJOENN as kjønn
import db/SIVSTANDFDT_SIVSTAND 2020-01-01 as sivstand
import db/INNTEKT_BRUTTOFORM 2020-01-01 as formue
import db/INNTEKT_WYRKINNT 2021-01-01 as innt21

// Tilrettelegger de uavhengige variablene slik at de passer med den statistiske modellen
// (innebærer at de fleste variabler gjøres som til dummy’er)
generate mann = kjønn == '1'
generate gift = sivstand == '2'
generate formuehøy = formue > 1500000

// Tester for korrelasjon mellom to av de uavhengige variablene
correlate alder formuehøy

// Kjører regresjonsanalysen der den avhengige variabelen alltid listes først
regress innt21 mann gift alder formuehøy

```
