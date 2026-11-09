<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Str%C3%B8mdata/Analysere%20str%C3%B8mforbruk%20for%20prim%C3%A6rboliger -->

# Analysere strømforbruk for primærboliger

Skriptet nedenfor kan benyttes som et utgangspunkt for å lage statistikk og analyser over sammenhengen mellom boligtyper og strømforbruk målt i januar 2023 samt gjennomsnittet for 2023. Strømforbruksdata hentes fra strømavlesninger fra hele landets strømmålere på månedlig basis via Elhub-databasen. Vi ser blant annet på faktorer som boligtype, boligstørrelse, byggeår, antall personer og inntekt, og lager tall både for faktisk og relativt strømforbruk per bolig. Med relativt forbruk menes forbruk per m2 bruksareal.

Denne varianten viser hvordan man kan skille ut sekundærboliger, slik at man bare inkluderer boliger som befinner seg i samme kommune som eiers registrerte bosted. Merk at for personer som eier flere boliger i samme kommune, vil strømforbruket summeres over alle disse. Strømforbruket vil derfor bli kunstig høyt for disse individene.

Dette eksempelet viser hvordan man summerer strømforbruket over alle boliger per individ, uavhengig om det er primær- eller sekundærbolig: Analysere sammenheng mellom strømforbruk og boligtyper

Merk at resultatene som skriptet genererer ikke kan regnes som offisiell statistikk uten videre kvalitetssjekk og bearbeiding av dataene.

```
 textblock
Analyse av sammenheng mellom strømforbruk, boligtype, boligstørrelse, byggeår, antall personer og inntekt for primærboliger
---------------------------------------------------------------------------------------------------------------------------
endblock

require no.ssb.fdb:40 as db

create-dataset elhubdata

// Henter data om strømforbruk og strømproduksjon for alle målepunkter
for mnd, dag in 1:12, 31 28 31 30 31 30 31 31 30 31 30 31
  import db/ELHUB_PERS_STROMFORBRUK date_fmt(2023, $mnd, $dag) as strømforbruk++$mnd, outer_join
end

generate snittforbruk = rowmean(strømforbruk1, strømforbruk2, strømforbruk3, strømforbruk4, strømforbruk5, \
    strømforbruk6, strømforbruk7, strømforbruk8, strømforbruk9, strømforbruk10, strømforbruk11, strømforbruk12)

keep strømforbruk1 snittforbruk

// Henter data om målepunktkommune og personid tilknyttet målepunkt per januar 2023
import db/ELHUB_PERS_MALEPUNKT_ADR_KOMMUNE 2023-01-31 as målepunktkommune1
import db/ELHUB_PERS_MALEPUNKTID_FNR 2023-01-31 as personid

// Kobler på personopplysninger om bostedskommune per januar 2023
create-dataset persondata
import db/BEFOLKNING_KOMMNR_FAKTISK 2023-01-01 as bostedskommmune1
merge bostedskommmune1 into elhubdata on personid

use elhubdata
generate bostedsmålepunkt1 = målepunktkommune1 == bostedskommmune1
piechart bostedsmålepunkt1

// Beholder målepunkter som befinner seg i bostedskommunen til målepunkteier (dropper resten)

// Merk at det er kun boliger som befinner seg i en annen kommune som skilles ut, og at strømforbruket
//summeres over flere boliger per individ gitt at disse befinner seg i samme kommune.
//Strømforbruket vil derfor være kunstig høyt for personer med flere boliger i samme kommune.

keep if bostedsmålepunkt1

// Aggregerer fra målepunktenhet til person for å koble på boforholdsopplysninger og lage personstatistikk
collapse (sum) strømforbruk1 snittforbruk, by(personid)

import db/BOFORHOLD_BYGNINGSTYPE 2023-01-01 as bygningstype
import db/BOFORHOLD_HUSHTYPE 2023-01-01 as husholdningstype
import db/BOFORHOLD_BRUKSENHETSTYPE 2023-01-01 as bruksenhetstype

import db/BOFORHOLD_BYGGEAAR 2023-01-01 as byggeår
import db/BOFORHOLD_ANTALL_ROM 2023-01-01 as ant_rom
import db/BOFORHOLD_BRUKSAREAL 2023-01-01 as bruksareal

import db/BEFOLKNING_ANTPERS_I_REGSTAT_FAMNR 2023-01-01 as ant_personer
import db/INNTEKT_HUSH_IES 2022-12-31 as husholdningsinntekt

generate forbruk_per_m2 = strømforbruk1 / bruksareal

summarize strømforbruk1 snittforbruk forbruk_per_m2 byggeår ant_rom bruksareal ant_personer husholdningsinntekt

tabulate husholdningstype
tabulate bruksenhetstype
keep if husholdningstype == 'P' & bruksenhetstype == 'B'

tabulate bygningstype
generate bygningstype_gr = substr(bygningstype,1,2)
keep if inlist(bygningstype_gr,'11','12','13','14')

textblock
Strømforbruk vs. bygningstype
endblock
tabulate bygningstype, summarize(bruksareal) mean freq
tabulate bygningstype, summarize(strømforbruk1) mean freq
barchart (count) bygningstype
barchart (mean) bruksareal, over(bygningstype)
barchart (mean) strømforbruk1, over(bygningstype)
barchart (mean) forbruk_per_m2, over(bygningstype)

textblock
Strømforbruk vs. antall rom og personer
endblock
tabulate ant_rom, summarize(strømforbruk1)
tabulate ant_personer, summarize(strømforbruk1)
barchart (mean) strømforbruk1, over(ant_rom)
barchart (mean) forbruk_per_m2, over(ant_rom)
barchart (mean) strømforbruk1, over(ant_personer)
barchart (mean) forbruk_per_m2, over(ant_personer)

textblock
Strømforbruk vs. byggeår
endblock
recode byggeår \
    (min/1939 = 1 'Før 2. verdenskrig') \
	(1940/1959 = 2 '40- og 50-tallet') \
	(1960/1969 = 3 '60-tallet') \
	(1970/1979 = 4 '70-tallet') \
	(1980/1989 = 5 '80-tallet') \
	(1990/1999 = 6 '90-tallet') \
	(2000/2009 = 7 '00-tallet') \
	(2010/2019 = 8 '10-tallet') \
	(2020/max = 9 '20-tallet')

tabulate byggeår
barchart (count) byggeår
barchart (mean) strømforbruk1, over(byggeår)
barchart (mean) forbruk_per_m2, over(byggeår)

textblock
Strømforbruk vs. boligstørrelse og inntekt
endblock
hexbin strømforbruk1 bruksareal, gridsize(25)
hexbin strømforbruk1 husholdningsinntekt, gridsize(25)

recode bruksareal \
    (min/49 = 1 'Under 50') \
	(50/99 = 2 '50-99') \
	(100/149 = 3 '100-149') \
	(150/199 = 4 '150-199') \
	(200/249 = 5 '200-249') \
	(250/299 = 6 '250-299') \
	(300/max = 7 '300 ->')

barchart (mean) strømforbruk1, over(bruksareal)
barchart (mean) forbruk_per_m2, over(bruksareal)

```
