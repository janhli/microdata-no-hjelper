<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Kj%C3%B8ret%C3%B8yanalyser/Lage%20kj%C3%B8ret%C3%B8ystatistikk -->

# Lage kjøretøystatistikk

Eksempelet under viser hvordan man kan lage statistikk over alle registrerte kjøretøy i Norge, inkludert geografiske opplysninger knyttet til kjøretøyets eier som man kobler på kjøretøydatasettet via en personidentifikator.

I dette tilfellet bruker man et kjøretøydatasett som basis, siden det er kjøretøy som er i fokus (og ikke personer). Kjøretøy med manglende link til kommune skyldes at eieren ikke var bosatt i Norge på det gitte tidspunktet (1/1 2024). Disse klassifiseres som "Ikke bosatt i Norge" i den geografiske statistikken.

```
 require no.ssb.fdb:32 as db

// Lager kjøretøydatasett
create-dataset kjøretøy
import db/KJORETOY_KJT_GRUP 2023-12-31 as kjøretøygruppe
import db/KJORETOY_KJ_ART 2023-12-31 as kjøringens_art
import db/KJORETOY_FREG_AR 2023-12-31 as årsmodell
import db/KJORETOY_BRUKTIMP 2023-12-31 as bruktimportert

import db/KJORETOY_DRIVSTOFF_OMK 2023-12-31 as drivstofftype
import db/KJORETOY_TEKN_CO2_UTSLIPP 2023-12-31 as utslipp_co2
import db/KJORETOY_TEKN_DRIVSTOFF_FORBRUK 2023-12-31 as drivstoff_forbruk

import db/KJORETOY_EG_VEKT 2023-12-31 as egenvekt
import db/KJORETOY_KJORETOYID_FNR 2023-12-31 as idnr

textblock
Oversikt over typer kjøretøy og bruksområde
endblock
tabulate kjøretøygruppe
clone-variables kjøretøygruppe -> kjøretøygruppe_gr
destring kjøretøygruppe_gr
recode kjøretøygruppe_gr \
    (101 = 1 'Personbil') \
	(106/107 = 2 'Personbilambulanser') \
	(201/215 = 3 'Buss') \
	(301/315 = 4 'Varebil/kombinert bil') \
	(316 = 5 'Campingbil') \
	(320/336 = 6 'Lastebil') \
	(360/381 = 6) \
	(340 = 7 'Trekkbil') \
	(350 = 8 'Beltebil') \
	(401 = 9 'Traktor') \
	(501/509 = 10 'Motorredskap') \
	(601/621 = 11 'Moped/motorsykkel') \
	(630 = 12 'Snøscooter')

piechart kjøretøygruppe_gr
tabulate kjøretøygruppe_gr, freq cellpct
tabulate kjøretøygruppe_gr kjøringens_art, rowpct

textblock
Kjøretøyets alder fordelt på kjøretøytype
endblock
generate alder = 2024 - årsmodell
tabulate kjøretøygruppe_gr, summarize(alder) rowsort()
barchart(mean) alder, over(kjøretøygruppe_gr)

textblock
Andel bruktimporterte kjøretøy fordelt på kjøretøytype
endblock
tabulate kjøretøygruppe_gr bruktimportert, rowpct

destring drivstofftype
recode drivstofftype (3 4 6 9 10 11 12 13 14 15 = 9) (7 8 = 3 'Hybrid') (5 = 4 'Elektrisk')

generate personbil = kjøretøygruppe_gr == 1
generate fossilbil = inlist(drivstofftype,1,2)
generate hybridbil = drivstofftype == 3
generate elbil = drivstofftype == 4

textblock
Kjøretøy fordelt på drivstofftype og kjøretøytype
endblock
tabulate kjøretøygruppe_gr drivstofftype, missing rowpct

textblock
Personbilers alder fordelt på drivstofftype (sortert på alder)
endblock
tabulate drivstofftype if personbil, summarize(alder) rowsort()

textblock
Co2-utslipp fordelt på kjøretøytype (sortert på co2-utslipp)
endblock
tabulate kjøretøygruppe_gr, summarize(utslipp_co2) rowsort()
barchart(mean) utslipp_co2, over(kjøretøygruppe_gr)

textblock
Drivstoff-forbruk fordelt på kjøretøytype (sortert på drivstoff-forbruk)
endblock
tabulate kjøretøygruppe_gr, summarize(drivstoff_forbruk) rowsort()
barchart(mean) drivstoff_forbruk, over(kjøretøygruppe_gr)

textblock
Egenvekt fordelt på kjøretøytype (sortert på egenvekt)
endblock
tabulate kjøretøygruppe_gr, summarize(egenvekt) rowsort()
barchart(mean) egenvekt, over(kjøretøygruppe_gr)

textblock
Kjøretøyet egenvekt fordelt på drivstofftype og kjøretøytype (sortert på kjøretøytypens gjennomsnittlige egenvekt)
endblock
tabulate kjøretøygruppe_gr drivstofftype, summarize(egenvekt) rowsort()
barchart(mean) egenvekt, over(drivstofftype)

// Lager persondatasett og kobler bostedsopplysninger på kjøretøydatasettet
create-dataset befolkning
import db/BEFOLKNING_KOMMNR_FORMELL 2024-01-01 as kommune
merge kommune into kjøretøy on idnr

// Lager geografisk statistikk for kjøretøy
use kjøretøy
generate fylke = substr(kommune,1,2)
replace fylke = '99' if sysmiss(fylke)
define-labels fylkelbl \
	'03' Oslo \
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
	'56' Finnmark \
	'99' 'Ikke bosatt i Norge'
assign-labels fylke fylkelbl

//Kloner kommunevariabel og trekker ut storbyer fra den ene variabelen (resten plasseres i samlet kategori)
clone-variables kommune -> storby
replace storby = '9999' if sysmiss(storby)
replace storby = '8888' if !inlist(storby, '0301', '1103', '3201', '3301', '4204', '4601', '5001', '5501', '9999')
recode storby ('8888' = '8888' 'Øvrige kommuner') ('9999' = '9999' 'Ikke bosatt i Norge')

textblock
Antall kjøretøy fordelt på eiers bosted
endblock
tabulate fylke
barchart(count) fylke

tabulate fylke kjøretøygruppe_gr, rowpct
tabulate storby kjøretøygruppe_gr, rowpct

barchart(count) kjøretøygruppe_gr, over(fylke) stack
barchart(percent) kjøretøygruppe_gr, over(fylke) stack

barchart(count) drivstofftype, over(fylke) stack
barchart(percent) drivstofftype, over(fylke) stack

barchart(percent) kjøretøygruppe_gr, over(storby) stack
barchart(percent) drivstofftype, over(storby) stack

```
