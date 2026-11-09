<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Jobb-%20og%20inntektsanalyser/Bruke%20outer%20join%20til%20%C3%A5%20fange%20opp%20personer%20som%20kommer%20i%20jobb%20i%20l%C3%B8pet%20av%20observasjonsperioden -->

# Bruke outer join til å fange opp personer som kommer i jobb i løpet av observasjonsperioden

Skriptet nedenfor viser hvordan man kan jobbe med jobbdata fra A-ordningen. Dette ble gjennomgått i vårt temakurs som ble kjørt to ganger i 2022.

Dette konkrete eksempelet demonstrerer hvordan man bør gjøre det dersom man vil foreta en fulltelling av arbeidstakere over en lengre tidsperiode evt. flere enn ett tidspunkt. Ved å bruke import-opsjonen `outer_join` fra og med variabel nr. 2, kobler man på alle observasjoner for de neste variablene, også de det ikke eksisterer observasjoner på for variabel nr. 1. Dermed får man fanget opp alle nye jobbobservasjoner (de som kommer til underveis og ikke eksisterte ved tidspunktet for variabel nr. 1). Det totale utvalget utvides i tråd med antallet nye observasjoner som legges til for hvert import-trinn med `outer_join`-opsjon. Enhetene det ikke fantes opplysninger om ved foregående måletidspunkt får verdien missing.

Om man dropper opsjonen `outer_join` ved import, vil standardløsningen "left join" benyttes. Det vil si at populasjonen defineres av variabel nr. 1, og man får bare koblet sammen data fra de neste variablene med de enhetene som allerede eksisterer gitt ved import nr. 1. Dermed går man glipp av alle nye enheter som ikke eksisterte ved det første måletidspunktet.

```
 require no.ssb.fdb:30 as db

create-dataset jobber_alle
import db/ARBLONN_ARB_ARBEIDSTID 2021-01-16 as arbtid2101
import db/ARBLONN_ARB_ARBEIDSTID 2021-02-16 as arbtid2102, outer_join
import db/ARBLONN_ARB_ARBEIDSTID 2021-03-16 as arbtid2103, outer_join

summarize

```
