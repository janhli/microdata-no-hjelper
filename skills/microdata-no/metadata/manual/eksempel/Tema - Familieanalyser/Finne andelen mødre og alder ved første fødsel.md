<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Familieanalyser/Finne%20andelen%20m%C3%B8dre%20og%20alder%20ved%20f%C3%B8rste%20f%C3%B8dsel -->

# Finne andelen mødre og alder ved første fødsel

Skriptet under viser hvordan man kan finne andelen mødre og alder ved første fødsel blant kvinner 16 år eller eldre, og som er bosatt i Norge per 1/1 2023.

```
 // Kobler til database
require no.ssb.fdb:30 as db

// Lager populasjonsdatasett av kvinner 16 år eller eldre, bosatt i Norge per 1/1 2023
create-dataset kvinner
import db/BEFOLKNING_STATUSKODE 2023-01-01 as regstat
import db/BEFOLKNING_KJOENN as kjønn
import db/BEFOLKNING_FOEDSELS_AAR_MND as faarmnd
generate fødselsår = int(faarmnd / 100)
generate alder = 2023 - fødselsår
keep if kjønn == '2' & alder >= 16 & regstat == '1'

// Lager barnedatasett bestående av førstefødte (paritet == 1)
create-dataset barnedata
import db/BEFOLKNING_PARITET as paritet
keep if paritet == 1

import db/BEFOLKNING_MOR_FNR as morid
import db/BEFOLKNING_FOEDSELS_AAR_MND as faarmnd
generate fødselsår_barn = int(faarmnd / 100)

collapse(mean) fødselsår_barn, by(morid)

textblock
Barnedatasettet har nå mor som enhet og inneholder gjennomsnittlig fødselsår for førstefødte = faktisk fødselsår for
førstefødte (man kan alternativt bruke kommandoen collapse(min), og da trenger man ikke først selektere på paritet == 1
siden man uansett finner tidspunkt for første fødsel per mor). Datasettet kan nå kobles med kvinnedatasettet
endblock

merge fødselsår_barn into kvinner

textblock
Nå har en fødselsår for førstefødte påkoblet for alle mødre i kvinnedatasettet.
De som har missing for fødselsår_barn er ikke mødre.
endblock

use kvinner
generate mor = !sysmiss(fødselsår_barn)
generate fødselsalder = fødselsår_barn - fødselsår

textblock
Andelen mødre blant kvinner 16 år og eldre bosatt i Norge per 1/1 2023:
endblock

tabulate mor, freq cellpct
piechart mor

textblock
Fødselsalder ved første fødsel for alle mødre, og for mødre født på hhv. 40-, 50-, 60-, og 70-tallet
endblock

summarize fødselsalder
histogram fødselsalder, discrete

tabulate fødselsår if inrange(fødselsår,1970,1979), summarize(fødselsalder)
tabulate fødselsår if inrange(fødselsår,1960,1969), summarize(fødselsalder)
tabulate fødselsår if inrange(fødselsår,1950,1959), summarize(fødselsalder)
tabulate fødselsår if inrange(fødselsår,1940,1949), summarize(fødselsalder)

```
