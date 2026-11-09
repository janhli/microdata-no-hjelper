<!-- Kilde: https://microdata.no/manual/eksempel/Grunnleggende%20operasjoner/Trekke%20tilfeldige%20utvalg%20fra%20en%20totalpopulasjon -->

# Trekke tilfeldige utvalg fra en totalpopulasjon

Eksempelet under demonstrerer hvordan en kan trekke ut tilfeldige utvalg fra en totalpopulasjon/større populasjon. Dette gjøres vha. kommandoen `sample`.

Første inputparameter angir størrelsen på uttrekket. Om dette er et desimaltall (0.0-1.0), trekkes det ut en andel. Ønsker en et tilfeldig uttrekk av et spesifikt antall individer, oppgis et heltall > 1000.

Siste inputparameter er et egendefinert positivt heltall som en står fritt til å velge selv, dvs. et seed-nummer. Dette sikrer at individene i utvalget en trekker ut blir identisk ved påfølgende kjøringer. Om en ønsker å trekke flere utvalg bestående av nye personer for hvert uttrekk, velges et nytt seed-nummer for hver gang kommandoen kjøres.

```
 //Kobler til databank
require no.ssb.fdb:23 as db

// Lager datasett med alle bosatte i Norge per 1/1 2021 og trekker så ut et 10% utvalg av disse
create-dataset totalpop
import db/BEFOLKNING_STATUSKODE 2021-01-01 as registerstatus21
keep if registerstatus21 == '1'
sample 0.1 999

// Lager datasett med alle bosatte i Norge per 1/1 2021 og trekker så ut et utvalg bestående av 5000 individer
create-dataset totalpop2
import db/BEFOLKNING_STATUSKODE 2021-01-01 as registerstatus21
keep if registerstatus21 == '1'
sample 5000 888

// Lager datasett med alle bosatte i Norge per 1/1 2021 og trekker så ut et utvalg bestående av 5000 nye individer
// (forskjellige fra forrige uttrekk)
create-dataset totalpop3
import db/BEFOLKNING_STATUSKODE 2021-01-01 as registerstatus21
keep if registerstatus21 == '1'
sample 5000 950

```
