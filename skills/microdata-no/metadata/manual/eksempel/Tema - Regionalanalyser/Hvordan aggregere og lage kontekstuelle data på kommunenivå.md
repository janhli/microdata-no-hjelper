<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Regionalanalyser/Hvordan%20aggregere%20og%20lage%20kontekstuelle%20data%20p%C3%A5%20kommuneniv%C3%A5 -->

# Hvordan aggregere og lage kontekstuelle data på kommunenivå

Eksempelet nedenfor viser hvordan man kan lage aggregerte data på kommunenivå (kontekstuelle data) til bruk i en enkel regresjonsanalyse.

Man begynner med å lage et vanlig persondatasett med utvalgte opplysninger, inkludert en variabel som skal brukes som koblingsnøkkel for de aggregerte dataene, i dette tilfellet variabelen kommune (faktisk bostedskommune). Deretter lages to nye datasett som brukes til å hente ut hhv. lønn/formue og ledighets-/bosettingstall på kommunenivå.

Metoden for å aggregere er å bruke kommandoen `collapse()`, der en bruker opsjonen `by()` til å spesifisere nivået en skal aggregere på (kommune). Deretter brukes kommandoen `merge` til å koble de aggregerte dataene på persondatasettet via oppgitt koblingsnøkkel (kommune).

Husk å døpe om navn på de aggregerte variablene før de kobles på persondatasettet.

Skriptet ble gjennomgått som en del av temakurset om kontekstuelle data, der også jobbing med familiedata ble demonstrert. [Klikk her](http://microdata.no/kurs) for mer om våre kurs.

```
 textblock
Hvordan koble kontekstuelle data på et persondatasett
-----------------------------------------------------
endblock

// Kobler på database
require no.ssb.fdb:30 as db

// Lager persondatasett
create-dataset personer
import db/BEFOLKNING_KOMMNR_FAKTISK 2021-01-01 as kommune
import db/BEFOLKNING_KJOENN as kjønn
import db/INNTEKT_WLONN 2021-01-01 as lønn
import db/INNTEKT_BER_BRFORM 2021-01-01 as formue
summarize lønn formue
histogram lønn, freq
histogram formue, freq

// Lager tall for snittlønn og snittformue per kommune og kobler på persondatasett
create-dataset kommunedata_lønn_formue
import db/BEFOLKNING_KOMMNR_FAKTISK 2021-01-01 as kommune
import db/INNTEKT_WLONN 2021-01-01 as lønn
import db/INNTEKT_BER_BRFORM 2021-01-01 as formue
collapse (mean) lønn formue, by(kommune)
rename lønn snittlønn_kommune
rename formue snittformue_kommune
summarize snittlønn_kommune snittformue_kommune
merge snittlønn_kommune snittformue_kommune into personer on kommune

// Lager tall for antall arbeidsledige og bosatte per kommune og kobler på persondatasett
create-dataset kommunedata_ledig_bosatt
import db/BEFOLKNING_KOMMNR_FAKTISK 2021-01-01 as kommune
import db/ARBSOEK2001FDT_HOVED 2021-01-01 as as_status
generate ant_ledig = 1 if as_status == '1'
generate ant_bosatt = 1
collapse (sum) ant_ledig ant_bosatt, by(kommune)
summarize ant_ledig ant_bosatt
merge ant_ledig ant_bosatt into personer on kommune

// Bruker til slutt persondatasettet til å foreta en enkelt regresjonsanalyse
use personer
generate ledig_pst = (ant_ledig / ant_bosatt) * 100

generate mann = 0
replace mann = 1 if kjønn == '1'

generate oslo = 0
replace oslo = 1 if kommune == '0301'

generate storkommune = 0
replace storkommune = 1 if ant_bosatt > 80000

generate rik_kommune = 0
replace rik_kommune = 1 if snittformue_kommune > 2000000

regress lønn mann oslo formue snittformue_kommune snittlønn_kommune ledig_pst ant_bosatt
regress lønn mann oslo formue rik_kommune snittlønn_kommune ledig_pst storkommune

```
