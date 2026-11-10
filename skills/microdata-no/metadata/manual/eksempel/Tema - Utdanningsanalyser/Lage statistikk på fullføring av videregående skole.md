<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Utdanningsanalyser/Lage%20statistikk%20p%C3%A5%20fullf%C3%B8ring%20av%20videreg%C3%A5ende%20skole -->

# Lage statistikk på fullføring av videregående skole

Dette skriptet kan benyttes som et utgangspunkt for å lage statistikk over fullføring av videregående utdanning. Merk at resultatene som skriptet genererer ikke kan regnes som offisiell statistikk uten videre kvalitetssjekk og bearbeiding av dataene.

Skriptet baserer seg på et innspill fra noen av våre brukere, der vi prøver å gjenskape tall over fullføringsgrad for elever ved videregående skoler, nærmere bestemt SSBs statistikkbank-tabell: [https://www.ssb.no/statbank/table/12971/tableViewLayout1/](https://www.ssb.no/statbank/table/12971/tableViewLayout1/)

Den aktuelle statistikkbank-tabellen måler elever som startet på videregående skole høsten 2017, der man følger elevene frem til utgangen av vårsemesteret 2023. Man opererer med en måleperiode på 5 år for allmennfaglig utdanning, og 6 år for yrkesfaglig utdanning. Videre ser man på fullføring på normert tid og ulike underkategorier for de som ikke fullfører på normert tid. De faktiske tallene ser slik ut:

- I alt (64 392)
- Fullført med studie- eller yrkeskompetanse på normert tid (46 310)
- Fullført med studie- eller yrkeskompetanse på mer enn normert tid (6 649)
- Fullført planlagt grunnkompetanse innen fem/seks år (1 648)
- Fortsatt i videregående opplæring etter fem/seks år, uten å ha fullført (1 723)
- Gjennomført vg3/gått opp til fag-/svenneprøve, ikke bestått (1 856)
- Sluttet underveis (6 206)

Den største utfordringen er å identifisere "normert tid" for elever ved yrkesfaglig utdanning, siden denne varierer veldig etter hva slags fag man tar.

Om normert tid (kilde SSB):

Normert tid: Med normert tid menes den tid et programområde i videregående opplæring skal gjennomføres på i henhold til læreplanen for en heltidselev. Normert tid tilsvarer normalt treårig opplæring for elever og fireårig opplæring for lærlinger (to år i skole og to år i bedrift).

Enkelte programområder har en læretid på to og et halvt år og i noen tilfeller også tre år, kombinert med to år i skole. Noen kommer opp i 5 års normert tid, tre år i skole kombinert med 2 år i lære. Det siste gjelder særlig innenfor utdanningsprogrammet elektrofag, men også innenfor bygg- og anleggsteknikk og design og håndverk. For å ta hensyn til ulik lengde på de normerte løpene innen yrkesfaglige utdanningsprogrammer benyttes normert læretid fra VIGOs kodeverksdatabase.

I skriptet under gjør vi noen forenklinger knyttet til "normert tid". Dermed blir ikke tallene fullt ut sammenliknbare med de offisielle tallene til SSB. For å få det mer sammenliknbart, bør man foreta mer detaljerte vurderinger av hva som er normert tid knyttet til de ulike yrkesfaglige utdanningene.

En annen utfordring er å gjenskape alle tallene i gruppen som ikke fullfører på normert tid. Skriptet kommer ikke helt i mål med dette, men lager likevel andre interessante tall som kan være av relevans. Blant annet benyttes det kursdata for å kontrollere for om elever som ikke fullfører på normert tid fortsatt studerer etter endt måleperiode. Dette gir en indikasjon på om man har droppet ut av videregående eller tatt et pauseår, eller ikke.

```
 
require no.ssb.fdb:34 as db

create-dataset vgselever
import db/NUDB_AAR_NY_I_VID_UTD_LOV as første_gang_reg_vgs
keep if første_gang_reg_vgs == 201708

import db/NUDB_AAR_FORSTE_FULLF_VS_LOV as første_gang_fullført_vgs
import db/NUDB_SEMESTER_FFF_VS_LOV as antall_semestre_vgs

import db/NUDB_AAR_FORSTE_FULLF_VSA_LOV as første_gang_fullført_allmenn
import db/NUDB_AAR_FORSTE_FULLF_VSY_LOV as første_gang_fullført_yrkesfag
import db/NUDB_SEMESTER_FFF_VSA_LOV as antall_semestre_allmenn
import db/NUDB_SEMESTER_FFF_VSY_LOV as antall_semestre_yrkesfag

tabulate antall_semestre_vgs, missing
tabulate første_gang_fullført_vgs, missing

tabulate antall_semestre_allmenn, missing
tabulate første_gang_fullført_allmenn, missing

tabulate antall_semestre_yrkesfag, missing
tabulate første_gang_fullført_yrkesfag, missing

// Kobler på kursdata for å kontrollere for om noen fortsatt studerer etter endt måleperiode
create-dataset kursdata
import db/NUDB_KURS_NUS 2023-09-01 as kurstype
import db/NUDB_KURS_KOMP 2023-09-01 as vgs_kompetanse
import db/NUDB_KURS_FNR as personid
destring kurstype vgs_kompetanse
collapse(count) kurstype -> ant_kurs (max) kurstype -> høyeste_nivå (max) vgs_kompetanse, by(personid)
merge ant_kurs høyeste_nivå vgs_kompetanse into vgselever

use vgselever
generate under_opplæring = ant_kurs > 0

summarize høyeste_nivå
replace høyeste_nivå = int(høyeste_nivå/100000)

// Lager gjensidig utelukkende statuser for fullføring av VGS
generate status = 1 if antall_semestre_allmenn <= 6 | antall_semestre_yrkesfag <= 10
replace status = 2 if antall_semestre_allmenn > 6 | antall_semestre_yrkesfag > 10
// replace status = 3 if ....  // fullført grunnkompetanse innen tidsrammen på 5-6 år
replace status = 4 if !inlist(status,1,2) & under_opplæring & inrange(høyeste_nivå,3,5)
replace status = 5 if !inlist(status,1,2) & under_opplæring & inrange(høyeste_nivå,6,7)
replace status = 6 if !inlist(status,1,2) & !under_opplæring

define-labels statuslbl \
	1 'Fullført på normert tid' \
	2 'Fullført på mer enn normert tid' \
	3 'Fullført grunnkompetanse innen 5-6 år' \
	4 'Ikke fullført innen tidsrammen, men fortsatt under opplæring på VGS-nivå' \
	5 'Ikke fullført innen tidsrammen, men fortsatt under opplæring på UH-nivå' \
	6 'Ikke fullført, og avbrutt utdanning'
assign-labels status statuslbl

tabulate status, missing
tabulate vgs_kompetanse status, missing

textblock
Kommentarer til tallene:

- 1 - Fullført på normert tid: 47 968 vs 46 310 - avvik grunnet variasjon i hva som anses som normert tid, særlig innen yrkesfag
- 2 - Fullført på mer enn normert tid: 5 732 vs 6 649 - avvik grunnet det samme som over
- 3 - Fullført grunnkompetanse: Vanskelig å finne tall på dette i microdata.no
- 4 - Ikke fullført innen tidsrammen, men fortsatt under opplæring på VGS-nivå: 1 911 - basert på kursdata målt per 1. september 2023.
  SSB-tallene viser at 1 723 ikke fullfører innen tidsrammen og fortsetter med VGS-utdanning. Tallene våre matcher disse ganske bra.

1 032 av 1 911 med status = 4 har kompetansekoden 2, altså "Yrkeskompetanse dokumentert med svennebrev eller fagbrev,
læretid normalt etter to år i skole"

- 5 - Ikke fullført innen tidsrammen, men fortsatt under opplæring på UH-nivå: 517 - basert på kursdata målt per 1.
  september 2023 (de aller fleste av disse må ha fullført VGS og tilhører derfor egentlig status = 1 eller 2, slik at
  tallene der bør justeres opp tilsvarende)
- 6 - Ikke fullført innen tidsrammen, og avbrutt utdanning: 10 234 - ifølge SSB-tallene har 6 206 av disse sluttet underveis,
  noe som betyr at 4 028 tar pause fra utdanningen
endblock

```
