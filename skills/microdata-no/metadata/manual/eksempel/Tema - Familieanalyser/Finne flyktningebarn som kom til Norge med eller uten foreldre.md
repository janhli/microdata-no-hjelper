<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Familieanalyser/Finne%20flyktningebarn%20som%20kom%20til%20Norge%20med%20eller%20uten%20foreldre -->

# Finne flyktningebarn som kom til Norge med eller uten foreldre

Eksempelet under viser hvordan man kan finne ut om flyktningebarn som får opphold i Norge kommer sammen med foreldre eller ikke.

Man bruker oppholdsdato og sammenlikner med foreldres oppholdsdato. Om man har samme årstall for første opphold i Norge, anser man at barnet kommer sammen med de respektive foreldre.

Videre brukes opplysninger om innvandringsgrunn til å finne flyktningestatus, fødeland til å finne ut hvor man kommer fra, og alder ved første opphold til å avgrense til aldersgruppen 0-17 år.

I dette konkrete eksempelet ser man på flyktningebarn som kommer fra Bosnia.

```
 textblock
Finne ut om et barn (0-17 år) kom som flyktning med eller uten foreldre.
Dette eksempelet ser på flyktninger fra Bosnia.
endblock

require no.ssb.fdb:30 as db

create-dataset flyktningebarn
import db/BEFOLKNING_INNGRUNN1 as innvandringsgrunn
import db/BEFOLKNING_FODELAND as fødeland
import db/BEFOLKNING_INNALDER as innvandringsalder
tabulate innvandringsgrunn if fødeland == '155'
summarize innvandringsalder if innvandringsgrunn == 'FLU' & fødeland == '155'
keep if innvandringsgrunn == 'FLU' & fødeland == '155' & inrange(innvandringsalder,0,17)

import db/BEFOLKNING_FAR_FNR as farid
import db/BEFOLKNING_MOR_FNR as morid
import db/BEFOLKNING_FORSTDATO as første_opphold
replace første_opphold = int(første_opphold / 10000)
histogram første_opphold, discrete
// Kommentar: De fleste fikk opphold i 1993 eller 1994

create-dataset flyktningforeldre
import db/BEFOLKNING_INNGRUNN1 as innvandringsgrunn
keep if innvandringsgrunn == 'FLU'

import db/BEFOLKNING_FORSTDATO as første_opphold_far
replace første_opphold_far = int(første_opphold_far / 10000)
clone-variables første_opphold_far -> første_opphold_mor

merge første_opphold_far into flyktningebarn on farid
merge første_opphold_mor into flyktningebarn on morid

use flyktningebarn
histogram første_opphold_far, discrete
histogram første_opphold_mor, discrete
tabulate første_opphold, missing
tabulate første_opphold_far, missing
tabulate første_opphold_mor, missing

generate kom_sammen_med_far = første_opphold == første_opphold_far
generate kom_sammen_med_mor = første_opphold == første_opphold_mor
generate kom_sammen_med_mor_og_far = kom_sammen_med_far & kom_sammen_med_mor
generate kom_sammen_med_mor_eller_far = kom_sammen_med_far | kom_sammen_med_mor

tabulate kom_sammen_med_far, cellpct freq
tabulate kom_sammen_med_mor, cellpct freq
tabulate kom_sammen_med_mor_og_far, cellpct freq
tabulate kom_sammen_med_mor_eller_far, cellpct freq
piechart kom_sammen_med_mor_eller_far
// Kommentar: Kun 4% av flyktningebarn fra Bosnia kom til Norge uten foreldre.
// Resten kom med enten mor eller far (eller begge). De fleste av dem som kom med minst en forelder kom med mor.

```
