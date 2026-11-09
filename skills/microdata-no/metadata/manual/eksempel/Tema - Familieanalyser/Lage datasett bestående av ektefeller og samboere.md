<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Familieanalyser/Lage%20datasett%20best%C3%A5ende%20av%20ektefeller%20og%20samboere -->

# Lage datasett bestående av ektefeller og samboere

Microdata.no har i 2025 publisert en rekke nye familieidentifikatorer som lar deg finne opplysninger om ektefeller, partnere og samboere tilknyttet enhver populasjon, slik at du kan lage datasett bestående av par. For å finne ektefeller/partnere eller samboere, brukes henholdsvis personidentifikatorvariablene BEFOLKNING_EKT_FNR eller BEFOLKNING_SAMB_FNR. Det er også mulig å identifisere enslige gjennom variabelen BEFOLKNING_PARSTATUS.

Sammenkoblinger av par gjør det mulig å analysere statistiske sammenhenger innad i et parforhold. Skriptet nedenfor demonstrerer hvordan dette gjøres, inkludert statistikk for enslige.

Merk at identifikator for samboere også inkluderer ektefeller (men ikke motsatt). Derfor er det viktig å spesifikt definere ektefeller og samboere gjennom variabelen parstatus når man skal lage analyser og statistikk.

Dette er en helt ny versjon av det opprinnelige analyseeksempelet om ektefeller og samboere, oppdatert per august 2025. De nye familieidentifikatorene gjør prosessen med å koble sammen ulike typer familiemedlemmer mye enklere enn tidligere, og vi har derfor fornyet alle eksemplene der disse nå er tilgjengelig.

```
 // Kobler til databasen
require no.ssb.fdb:43 as ds

// Lager populasjon
create-dataset alle
import ds/BEFOLKNING_PARSTATUS 2021-01-01 as parstatus
import ds/BEFOLKNING_REGSTAT_PERSONKODE 2021-01-01 as personkode
import ds/BEFOLKNING_KJOENN as kjønn
import ds/INNTEKT_WLONN 2021-01-01 as lønn
import ds/NUDB_BU 2021-01-01 as utd
import ds/BEFOLKNING_EKT_FNR 2021-01-01 as ektefellefnr
import ds/BEFOLKNING_SAMB_FNR 2021-01-01 as samboerfnr

generate eldst = personkode == '1'
generate mann = kjønn == '1'

tabulate parstatus personkode

recode parstatus ('1' '2' = '1' 'Ektefelle')('3' '5' '6' '7' = '2' 'Samboer')(* = '3' 'Enslig')
tabulate parstatus personkode

create-dataset ektefelledata
import ds/BEFOLKNING_PARSTATUS 2021-01-01 as parstatus
keep if inlist(parstatus,'1','2')
import ds/INNTEKT_WLONN 2021-01-01 as lønn_ektefelle
import ds/NUDB_BU 2021-01-01 as utd_ektefelle
merge lønn_ektefelle utd_ektefelle into alle on ektefellefnr

create-dataset samboerdata
import ds/BEFOLKNING_PARSTATUS 2021-01-01 as parstatus
keep if inlist(parstatus,'3','5','6','7')
import ds/INNTEKT_WLONN 2021-01-01 as lønn_samboer
import ds/NUDB_BU 2021-01-01 as utd_samboer
merge lønn_samboer utd_samboer into alle on samboerfnr

use alle
textblock
Gjennomsnittslønn for alle ektefeller, samboere og enslige i 2021 (personer med nullverdier holdes utenfor statistikkgrunnlaget)
endblock
barchart(mean) lønn, over(parstatus)

textblock
Egen og ektefelles lønn i 2021 målt for eldste person i forholdet (personer med nullverdier holdes utenfor statistikkgrunnlaget)
endblock
summarize lønn lønn_ektefelle if parstatus == '1' & eldst

textblock
Egen og samboers lønn i 2021 målt for eldste person i forholdet (personer med nullverdier holdes utenfor statistikkgrunnlaget)
endblock
summarize lønn lønn_samboer if parstatus == '2' & eldst

textblock
Egen og ektefelles lønn i 2021 målt for mannen i forholdet (personer med nullverdier holdes utenfor statistikkgrunnlaget)
endblock
summarize lønn lønn_ektefelle if parstatus == '1' & mann

textblock
Egen og samboers lønn i 2021 målt for mannen i forholdet (personer med nullverdier holdes utenfor statistikkgrunnlaget)
endblock
summarize lønn lønn_samboer if parstatus == '2' & mann

textblock
Korrelasjon mellom egen og ektefelles lønn i 2021 målt for eldste person i forholdet (personer med nullverdier holdes utenfor statistikkgrunnlaget)
endblock
correlate lønn lønn_ektefelle if parstatus == '1' & eldst, obs

textblock
Korrelasjon mellom egen og samboers lønn i 2021 målt for eldste person i forholdet (personer med nullverdier holdes utenfor statistikkgrunnlaget)
endblock
correlate lønn lønn_samboer if parstatus == '2' & eldst, obs

generate utdnivå = substr(utd,1,1)
destring utdnivå

textblock
Gjennomsnittlig utdanningsnivå (0-8 der 8 er høyest) for alle ektefeller, samboere og enslige i 2021
endblock
barchart(mean) utdnivå, over(parstatus)

generate utdnivå_ektefelle = substr(utd_ektefelle,1,1)
generate utdnivå_samboer = substr(utd_samboer,1,1)
destring utdnivå_ektefelle utdnivå_samboer

textblock
Eget og ektefelles utdanningsnivå per 2021 målt for eldste person i forholdet
endblock
tabulate utdnivå utdnivå_ektefelle if parstatus == '1' & eldst, rowpct

textblock
Eget og samboers utdanningsnivå per 2021 målt for eldste person i forholdet
endblock
tabulate utdnivå utdnivå_samboer if parstatus == '2' & eldst, rowpct

textblock
Korrelasjon mellom eget og ektefelles utdanningsnivå per 2021 målt for eldste person i forholdet
endblock
correlate utdnivå utdnivå_ektefelle if parstatus == '1' & eldst, obs

textblock
Korrelasjon mellom eget og samboers utdanningsnivå per 2021 målt for eldste person i forholdet
endblock
correlate utdnivå utdnivå_samboer if parstatus == '2' & eldst, obs

textblock
Lineær regresjonsanalyse (OLS) med lønn som responsvariabel, og kjønn, ektefelles lønn, utdanningsnivå og ektefelles utdanningsnivå som forklaringsvariabler. Populasjon = alle ektefeller
endblock
regress lønn i.kjønn lønn_ektefelle i.utdnivå i.utdnivå_ektefelle if parstatus == '1'
coefplot regress lønn i.kjønn lønn_ektefelle i.utdnivå i.utdnivå_ektefelle if parstatus == '1'

textblock
Lineær regresjonsanalyse (OLS) med lønn som responsvariabel, og kjønn, samboers lønn, utdanningsnivå og samboers utdanningsnivå som forklaringsvariabler. Populasjon = alle samboere
endblock
regress lønn i.kjønn lønn_samboer i.utdnivå i.utdnivå_samboer if parstatus == '2'
coefplot regress lønn i.kjønn lønn_samboer i.utdnivå i.utdnivå_samboer if parstatus == '2'

```
