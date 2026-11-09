<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Familieanalyser/Aggregere%20data%20til%20familieniv%C3%A5 -->

# Aggregere data til familienivå

Individer kan knyttes opp mot et familienummer som kan brukes til å aggregere opplysninger på familienivå. Individer tilhørende samme familie vil være registrert med det samme familienummeret som består av person-id’en til den eldste personen i familien.

I eksempelet opprettes først et persondatasett der en filtrerer ned på person i familier bestående av ektepar med små barn (kode 2.1.1). Deretter kobles det på demografiske opplysninger.

Familieinntekt er en opplysning på familienivå, dvs. familie = enhet. Derfor må en opprette et nytt datasett for dette formålet (datasett kan ikke bestå av variabler med ulike enhetstyper). En importerer da yrkesinntekt på personnivå, og bruker så kommandoen `collapse(sum)` til å summere inntektene på familienivå (`by(famnr)`). Resultatet blir et datasett med familie som enhet.

Til slutt kobles familieinntekt på persondatasettet vha. kommandoen `merge`.

```
 // Kobler til databank
require no.ssb.fdb:30 as db

// Oppretter først et persondatasett for personer i familier bestående av ektepar med små barn
create-dataset persondata
import db/BEFOLKNING_REGSTAT_FAMTYP 2021-01-01 as famtype
tabulate famtype
keep if famtype == '2.1.1'

// Legger til diverse demografiske opplysninger
import db/BEFOLKNING_KJOENN as kjønn
import db/BEFOLKNING_FOEDSELS_AAR_MND as faarmnd
generate alder = 2021 - int(faarmnd/100)

import db/BEFOLKNING_KOMMNR_FAKTISK 2021-01-01 as bosted
generate fylke = substr(bosted, 1, 2)

import db/BEFOLKNING_BARN_I_HUSH 2021-01-01 as antbarn

// Oppretter datasett for generering av total yrkesinntekt per familie => enhet = familie
create-dataset familiedata
import db/BEFOLKNING_REGSTAT_FAMNR 2021-01-01 as famnr
import db/INNTEKT_WYRKINNT 2021-01-01 as yrkesinnt
collapse (sum) yrkesinnt, by(famnr)
rename yrkesinnt familieinnt

// Kobler familieinntekt på persondatasettet (enhet = personer)
merge familieinnt into persondata on PERSONID_1

// Lager familiestatistikk. Familienummeret består av person-id til eldste person i familien, så når en fjerner
// individer med manglende familieinntekt sitter en igjen med et datasett med familie som enhet.
// Alle personopplysninger vil da gjelde for eldste person i familien
use persondata
drop if sysmiss(familieinnt)

rename alder alder_eldst
rename kjønn kjønn_eldst

define-labels fylketekst \
	'03' Oslo \
	'11' Rogaland \
	'15' 'Møre og Romsdal' \
	'18' Nordland \
	'30' Viken \
	'34' Innlandet \
	'38' 'Vestfold og Telemark' \
	'42' Agder \
	'46' Vestland \
	'50' Trøndelag \
	'54' 'Troms og Finnmark' \
	'21' Spitsbergen \
	'25' 'Utdanning i utlandet' \
	'99' Uoppgitt
assign-labels fylke fylketekst

tabulate fylke

histogram alder_eldst, discrete
histogram antbarn, discrete percent

tabulate antbarn
tabulate antbarn, cellpct
tabulate antbarn kjønn_eldst

summarize familieinnt
barchart (mean) familieinnt, over(fylke)
barchart (mean) familieinnt, over(antbarn)
histogram familieinnt, freq
histogram familieinnt, by(antbarn) percent

```
