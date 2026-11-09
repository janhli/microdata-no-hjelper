<!-- Kilde: https://microdata.no/manual/eksempel/Regresjonsanalyser/Diff-in-diff-analyse -->

# Diff-in-diff-analyse

I eksempelet under kjøres en diff-in-diff-analyse.

Først trekkes et tilfeldig utvalg på 100000 individer. Dette er valgfritt, det er fullt mulig å kjøre analysen på fulle populasjoner. Deretter lages det et paneldatasett for dette utvalget ved bruk av `import-panel`, og man importerer data for årene 2018 – 2021. Etterpå balanseres paneldatasettet ved å slette alle observasjoner med minst én missing-verdi (valgfritt).

Deretter kodes gruppevariabelen der man bruker kvinner som behandlingsgruppe og menn som kontrollgruppe. Behandlingstidspunkt settes til 2020.

Til slutt kjøres kommandoen `regress-panel-diff`, og man får ut diff-in-diff-verdien (ATET) -1991.77 når man kontrollerer for sivilstand = gift, bosted = Oslo, og utdanningsnivå lik mastergrad eller høyere. ATET-verdien er ikke signifikant i dette tilfellet.

```
 require no.ssb.fdb:23 as db

// Lager et tilfeldig utvalg på 100000
create-dataset populasjon
import db/BEFOLKNING_KJOENN as kjønn
sample 100000 3322
clone-units populasjon paneldata

// Lager et paneldatasett for den tilfeldige populasjonen
use paneldata
import-panel db/INNTEKT_LONN db/SIVSTANDFDT_SIVSTAND db/BOSATTEFDT_BOSTED db/BEFOLKNING_KJOENN \
    db/NUDB_BU 2018-01-01 2019-01-01 2020-01-01 2021-01-01
rename INNTEKT_LONN lønn
rename SIVSTANDFDT_SIVSTAND sivstand
rename BOSATTEFDT_BOSTED bosted
rename BEFOLKNING_KJOENN kjønn
rename NUDB_BU utd

// Balanserer paneldatasettet
drop if sysmiss(lønn) | sysmiss(sivstand) | sysmiss(bosted) | sysmiss(kjønn) | sysmiss(utd)

// Lager gruppe- og behandingsvariablene (obligatorisk)
generate gruppe = 0
replace gruppe = 1 if kjønn == '2'

generate behandling = 0
replace behandling = 1 if year(date@panel) >= 2020

// Koder øvrige forklaringsvariabler
generate gift = 0
replace gift = 1 if sivstand == '2'

generate oslo = 0
replace oslo = 1 if bosted == '0301'

generate høyutd = 0
replace høyutd = 1 if substr(utd,1,1) == '7' | substr(utd,1,1) == '8'

// Kjører diff-in-diff-analyse
summarize-panel lønn if gruppe == 1
summarize-panel lønn if gruppe == 0

regress-panel-diff lønn gruppe behandling gift oslo høyutd

```
