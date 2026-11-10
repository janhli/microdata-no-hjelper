<!-- Kilde: https://microdata.no/manual/eksempel/Grunnleggende%20operasjoner/Gjenbruk%20av%20populasjon%20ved%20import -->

# Gjenbruk av populasjon ved import

Opsjonen `values_from()` brukes etter en `import` når man ønsker å opprette et nytt datasett med den samme populasjonen som finnes i et eksisterende datasett. Dette er nyttig når du vil importere andre variabler i nye datasett, men med samme populasjon.

Når man bruker `values_from()`, må man importere en koblingsnøkkel i det nye datasettet som gir deg muligheten til å koble ulike enhetstyper.

I eksempelet nedenfor brukes populasjonen fra datasettet `oslobosatte` når det importeres en nøkkelvariabel (variabel som knytter sammen jobb og person) inn i et nytt datasett med arbeidsforhold kalt `jobb`. Deretter importeres yrkeskode, og den filtreres ned til å kun inneholde sykepleiere. Datasettet `jobb` inneholder da arbeidsforhold med yrkeskode for sykepleiere (2223) som tilhører personer bosatt i Oslo per 1.1.2025.

I eksempelet bestemmes populasjonen av datasettet `oslobosatte`. Ved hjelp av `values_from(oslobosatte)` importeres bare observasjoner som allerede finnes i det datasettet, i det nye datasettet `jobb`.

```
 //Kobler til databank
require no.ssb.fdb:54 as db

create-dataset oslobosatte
import db/BEFOLKNING_KOMMNR_FORMELL 2025-01-01 as kommune25, values("0301")

create-dataset jobb 
//Importerer koblingsnøkkel med verdier fra oslo-datasettet
import db/ARBEIDSFORHOLD_PERSON, values_from(oslobosatte)

//Importerer yrkeskode
import db/ARBLONN_ARB_YRKE_STYRK08 2025-12-16 as yrke25

//Beholder kun yrkeskode "2223" Sykepleiere
keep if yrke25 == "2223"
tabulate yrke25

```
