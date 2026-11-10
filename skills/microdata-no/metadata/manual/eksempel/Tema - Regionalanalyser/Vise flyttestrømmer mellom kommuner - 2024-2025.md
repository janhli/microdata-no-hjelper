<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Regionalanalyser/Vise%20flyttestr%C3%B8mmer%20mellom%20kommuner%20-%202024-2025 -->

# Vise flyttestrømmer mellom kommuner - 2024-2025

Flyttestrømmer mellom kommuner kan vises ved hjelp av variabel for bostedskommune: [BEFOLKNING_KOMMNR_FORMELL](https://microdata.no/discovery/variable/no.ssb.fdb/41/BEFOLKNING_KOMMNR_FORMELL?searchString=kommune). Dataene for denne variabelen oppdateres årlig per 1/1, slik at man kan vise bevegelser på årlig basis.

Om du ønsker å følge flyttebevegelser med kortere tidsintervaller, kan du benytte variabelen [BOSATTEFDT_BOSTED](https://microdata.no/discovery/variable/no.ssb.fdb/41/BOSATTEFDT_BOSTED?searchString=kommune) som har forløpstemporalitet og som måler endringer i bosted kontinuerlig. Dette lar deg vise flyttestrømmer fra dag til dag om ønskelig.

Om du ikke trenger hyppige målinger av flyttestrømmer, er det best å bruke [BEFOLKNING_KOMMNR_FORMELL](https://microdata.no/discovery/variable/no.ssb.fdb/41/BEFOLKNING_KOMMNR_FORMELL?searchString=kommune) siden den har ferskere data (bostedskommune per 1/1 inneværende år oppdateres rundt mars).

Det konkrete eksempelet under viser alle flyttinger som skjer mellom 1/1 2024 og 1/1 2025. Om du vil lage tilsvarende statistikk for flyttinger litt lenger bakover i tid, vil det fort kunne oppstå utfordringer pga. alle kommune- og fylkesreformene i nyere tid:

-

1/1 2024: Reversering av deler av Kommunereformen

-

1/1 2020: Kommunereformen

-

1/1 2019: Ny kommunekode og endret fylke for Rindal

-

1/1 2018: Fylkessammenslåing Trøndelag

-

1/1 2017: Første sammenslåinger i Kommunereformen

Tilsvarende eksempelskript der vi demonstrerer hvordan man viser flyttestrømmer der måletidspunktene er før og etter de respektive kommuneendringene vi nevner over, finner du i egne analyseeksempler:

-

Vise flyttestrømmer mellom kommuner - 2023-2024

-

Vise flyttestrømmer mellom kommuner - 2019-2020

-

Vise flyttestrømmer mellom kommuner - 2018-2019

-

Vise flyttestrømmer mellom kommuner - 2017-2018

-

Vise flyttestrømmer mellom kommuner - 2016-2017

Siden statistikkvisninger av bevegelser mellom kommuner fører til store og uoversiktlige tabeller/grafer, viser vi flyttinger mellom kommuner på fylkesnivå. Personer som flytter mellom to kommuner innen samme fylke, vises da med samme fylke før og etter flytting. Personer som ikke flytter holdes utenfor statistikken.

```
 require no.ssb.fdb:41 as db

create-dataset flytting
import db/BEFOLKNING_KOMMNR_FORMELL 2024-01-01 as kommune24
import db/BEFOLKNING_KOMMNR_FORMELL 2025-01-01 as kommune25

//Lager en dummy-variabel som viser om man flytter fra en kommune
generate flytter = kommune25 != kommune24 & !sysmiss(kommune25) 

define-labels flyttelbl 0 'Bor i samme kommune' 1 'Flyttet til ny kommune'
assign-labels flytter flyttelbl

textblock
Andelen personer som flytter til ny kommune mellom 1/1 2024 og 1/1 2025:
endblock
piechart flytter
tabulate flytter, cellpct freq

//Lager en variabel som viser bostedsfylke (= de to første sifrene i kommunekoden)
generate fylke24 = substr(kommune24,1,2)
generate fylke25 = substr(kommune25,1,2)

define-labels fylkelabel '03' Oslo \
                         '11' Rogaland \
                         '15' 'Møre og Romsdal' \
                         '18' Nordland \
                         '31' Østfold \
                         '32' Akershus \
                         '33' Buskerud \
                         '34' Innlandet \
                         '39' Vestfold \
                         '40' Telemark \
                         '42' Agder \
                         '46' Vestland \
                         '50' Trøndelag \
                         '55' Troms \
                         '56' Finnmark

assign-labels fylke24 fylkelabel
assign-labels fylke25 fylkelabel

textblock
Personer som flytter til ny kommune mellom 1/1 2024 og 1/1 2025, fordelt på bostedsfylke før/etter flytting:
endblock
tabulate fylke24 fylke25 if flytter
tabulate fylke24 fylke25 if flytter, rowpct
sankey fylke24 fylke25 if flytter
barchart(percent) fylke25 if flytter, over(fylke24) stack

textblock
Personer som flytter til Oslo mellom 1/1 2024 og 1/1 2025, fordelt på bostedsfylke før flytting:
endblock
sankey fylke24 fylke25 if flytter & kommune25 == '0301'
barchart(count) fylke25 if flytter & kommune25 == '0301', over(fylke24)

textblock
Personer som flytter fra en kommune i Nord-Norge mellom 1/1 2024 og 1/1 2025, fordelt på bostedsfylke før/etter flytting:
endblock
sankey fylke24 fylke25 if flytter & inlist(fylke24,'18','55','56')
barchart(count) fylke25 if flytter & inlist(fylke24,'18','55','56'), over(fylke24)

textblock
Personer som flytter fra landsdelen Nord-Norge mellom 1/1 2024 og 1/1 2025, fordelt på bostedsfylke før/etter flytting:
endblock
sankey fylke24 fylke25 if flytter & inlist(fylke24,'18','55','56') & !inlist(fylke25,'18','55','56')
barchart(count) fylke25 if flytter & inlist(fylke24,'18','55','56') & !inlist(fylke25,'18','55','56'), over(fylke24)

```
