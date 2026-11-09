<!-- Kilde: https://microdata.no/manual/eksempel/Grunnleggende%20operasjoner/Opprette%20flere%20datasett%20og%20flytte%20seg%20mellom%20dem -->

# Opprette flere datasett og flytte seg mellom dem

Det er mulig å opprette flere enn ett datasett. Dette gjøres gjennom kommandoen `create-dataset`. Alle operasjoner en foretar gjøres på datasettet en sist opprettet (en flytter seg automatisk til et nyopprettet datasett). Ønsker en å arbeide på et annet datasett som allerede er opprettet, brukes kommandoen `use`.

I eksempelet demonstreres det hvordan en oppretter et nytt datasett, datasett2, importerer variabler til dette, for så å flytte seg tilbake til det første datasettet. Datasettet demografidata vil inneholde alle individer i databasen med et kjønn, mens datasett2 kun inneholder individer som er registrert med en sivilstatus per 2021-01-01. De har altså ulike populasjoner.

Merk at det første import-trinnet som utføres bestemmer størrelsen på populasjonen for det aktuelle datasettet (systemet kobler på nye variabler gjennom “left-join”-prinsippet). Derfor må en passe på å ikke starte med å importere variabler der bare deler av et ønsket utvalg har en verdi.

```
 // Kobler til databank
require no.ssb.fdb:23 as db

create-dataset demografidata
import db/BEFOLKNING_KJOENN as kjønn

create-dataset datasett2
import db/SIVSTANDFDT_SIVSTAND 2021-01-01 as sivstand

use demografidata

```
