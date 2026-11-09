<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Familieanalyser/Lage%20analyse%20av%20s%C3%B8sken -->

# Lage analyse av søsken

Skriptet under demonstrerer hvordan man bruker søskenidentifikatorvariabelen [BEFOLKNING_SOESKEN_FNR](https://microdata.no/discovery/variable/no.ssb.fdb/43/BEFOLKNING_SOESKEN_FNR) til å finne alle søsken som tilhører samme søskenflokk. Dette lar deg lage aggregert statistikk over søskenflokker, f.eks. gjennomsnittslønn eller antall søsken, som igjen kan kobles på et persondatasett for videre analyser der søskenopplysninger brukes som forklaringsfaktor.

Søskenidentifikatorvariabelen BEFOLKNING_SOESKEN_FNR fungerer på samme måte som familieidentifikatoren BEFOLKNING_REGSTAT_FAMNR, ved at alle som tilhører samme søskenflokk har samme identifikatornummer (= personidentifikatoren til eldste person i søskenflokken).

NB! Dette skriptet er en oppdatert versjon som tar i bruk nye søskenidentifikatorer (gjort tilgjengelig i 2025). Disse gjør det mye enklere enn tidligere å lage søskendatasett.

```
 require no.ssb.fdb:43 as db

create-dataset bosatte
import db/BEFOLKNING_STATUSKODE 2023-01-01 as regstat
keep if regstat == '1'
import db/INNTEKT_WLONN 2023-12-31 as lønn
import db/BEFOLKNING_SOESKEN_FNR as søskennr

create-dataset søskendata
import db/BEFOLKNING_SOESKEN_FNR as søskennr
import db/BEFOLKNING_FOEDSELS_AAR_MND as fdato
import db/INNTEKT_WLONN 2023-12-31 as lønn
collapse(mean) lønn -> snittlønn_søsken (count) fdato -> ant_søsken, by(søskennr)
merge snittlønn_søsken ant_søsken into bosatte on søskennr

use bosatte
summarize lønn snittlønn_søsken ant_søsken

textblock
Antall søsken for personer med minst ett søsken
endblock
tabulate ant_søsken
barchart(count) ant_søsken

textblock
Gjennomsnittslønn for søsken fordelt på antall søsken i søskenflokken. Populasjon = alle bosatte personer med søsken. Personer med null i lønn holdes utenfor statistikken.
endblock
tabulate ant_søsken, summarize(snittlønn_søsken)
barchart(mean) snittlønn_søsken, over(ant_søsken)

```
