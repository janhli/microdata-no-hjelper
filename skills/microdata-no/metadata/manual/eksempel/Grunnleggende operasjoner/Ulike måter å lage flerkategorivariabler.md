<!-- Kilde: https://microdata.no/manual/eksempel/Grunnleggende%20operasjoner/Ulike%20m%C3%A5ter%20%C3%A5%20lage%20flerkategorivariabler -->

# Ulike måter å lage flerkategorivariabler

Koding av flerkategorivariabler kan gjøres på mange forskjellige måter. Den enkleste løsningen er å bruke kommandoene `generate` og `replace` for å kode en og en kategori. Denne fungerer fint ved få kategorier. Man starter da med å kode en utgangsverdi ved hjelp av `generate`, og benytter så `replace`-kommandoer for å moderere verdier basert på betingelser (én kommandolinje for hver verdi). Ulempen ved dette er at man risikerer å ende opp med mange kommandolinjer og lange skript som er ressurskrevende, og tar lang tid å kjøre.

Dersom man ønsker å kode mange kategorier, eventuelt bruke kompliserte betingelser, så anbefales det å benytte kommandoen `recode()`. Denne kan brukes til å sette opp alle kodebetingelsene i et enkelt kommandouttrykk, noe som gjør at skript blir mer komprimerte og raskere å kjøre. Gjennom `recode()` kan du blant annet angi verdi-intervaller og lage tilhørende verdi-labler (slik at du slipper å gjøre dette etterpå gjennom kommandoene `define-labels` og `assign-labels`).

Et tredje sett med hjelpemidler for å sette opp kodeuttrykk for flerkategorivariabler er funksjonene `inlist()` og `inrange()`. Disse er ideelle dersom man vil lage omfattende kodebetingelser, som oftest i kombinasjon med `generate` og `replace`, f.eks. dersom man vil lage en grov gruppering av kommuner, der man trenger å liste opp større sett med kommunekoder.

For deg som vil sette opp kodeuttrykk for mange kategorier, finnes det er fjerde alternativ: Automatisk generering av omkoding gjennom opplasting av skilletegnseparert omkodingsfil. For mer om dette, [klikk her](https://microdata.no/manual/brukermanual/Tilrettelegging%20av%20variabler/3.2.1%20Automatisk%20omkoding%20ved%20hjelp%20av%20opplasting%20av%20skilletegnseparerte%20filer).

Du finner mer informasjon om bruk av `generate`, `replace`, `recode()`, `inlist()`, `inrange()` og automatisk omkoding i [brukermanualen kapittel 3.1 – 3.2](https://microdata.no/manual/brukermanual/Tilrettelegging%20av%20variabler/3.1%20Opprettelse%20av%20nye%20variabler%20og%20omkoding%20-%20generate%E2%88%95replace).

Dette skriptet demonstrerer de ulike måtene å kode flerkategorivariabler på:

```
 require no.ssb.fdb:23 as ds

create-dataset demo

// Lage flere kategorier vha generate og replace
import ds/INNTEKT_BRUTTOFORM 2020-01-01 as formue

generate formueint = 1
replace formueint = 2 if formue > 500000
replace formueint = 3 if formue > 1000000
replace formueint = 4 if formue > 1500000

tabulate formueint

// Lage flere kategorier (verdensregioner) vha recode
create-dataset befolkning
import ds/BEFOLKNING_STATUSKODE 2021-01-01 as statuskode
keep if statuskode == '1'

import ds/BEFOLKNING_FODELAND as fødeland
tabulate fødeland

destring fødeland
recode fødeland \
    (111 120 138 139 140 148 155 156 159/164 = 2 'Europeiske land utenom EU') \
    (101/141 144/158 = 1 'EU/EØS') (203/393 = 3 'Afrika') \
    (143 404/578 = 4 'Asia med Tyrkia') \
    (612 684 = 5 'Nord-Amerika') \
    (601/775 = 6 'Sør- og Mellom-Amerika') \
    (802/840 = 7 'Oseania') \
    (980 = 8 'Statsløse') \
    (990 = 9 'Uoppgitt')
tabulate fødeland

// Lager kode for storby basert på kommunenumre til de fire største kommunene ved bruk av inlist()
import ds/BOSATTEFDT_BOSTED 2021-12-31 as kommune
generate storby = 0
replace storby = 1 if inlist(kommune,'0301','4601','1103','5001')
tabulate kommune if storby, rowsort()

// Grupperer årlig lønnsinntekt i seks grupper ved bruk av inrange()
import ds/INNTEKT_LONN 2021-12-31 as lønn

generate lønn_gr = 0
replace lønn_gr = 1 if inrange(lønn,1,200000)
replace lønn_gr = 2 if inrange(lønn,200001,400000)
replace lønn_gr = 3 if inrange(lønn,400001,600000)
replace lønn_gr = 4 if inrange(lønn,600001,800000)
replace lønn_gr = 5 if lønn > 800000

define-labels lønn_int \
    0 '0 kr' \
    1 '1 - 200 000 kr' \
    2 '200001 - 400 000 kr' \
    3 '400 001 - 600 000 kr' \
    4 '600 001 - 800 000 kr' \
    5 '800 000 kr ->'
assign-labels lønn_gr lønn_int
tabulate lønn_gr

// Alternativ måte å gruppere lønnsinntekt ved bruk av recode
replace lønn = 0 if sysmiss(lønn)
recode lønn (1/200000 = 1)(200001/400000 = 2)(400001/600000 = 3)(600001/800000 = 4)(800001/max = 5)
assign-labels lønn lønn_int
tabulate lønn

```
