<!-- Kilde: https://microdata.no/manual/eksempel/Grunnleggende%20operasjoner/Konvertere%20fra%20alfanumerisk%20til%20numerisk%20verdiformat -->

# Konvertere fra alfanumerisk til numerisk verdiformat

En del variabler har alfanumeriske verdier (tekst), der en benytter fnutter (enkle eller doble) når en benevner verdiene, f.eks. "1", "2". Kommandoen `destring` kan brukes til å gjøre slike variabler numeriske (tallverdier).

I eksempelet nedenfor gjøres variabelen kjønn om fra alfanumerisk til numerisk. Merk at variabelen får samme navn etter operasjonen. Det er bare verdiformatet som endres.

```
 // Kobler til databank
require no.ssb.fdb:23 as db

create-dataset demografidata
import db/BEFOLKNING_KJOENN as kjønn
tabulate kjønn
destring kjønn

// Fremstiller enkel statistikk for den numeriske variabelen kjønn
summarize kjønn

```
