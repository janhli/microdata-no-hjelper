<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Utdanningsanalyser/Hente%20ut%20informasjon%20om%20p%C3%A5g%C3%A5ende%20utdanning%20for%20et%20gitt%20tidspunkt -->

# Hente ut informasjon om pågående utdanning for et gitt tidspunkt

Opplysninger om pågående utdanning (såkalte kursdata) foreligger med kurs som enhetsnivå (med tilhørende kurs-identifikator). Kurs er gitt ved kombinasjonen person x kurstype, der hvert individ i praksis kan være representert med flere kurstyper til samme tid.

Siden kursdata ikke har person som enhet, kan ikke disse importeres inn i persondatasett på vanlig måte, men må kobles på vha. kommandoen `merge`.

Først må en legge til en lenke mellom kurs-id og person-id på kursdataene. Deretter må en aggregere opp til personnivå vha. kommandoen `collapse` før en tilslutt kobler på persondatasettet.

I eksempelet opprettes det først et persondatasett bestående av personer bosatt i Norge (`regstatus == '1'`) per 2020-01-01. Deretter opprettes et nytt datasett der en importerer status for pågående utdanning per 2020-11-01. Kommandoen `collapse(count)` brukes til å telle opp antall observasjoner med pågående utdanning per individ for den gitte datoen, og resultatet kobles så på persondatasettet for videre analyse.

NB! Merk at variabelen kurstype etter bruk av `collapse` vil bestå av verdier for den aktuelle statistikken som blir kjørt, i dette tilfellet antall observasjoner (`count`).

```
 // Kobler til databank
require no.ssb.fdb:30 as db

// Oppretter persondatasett for bosatte per 2020-01-01
create-dataset bosatte
import db/BEFOLKNING_KJOENN as kjønn
import db/BEFOLKNING_STATUSKODE 2020-01-01 as regstatus
keep if regstatus == '1'

// Henter personer som tar utdanning per 1. november 2020, og kobler dette på persondatasettet. Siden kursdata kan ha
// flere observasjoner per individ, må kommandoen collapse brukes til å aggregere opp til personnivå. Vi bruker count som
// aggregeringsverdi (antall records)
create-dataset kursdata
import db/NUDB_KURS_NUS 2020-11-01 as kurstype
import db/NUDB_KURS_FNR as fnr
collapse (count) kurstype -> ant_kurs, by(fnr)
merge ant_kurs into bosatte

// Lager tabell over antall personer som studerer per 1. november 2020
use bosatte
generate studerer = 0
replace studerer = 1 if ant_kurs >= 1
tabulate studerer kjønn

```
