<!-- Kilde: https://microdata.no/manual/systemendringer -->

# Systemendringer som kan påvirke resultater

Reproduserbare resultater har vært sentralt i utviklingen av microdata.no. [Innebygget dataversjonering](https://www.microdata.no/wp-content/uploads/2022/02/FAIR_Data_Versioning_in_Microdata.pdf) er blant virkemidlene for å oppnå dette. Omfattende testbatterier som sørger for at oppdateringer av underliggende biblioteker og komponenter ikke gir endringer i analyseresultater er et annet viktig tiltak.

I visse tilfeller er det imidlertid ikke mulig å unngå endringer som påvirker resultater/analyser. Endringer i konfidensialiseringsmekanismene er én type systemendring som kan føre til at nye kjøringer av eldre skript gir litt andre resultater enn før.

Vi dokumenterer her systemendringer som gir endrede resultater.

## 2025-10-01

### Kaplan-meier-grafer vises ikke lenger

Kaplan-Meier-grafer fremstiller faktiske endringer i overlevelsesrater (og ikke estimerte). Det har i enkelte situasjoner vist seg å være vanskelig å beskytte personvernet optimalt uten å støylegge endringene i overlevelsesratene som tegnes i grafen. Men det har også vist seg vanskelig å støylegge disse endringene uten å introdusere for stor usikkerhet mtp tolkning av Kaplan-Meier-grafene, fordi støyleggingen har en kumulativ effekt over tidsperioden. Vi har derfor valgt å fjerne den grafiske fremstillingen for kommandoen `kaplan-meier`. De mindre detaljerte hovedtallene under grafen beholdes og kan brukes som før. For kommandoen `weibull` baserer de genererte overlevelsesgrafene seg på estimerte/predikerte overlevelsesrater (med utgangspunkt i de faktiske observasjoner), og personvernutfordringene er vesentlig mindre. Om det viktigste for deg er å lage grafiske fremstillinger av overlevelsesrater, anbefaler vi derfor å benytte kommandoen `weibull`. Merk at hovedtallene hentes ut fra den estimerte grafen, og at tallene derfor har en viss unøyaktighet i forhold til det `kaplan-meier` rapporterer. Om korrekte tall er det viktigste, anbefaler vi å bruke `kaplan-meier` som fortsatt produserer en tabell. De to kommandoene kan også kombineres. Men da må det tas forbehold om at weibull-grafene er basert på estimater, og ikke de observerte endringene.

## 2025-04-23

### Endring: Persentiler beregnes på en ny måte

Persentil-resultater fra kommandoene `summarize`, `tabulate, summarize()`, `boxplot`, `collapse` og `aggregate` er endret etter innføring av tiltak 10 (mikroaggregering + glatting av persentiler).

## 2025-04-04

### Endring: Histogram har ny implementasjon

Kommandoen `histogram` er endret og har nå bl.a. samme støylegging som tabuleringer og vanlige søylediagrammer.

## 2024-08-19

### Endring: Barchart (søylediagram) er strammet opp og utvidet

Kommandoen `barchart` har frem til denne datoen hatt en del logiske problemer og inkonsistent virkemåte.

Dette er det nå ryddet opp i. For visse eldre skript som inkluderte `barchart` kan endringen medføre endret output eller feilmelding.

Det vil i de fleste slike tilfeller være kurant å justere kommandoen noe, og få bedre og mer forståelige søylediagrammer.

## 2024-06-18

### Endring: Winsorisering ved collapse til ikke-pseudonymisert variabel

Dersom mål-enhetstypen til `collapse()` (angitt i `by()`-leddet) er en enhetstype gitt ved en vanlig ikke-pseudonymisert variabel, f.eks. kommune, fylke, næringstype, eller utdanningsnivå, vil beregninger gjort gjennom `collapse()` være gjenstand for samme winsorisering som for deskriptiv statistikk utført på standard pseudonymiserte enhetstyper som f.eks. personid og familieid.

Mer informasjon om winsorisering [her](https://microdata.no/manual/konfidensialitet#tiltak-2-winsorisering).
