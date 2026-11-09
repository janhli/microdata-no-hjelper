<!-- Kilde: https://microdata.no/manual/eksempel/Regresjonsanalyser/Paneldata-analyse -->

# Paneldata-analyse

Paneldata-analyse er en mer avansert form for lineær regresjonsanalyse der en tar hensyn til varians over tid for variablene som inngår. Denne formen for analyse har mange likheter med vanlig regresjonsanalyse (OLS). Blant annet skal den avhengige variabelen (som listes først i `regress-panel`-kommandoen) inneholde verdier med kontinuerlig/metrisk format, f.eks. inntekt.

Hovedforskjellen fra vanlig regresjonsanalyse (jfr. kommandoen `regress`) er at dataene må være organisert på et panelformat der samtlige variabler måles flere ganger avhengig av hvor mange måletidspunkter som oppgis gjennom kommandoen `import-panel`. Et paneldatasett vil da bestå av T x N observasjoner, der T står for antall måletidspunkt og N står for antall enheter i populasjonen.

NB! Paneldatasett kan ofte bli veldig store ettersom hver enhet måles mer enn én gang: Om en analyserer hele befolkningen og bruker 2 måletidspunkter, vil datasettet typisk bestå av ca. 10 mill observasjoner (5 mill x 2). ALTSÅ: Bruk helst så små populasjoner som mulig, og helst under 1 mill enheter. Hvis ikke vil systemet bli belastet slik at kjøringer blir veldig tidkrevende.

```
 // Kobler til databank
require no.ssb.fdb:23 as db

// Lager først en paneldatapopulasjon (bør være minst mulig)
// Populasjon: Personer som fullfører masterstudium i høstsemesteret 2015
create-dataset populasjon
import db/NUDB_AAR_FORSTE_FULLF_HOV as fullf_master
keep if fullf_master > 201507 & fullf_master < 201601

// Oppretter et nytt tomt datasett som består av individene fra datasettet populasjon
clone-units populasjon paneldata

// Henter et sett med variabler med gitte måletidspunkter inn i det tomme datasettet
use paneldata
import-panel db/INNTEKT_WLONN db/SIVSTANDFDT_SIVSTAND db/BEFOLKNING_KOMMNR_FAKTISK \
    2016-01-01 2017-01-01 2018-01-01 2019-01-01

// Koder om og kjører deskriptiv statistikk samt regresjonsanalyse
rename INNTEKT_WLONN årslønn
generate gift = 0
replace gift = 1 if SIVSTANDFDT_SIVSTAND == '2'
generate oslo = 0
replace oslo = 1 if BEFOLKNING_KOMMNR_FAKTISK == '0301'

tabulate-panel gift
tabulate-panel oslo
tabulate-panel gift oslo

summarize-panel årslønn
transitions-panel oslo gift

// Gjennomfører paneldata-regresjon med hhv. fixed og random effects
regress-panel årslønn gift oslo, fe
regress-panel årslønn gift oslo, re

// Foretar hausman-test
hausman årslønn gift oslo

```
