<!-- Kilde: https://microdata.no/manual/eksempel/Grunnleggende%20operasjoner/Lage%20dummyvariabel -->

# Lage dummyvariabel

Dummyvariabler blir mye brukt i forbindelse med blant annet regresjonsanalyser. Disse må være numeriske og dessuten ta verdiene 0 og 1.

```
 // Kobler til databank
require no.ssb.fdb:32 as db

textblock
Eksempel 1:
Koding av dummyen "mann" - tradisjonell metode: Først settes alle verdier til 0.
Kommandoen `replace` erstatter så verdien 0 med 1 der hvor variabelen kjønn har verdien "1".
endblock

create-dataset demografidata1
import db/BEFOLKNING_KJOENN as kjønn

// Lager en dummyvariabel som angir mann ut i fra variabelen kjønn
generate mann = 0
replace mann = 1 if kjønn == '1'

tabulate mann

textblock
Eksempel 2:
Koding av dummyen "mann" - komprimert metode: Ved å sette opp uttrykket på en spesifikk måte, kan du gjøre alt i ett
steg ved kommandoen `generate`. Verdien 1 gis til observasjoner som tilfredsstiller betingelsen man setter. Den andre
verdien (0) settes automatisk for alle observasjoner som *ikke* tilfredsstiller betingelsen. Dermed slipper man å kode i
to operasjoner, og man unngår dessuten å kode missingverdier om til 0.
endblock

create-dataset demografidata2
import db/BEFOLKNING_KJOENN as kjønn

// Lager en dummyvariabel som angir mann ut i fra variabelen kjønn
generate mann = kjønn == '1'

tabulate mann

```
