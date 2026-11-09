<!-- Kilde: https://microdata.no/manual/eksempel/Sammensatte%20operasjoner/Bruke%20bindinger%20og%20l%C3%B8kker -->

# Bruke bindinger og løkker

Bindinger og løkker kan brukes til å generalisere og komprimere lange skript med gjentakende struktur. For eksempel om man vil kjøre noen identiske sett med operasjoner flere ganger, kan dette generaliseres ved å opprette en løkke (loop). Bindinger opprettes gjennom kommandoen `let` mens løkker lages med kommandoen `for`

Dette skriptet gir en detaljert introduksjon til hvordan dette fungerer. Det anbefales å kjøre skriptet for å se på resultatene og virkemåten knyttet til kommandoene.

```
 textblock
# Introduksjon til ny funksjonalitet: Bindinger og løkker
endblock
require no.ssb.fdb:26 as f
create-dataset ds

textblock
# Bindinger

Bindinger er lokale verdier som lagres i klienten med `let`. Verdiene kan enten brukes lokalt, eller settes inn i
uttrykk før de sendes til analyse.

Bindinger lager i praksis globale variabler man kan referere til på tvers av datasett, og kan være nyttige til å
generalisere et skript.

Man kan f.eks. gjøre et skript tidsuavhengig ved å lage en let-binding som inneholder et årstall. I stedet for å angi de
konkrete årstallet alle steder i et skript, brukes i stedet bindingen. Om man senere vil kjøre skriptet på en ny årgang,
trenger man bare endre verdien på bindingen (og man slipper å gå gjennom hele skriptet for å endre på årstall).

Bruk `help let` for den fulle syntaksbeskrivelsen.

Man kan binde til både strenger og tall:
endblock
let string = "foo"
let totusen = 2000

textblock
Matematiske uttrykk kan også brukes i bindinger
endblock
let approx_pi = 22/7

textblock
Funksjoner som opererer kun på bindinger, kalt `prosedyrer` kan også brukes. Bruk `help-procedure` for å se listen av disse
endblock

let pi = pi()
let en = cos(2 * pi())

textblock
Den nye operatoren, `++` konkatenerer strenger sammen med hverandre, eller med tall. Merk at tall + streng = streng.
endblock
let dato = 2000 ++ "-01-01"

textblock
For å referere til en eksisterende binding settes et `$`-tegn foran:
endblock
let totusen_verdi = $totusen
let startdato = $totusen ++ "-01-01"

textblock
Man kan også sette en binding til et symbol. Dette er et konkret objekt som man senere vil referere til, vanligvis en variabel.
Det trenger ikke nødvendigvis være en eksisterende variabel, men kan settes inn i et uttrykk hvor variabelen skal genereres.

Symboler skal ikke angis med fnutter slik som strenger.

Eksempel:
endblock
let siv = sivstand

textblock
Symboler kan også konkateneres i uttrykk
endblock
let totusen_symbol = to ++ tusen

textblock
Symboler i bindinger kan altså brukes slik. Dette importerer variabelen til symbolet pekt på av bindingen `$siv`, som er `sivstand`
endblock
import f/SIVSTANDFDT_SIVSTAND $startdato as $siv

textblock
Merk over at bindinger gitt til datovariabelen i import-kommandoer håndteres spesielt.
De lagres som en streng og blir konvertert til en dato-verdi når de brukes her.

NB: Bindinger kan trykkes på i grensesnittet for å få opp et vindu som viser opphavet til bindingen. Prøv med
`$startdato` i resultatvinduet eller i datasettdetaljene. Om bindingen er avledet fra en annen binding, som `$totusen`,
kan denne videre trykkes på for å se dens opphav.
endblock

textblock
# Løkker

Løkker er en måte å kjøre en kommando på flere ganger, hvor verdien i en eller flere gitte bindinger endrer seg for hver
iterasjon. I løkkehodet setter man en iterator som vil oppføre seg akkurat som let-bindingene.
Forskjellen er at man kan definere flere verdier som vil brukes etter hverandre.

Bruk `help for` for den fulle syntaksbeskrivelsen
endblock

for iterator in 1 2 3
  let double = $iterator * 2
end

textblock
Frem til løkken er lukket er dette ekvivalent med `let iterator = 1`.
Når `end` kjøres, eksekveres så alle kommandoene inne i løkken for de resterende iteratorene 2 og 3.

Dette lar deg kjøre den første iterasjonen av løkken og se resultatene før du kjører de resterende iterasjonene.
Dette kan være nyttig når du utvikler er skript og vil sjekke at du får riktige/forventede resultater fra
kostnadskrevende operasjoner.

Prøv dette ved å enten sette et breakpoint på kommandoen inne i løkka (klikke på margen eller `alt+enter` når linjen er
valgt), eller ved å eksekvere stegene én etter én i kommandolinja.
endblock

textblock
Man kan definere iteratorverdiene på to måter: som en liste med tall, strenger og/eller symboler (som over), eller ved
et __numerisk__ verdiområde `fra : til` (inklusiv)
endblock

for iterator in 1:3
  let double = $iterator * 2
end

textblock
Bindingene som skapes inne i løkken er lokale for iterasjonen og forsvinner etterpå.
Variabler som skapes inn det aktuelle datasettet vil eksistere etter løkken.

Dette er for å f.eks kunne importere variabler slik som dette:
endblock

for år in 2000 : 2002
  let siv_dato = $år ++ "-01-01"
  let siv_år = siv_ ++ $år
  import f/SIVSTANDFDT_SIVSTAND $siv_dato as $siv_år
end

textblock
Å importere variabler over flere år er et vanlig brukstilfelle for løkker.

Men å angi en dato med spesifiserte datoer og måneder kan være tungvint å gjøre programatisk.
Vi tilbyr derfor prosedyren `date_fmt` for å gjøre dette enklere.
endblock

let dt1 = date_fmt(2000)
let dt2 = date_fmt(2000, 10)
let dt3 = date_fmt(2000, 10, 20)

textblock
Det kan bli mange midlertidige bindinger i løkker. I løkke-eksempelet over brukes dessuten `siv_dato` og `siv_år` kun én gang.
Man også benytte bindings-uttrykk inne i selve kommandoen for å slippe slike midlertidige bindinger. Det er forskjellige
måter hvordan dette kan gjøres:

1) I uttrykk hvor det genereres en ny variabel, kan denne spesifiseres med et bindings-uttrykk direkte. Dette gjelder
`import`, `generate` og flere. Se etter `name` i kommandoparameterene i hjelpeteksten.

Altså tilsvarer denne import-setningen den vi definerte i løkken over:
endblock
let år = 2000
import f/SIVSTANDFDT_SIVSTAND 2000-01-01 as siv_inline ++ $år

textblock
2) Dato-uttrykket i en importsetning behandles spesielt slik at du kan bruke enten en dato (som vanlig), en binding (som
vist over), eller en prosedyre direkte. Dette legger først og fremst til rette for å bruke `date_fmt`-prosedyren til å
angi en dato direkte. import-setningen over kan da forenkles til
endblock
import f/SIVSTANDFDT_SIVSTAND date_fmt(2000) as siv_proc ++ $år

textblock
3) I generelle uttrykk, som i `generate` eller etter `if` kan ikke bindingene benyttes fritt slik som i `name`.
Det er fordi det ikke er mulig å skille mellom hva som skal gjelde for bindingen og hva som gjelder for uttrykket i seg selv.

Operatoren `++` er derimot spesiell siden den kun er definert for bindinger. `++` vil derfor bli evaluert selv om vi er
inne i et annet uttrykk.
endblock
generate gift = 1 if siv_ ++ $år + 2 == "1"

textblock
Merk at `++` har lavere presedens enn `+` og `-`. Det betyr at

`siv_ ++ $år + 2 == 1`

er det samme som

`(siv_ ++ ($år + 2)) == 1`.

Vær obs på dette om du faktisk vil bruke variabelen i et matematisk uttrykk.

Om du f.eks vil legge 1 til alle variabler med navnet `siv_ ++ $år` må dette gjøres slik:

`(siv_ ++ $år) + 1`
endblock

textblock
Bruken av disse to teknikkene gir oss da den kortere løkkevarianten:
endblock
for år in 2000 : 2002
  import f/SIVSTANDFDT_SIVSTAND date_fmt($år) as inline_siv ++ $år
end

textblock
Det er lurt å tenke seg om ved bruk av inline-bindinger, da koden kan bli vanskeligere å lese ved overdreven bruk. Under
skrivingen av disse i kommando-linjen vil heller ikke feilmeldingene bli like gode siden det er vanskeligere å samsvare
med det evaluerte uttrykket med hvor det skal puttes inn.

Navngitte bindinger med `let` er også nyttige til å angi intensjonen med verdien direkte i programmet, spesielt om
verdien er knyttet til en konstant verdi som kommer utenfra systemet.
endblock

textblock
## Eksempel

Et typisk eksempel på bruk av bindinger og løkker der man importerer av et sett med variabler målt over flere år, for et
tilfeldig utvalg av bosatte individer i en gitt aldergruppe:
endblock

let start_år = 2020
let start_dato = date_fmt($start_år + 1)

let minalder = 40
let maxalder = 50

create-dataset totalpop
import f/BEFOLKNING_FOEDSELS_AAR_MND as faarmnd
sample 0.1 12345
generate alder = $start_år - int(faarmnd/100)

import f/BEFOLKNING_STATUSKODE $start_dato as regstat

keep if regstat == '1' & alder >= $minalder & alder <= $maxalder
histogram alder, discrete freq

textblock
Variant 1
Her er alle bindinger angitt eksplisitt
endblock
for år in 2016 : 2020
  let dato = date_fmt($år, 12, 31)
  let yy = $år - 2000
  let var = lønn ++ $yy
  import f/INNTEKT_LONN $dato as $var
end

textblock
Variant 2
Her angis alle bindingene på samme linje.
Det gir et kortere skript, men kan være vanskeligere å forstå
endblock
for år in 2016 : 2020
  import f/INNTEKT_LONN date_fmt($år, 12, 31) as lønn ++ $år - 2000 ++ "_2"
end

textblock
Foreløpig er det ikke mulig å lage bindinger som består av lister av symboler (variabler), f.eks. `let vars = kjønn
alder utdanning`. Dette er under utvikling
endblock

textblock
## Viderekommende løkker

Løkker kan også iterere over flere verdier, nøste over flere verdier, eller begge to samtidig.
Dette oppnås med en generator-syntaks.

Iterere over flere verdier: Om man f.eks vil importere en menge av datoer og gi de navn som ikke kan avledes av årstallet:
endblock

for år, sivnavn in 2000 : 2002, første andre tredje
  import f/SIVSTANDFDT_SIVSTAND date_fmt($år) as $sivnavn
end

textblock
Nøstede løkker: Om du har lyst til å gjøre dette flere ganger for å generere like variabler med andre navn.
Dette er det samme som å nøste løkken etter `;` inne i løkken foran.
Dette vil da iterere over verdiene 2000 og første, 2000 og andre, 2001 og første, osv.:
endblock

for år in 2000 : 2002; sivnavn in første andre
  import f/SIVSTANDFDT_SIVSTAND date_fmt($år) as $sivnavn ++ $år ++ nøstet
end

textblock
Disse to teknikkene kan kombineres for å iterere over flere verdier i en nøstet løkke:
endblock

for år, farge in 2000 : 2002, blå gul grønn; sivnavn in første andre
  import f/SIVSTANDFDT_SIVSTAND date_fmt($år) as $sivnavn ++ $år ++ $farge
end

```
