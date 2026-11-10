"""Felles bygging av recode-linjer for verktøyene i verktoy/.

Semantikken i microdata.no (manualen, kommandoen recode): innen ÉN recode-kommando kjøres reglene i
rekkefølge, og en verdi som allerede er omkodet påvirkes ikke av senere regler i samme kommando. Mellom
kommandoer gjelder ikke dette: en senere kommando ser resultatet av den forrige.

Derfor:
  * Regler der kilden er mål for en annen regel, eller målet er kilde for en annen regel, samles i én
    kommando. Ellers kan en verdi omkodes to ganger (f.eks. 25.300 -> 25.400 og deretter 25.400 -> 25.500).
  * En sluttregel (* = ...) må stå sist i samme kommando som alle de andre reglene. Med sluttregel blir
    det derfor én kommando.
  * Øvrige regler kan trygt deles på flere kommandoer, så linjene ikke blir for lange.
  * Regler som ikke endrer noe (kode = samme kode) utelates.

simuler() gjør det samme som microdata.no etter denne beskrivelsen, og brukes til å teste utskriften.
Atferden er bekreftet i microdata.no (versjon 59, november 2026, TESTLISTE 1.1, 1.2 og 1.9).

Avsløringskontrollen stopper en recode-kommando hvis én målverdi treffer 1–9 enheter (0 er greit).
Det kan ikke sjekkes her, så detaljerte omkodinger kan måtte kjøres flere ganger med koden fra
feilmeldingen tatt ut.
"""

import re
from collections import defaultdict

MAKS_KODER = 25  # kildekoder per regel
MAKS_TEGN = 600  # omtrentlig makslengde på vanlige recode-linjer. microdata.no har godtatt 2 789 tegn (v59, 2026-11)


def q(tekst):
    """Streng i enkle anførselstegn. Apostrof i teksten byttes med ’."""
    return "'" + str(tekst).replace("'", "’") + "'"


def konflikter(kart):
    """Kilder som må stå i samme kommando som reglene de henger sammen med."""
    kilder, mal = set(kart), set(kart.values())
    return {k for k, m in kart.items() if k in mal or m in kilder}


def _regler(kart, merkelapper, maks_koder):
    per_mal = defaultdict(list)
    for k, m in kart.items():
        per_mal[m].append(k)
    regler = []
    for m in sorted(per_mal):
        kilder = sorted(per_mal[m])
        for i in range(0, len(kilder), maks_koder):
            bit = " ".join(q(k) for k in kilder[i : i + maks_koder])
            lab = f" {q(merkelapper[m])}" if i == 0 and merkelapper.get(m) else ""
            regler.append(f"({bit} = {q(m)}{lab})")
    return regler


def _pakk(regler, maks_tegn):
    linjer, naa = [], ""
    for regel in regler:
        if naa and len(naa) + 1 + len(regel) > maks_tegn:  # + 1 for mellomrommet
            linjer.append(naa)
            naa = ""
        naa = f"{naa} {regel}" if naa else regel
    if naa:
        linjer.append(naa)
    return linjer


def recode_linjer(variabel, kart, merkelapper=None, sluttregel=None, maks_koder=MAKS_KODER, maks_tegn=MAKS_TEGN):
    """Lager recode-linjer for variabel.

    kart: {kildekode: målkode}. merkelapper: {målkode: tekst}. sluttregel: (målkode, tekst) for (* = ...).
    Returnerer en liste med linjer som starter med «recode <variabel>».
    """
    merkelapper = merkelapper or {}
    kart = {k: m for k, m in kart.items() if k != m}
    if sluttregel:
        regler = _regler(kart, merkelapper, maks_koder)
        mal, tekst = sluttregel
        regler.append(f"(* = {q(mal)}{' ' + q(tekst) if tekst else ''})")
        return [f"recode {variabel} " + " ".join(regler)] if regler else []

    konf = konflikter(kart)
    linjer = []
    if konf:
        felles = {k: m for k, m in kart.items() if k in konf}
        linjer.append(" ".join(_regler(felles, merkelapper, maks_koder)))
    resten = {k: m for k, m in kart.items() if k not in konf}
    linjer += _pakk(_regler(resten, merkelapper, maks_koder), maks_tegn)
    return [f"recode {variabel} {l}" for l in linjer]


REGEL = re.compile(r"\(([^()]*?) = '([^']*)'(?: '[^']*')?\)")


def simuler(linjer, verdier):
    """Kjører recode-linjene på en liste verdier slik manualen beskriver det. Returnerer ny liste."""
    ut = list(verdier)
    for linje in linjer:
        if not linje.startswith("recode "):
            continue
        regler = [(venstre.strip(), mal) for venstre, mal in REGEL.findall(linje)]
        ny = []
        for v in ut:
            for venstre, mal in regler:
                if venstre == "*" or f"'{v}'" in venstre.split():
                    v = mal
                    break
            ny.append(v)
        ut = ny
    return ut
