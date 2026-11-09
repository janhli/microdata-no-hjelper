<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Utdanningsanalyser/Hente%20ut%20informasjon%20om%20p%C3%A5g%C3%A5ende%20utdanning%20i%20l%C3%B8pet%20av%20et%20%C3%A5r -->

# Hente ut informasjon om pågående utdanning i løpet av et år

Opplysninger om pågående utdanning (såkalte kursdata) foreligger med kurs som enhetsnivå (med tilhørende kurs-identifikator). Kurs er gitt ved kombinasjonen person x kurstype, der hvert individ i praksis kan være representert med flere kurstyper til samme tid.

Siden kursdata ikke har person som enhet, kan ikke disse importeres inn i persondatasett på vanlig måte, men må kobles på vha. kommandoen `merge`.

Først må en legge til en lenke mellom kurs-id og person-id på kursdataene. Deretter må en aggregere opp til personnivå vha. kommandoen `collapse` før en tilslutt kobler på persondatasettet.

I eksempelet opprettes det først et persondatasett bestående av personer bosatt i Norge (`regstatus == '1'`) per 2020-01-01. Deretter hentes det ut historikk over pågående utdanning for hele året 2020, der en tar vare på utdanning på høyere nivå (master eller høyere, nivå 7 og 8). Kommandoen `collapse(count)` brukes til å telle opp antall observasjoner med pågående utdanning per individ over året 2020, og resultatet kobles så på persondatasettet for videre analyse.

NB! Merk at variabelen kurstype etter bruk av `collapse` vil bestå av verdier for den aktuelle statistikken som blir kjørt, i dette tilfellet antall observasjoner (`count`).

```
 // Kobler til databank
require no.ssb.fdb:30 as db

// Oppretter persondatasett for bosatte per 2020-01-01
create-dataset bosatte
import db/BEFOLKNING_KJOENN as kjønn
import db/BEFOLKNING_STATUSKODE 2020-01-01 as regstatus
keep if regstatus == '1'

// Henter personer som tar høyere utdanning i løpet av 2020
create-dataset kursdata
import-event db/NUDB_KURS_NUS 2020-01-01 to 2020-12-31 as kurstype
destring kurstype
keep if kurstype >= 700000 & kurstype < 900000

// Kobler på lenke mellom kurs-id og fødselsnumre
create-dataset lenke_kurs_person
import db/NUDB_KURS_FNR as fnr
merge fnr into kursdata

// Lager statistikk (collapser) over antall hendelser med høy utdanning per individ, og kobler dette på persondatasettet
use kursdata
collapse (count) kurstype -> ant_kurs, by(fnr)
merge ant_kurs into bosatte

// Lager tabell over antall personer som tok høy utdanning i løpet av 2020
use bosatte
generate utdanning_høy = 0
replace utdanning_høy = 1 if ant_kurs >= 1
tabulate utdanning_høy kjønn

```
