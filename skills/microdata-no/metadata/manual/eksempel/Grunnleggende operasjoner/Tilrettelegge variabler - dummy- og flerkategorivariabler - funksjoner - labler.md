<!-- Kilde: https://microdata.no/manual/eksempel/Grunnleggende%20operasjoner/Tilrettelegge%20variabler%20-%20dummy-%20og%20flerkategorivariabler%20-%20funksjoner%20-%20labler -->

# Tilrettelegge variabler - dummy- og flerkategorivariabler - funksjoner - labler

Eksempelet under viser ulike måter å tilrettelegge variabler på, inkludert bruk av labler.

Variabler som benyttes slik de er, uten noen form for bearbeiding, har allerede labler som vises når man lager statistikk. Men når man tilrettelegger og lager nye variabler og kategoriinndelinger, er det nyttig å opprette labler for å få bedre oversikt over betydningen av de ulike kodene. Labler lages gjennom kommandoen `define-labels` og kobles til de relevante variabler ved kommandoen `assign-labels`. Om du lager flere variabler med identisk kodeliste, holder det å benytte `assign-labels` der du refererer til allerede opprettet labelsett-navn.

```
 // Kobler til databank
require no.ssb.fdb:23 as db

// Henter variablene en trenger
create-dataset demografidata
import db/BEFOLKNING_KJOENN as kjonn
import db/BEFOLKNING_FOEDSELS_AAR_MND as faarmnd
import db/INNTEKT_BRUTTOFORM 2020-01-01 as formue
import db/BOSATTEFDT_BOSTED 2020-01-01 as bosted

// Beregner alder i 2020 ut i fra fødselsår
generate alder = 2020 - int( faarmnd / 100 )

// Lager en dummyvariabel som angir mann ut i fra kjønn
generate mann = 0
replace mann = 1 if kjonn == '1'

// Gruppere formue i 4 intervaller
generate formueint = 1
replace formueint = 2 if formue > 150000
replace formueint = 3 if formue > 250000
replace formueint = 4 if formue > 400000

// Angi formue i 1000 kr
generate formue1000 = formue / 1000

// Koder om fra kommune- til fylkesnivå
generate fylke = substr(bosted,1,2)

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
