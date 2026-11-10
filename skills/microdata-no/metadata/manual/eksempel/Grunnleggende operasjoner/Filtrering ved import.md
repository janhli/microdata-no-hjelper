<!-- Kilde: https://microdata.no/manual/eksempel/Grunnleggende%20operasjoner/Filtrering%20ved%20import -->

# Filtrering ved import

Opsjonen `values()` brukes etter en `import` når du ønsker å importere observasjoner som kun har bestemte verdier i variabelen du importerer. Filtreringen skjer under import, slik at bare de valgte observasjonene blir en del av datasettet.

I eksempelet nedenfor opprettes et datasett som kun inneholder personer registrert bosatt i Oslo (kommunenummer 0301), Bergen (kommunenummer 4601) eller Trondheim (kommunenummer 5001) per 1. januar 2025.

```
 //Kobler til databank
require no.ssb.fdb:54 as db
create-dataset kom

//Importerer kommuner og filtrerer på kommunenr for Oslo, Bergen og Trondheim
import db/BEFOLKNING_KOMMNR_FORMELL 2025-01-01 as kommune25, values("0301", "4601", "5001")
tabulate kommune25

```

Ved å bruke `values()` blir bare observasjoner med kommunenummer 0301, 4601 eller 5001 importert. Observasjoner med andre kommunenummer blir ikke med i datasettet.
