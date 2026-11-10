<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Utdanningsanalyser/Finne%20studiekoder%20for%20personer%20som%20starter%20videreg%C3%A5ende%20utdanning%20et%20gitt%20%C3%A5r -->

# Finne studiekoder for personer som starter videregående utdanning et gitt år

Skriptet under viser hvordan man kan lage en populasjon av personer som starter videregående utdanning i løpet av et gitt år (2022), og deretter finne ut hvilke typer studier disse tar ved slutten av året. Vi viser kun tosifret NUS-kode-inndeling siden full sekssifret inndeling fører til for mange koder med få observasjoner.

Skriptet demonstrerer også hvordan man kan sjekke andelen elever som tar ett vs flere studier samtidig ved slutten av året.

Det er mulig å justere på skriptet og spesifisere nærmere når man begynner på videregående utdanning, f.eks. en gitt måned, vårsemester, høstsemester etc. Og man kan også velge andre datoer for måling av studium.

```
 require no.ssb.fdb:40 as db

// Lager populasjon av personer som startet på videregående utdanning i 2022
create-dataset elever
import db/NUDB_AAR_NY_I_VID_UTD as regvgo
generate regår = int(regvgo/100)
keep if regår == 2022
tabulate regår

// Finner utdanningskode ved slutten av 2022 og kobler på populasjonsdatasettet
create-dataset kursdata
import db/NUDB_KURS_NUS 2022-12-31 as kurs2212
import db/NUDB_KURS_FNR as personid
destring kurs2212
collapse (max) kurs2212 -> høyeste_kode2212 (min) kurs2212 -> laveste_kode2212, by(personid)
merge høyeste_kode2212 laveste_kode2212 into elever

// Finner elever som tar ett vs flere studium ved slutten av 2022
use elever
generate kun_ett_studium = høyeste_kode2212 == laveste_kode2212
define-labels studiumlbl 0 'Tar flere studium' 1 'Tar ett studium'
assign-labels kun_ett_studium studiumlbl
piechart kun_ett_studium

// Lager oversikt over alle studier som populasjonen tar ved slutten av 2022
// Bruker en grovere inndeling pga. for mange koder med få observasjoner (2-sifret NUS-kode)
replace høyeste_kode2212 = int(høyeste_kode2212/10000)
tabulate høyeste_kode2212

```
