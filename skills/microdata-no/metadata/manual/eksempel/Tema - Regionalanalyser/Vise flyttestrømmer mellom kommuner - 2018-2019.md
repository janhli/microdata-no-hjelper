<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Regionalanalyser/Vise%20flyttestr%C3%B8mmer%20mellom%20kommuner%20-%202018-2019 -->

# Vise flyttestrømmer mellom kommuner - 2018-2019

Flyttestrømmer mellom kommuner kan vises ved hjelp av variabel for bostedskommune: [BEFOLKNING_KOMMNR_FORMELL](https://microdata.no/discovery/variable/no.ssb.fdb/41/BEFOLKNING_KOMMNR_FORMELL?searchString=kommune). Dataene for denne variabelen oppdateres årlig per 1/1, slik at man kan vise bevegelser på årlig basis.

Om du ønsker å følge flyttebevegelser med kortere tidsintervaller, kan du benytte variabelen [BOSATTEFDT_BOSTED](https://microdata.no/discovery/variable/no.ssb.fdb/41/BOSATTEFDT_BOSTED?searchString=kommune) som har forløpstemporalitet og som måler endringer i bosted kontinuerlig. Dette lar deg vise flyttestrømmer fra dag til dag om ønskelig.

Det konkrete eksempelet under viser alle flyttinger som skjer mellom 1/1 2018 og 1/1 2019. Siden kommunen Rindal endret fylke og kommunenummer 1/1 2019, må man gjøre en mindre justering i kommunekodene for 2018 slik at de blir sammenliknbare med 2019.

Siden statistikkvisninger av bevegelser mellom kommuner fører til store og uoversiktlige tabeller/grafer, viser vi flyttinger mellom kommuner på fylkesnivå. Personer som flytter mellom to kommuner innen samme fylke, vises da med samme fylke før og etter flytting. Personer som ikke flytter holdes utenfor statistikken.

```
 require no.ssb.fdb:41 as db

create-dataset flytting
import db/BEFOLKNING_KOMMNR_FORMELL 2018-01-01 as kommune18
import db/BEFOLKNING_KOMMNR_FORMELL 2019-01-01 as kommune19
destring kommune18 kommune19

//Omkoder kommunekoder for 2018 for å få dem konsistente med 2019-kodene
recode kommune18 (1567 = 5061 'Rindal')

//Lager en dummy-variabel som viser om man flytter fra en kommune
generate flytter = kommune19 != kommune18 & !sysmiss(kommune19) 

define-labels flyttelbl 0 'Bor i samme kommune' 1 'Flyttet til ny kommune'
assign-labels flytter flyttelbl

textblock
Andelen personer som flytter til ny kommune mellom 1/1 2018 og 1/1 2019:
endblock
piechart flytter
tabulate flytter, cellpct freq

//Lager en variabel som viser bostedsfylke (= de to første sifrene i kommunekoden)
generate fylke18 = int(kommune18/100)
generate fylke19 = int(kommune19/100)

define-labels fylkelabel 1 Østfold \
                         2 Akershus \
                         3 Oslo \
                         4 Hedmark \
                         5 Oppland \
                         6 Buskerud \
                         7 Vestfold \
                         8 Telemark \
                         9 'Aust-Agder' \
                         10 'Vest-Agder' \
                         11 Rogaland \
                         12 Hordaland \
                         14 'Sogn og Fjordane' \
                         15 'Møre og Romsdal' \
                         18 Nordland \
                         19 Troms \
                         20 Finnmark \
                         50 Trøndelag

assign-labels fylke18 fylkelabel
assign-labels fylke19 fylkelabel

textblock
Personer som flytter til ny kommune mellom 1/1 2018 og 1/1 2019, fordelt på bostedsfylke før/etter flytting:
endblock
tabulate fylke18 fylke19 if flytter
tabulate fylke18 fylke19 if flytter, rowpct
sankey fylke18 fylke19 if flytter
barchart(percent) fylke19 if flytter, over(fylke18) stack

textblock
Personer som flytter til Oslo mellom 1/1 2018 og 1/1 2019, fordelt på bostedsfylke før flytting:
endblock
sankey fylke18 fylke19 if flytter & kommune19 == 301
barchart(count) fylke19 if flytter & kommune19 == 301, over(fylke18)

textblock
Personer som flytter fra en kommune i Nord-Norge mellom 1/1 2018 og 1/1 2019, fordelt på bostedsfylke før/etter flytting:
endblock
sankey fylke18 fylke19 if flytter & inlist(fylke18,18,19,20)
barchart(count) fylke19 if flytter & inlist(fylke18,18,19,20), over(fylke18)

textblock
Personer som flytter fra landsdelen Nord-Norge mellom 1/1 2018 og 1/1 2019, fordelt på bostedsfylke før/etter flytting:
endblock
sankey fylke18 fylke19 if flytter & inlist(fylke18,18,19,20) & !inlist(fylke19,18,19,20)
barchart(count) fylke19 if flytter & inlist(fylke18,18,19,20) & !inlist(fylke19,18,19,20), over(fylke18)

```
