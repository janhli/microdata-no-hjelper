<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Utdanningsanalyser/Analysere%20voksne%20under%20utdanning -->

# Analysere voksne under utdanning

Dette skriptet kan benyttes som et utgangspunkt for å lage statistikk over utdanning for voksne. Merk at resultatene som skriptet genererer ikke kan regnes som offisiell statistikk uten videre kvalitetssjekk og bearbeiding av dataene.

Skriptet baserer seg på et innspill fra noen av våre brukere, der vi prøver å lage mest mulig dekkende statistikk for gruppen "voksne som tar utdanning":

Vi ser for oss at microdata.no ikke klarer å svare på deltakelse i ikke-formell opplæring eller læringsintensivt arbeid, men man burde kunne finne antall og andeler av befolkning/sysselsatte som deltar i formell opplæring.

- Hvor mange/hvor stor andel deltar på kurs? Innrullert per 1. sept hvert år for eksempel?
- Hvilke kurs, hvilke nivå er det voksne deltar på?
- Hvem deltar på kurs? F.eks. arbeidsmarkedsstatus, stillingsprosent, familie.

Det er et poeng å skille voksne fra ungdom som fortsatt er i utdanning.

Aktuelle opplysninger: Alder, stillingsandel, opphold fra utdanning i x år

Usikker på om det er nødvendig og mulig å skille mellom formell utdanning og formell videreutdanning.

Vi velger å operasjonalisere i skriptet under ved å se på voksne som personer i alderen 40 og oppover som er under utdanning per 1. september 2023. Vi benytter videre litt ulike kursvariabler som kan gi relevant informasjon om utdanningen som voksne tar.

```
 
require no.ssb.fdb:34 as db

create-dataset persondata
import db/BEFOLKNING_STATUSKODE 2023-01-01 as regstat
keep if regstat == '1'
import db/BEFOLKNING_FOEDSELS_AAR_MND as alder
replace alder = 2023 - int(alder / 100)
generate voksen = 0
replace voksen = 1 if alder >= 40 // Klassifiserer voksne som 40+


// Opprett kursdatasett per 1. september 2023 (nyeste data)
create-dataset kursdata1
import db/NUDB_KURS_NUS 2023-09-01 as kurs_type
import db/NUDB_KURS_FNR as fnr
destring kurs_type
collapse (count) kurs_type -> antall_kurs (max) kurs_type, by(fnr)
merge antall_kurs kurs_type into persondata

create-dataset kursdata2
import db/NUDB_KURS_UHGRUPPE 2023-09-01 as uh_gruppe
import db/NUDB_KURS_FNR as fnr
keep if inlist(uh_gruppe,'18','19','20','21','22','66','67','68')
tabulate uh_gruppe
collapse (count) uh_gruppe -> antall_videreopplæring, by(fnr)
merge antall_videreopplæring into persondata

create-dataset kursdata3
import db/NUDB_KURS_EIERF 2023-09-01 as eierforhold
import db/NUDB_KURS_FNR as fnr
keep if inlist(eierforhold,'3')
tabulate eierforhold
collapse (count) eierforhold -> antall_privat, by(fnr)
merge antall_privat into persondata

create-dataset kursdata4
import db/NUDB_KURS_ORGANISERING 2023-09-01 as organisering
import db/NUDB_KURS_FNR as fnr
keep if inlist(organisering,'3','4','5')
tabulate organisering
collapse (count) organisering -> antall_nettbasert, by(fnr)
merge antall_nettbasert into persondata


use persondata
generate opplæring = antall_kurs > 0
generate videreopplæring = antall_videreopplæring > 0
generate privat = antall_privat > 0
generate nettbasert = antall_nettbasert > 0

textblock
Antall voksne (40+) vs unge (under 40) som studerer
endblock
tabulate opplæring voksen, freq colpct

textblock
Antall voksne (40+) vs unge (under 40) som studerer, fordelt på videreopplæring
endblock
tabulate videreopplæring voksen if opplæring, freq colpct

textblock
Antall voksne (40+) vs unge (under 40) som studerer, fordelt på privat vs off. skole
endblock
tabulate privat voksen if opplæring, freq colpct

textblock
Antall voksne (40+) vs unge (under 40) som studerer, fordelt på nettbasert vs. undervisning ved institusjon
endblock
tabulate nettbasert voksen if opplæring, freq colpct

textblock
Antall voksne (40+), fordelt på de vanligste kurstypene
endblock
define-labels utdlbl \
	625202 'Norsk videreutdanning for lærere' \
	361903 'Helsearbeiderfag VG2' \
	623802 'Praktisk-pedagogisk utdanning for yrkesfaglærere' \
	625304 'Spesialpedagogikk - videreutdanning for lærere' \
	641141 'Bachelor - treårig økonomi og administrasjon' \
	621107 'Bachelor - treårig barnehagelærerutdanning' \
	682304 'Videreutdanning - Politihøgskolen' \
	863105 'Ph.d.-program - medisinske fag' \
	649999 'Økonomiske og administrative fag - andre uspesifiserte - lavere nivå' \
	741199 'Økonomisk-administrative fag - uspesifiserte - høyere nivå' \
	741132 'Master - 1. 5-årig ledelse' \
	369913 'Helse- og oppvekstfag VG1' \
	769999 'Helse-sosial og idrettsfag - andre uspesifiserte - høyere nivå' \
	641199 'Økonomisk-administrative fag - uspesifiserte - lavere nivå' \
	461903 'Helsearbeiderfaget - VG3' \
	661120 'Bachelor - treårig sykepleie' \
	401105 'Studiespesialisering - studiekompetansegivende enkeltfag/delkurs VG3' \
	699999 'Universitets- og høgskoleutdanning - uspesifisert fagfelt - lavere nivå' \
	641999 'Økonomisk-administrative fag - andre uspesifiserte - lavere nivå' \
	399999 'Videregående, grunnutdanning - uspesifisert fagfelt'
assign-labels kurs_type utdlbl

tabulate kurs_type if voksen & opplæring, rowsort() bottom(20)

textblock
Antall voksne (40+) under opplæring, fordelt på arbeidsmarkedsstatus og vanligste yrker
endblock
import db/REGSYS_ARB_ARBMARK_STATUS 2023-11-16 as arbm_status
import db/REGSYS_ARB_YRKE_STYRK08 2023-11-16 as yrke

tabulate arbm_status if voksen & opplæring, freq cellpct
tabulate yrke if voksen & opplæring, rowsort() bottom(20)

```
