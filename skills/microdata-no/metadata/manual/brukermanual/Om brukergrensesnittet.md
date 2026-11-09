<!-- Kilde: https://microdata.no/manual/brukermanual/Om%20brukergrensesnittet/ -->

# 1. Om brukergrensesnittet

Microdata.no er et nettleserbasert analyseverktøy som baserer seg på en relativt enkel og intuitiv kommandostruktur. Det anbefales å bruke moderne versjoner av nettlesere som Chrome og Firefox eller tilsvarende for best mulig brukeropplevelse.

Innlogging i microdata.no gjøres via følgende nettside: [http://microdata.no/](http://microdata.no/)

Det som møter deg etter innlogging er en nettside bestående av et analyseområde, dvs. kommandovinduet (se kapittel 1.1). Dette brukes til å utforske variabler og teste ut kommandokjøringer:

En kan klikke på variabler for å gjøre seg kjent med innholdet, verdiformat, gyldighetsperiode m.m. Gjennom kommandoer som kjøres enkeltvis, kan variabler importeres til egne datasett for videre bearbeiding og analyser. I tillegg til deskriptive statistiske muligheter, kan en dessuten foreta avanserte statistiske operasjoner som regresjonsanalyser m.m. Se kapittel 1.1-1.4 for mer informasjon om hvordan jobbe i kommandovinduet.

**Etter å ha utforsket og gjort seg kjent med data en ønsker å benytte i analyser, anbefales det på det sterkeste å benytte skript-funksjonaliteten for å systematisere analysearbeidet.** Dette gjelder særlig om en har til hensikt å foreta en mer omfattende analyse (utover å bare lage enkel deskriptiv statistikk for et fåtall variabler). Bruk av skript har mange fordeler fremfor å utelukkende jobbe i kommandovinduet gjennom bruk av enkeltkommandoer:

1. En kan sette opp kommandosekvenser som kan kjøres i én operasjon. Resultatet av skriptkjøringer vises fortløpende etterhvert som kommandoer kjøres, og kjøringen stoppes dersom feil oppdages i skript (syntax- eller logiske feil)
1. Kommandosekvenser kan redigeres og kjøres på nytt
1. Mye enklere å identifisere hvor eventuelle feil oppstår i en lang rekke med kommandosekvenser
1. Fungerer som dokumentasjon/logg av arbeidet
1. Forskjellige arbeidsøkter kan lagres med egne navn og enkelt kalles frem fra en meny
1. Innholdet i et skript kan kopieres over til egne dokumenter for ekstra backup

Arbeid en allerede har utført i kommandovinduet kan enkelt overføres til et skript for videre redigering. Det kan gjøres på tre måter:

-

I skriptvinduet finnes det en menyknapp helt oppe til venstre. Der kan en velge "Nytt skript med historikk fra kommandolinjen". Husk å legge inn et navn på skriptet i linjen over skriptvinduet. Skriptet vil da lagres med dette navnet.

-

I kommandovinduet kan en skrive kommandoen `history`. Dette frembringer alle kommandoer en har kjørt i en enkelt liste som kan kopieres på vanlig måte ved å klikke på kopieringsknappen som vises når musepeker holdes over. Bruk så tastekombinasjonen CTRL + C og lim inn i et tomt skriptvindu. Husk også her å lage navn på skriptet, jfr. punktet over.

-

I kommandovinduet kan en skrive kommandoen `save` etterfulgt av et valgfritt navn som du bruker på skriptet. Navnet kan bestå av bokstaver, tall og "underscore" (`_`), og trenger ikke ha anførselstegn rundt, f.eks. `save Analyse_1`. Dersom du ønsker å bruke mellomrom eller andre tegn/symboler i navnet, må du bruke anførselstegn rundt navnet, f.eks. `save "Analyse 1 - utkast"`. Men da lagres skriptet med et navn der anførselstegnene blir en del av navnet. Disse kan du imidlertid fjerne fra skriptnavnet i linjen over skriptet ditt etterpå. Ved denne fremgangsmåten trenger du ikke lage navn på skriptet i skriptvinduet etterpå, siden det opprettes automatisk.

For mer informasjon om bruk av skript, se kapittel 1.5.
