<!-- Kilde: https://microdata.no/manual/eksempel/Grunnleggende%20operasjoner/Trekke%20ut%20deler%20av%20alfanumeriske%20verdier -->

# Trekke ut deler av alfanumeriske verdier

For variabler med alfanumeriske verdier kan en trekke ut deler av verdiene/strengene ved hjelp av funksjonen `substr()`. Første parameter angir variabelnavn, den neste startposisjon, mens den siste parameteren angir antall posisjoner som skal leses inn. F.eks. vil `substr(bosted, 1, 2)` lese inn to karakterer fra og med første tegn.

```
 // Kobler til databank
require no.ssb.fdb:23 as db

create-dataset demografidata
import db/BEFOLKNING_KOMMNR_FAKTISK 2021-01-01 as bosted

// Koder om fra kommune- til fylkesnivå
generate fylke = substr(bosted, 1, 2)

// Legger til verdilabler for å navngi fylker med navn (=> penere deskriptiv output)
define-labels fylkerstring \
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
assign-labels fylke fylkerstring

tabulate fylke

```
