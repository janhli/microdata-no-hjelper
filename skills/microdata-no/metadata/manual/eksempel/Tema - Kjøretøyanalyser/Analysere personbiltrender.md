<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Kj%C3%B8ret%C3%B8yanalyser/Analysere%20personbiltrender -->

# Analysere personbiltrender

Eksempelet under viser hvordan man kan lage statistikk over personbiltrender i Norge, inkludert geografiske opplysninger knyttet til kjøretøyets eier som man kobler på kjøretøydatasettet via en personidentifikator. Variabelen `KJORETOY_FREG_AR` (årstall for første gangs registrering) brukes til å lage trendstatistikk.

Man bruker et kjøretøydatasett som basis (selekterer på personbiler), siden det er kjøretøy som er i fokus (og ikke personer). Kjøretøy med manglende link til kommune skyldes at eieren ikke var bosatt i Norge på det gitte tidspunktet (1/1 2024). Disse klassifiseres som "Ikke bosatt i Norge" i den geografiske statistikken.

```
 require no.ssb.fdb:32 as db

// Lager personbildatasett
create-dataset personbiler
import db/KJORETOY_KJT_GRUP 2023-12-31 as kjøretøygruppe
keep if kjøretøygruppe == '101'
drop kjøretøygruppe

import db/KJORETOY_KJ_ART 2023-12-31 as kjøringens_art
import db/KJORETOY_FREG_AR 2023-12-31 as årsmodell
import db/KJORETOY_BRUKTIMP 2023-12-31 as bruktimportert

import db/KJORETOY_DRIVSTOFF_OMK 2023-12-31 as drivstofftype
import db/KJORETOY_TEKN_CO2_UTSLIPP 2023-12-31 as utslipp_co2
import db/KJORETOY_TEKN_DRIVSTOFF_FORBRUK 2023-12-31 as drivstoff_forbruk

import db/KJORETOY_EG_VEKT 2023-12-31 as egenvekt
import db/KJORETOY_KJORETOYID_FNR 2023-12-31 as idnr

piechart kjøringens_art
tabulate kjøringens_art

piechart bruktimportert
tabulate bruktimportert

destring drivstofftype
recode drivstofftype (3 4 6 9 10 11 12 13 14 15 = 9) (7 8 = 3 'Hybrid') (5 = 4 'Elektrisk')
piechart drivstofftype
tabulate drivstofftype, freq cellpct

textblock
Personbilens alder fordelt på drivstofftype (sortert på gjennomsnittlig alder)
endblock
generate alder = 2024 - årsmodell
tabulate drivstofftype, summarize(alder) rowsort()
barchart(mean) alder, over(drivstofftype)

generate fossilbil = inlist(drivstofftype, 1, 2)
generate hybridbil = drivstofftype == 3
generate elbil = drivstofftype == 4

textblock
Overordnet salgstrend for personbiler
endblock
barchart(count) årsmodell

textblock
Drivstoff-trend
endblock
barchart(count) drivstofftype if årsmodell >= 1970, over(årsmodell) stack
barchart(percent) drivstofftype if årsmodell >= 1970, over(årsmodell) stack

textblock
Bruktimport-trend
endblock
barchart(count) bruktimportert if årsmodell >= 1970, over(årsmodell) stack
barchart(percent) bruktimportert if årsmodell >= 1970, over(årsmodell) stack

textblock
Utslippstrend for fossilbiler
endblock
summarize utslipp_co2 if fossilbil
histogram utslipp_co2 if fossilbil, freq bin(20)

tabulate årsmodell if fossilbil & årsmodell >= 2000, summarize(utslipp_co2) mean freq

generate utslippdesil = quantile(utslipp_co2, 10) if fossilbil
barchart(count) utslippdesil, over(årsmodell) stack
barchart(percent) utslippdesil, over(årsmodell) stack

textblock
Forbrukstrend for fossilbiler
endblock
summarize drivstoff_forbruk if fossilbil

tabulate årsmodell if fossilbil & årsmodell >= 2000, summarize(drivstoff_forbruk) mean freq

generate forbrukdesil = quantile(drivstoff_forbruk,10) if fossilbil
barchart(count) forbrukdesil, over(årsmodell) stack
barchart(percent) forbrukdesil if årsmodell >= 1970, over(årsmodell) stack

textblock
Egenvekttrend
endblock
summarize egenvekt
tabulate drivstofftype, summarize(egenvekt)
histogram egenvekt, freq bin(20)

tabulate årsmodell if årsmodell >= 2000, summarize(egenvekt) mean freq

generate egenvektdesil = quantile(egenvekt,10)
barchart(count) egenvektdesil if årsmodell >= 2000, over(årsmodell) stack
barchart(percent) egenvektdesil if årsmodell >= 2000, over(årsmodell) stack

barchart(mean) egenvekt, over(drivstofftype)

textblock
Geografiske trender
endblock

// Lager persondatasett og kobler bostedsopplysninger på personbildatasettet
create-dataset befolkning
import db/BEFOLKNING_KOMMNR_FORMELL 2024-01-01 as kommune
merge kommune into personbiler on idnr

// Lager geografisk statistikk for personbiler
use personbiler
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

// Kloner kommunevariabel og trekker ut storbyer fra den ene variabelen (resten plasseres i samlet kategori)
clone-variables kommune -> storby
replace storby = '9999' if sysmiss(storby)
replace storby = '8888' if !inlist(storby, '0301', '1103', '3201', '3301', '4204', '4601', '5001', '5501', '9999')
recode storby ('8888' = '8888' 'Øvrige kommuner') ('9999' = '9999' 'Ikke bosatt i Norge')

textblock
Antall personbiler fordelt på eiers bosted per 1/1 2024
endblock
tabulate fylke
barchart(count) fylke

textblock
Antall personbiler fordelt på storby (eiers bosted per 1/1 2024)
endblock
tabulate storby

textblock
Personbilers drivstofftype fordelt på eiers bostedsfylke
endblock
barchart(count) drivstofftype, over(fylke) stack
barchart(percent) drivstofftype, over(fylke) stack

textblock
Salgstrend fordelt på fylker (eiers bosted per 1/1 2024)
endblock
barchart(count) fylke if årsmodell >= 2000, over(årsmodell) stack
barchart(percent) fylke if årsmodell >= 2000, over(årsmodell) stack

textblock
Personbilers drivstofftype fordelt på storbyer
endblock
barchart(percent) drivstofftype, over(storby) stack

```
