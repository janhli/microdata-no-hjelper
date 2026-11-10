<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Regionalanalyser/Vise%20flyttestr%C3%B8mmer%20mellom%20kommuner%20-%202016-2017 -->

# Vise flyttestrømmer mellom kommuner - 2016-2017

Flyttestrømmer mellom kommuner kan vises ved hjelp av variabel for bostedskommune: [BEFOLKNING_KOMMNR_FORMELL](https://microdata.no/discovery/variable/no.ssb.fdb/41/BEFOLKNING_KOMMNR_FORMELL?searchString=kommune). Dataene for denne variabelen oppdateres årlig per 1/1, slik at man kan vise bevegelser på årlig basis.

Om du ønsker å følge flyttebevegelser med kortere tidsintervaller, kan du benytte variabelen [BOSATTEFDT_BOSTED](https://microdata.no/discovery/variable/no.ssb.fdb/41/BOSATTEFDT_BOSTED?searchString=kommune) som har forløpstemporalitet og som måler endringer i bosted kontinuerlig. Dette lar deg vise flyttestrømmer fra dag til dag om ønskelig.

Det konkrete eksempelet under viser alle flyttinger som skjer mellom 1/1 2016 og 1/1 2017. Siden de første sammenslåingene i Kommunereformen (kommuner i Vestfold) skjedde 1/1 2017, må disse kommunekodene justeres for 2016 slik at de blir sammenliknbare med 2017.

Følgende endringer skjedde per 1/1 2017:

-

Sandefjord, Andebu og en del av Stokke ble slått sammen til Sandefjord og fikk nye koder

-

Resten av Stokke ble innlemmet i Tønsberg og fikk ny kode

Siden statistikkvisninger av bevegelser mellom kommuner fører til store og uoversiktlige tabeller/grafer, viser vi flyttinger mellom kommuner på fylkesnivå. Personer som flytter mellom to kommuner innen samme fylke, vises da med samme fylke før og etter flytting. Personer som ikke flytter holdes utenfor statistikken.

```
 require no.ssb.fdb:41 as db

create-dataset flytting
import db/BEFOLKNING_KOMMNR_FORMELL 2016-01-01 as kommune16
import db/BEFOLKNING_KOMMNR_FORMELL 2017-01-01 as kommune17
destring kommune16 kommune17

//Omkoder kommunekoder for 2016 for å få dem konsistente med 2017-kodene

//0720 Stokke ble splittet opp og fordelt på 0710 Sandefjord og 0704 Tønsberg per 1/1 2017. Siden vi ikke kan vite med sikkerhet hvem i Stokke som tilhører de respektive nye kommunene etter endringen, må kommune16 korrigeres til Sandefjord eller Tønsberg for de som var bosatt i hhv. Sandefjord eller Tønsberg året etter (1/1 2017). Vi antar altså at alle bostedsendringer fra Stokke til Sandefjord og Tønsberg skyldes administrative endringer og ikke reelle flyttinger.

recode kommune16 (706 719 = 710 'Sandefjord')
recode kommune16 (720 = 710 'Sandefjord') if kommune17 == 710
recode kommune16 (720 = 704 'Tønsberg') if kommune17 == 704 

textblock
Personer bosatt i Vestfold begge år, etter korrigering (de 141 som fortsatt har bosted = Stokke er personer som ikke bor i hhv. Sandefjord eller Tønsberg året etter, og som derfor vil regnes som "flyttet" i trinnet under):
endblock
tabulate kommune16 if int(kommune16/100) == 7 & int(kommune17/100) == 7


//Lager en dummy-variabel som viser om man flytter fra en kommune
generate flytter = kommune17 != kommune16 & !sysmiss(kommune17) 

define-labels flyttelbl 0 'Bor i samme kommune' 1 'Flyttet til ny kommune'
assign-labels flytter flyttelbl

textblock
Andelen personer som flytter til ny kommune mellom 1/1 2016 og 1/1 2017:
endblock
piechart flytter
tabulate flytter, cellpct freq

//Lager en variabel som viser bostedsfylke (= de to første sifrene i kommunekoden)
generate fylke16 = int(kommune16/100)
generate fylke17 = int(kommune17/100)

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
                         16 'Sør-Trøndelag' \
                         17 'Nord-Trøndelag' \
                         18 Nordland \
                         19 Troms \
                         20 Finnmark

assign-labels fylke16 fylkelabel
assign-labels fylke17 fylkelabel

textblock
Personer som flytter til ny kommune mellom 1/1 2016 og 1/1 2017, fordelt på bostedsfylke før/etter flytting:
endblock
tabulate fylke16 fylke17 if flytter
tabulate fylke16 fylke17 if flytter, rowpct
sankey fylke16 fylke17 if flytter
barchart(percent) fylke17 if flytter, over(fylke16) stack

textblock
Personer som flytter til Oslo mellom 1/1 2016 og 1/1 2017, fordelt på bostedsfylke før flytting:
endblock
sankey fylke16 fylke17 if flytter & kommune17 == 301
barchart(count) fylke17 if flytter & kommune17 == 301, over(fylke16)

textblock
Personer som flytter fra en kommune i Nord-Norge mellom 1/1 2016 og 1/1 2017, fordelt på bostedsfylke før/etter flytting:
endblock
sankey fylke16 fylke17 if flytter & inlist(fylke16,18,19,20)
barchart(count) fylke17 if flytter & inlist(fylke16,18,19,20), over(fylke16)

textblock
Personer som flytter fra landsdelen Nord-Norge mellom 1/1 2016 og 1/1 2017, fordelt på bostedsfylke før/etter flytting:
endblock
sankey fylke16 fylke17 if flytter & inlist(fylke16,18,19,20) & !inlist(fylke17,18,19,20)
barchart(count) fylke17 if flytter & inlist(fylke16,18,19,20) & !inlist(fylke17,18,19,20), over(fylke16)

```
