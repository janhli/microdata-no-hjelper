<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Utdanningsanalyser/Skoleelever%20-%20karakterer%20i%20grunnskolen%20og%20status%20for%20videreg%C3%A5ende%20utdanning -->

# Skoleelever - karakterer i grunnskolen og status for videregående utdanning

Skriptet under demonstrerer hvordan man kan følge elevkohorter gjennom utdanningssystemet fra grunnskole til videregående utdanning.

I dette konkrete eksempelet ser man på skoleelever som fullførte grunnskolen i 2018 og som var bosatt i Trøndelag. Man lager statistikk over karakterer i grunnskolen på ulike trinn og i utvalgte fag, og undersøker hvordan man så gjennomfører videregående utdanning. Blant annet lages en tabell til slutt som oppsummerer sammenheng mellom samlet karakterpoeng fra grunnskolen og antall semestre man har brukt før første gang fullført videregående utdanning.

Microdata.no har også mye data på høyskole- og universitetsnivå, men det blir vanskelig å følge elevkohorter over hele utdanningsforløpet pga. at historikken strekker seg lenger enn det man har data tilgjengelig for. Men det er fullt mulig å kjøre analyser av kohorter fra f.eks. videregående og frem til fullført utdanning, eller slik som her - fra grunnskole til videregående.

```
 textblock
Merk at 2018-kullet er det seneste kullet man kan se på dersom man vil ha full historikk til og med videregående. Da kan
man også måle utover det året man normalt fullfører videregående. Men dette gjør at man ikke får tak i data for
nasjonale prøver for 5. klassinger (gjelder kullene 2019 og før). Så her må man avveie hva som er viktigst, å inkludere
alle nasjonale prøver eller å inkludere data for videregående.

Etterhvert som nye oppdateringer legges inn av SSB, vil man kunne følge hele historikken fra nasjonale prøver for 5. kl.
og ut videregående.

Merk at også nasjonale prøver i engelsk for 9. klasse mangler det data for.
endblock

//------ Lager populasjon (personer bosatt i Trøndelag som fullførte grunnskolen i 2018) ------

require no.ssb.fdb:30 as db

create-dataset elever
import db/NUDB_AAR_FORSTE_FULLF_GS as år_fullført_gs
import db/NUDB_KOMM_16 as bosted16
keep if substr(bosted16,1,2) == '50' & år_fullført_gs == 2018

//------ Grunnskole: Norsk/lesing ------
import db/NUDB_NP_SKALAPOENG_NPLES05 as np_5_lesing //Har ikke data tilgjengelig for 2019-kullet og før
import db/NUDB_NP_SKALAPOENG_NPLES08 as np_8_lesing
import db/NUDB_NP_SKALAPOENG_NPLES09 as np_9_lesing
import db/NUDB_GS_STP_NOH as stp_gs_norsk_hoved
import db/NUDB_GS_STP_NOM as stp_gs_norsk_hoved_muntlig

summarize np_5_lesing np_8_lesing np_9_lesing
//histogram np_5_lesing, percent
histogram np_8_lesing, percent
histogram np_9_lesing, percent

tabulate stp_gs_norsk_hoved, missing
destring stp_gs_norsk_hoved, force
summarize stp_gs_norsk_hoved

tabulate stp_gs_norsk_hoved_muntlig, missing
destring stp_gs_norsk_hoved_muntlig, force
summarize stp_gs_norsk_hoved_muntlig

//boxplot np_5_lesing, over(stp_gs_norsk_hoved)
boxplot np_8_lesing, over(stp_gs_norsk_hoved)
boxplot np_9_lesing, over(stp_gs_norsk_hoved)
histogram stp_gs_norsk_hoved, discrete
//histogram np_5_lesing, by(stp_gs_norsk_hoved) normal
histogram np_8_lesing, by(stp_gs_norsk_hoved) normal
histogram np_9_lesing, by(stp_gs_norsk_hoved) normal
tabulate stp_gs_norsk_hoved, cellpct freq missing
//tabulate stp_gs_norsk_hoved, summarize(np_5_lesing) missing
tabulate stp_gs_norsk_hoved, summarize(np_8_lesing) missing
tabulate stp_gs_norsk_hoved, summarize(np_9_lesing) missing
barchart(mean) np_8_lesing np_9_lesing
barchart(mean) np_8_lesing np_9_lesing, over(stp_gs_norsk_hoved)

//------ Grunnskole: Matte ------
import db/NUDB_NP_SKALAPOENG_NPREG05 as np_5_regning //Har ikke data tilgjengelig for 2019-kullet og før
import db/NUDB_NP_SKALAPOENG_NPREG08 as np_8_regning
import db/NUDB_NP_SKALAPOENG_NPREG09 as np_9_regning
import db/NUDB_GS_STP_MAT as stp_gs_matematikk

summarize np_5_regning np_8_regning np_9_regning
//histogram np_5_regning, percent
histogram np_8_regning, percent
histogram np_9_regning, percent

tabulate stp_gs_matematikk, missing
destring stp_gs_matematikk, force
summarize stp_gs_matematikk

//boxplot np_5_regning, over(stp_gs_matematikk)
boxplot np_8_regning, over(stp_gs_matematikk)
boxplot np_9_regning, over(stp_gs_matematikk)
histogram stp_gs_matematikk, discrete
//histogram np_5_regning, by(stp_gs_matematikk) normal
histogram np_8_regning, by(stp_gs_matematikk) normal
histogram np_9_regning, by(stp_gs_matematikk) normal
tabulate stp_gs_matematikk, cellpct freq missing
//tabulate stp_gs_matematikk, summarize(np_5_regning) missing
tabulate stp_gs_matematikk, summarize(np_8_regning) missing
tabulate stp_gs_matematikk, summarize(np_9_regning) missing
barchart(mean) np_8_regning np_9_regning
barchart(mean) np_8_regning np_9_regning, over(stp_gs_matematikk)

//------ Grunnskole: Engelsk ------
import db/NUDB_NP_SKALAPOENG_NPENG05 as np_5_engelsk //Har ikke data tilgjengelig for 2019-kullet og før
import db/NUDB_NP_SKALAPOENG_NPENG08 as np_8_engelsk
//Nasjonale prøver, 9. trinn: Data ikke tilgjengelig
import db/NUDB_GS_STP_ENS as stp_gs_engelsk

summarize np_5_engelsk np_8_engelsk
//histogram np_5_engelsk, percent
histogram np_8_engelsk, percent

tabulate stp_gs_engelsk, missing
destring stp_gs_engelsk, force
summarize stp_gs_engelsk

//boxplot np_5_engelsk, over(stp_gs_engelsk)
boxplot np_8_engelsk, over(stp_gs_engelsk)
histogram stp_gs_engelsk, discrete
//histogram np_5_engelsk, by(stp_gs_engelsk) normal
histogram np_8_engelsk, by(stp_gs_engelsk) normal
tabulate stp_gs_engelsk, cellpct freq missing
//tabulate stp_gs_engelsk, summarize(np_5_engelsk) missing
tabulate stp_gs_engelsk, summarize(np_8_engelsk) missing
barchart(mean) np_8_engelsk
barchart(mean) np_8_engelsk, over(stp_gs_engelsk)

//------ Grunnskole: Grunnskolepoeng (samlet karakterpoeng ved avsluttet grunnskole) ------
import db/NUDB_KURS_GRPOENG as grpoeng
summarize grpoeng
histogram grpoeng, percent

// ------ Videregående utdanning ------
// Merk at siste oppdatering for 2018-kullet er året etter normaltid.
// Man fanger derfor ikke opp de som fullfører to år etter normaltid eller mer.

// Dato første gang fullført vg - har ikke oppdaterte data for 2020-kullet og senere
import db/NUDB_AAR_FORSTE_FULLF_VS as dato_fullført_vg
// Ant semestre brukt før første gang fullført vg - har ikke oppdaterte data for 2020-kullet og senere
import db/NUDB_SEMESTER_FFF_VS as ant_semestre_vg
// Stp karakter norsk hovedmål skriftlig - har ikke oppdaterte data for 2020-kullet og senere
import db/NUDB_VGS_STP_NOR1231 as stp_vg_norsk

summarize år_fullført_gs dato_fullført_vg ant_semestre_vg

// Her måler man samlet karakterpoeng fra grunnskolen fordelt på antall semestre brukt før første gang fullført videregående utdanning.
// Missing inkluderer de som ennå ikke har fullført ved siste dataoppdatering eller som har sluttet.
tabulate ant_semestre_vg, summarize(grpoeng) missing

```
