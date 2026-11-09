<!-- Kilde: https://microdata.no/manual/eksempel/Grunnleggende%20operasjoner/Fjerning%20av%20enheter%20fra%20et%20datasett -->

# Fjerning av enheter fra et datasett

Før en utfører analyser på et datasett, er det som regel ønskelig å “trimme det ned” ved å fjerne personer en ikke ønsker å inkludere. Dette kan gjøres gjennom kommandoene `drop` og `keep` i kombinasjon med standard if-betingelser.

I eksempelet nedenfor “trimmes utvalget ned” til å inneholde personer mellom 16 og 66.

```
 // Kobler til databank
require no.ssb.fdb:23 as db

create-dataset demografidata
import db/BEFOLKNING_KJOENN as kjønn
import db/BEFOLKNING_FOEDSELS_AAR_MND as faarmnd

generate alder = 2021 - int(faarmnd / 100)

keep if alder >= 16 & alder < 67

```
