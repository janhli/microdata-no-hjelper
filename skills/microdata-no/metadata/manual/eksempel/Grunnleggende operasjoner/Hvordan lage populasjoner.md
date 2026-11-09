<!-- Kilde: https://microdata.no/manual/eksempel/Grunnleggende%20operasjoner/Hvordan%20lage%20populasjoner -->

# Hvordan lage populasjoner

Analyseverktøyet i microdata.no baserer seg på left-join-prinsippet. Det betyr at første variabelen som opprettes bestemmer populasjonens størrelse. Om dette er en universell variabel som f.eks. kjønn, vil datasettet ditt bestå av flest mulig individer fra den totale databasen, inkludert personer som er døde, emigrerte eller ikke er født på det tidspunktet en ønsker å analysere.

Begynner du med å importere en variabel som bare gjelder et begrenset antall individer som f.eks. uføretrygd, vil datasettet ditt kun bestå av personer i Norge som mottok uføretrygd på det aktuelle tidspunktet du måler for.

En kan ikke gjøre populasjonen større enn det variabel nr. 1 gir mulighet for (med mindre man bruker opsjonen `outer_join`). Så en må tenke over hvilken variabel en begynner å importere, slik at en får med seg alle personene en ønsker å analysere. En kan imidlertid gjøre populasjoner mindre om en ønsker. Dette gjøres ved å bruke kommandoen `drop if` eller `keep if`.

```
 // Kobler til databank
require no.ssb.fdb:23 as db

// Eksempel 1: Populasjon = alle bosatte i Bergen per 1/1 2021
create-dataset eks1
import db/BEFOLKNING_KOMMNR_FAKTISK 2021-01-01 as bosted
keep if bosted == '4601'

// Eksempel 2: Populasjon = alle bosatte i Vestland per 1/1 2021
create-dataset eks2
import db/BEFOLKNING_KOMMNR_FAKTISK 2021-01-01 as bosted
keep if substr(bosted, 1, 2) == '46'

// Eksempel 3: Populasjon = alle med en yrkesinntekt i året 2021 (= alle med en årlig yrkesinntekt > 0 i 2021)
create-dataset eks3
import db/INNTEKT_WYRKINNT 2021-12-31 as yrkesinntekt

// Eksempel 4: Når en begynner med en universell variabel men egentlig vil
// analysere individer med gitte egenskaper på et gitt tidspunkt
create-dataset eks4
import db/BEFOLKNING_KJOENN as kjønn
import db/INNTEKT_WYRKINNT 2021-12-31 as yrkesinntekt
drop if sysmiss(yrkesinntekt)

// Eksempel 5: Når en begynner med en universell variabel men egentlig vil analysere individer som faktisk var bosatt i
// Norge på et gitt tidspunkt. Variabelen BEFOLKNING_STATUSKODE er egnet til dette formålet da den inneholder koder for
// hhv. "bosatt", "død" og "emigrert". "Bosatt" har koden '1'.
create-dataset eks5
import db/BEFOLKNING_KJOENN as kjønn
import db/BEFOLKNING_STATUSKODE 2021-01-01 as regstatus
keep if regstatus == '1'

```
