<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Regionalanalyser/Omkode%20fra%20land%20til%20verdensregion -->

# Omkode fra land til verdensregion

Eksempelet under demonstrerer hvordan man koder om en variabel som inneholder verdier på land-nivå til verdensregion-nivå. Landnivå blir i mange tilfeller for detaljert, og det kan da være nyttig å gruppere land etter SSBs standard for verdensregioner ([https://www.ssb.no/klass/klassifikasjoner/91/varianter/1466](https://www.ssb.no/klass/klassifikasjoner/91/varianter/1466)).

Ved å bruke kommandoen `destring` til å gjøre verdiene numeriske, kan en deretter benytte kommandoen `recode` til å kode om verdiene. Recode gjør det blant annet mulig å kode om alle verdier i et intervall til en gitt verdi. Omkodingen foregår i sekvensielt fra venstre mot høyre i recode-uttrykket, noe som kan utnyttes til å forenkle om kodingen. I eksempelet nedenfor, vil f.eks. verdien 1 tilegnes alle land med koder i intervallene 101 – 141 og 144 – 158, bortsett fra dem som allerede er blitt gitt koden 2 i parentesen foran.

```
 // Kobler til databank
require no.ssb.fdb:30 as db

create-dataset befolkning
import db/BEFOLKNING_STATUSKODE 2021-01-01 as statuskode
keep if statuskode == '1'

import db/BEFOLKNING_FODELAND as fødeland
tabulate fødeland

// Oppretter kopi av fødelandsvariabel for å kunne kontrollere omkodingen
clone-variables fødeland -> fødeland_orig

// Omkoder fødeland til verdensregion - bruker først destring for å gjøre formatet om til numerisk (kreves ved recode)
destring fødeland
recode fødeland \
     (111 120 138 139 140 148 155 156 159/164 = 2) \
	 (101/141 144/158 = 1) \
	 (203/393 = 3) \
	 (143 404/578 = 4) \
	 (612 684 = 5) \
	 (601/775 = 6) \
	 (802/840 = 7) \
	 (980 = 8) \
	 (990 = 9)

define-labels vregion \
	0 'Norge' \
	1 'EU/EØS' \
	2 'Europeiske land utenom EU' \
	3 'Afrika' \
	4 'Asia med Tyrkia' \
	5 'Nord-Amerika' \
	6 'Sør- og Mellom-Amerika' \
	7 'Oseania' \
	8 'Statsløse' \
	9 'Uoppgitt'
assign-labels fødeland vregion

tabulate fødeland
tabulate fødeland_orig fødeland

```
