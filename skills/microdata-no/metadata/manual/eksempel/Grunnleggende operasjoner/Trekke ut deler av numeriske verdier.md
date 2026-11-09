<!-- Kilde: https://microdata.no/manual/eksempel/Grunnleggende%20operasjoner/Trekke%20ut%20deler%20av%20numeriske%20verdier -->

# Trekke ut deler av numeriske verdier

For variabler med numeriske verdier kan en trekke ut deler av verdiene ved hjelp av funksjonen `int()`. Denne avrunder nedover til nærmeste heltall. Alternativt kan også funksjonen `floor()` brukes.

I eksempelet nedenfor genereres alder per 2021 ut i fra variabelen faarmnd som bruker det numeriske formatet YYYYMM.

```
 // Kobler til databank
require no.ssb.fdb:23 as db

create-dataset demografidata
import db/BEFOLKNING_FOEDSELS_AAR_MND as faarmnd

// Beregner alder i 2021 ut i fra fødselsår
generate alder = 2021 - int(faarmnd / 100)

```
