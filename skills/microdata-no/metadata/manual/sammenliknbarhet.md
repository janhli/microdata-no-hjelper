<!-- Kilde: https://microdata.no/manual/sammenliknbarhet -->

# Årsaker til avvik mellom tall fra microdata.no og SSBs statistikk

Tall man lager i microdata.no skal som hovedregel være relativt like tallene man finner på SSBs statistikksider, deriblant Statistikkbanken. Men det er sjeldent at tallene blir helt identiske. Dette har flere årsaker:

- Datakilden har mye å si for avvikene. Data man importerer fra de ulike registrene har ulike grader av avvik sammenliknet med offisiell SSB-statistikk.
- Forskjellige datakilder gir også forskjellige tall. Dette finnes ulike kilder til statistikk - derfor er det viktig at man sammenlikner data hentet fra de samme datakildene.
- Ulike måletidspunkt: Noen statistikker bruker årstall, kvartalstall, månedstall m.m., mens andre bruker statustall målt ved gitte datoer, f.eks. per 1/1, 31/12 eller referanseuken med datoen 16/11. Derfor er det viktig at man bruker samme måleperiode/-tidspunkt når man sammenlikner tall.
- Ulike populasjoner: Ofte gjøres det valg knyttet til populasjonen som brukes for den aktuelle statistikken. Dette må man ta hensyn til når man skal lage statistikk i microdata.no med hensikt å reprodusere offisielle SSB-tall. F.eks. kan det gjøres aldersavgrensninger eller valg knyttet til bosattstatus (kun permament bosatte eller alle bosatte inkludert personer med Dnr).
- Forskjeller i produksjon/tilrettelegging (på tross av samme datakilde): Selv om man sammenlikner tall hentet fra samme datakilde/register, kan det være avvik i tallene som skyldes at SSB foretar konsistensbehandling/"rensing" av dataene. Det er ikke nødvendigvis slik at det er disse ferdige produksjonsfilene man importerer og jobber med i microdata.no
- Personvernfilter i microdata.no støylegger frekvenser og sensurerer ekstremverdier: Blant de ulike personvernfiltrene som brukes i microdata.no, er det særlig støyfilteret og sensureringen av ekstremverdier (winsorisering) som kan bidra til avvik i tallene sammenliknet med offisiell statistikk. Støyfilteret bidrar riktignok med en usikkerhet på kun +/- 5 (+/- 10 når man måler differansen mellom to tall), så for store tall har ikke dette så mye å si. Men winsoriseringen vil kunne påvirke gjennomsnittsverdier, standardavvik og min-/max-verdier man lager gjennom bl.a. kommandoene tabulate og summarize. Graden av avvik kommer an på verdifordelingen. Jo mer normalfordelte tallen er, jo mindre blir avvikene.

**Metoder for å finne årsak til avvik**

- Sjekk "Om statistikken" for den aktuelle SSB-statistikken. Du vil finne en slik statistikkomtale for alle SSBs statistikker, deriblant hvilken populasjon som er benyttet, hvordan dataene er blitt konsistensbehandlet, eller om det er andre forhold som kan påvirke tallene. Ofte finner man en del relevant informasjon direkte knyttet til SSB-statistikken (bl.a. i tabelltittelen og i fotnoten).
- Sjekk variabelbeskrivelsen til den aktuelle variabelen du bruker til å lage statistikken din i microdata.no. Der finner du som regel en beskrivelse av populasjonsavgrensningen for denne variabelen m.m. Dette bør samsvare med SSB.
- Pass særlig på at du har valgt samme type aldersavgrensning, valg av permanent bosatte (alle med fnr) vs. alle bosatte (fnr og dnr), måletidspunkt/-periode, og geografiske avgrensning.
- Ikke sammenlikne "epler og pærer": SSB har ofte forskjellige varianter av den samme typen statistikk, som baserer seg på forskjellige datakilder. Det kan være lurt å forsikre seg om at man sammenlikner microdata.no-tallene med de tilsvarende SSB-tallene laget ved bruk av samme type datamateriale.

Du finner mer informasjon om dette temaet i kursmaterialet for temakurset "Jobbe med data du ikke ser" (siste halvdel):

 ⊳\rhd⊳ [Powerpoint-presentasjon](https://www.microdata.no/wp-content/uploads/2022/10/2022-10-19_temakurs_microdata.no_dataduikkeser.pdf)

 ⊳\rhd⊳ [Videoinnspilt kurs](https://vimeo.com/808207827)
