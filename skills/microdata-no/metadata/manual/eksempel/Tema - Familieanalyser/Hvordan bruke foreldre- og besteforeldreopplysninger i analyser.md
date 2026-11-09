<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Familieanalyser/Hvordan%20bruke%20foreldre-%20og%20besteforeldreopplysninger%20i%20analyser -->

# Hvordan bruke foreldre- og besteforeldreopplysninger i analyser

Skriptet under demonstrerer hvordan man kan bruke familieidentitetsvariablene BEFOLKNING_FAR_FNR, BEFOLKNING_MOR_FNR, BEFOLKNING_FARFAR_FNR, BEFOLKNING_FARMOR_FNR, BEFOLKNING_MORFAR_FNR og BEFOLKNING_MORMOR_FNR til å koble på informasjon om foreldre og besteforeldre.

1.

Man begynner med et vanlig persondatasett som inneholder opplysninger om en populasjon, pluss lenker til foreldre og besteforeldre

1.

Man lager et datasett bestående av opplysninger om foreldre og besteforeldre

1.

Opplysningene i foreldre- og besteforeldredatasettet kobles sammen med persondatasettet via identifikatorer for foreldre og besteforeldre til populasjonen

PS! Skriptet er oppdatert per august 2025: Nye identifikatorer for besteforeldre gjør det enklere å koble på opplysninger for disse (man slipper å koble sammen opplysningene i to operasjoner, dvs. gjennom å koble på opplysninger om foreldres foreldre)

```
 require no.ssb.fdb:43 as db

// Lager først et persondatasett med lenker til foreldre og besteforeldre
create-dataset persondata
import db/INNTEKT_WYRKINNT 2019-01-01 as inntekt
import db/BEFOLKNING_KJOENN as kjønn
import db/NUDB_BU 2019-01-01 as utd
import db/BEFOLKNING_FAR_FNR as fnr_far
import db/BEFOLKNING_MOR_FNR as fnr_mor
import db/BEFOLKNING_FARFAR_FNR as fnr_farfar
import db/BEFOLKNING_FARMOR_FNR as fnr_farmor
import db/BEFOLKNING_MORFAR_FNR as fnr_morfar
import db/BEFOLKNING_MORMOR_FNR as fnr_mormor

// Lager så et foreldre- og besteforeldredatasett med opplysninger om yrkesinntekt og utdanning,
// og kobler på persondatasettet via koblingsnøkler for hhv. far, mor og besteforeldre (oppdatert)
create-dataset foreldre_besteforeldre
import db/INNTEKT_WYRKINNT 2019-01-01 as inntekt_far
import db/NUDB_BU 2019-01-01 as utd_far, outer_join
clone-variables inntekt_far -> inntekt_mor
clone-variables inntekt_far -> inntekt_farfar
clone-variables inntekt_far -> inntekt_farmor
clone-variables inntekt_far -> inntekt_morfar
clone-variables inntekt_far -> inntekt_mormor
clone-variables utd_far -> utd_mor
clone-variables utd_far -> utd_farfar
clone-variables utd_far -> utd_farmor
clone-variables utd_far -> utd_morfar
clone-variables utd_far -> utd_mormor

merge inntekt_far utd_far into persondata on fnr_far
merge inntekt_mor utd_mor into persondata on fnr_mor
merge inntekt_farfar utd_farfar into persondata on fnr_farfar
merge inntekt_farmor utd_farmor into persondata on fnr_farmor
merge inntekt_morfar utd_morfar into persondata on fnr_morfar
merge inntekt_mormor utd_mormor into persondata on fnr_mormor

// Man har nå laget et datasett bestående av informasjon om enkeltindivider, og deres foreldre og besteforeldre,
// og kan kjøre analyser av dette
use persondata
summarize inntekt inntekt_far inntekt_mor inntekt_farfar inntekt_farmor inntekt_morfar inntekt_mormor
barchart(mean) inntekt inntekt_far inntekt_mor inntekt_farfar inntekt_farmor inntekt_morfar inntekt_mormor

```
