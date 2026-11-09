# Kodesnutter for microdata.no

Gjenbrukbare biter med fast format og kjent teststatus. Hver snutt er **frittstående**: den har
`require`, oppretter sitt eget datasett og kan limes rett inn i microdata.no for å prøves.

## Statusnivåer

| Status | Betyr |
|---|---|
| `testet` | Kjørt uten feil i microdata.no, med versjonen og datoen som står i toppseksjonen |
| `testet i større skript` | Logikken er kjørt som del av en større analyse, men den frittstående versjonen er ikke kjørt alene |
| `utkast` | Ikke kjørt. Syntaks og koder er sjekket mot manual og kodelister |

Når datalageret får ny versjon, blir status stående, men versjonen i toppseksjonen viser hvor gammel
testen er. Kjør snutten på nytt og oppdater linjen når du har gjort det.

## Oversikt

| Fil | Hva den gir | Status |
|---|---|---|
| [mal_analyse.txt](mal_analyse.txt) | Skjelett for et helt analyseskript med `textblock`-titler | testet i større skript |
| [alder.txt](alder.txt) | Alder som i Statistikkbanken, og aldersgrupper | testet i større skript |
| [innvandringskategori.txt](innvandringskategori.txt) | Innvandrer / norskfødt med innvandrerforeldre / øvrige | testet i større skript |
| [landbakgrunn_region.txt](landbakgrunn_region.txt) | Landbakgrunn gruppert i verdensregioner | testet i større skript |
| [utdanningsniva.txt](utdanningsniva.txt) | Høyeste fullførte utdanning, seks nivåer (NUS) | testet i større skript |
| [arbeidsstyrkestatus.txt](arbeidsstyrkestatus.txt) | Prioritert arbeidsstyrkestatus i åtte grupper | testet i større skript |
| [samlivsstatus.txt](samlivsstatus.txt) | Gift / samboer / enslig / bor hos foreldre | testet i større skript |
| [lavinntekt_eu60.txt](lavinntekt_eu60.txt) | Flagg for lavinntekt (EU-60) med egen medianberegning | testet i større skript |
| [verdi_ved_hendelse.txt](verdi_ved_hendelse.txt) | Verdi av en variabel året før en hendelse (f.eks. fødsel) | testet i større skript |
| [mor_barn.txt](mor_barn.txt) | Koble barn til mor, og telle barn per mor | testet i større skript |
| [forlop_til_person.txt](forlop_til_person.txt) | Første start og siste stopp i et forløp, per person | testet i større skript |

## Ønskeliste (bidra gjerne)

- Kommunenummer fra alle regionreformene omkodet til gjeldende inndeling (hele landet)
- Fylke med navn (2024-inndeling)
- Familietype og husholdningstype
- Pendling (bosted mot arbeidssted)
- Tilknytning til arbeid, utdanning og velferd (NEET)
- Sysselsetting fra a-ordningen med statsborgerskap

## Format

Kopier toppseksjonen fra en eksisterende snutt. Den skal ha tittel, status, variabler med kilde-URL,
hva snutten lager, og fallgruver. Se [CONTRIBUTING.md](../../../CONTRIBUTING.md).
