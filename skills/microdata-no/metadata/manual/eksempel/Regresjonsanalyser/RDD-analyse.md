<!-- Kilde: https://microdata.no/manual/eksempel/Regresjonsanalyser/RDD-analyse -->

# RDD-analyse

Skriptet under demonstrerer hvordan kommandoen `rdd` kan brukes til RDD-analyser.

Ideelt sett så passer en RDD-modell best på tilfeller der man kan observere et tydelig hopp i en variabel dersom en annen kontinuerlig variabel beveger seg over en terskelverdi. Naturlige data som passer perfekt til en RDD-analyse er ikke så lette å finne. Derfor har vi i eksempelet under manipulert en lønnsvariabel (lønn) ved å multiplisere med en faktor på 1.5 dersom lønnsverdien for året før overstiger 600000. Vi gjør også en manipulering for å tilpasse dataene en Fuzzy-modell (gjør hoppet ved terskelverdien mindre deterministisk).

Kommandoen `hexbin` benyttes for å visualisere plottene for lønn vs lønn_1.

```
 require no.ssb.fdb:30 as db

create-dataset rddtest
// Importerer utfallsvariabelen lønn og avgrenser populasjonen
import db/INNTEKT_LONN 2022-12-31 as lønn
keep if lønn > 200000 & lønn < 1000000
histogram lønn

// Importerer cutoff-variabelen lønn_1 (lønn året før)
import db/INNTEKT_LONN 2021-12-31 as lønn_1
hexbin lønn lønn_1

// Kjører RDD-analyse på lønn vs lønn året før og setter et cutoff-punkt til 600000 (gir ikke-signifikant effekt)
rdd lønn lønn_1, cutoff(600000)

// Manipulerer variabelen lønn slik at den gjør et hopp fra og med lønn_1 = 600000
replace lønn = lønn*1.5 if lønn_1 >= 600000
hexbin lønn lønn_1

// Kjører samme RDD-analyse på nytt på data som passer en RDD-modell (gir signifikant effekt)
rdd lønn lønn_1, cutoff(600000)

//Standardiserer verdier for cutoff-variabel ved å sette nullpunktet til verdien 600000
replace lønn_1 = lønn_1 - 600000
hexbin lønn lønn_1

// RDD bruker verdien 0 som standard for cutoff, og man slipper da å bruke cutoff-opsjonen siden vi nå har standardisert
// cutoff-variabelen. De to alternativene under gir da samme resultat
rdd lønn lønn_1
rdd lønn lønn_1, cutoff(0)

// Kjører en Fuzzy RDD-modell på vanlige standardiserte data (gir samme resultat som vanlig RDD-modell).
// Fuzzy-modeller krever at man oppretter en treatmentvariabel som tar verdien 1 fra og med cutoff-punktet og 0 før.
generate treatment = 0
replace treatment = 1 if lønn_1 >= 0
rdd lønn lønn_1, fuzzy(treatment)

// Gjør først dataene mer fuzzy ved å gjøre hoppet ved cutoff-punktet ikke-deterministisk (mer flytende overgang).
// Estimatene endres da, men gir fortsatt signifikant effekt siden vi benytter en fuzzy modell
generate treatment2 = 0
replace treatment2 = 1 if lønn_1 >= 0
replace treatment2 = 1 if lønn_1 > -10000 & lønn_1 < -5000
replace treatment2 = 0 if lønn_1 > 5000 & lønn_1 < 10000
rdd lønn lønn_1, fuzzy(treatment2)

// Eksempel på bruk av kovariater (ekstra forklaringsvariabler) - merk at estimater for forklaringsvariabler ikke vises
// i resultatet for RDD-analyser
import db/BEFOLKNING_KJOENN as kjønn
import db/BEFOLKNING_KOMMNR_FAKTISK 2021-01-01 as kommune
generate fylke = substr(kommune,1,2)

generate oslo = kommune == '0301'
generate bergen = kommune == '4601'
generate trondheim = kommune == '5001'
generate stavanger = kommune == '1103'
generate tromsø = kommune == '5401'

rdd lønn lønn_1 i.kjønn oslo bergen trondheim stavanger tromsø

// Eksempel på cluster-estimering (vanlig vs cluster)
destring fylke
rdd lønn lønn_1
rdd lønn lønn_1, cluster(fylke)

// Eksempel på bruk av opsjoner
rdd lønn lønn_1 i.kjønn
rdd lønn lønn_1 i.kjønn, cluster(fylke) level(90)
rdd lønn lønn_1 i.kjønn, cluster(fylke) level(90) polynomial(2)

```
