# kommune-2015-mot-2024: copilot, kjøring 1

- Modell: Copilot CLI 1.0.114, GPT-6 Luna
- Dato: 2026-11-23
- Skill: med, via `~/.agents/skills`

## Svar

Ferdig: `skript_kommune.txt` sammenligner folketallet 1.1.2015 og 1.1.2025, med 2015-kommunekodene omkodet til 2024-inndelingen. Skriptet viser folketall og endring i antall og prosent. Delte kommuner som Stokke, Snillfjord og Tysfjord kan ikke fordeles til dagens grenser uten adresseopplysninger; dette er forklart i skriptet. Jeg kunne ikke kjøre det inne i microdata.no.

- **Skill lastet:** `microdata-no`
- **Filer lest/søkt i:** `metadata/variabler.csv`, `kodesnutter/fylke.txt`, `referanser/fallgruver.md`, `metadata/manual/kommandoer_og_funksjoner/kommandoer.md`, `metadata/kommuneendringer.json` og kodesnutter søkt via `rg`.
- **Kommandoer/verktøy:** `kommuneomkoding.py --fra 2015 --til 2024 --navn kommune`; `rg`, `view`, `apply_patch`, PowerShell/Python for å sette inn de genererte omkodingsreglene og kontrollere skriptet.

## Skript

```
// Folketall per kommune 1.1.2015 og 1.1.2025, målt i 2024-inndelingen.
// Folketallet telles som antall bosatte med registrert kommune på datoen.
// Kommunekoder fra 2015 omkodes til dagens koder med SSB Klass 131.
// Variabel: BEFOLKNING_KOMMNR_FORMELL
// https://microdata.no/discovery/variable/no.ssb.fdb/60/BEFOLKNING_KOMMNR_FORMELL
//
// Begrensninger i omkodingen: 2015-kodene 0720 Stokke, 1613 og 5012 Snillfjord
// og 1850 Tysfjord ble delt og kan ikke fordeles til dagens kommuner uten adresse.
// De blir derfor stående uten omkoding; sammenligningen for kommunene som ble berørt,
// og totalsummen for 2015, vil mangle disse innbyggerne.

require no.ssb.fdb:60 as fdb

// --- Folketall 1.1.2015, omkodet til kommuneinndelingen fra 2024 ---
create-dataset telling2015
import fdb/BEFOLKNING_KOMMNR_FORMELL 2015-01-01 as kommune

// Recode-reglene er generert fra SSB Klass 131: fra 2015 til 2024.
// Ikke endre reglene enkeltvis; de må brukes samlet for å unngå dobbelt omkoding.
recode kommune ('1141' '1142' = '1103' 'Stavanger') ('1102' '1129' = '1108' 'Sandnes') ('1502' '1543' '1545' = '1506' 'Molde') ('1504' '1507' '1523' '1529' '1546' = '1508' 'Ålesund') ('1444' '1519' = '1577' 'Volda') ('1524' '1526' = '1578' 'Fjord') ('1548' '1551' = '1579' 'Hustadvika') ('1534' = '1580' 'Haram') ('1805' '1854' = '1806' 'Narvik') ('1849' = '1875' 'Hábmer - Hamarøy') ('0101' '3001' = '3101' 'Halden') ('0104' '0136' '3002' = '3103' 'Moss') ('0105' '3003' = '3105' 'Sarpsborg') ('0106' '3004' = '3107' 'Fredrikstad') ('0111' '3011' = '3110' 'Hvaler') ('0135' '3017' = '3112' 'Råde')
recode kommune ('0137' '3018' = '3114' 'Våler (Østfold)') ('0127' '3015' = '3116' 'Skiptvet') ('0122' '0123' '0124' '0125' '0138' '3014' = '3118' 'Indre Østfold') ('0128' '3016' = '3120' 'Rakkestad') ('0119' '3013' = '3122' 'Marker') ('0118' '3012' = '3124' 'Aremark') ('0219' '3024' = '3201' 'Bærum') ('0220' '0627' '0628' '3025' = '3203' 'Asker') ('0226' '0227' '0231' '3030' = '3205' 'Lillestrøm') ('0213' '0217' '3020' = '3207' 'Nordre Follo') ('0235' '3033' = '3209' 'Ullensaker') ('0216' '3023' = '3212' 'Nesodden') ('0215' '3022' = '3214' 'Frogn') ('0211' '3019' = '3216' 'Vestby')
recode kommune ('0214' '3021' = '3218' 'Ås') ('0229' '3028' = '3220' 'Enebakk') ('0230' '3029' = '3222' 'Lørenskog') ('0228' '3027' = '3224' 'Rælingen') ('0121' '0221' '3026' = '3226' 'Aurskog-Høland') ('0236' '3034' = '3228' 'Nes') ('0234' '3032' = '3230' 'Gjerdrum') ('0233' '3031' = '3232' 'Nittedal') ('0533' '3054' = '3234' 'Lunner') ('0532' '3053' = '3236' 'Jevnaker') ('0238' '3036' = '3238' 'Nannestad') ('0237' '3035' = '3240' 'Eidsvoll') ('0239' '3037' = '3242' 'Hurdal') ('0602' '0625' '0711' '3005' = '3301' 'Drammen') ('0604' '3006' = '3303' 'Kongsberg') ('0605' '3007' = '3305' 'Ringerike')
recode kommune ('0612' '3038' = '3310' 'Hole') ('0626' '3049' = '3312' 'Lier') ('0624' '3048' = '3314' 'Øvre Eiker') ('0623' '3047' = '3316' 'Modum') ('0622' '3046' = '3318' 'Krødsherad') ('0615' '3039' = '3320' 'Flå') ('0616' '3040' = '3322' 'Nesbyen') ('0617' '3041' = '3324' 'Gol') ('0618' '3042' = '3326' 'Hemsedal') ('0619' '3043' = '3328' 'Ål') ('0620' '3044' = '3330' 'Hol') ('0621' '3045' = '3332' 'Sigdal') ('0631' '3050' = '3334' 'Flesberg') ('0632' '3051' = '3336' 'Rollag') ('0633' '3052' = '3338' 'Nore og Uvdal') ('0402' = '3401' 'Kongsvinger') ('0403' = '3403' 'Hamar')
recode kommune ('0501' = '3405' 'Lillehammer') ('0502' = '3407' 'Gjøvik') ('0412' = '3411' 'Ringsaker') ('0415' = '3412' 'Løten') ('0417' = '3413' 'Stange') ('0418' = '3414' 'Nord-Odal') ('0419' = '3415' 'Sør-Odal') ('0420' = '3416' 'Eidskog') ('0423' = '3417' 'Grue') ('0425' = '3418' 'Åsnes') ('0426' = '3419' 'Våler (Innlandet)') ('0427' = '3420' 'Elverum') ('0428' = '3421' 'Trysil') ('0429' = '3422' 'Åmot') ('0430' = '3423' 'Stor-Elvdal') ('0432' = '3424' 'Rendalen') ('0434' = '3425' 'Engerdal') ('0436' = '3426' 'Tolga') ('0437' = '3427' 'Tynset') ('0438' = '3428' 'Alvdal') ('0439' = '3429' 'Folldal')
recode kommune ('0441' = '3430' 'Os') ('0511' = '3431' 'Dovre') ('0512' = '3432' 'Lesja') ('0513' = '3433' 'Skjåk') ('0514' = '3434' 'Lom') ('0515' = '3435' 'Vågå') ('0516' = '3436' 'Nord-Fron') ('0517' = '3437' 'Sel') ('0519' = '3438' 'Sør-Fron') ('0520' = '3439' 'Ringebu') ('0521' = '3440' 'Øyer') ('0522' = '3441' 'Gausdal') ('0528' = '3442' 'Østre Toten') ('0529' = '3443' 'Vestre Toten') ('0534' = '3446' 'Gran') ('0536' = '3447' 'Søndre Land') ('0538' = '3448' 'Nordre Land') ('0540' = '3449' 'Sør-Aurdal') ('0541' = '3450' 'Etnedal') ('0542' = '3451' 'Nord-Aurdal') ('0543' = '3452' 'Vestre Slidre')
recode kommune ('0544' = '3453' 'Øystre Slidre') ('0545' = '3454' 'Vang') ('0701' '3801' = '3901' 'Horten') ('0702' '0713' '0714' '0715' '3802' = '3903' 'Holmestrand') ('0704' '0716' '3803' = '3905' 'Tønsberg') ('0706' '0710' '0719' '3804' = '3907' 'Sandefjord') ('0709' '0712' '0728' '3805' = '3909' 'Larvik') ('0722' '0723' '0729' '3811' = '3911' 'Færder') ('0805' '3806' = '4001' 'Porsgrunn') ('0806' '3807' = '4003' 'Skien') ('0807' '3808' = '4005' 'Notodden') ('0811' '3812' = '4010' 'Siljan') ('0814' '3813' = '4012' 'Bamble') ('0815' '3814' = '4014' 'Kragerø') ('0817' '3815' = '4016' 'Drangedal')
recode kommune ('0819' '3816' = '4018' 'Nome') ('0821' '0822' '3817' = '4020' 'Midt-Telemark') ('0828' '3820' = '4022' 'Seljord') ('0827' '3819' = '4024' 'Hjartdal') ('0826' '3818' = '4026' 'Tinn') ('0829' '3821' = '4028' 'Kviteseid') ('0830' '3822' = '4030' 'Nissedal') ('0831' '3823' = '4032' 'Fyresdal') ('0833' '3824' = '4034' 'Tokke') ('0834' '3825' = '4036' 'Vinje') ('0901' = '4201' 'Risør') ('0904' = '4202' 'Grimstad') ('0906' = '4203' 'Arendal') ('1001' '1017' '1018' = '4204' 'Kristiansand') ('1002' '1021' '1029' = '4205' 'Lindesnes') ('1003' = '4206' 'Farsund') ('1004' = '4207' 'Flekkefjord')
recode kommune ('0911' = '4211' 'Gjerstad') ('0912' = '4212' 'Vegårshei') ('0914' = '4213' 'Tvedestrand') ('0919' = '4214' 'Froland') ('0926' = '4215' 'Lillesand') ('0928' = '4216' 'Birkenes') ('0929' = '4217' 'Åmli') ('0935' = '4218' 'Iveland') ('0937' = '4219' 'Evje og Hornnes') ('0938' = '4220' 'Bygland') ('0940' = '4221' 'Valle') ('0941' = '4222' 'Bykle') ('1014' = '4223' 'Vennesla') ('1026' = '4224' 'Åseral') ('1027' '1032' = '4225' 'Lyngdal') ('1034' = '4226' 'Hægebostad') ('1037' = '4227' 'Kvinesdal') ('1046' = '4228' 'Sirdal') ('1201' = '4601' 'Bergen') ('1401' '1439' = '4602' 'Kinn')
recode kommune ('1211' = '4611' 'Etne') ('1216' = '4612' 'Sveio') ('1219' = '4613' 'Bømlo') ('1221' = '4614' 'Stord') ('1222' = '4615' 'Fitjar') ('1223' = '4616' 'Tysnes') ('1224' = '4617' 'Kvinnherad') ('1227' '1228' '1231' = '4618' 'Ullensvang') ('1232' = '4619' 'Eidfjord') ('1233' = '4620' 'Ulvik') ('1234' '1235' = '4621' 'Voss') ('1238' = '4622' 'Kvam') ('1242' = '4623' 'Samnanger') ('1241' '1243' = '4624' 'Bjørnafjorden') ('1244' = '4625' 'Austevoll') ('1245' '1246' '1259' = '4626' 'Øygarden') ('1247' = '4627' 'Askøy') ('1251' = '4628' 'Vaksdal') ('1252' = '4629' 'Modalen') ('1253' = '4630' 'Osterøy')
recode kommune ('1256' '1260' '1263' = '4631' 'Alver') ('1264' = '4632' 'Austrheim') ('1265' = '4633' 'Fedje') ('1266' = '4634' 'Masfjorden') ('1411' = '4635' 'Gulen') ('1412' = '4636' 'Solund') ('1413' = '4637' 'Hyllestad') ('1416' = '4638' 'Høyanger') ('1417' = '4639' 'Vik') ('1418' '1419' '1420' = '4640' 'Sogndal') ('1421' = '4641' 'Aurland') ('1422' = '4642' 'Lærdal') ('1424' = '4643' 'Årdal') ('1426' = '4644' 'Luster') ('1428' = '4645' 'Askvoll') ('1429' = '4646' 'Fjaler') ('1430' '1431' '1432' '1433' = '4647' 'Sunnfjord') ('1438' = '4648' 'Bremanger') ('1441' '1443' = '4649' 'Stad')
recode kommune ('1445' = '4650' 'Gloppen') ('1449' = '4651' 'Stryn') ('1601' '1662' '5030' = '5001' 'Trondheim - Tråante') ('1702' '1724' '5004' '5039' = '5006' 'Steinkjer') ('1703' '1725' '1748' '5005' '5040' '5048' = '5007' 'Namsos - Nåavmesjenjaelmie') ('1620' = '5014' 'Frøya') ('1633' = '5020' 'Osen') ('1634' = '5021' 'Oppdal') ('1635' = '5022' 'Rennebu') ('1640' = '5025' 'Røros - Rosse') ('1644' = '5026' 'Holtålen') ('1648' = '5027' 'Midtre Gauldal') ('1653' = '5028' 'Melhus') ('1657' = '5029' 'Skaun') ('1663' = '5031' 'Malvik') ('1664' = '5032' 'Selbu') ('1665' = '5033' 'Tydal')
recode kommune ('1711' = '5034' 'Meråker') ('1714' = '5035' 'Stjørdal') ('1717' = '5036' 'Frosta') ('1719' = '5037' 'Levanger - Levangke') ('1721' = '5038' 'Verdal') ('1736' = '5041' 'Snåase - Snåsa') ('1738' = '5042' 'Lierne') ('1739' = '5043' 'Raarvihke - Røyrvik') ('1740' = '5044' 'Namsskogan') ('1742' = '5045' 'Grong') ('1743' = '5046' 'Høylandet') ('1744' = '5047' 'Overhalla') ('1749' = '5049' 'Flatanger') ('1755' = '5052' 'Leka') ('1756' = '5053' 'Inderøy') ('1624' '1718' = '5054' 'Indre Fosen') ('1571' '1612' '5011' = '5055' 'Heim') ('1617' '5013' = '5056' 'Hitra')
recode kommune ('1621' '1627' '5015' '5017' = '5057' 'Ørland') ('1630' '1632' '5018' '5019' = '5058' 'Åfjord') ('1622' '1636' '1638' '5016' '5023' '5024' = '5059' 'Orkland') ('1750' '1751' '5050' '5051' = '5060' 'Nærøysund') ('1567' = '5061' 'Rindal') ('1902' '5401' = '5501' 'Tromsø') ('1903' '5402' = '5503' 'Harstad - Hárstták') ('1911' '5411' = '5510' 'Kvæfjord') ('1852' '1913' '5412' = '5512' 'Dielddanuorri - Tjeldsund') ('1917' '5413' = '5514' 'Ibestad') ('1919' '5414' = '5516' 'Gratangen - Rivtták') ('1920' '5415' = '5518' 'Loabák - Lavangen') ('1922' '5416' = '5520' 'Bardu')
recode kommune ('1923' '5417' = '5522' 'Salangen') ('1924' '5418' = '5524' 'Målselv') ('1925' '5419' = '5526' 'Sørreisa') ('1926' '5420' = '5528' 'Dyrøy') ('1927' '1928' '1929' '1931' '5421' = '5530' 'Senja') ('1933' '5422' = '5532' 'Balsfjord') ('1936' '5423' = '5534' 'Karlsøy') ('1938' '5424' = '5536' 'Lyngen') ('1939' '5425' = '5538' 'Storfjord - Omasvuotna - Omasvuono') ('1940' '5426' = '5540' 'Gáivuotna - Kåfjord - Kaivuono') ('1941' '5427' = '5542' 'Skjervøy') ('1942' '5428' = '5544' 'Nordreisa - Ráisa - Raisi') ('1943' '5429' = '5546' 'Kvænangen') ('2012' '5403' = '5601' 'Alta')
recode kommune ('2004' '2017' '5406' = '5603' 'Hammerfest - Hámmerfeasta') ('2030' '5444' = '5605' 'Sør-Varanger') ('2003' '5405' = '5607' 'Vadsø') ('2021' '5437' = '5610' 'Kárášjohka - Karasjok') ('2011' '5430' = '5612' 'Guovdageaidnu - Kautokeino') ('2014' '5432' = '5614' 'Loppa') ('2015' '5433' = '5616' 'Hasvik') ('2018' '5434' = '5618' 'Måsøy') ('2019' '5435' = '5620' 'Nordkapp') ('2020' '5436' = '5622' 'Porsanger - Porsángu - Porsanki') ('2022' '5438' = '5624' 'Lebesby') ('2023' '5439' = '5626' 'Gamvik') ('2025' '5441' = '5628' 'Deatnu - Tana') ('2024' '5440' = '5630' 'Berlevåg')
recode kommune ('2028' '5443' = '5632' 'Båtsfjord') ('2002' '5404' = '5634' 'Vardø') ('2027' '5442' = '5636' 'Unjárga - Nesseby')

collapse (count) kommune -> folketall2015, by(kommune)

// --- Folketall 1.1.2025, allerede på dagens kommuneinndeling ---
create-dataset telling2025
import fdb/BEFOLKNING_KOMMNR_FORMELL 2025-01-01 as kommune
collapse (count) kommune -> folketall2025, by(kommune)

// Koble 2015-tallene til kommunene som hadde innbyggere 1.1.2025.
use telling2015
merge folketall2015 into telling2025 on kommune
use telling2025

generate endring = folketall2025 - folketall2015
generate endring_prosent = 100 * endring / folketall2015 if !sysmiss(folketall2015) & folketall2015 > 0

textblock
# Bosatte per kommune 1.1.2015
Kommunekodene fra 2015 er omkodet til 2024-inndelingen. Tallene er antall personer.
Noen 2015-koder kan ikke fordeles på dagens kommuner; se merknaden øverst i skriptet.
endblock
tabulate kommune, summarize(folketall2015) sum

textblock
# Bosatte per kommune 1.1.2025
Tallene er antall personer bosatt i kommunen 1. januar 2025.
endblock
tabulate kommune, summarize(folketall2025) sum

textblock
# Endring i antall bosatte fra 1.1.2015 til 1.1.2025
Viser differansen i antall personer per kommune. Manglende 2015-tall betyr at ingen 2015-rad ble koblet til; se begrensningene øverst.
endblock
tabulate kommune, summarize(endring) sum

textblock
# Prosentvis endring i folketall fra 1.1.2015 til 1.1.2025
Prosentvis endring relativt til 2015. Mangler når 2015-tallet mangler eller er null.
endblock
tabulate kommune, summarize(endring_prosent) mean

citation
```
