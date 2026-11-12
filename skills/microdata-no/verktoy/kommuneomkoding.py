"""Lager recode-linjer som kode om gamle kommunenumre til inndelingen på et valgt tidspunkt.

Bygger på metadata/kommuneendringer.json (SSB Klass 131). Oppdater den med
verktoy/hent_kommuneendringer.py. Utskriften limes inn i et microdata.no-skript.

Eksempler (fra prosjektmappen):
  python verktoy/kommuneomkoding.py                          # 1989 -> 2024, variabel 'kommune'
  python verktoy/kommuneomkoding.py --fra 2015 --til 2024 --navn bosted
  python verktoy/kommuneomkoding.py --til 2020 --splitt forste

Hvordan det virker:
  * Hver kommunekode følges gjennom alle endringer i perioden. Kodene fra Klass-endringene er
    enten sammenslåinger (flere gamle koder -> én ny) eller delinger (én gammel kode -> flere nye).
  * Etter en deling i flere kommuner velges først kommunen med samme navn som kommunen koden
    startet som (f.eks. Haram -> Haram etter at Ålesund ble delt i 2024). Finnes ingen slik, velges
    kommunen som har samme navn som kommunen som ble delt (Ålesund -> Ålesund). Gjenstår flere
    kandidater, er koden en ekte deling som ikke kan løses uten adresse. Slike koder står
    uendret (--splitt behold) eller får første kandidat (--splitt forste).
  * Kommunene det omkodes til får navnet de har i inndelingen (merkelapp), så de nye kodene får navn
    også i gamle årganger, der kodelisten på datoen ikke har dem. --norske-navn tar bort samiske og
    kvenske navn (Hábmer - Hamarøy -> Hamarøy).
  * recode-linjene lages av verktoy/recode_regler.py. Er en kode både kilde og mål, samles de reglene
    i én kommando, så ingen verdi omkodes to ganger.
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "metadata" / "kommuneendringer.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recode_regler import konflikter, recode_linjer  # noqa: E402


def navnesett(n):
    """'Unjárga - Nesseby (…)' -> {'unjárga', 'nesseby'} for navnesammenligning."""
    return {x.strip().lower() for x in re.split(r"\s+-\s+|\(|\)", n) if x.strip()}


def norsk_navn(navn, d):
    """'Hábmer - Hamarøy' -> 'Hamarøy'. Velger delen som har vært hele navnet på en kommune i Klass-historikken
    (de fleste kommuner med samisk eller kvensk navn het tidligere bare det norske). Ellers siste del
    (Guovdageaidnu - Kautokeino)."""
    deler = navn.split(" - ")
    if len(deler) == 1:
        return navn
    enkle = {c["navn"] for c in d["koder_ved_fra"]}
    for e in d["endringer"]:
        enkle |= {e["gammelt_navn"], e["nytt_navn"]}
    treff = [x for x in deler if x in enkle]
    return treff[0] if treff else deler[-1]


def last():
    if not DATA.exists():
        sys.exit(f"Mangler {DATA}. Kjør først: python verktoy/hent_kommuneendringer.py")
    return json.loads(DATA.read_text(encoding="utf-8"))


def bygg(d, fra, til):
    """Returnerer (kart, delt, antatt): kart[kode] = mål-kode, delt[kode] = kandidater, antatt = valgt ved navn."""
    endr = [e for e in d["endringer"] if fra <= e["dato"] <= til]
    ved_start = {c["kode"]: c["navn"] for c in d["koder_ved_fra"]}

    # Alle koder som kan forekomme i perioden: gyldige ved start + koder opprettet av en endring
    opprettet = {}  # kode -> (dato, navn) første gang den dukker opp som ny kode
    for e in endr:
        if e["ny"] not in ved_start and e["ny"] not in opprettet:
            opprettet[e["ny"]] = (e["dato"], e["nytt_navn"])
    kandidater = {k: (None, n) for k, n in ved_start.items()}
    kandidater.update({k: v for k, v in opprettet.items() if k not in ved_start})

    per_dato = defaultdict(list)
    for e in endr:
        per_dato[e["dato"]].append(e)
    datoer = sorted(per_dato)

    kart, delt, antatt, helt, malnavn = {}, {}, {}, {}, {}
    for kode, (opprett, startnavn) in kandidater.items():
        tilstand = {kode: startnavn}  # kode -> navn nå
        brukt_navn = {}
        for dato in datoer:
            if opprett and dato <= opprett:
                continue
            ny = {}
            for s, snavn in tilstand.items():
                tr = [e for e in per_dato[dato] if e["gammel"] == s]
                if not tr:
                    ny[s] = snavn
                    continue
                maal = {e["ny"]: e["nytt_navn"] for e in tr}
                if len(maal) > 1:
                    # 1) kommunen som har samme navn som koden startet som
                    treff = [k for k, n in maal.items() if navnesett(n) & navnesett(startnavn)]
                    if len(treff) == 1:
                        if s == kode:
                            # Koden selv deles (f.eks. Ålesund 1507 i 2024): personer i de andre delene
                            # (Haram) følger med. Riktig ved grensejusteringer, ellers ikke.
                            helt[kode] = (dato, sorted(maal.items()), treff[0])
                        maal = {treff[0]: maal[treff[0]]}
                    else:
                        # 2) ellers kommunen som fortsetter med samme navn som den delte kommunen
                        treff = [k for k, n in maal.items() if navnesett(n) & navnesett(snavn)]
                        if len(treff) == 1:
                            maal = {treff[0]: maal[treff[0]]}
                            antatt[kode] = (dato, snavn, treff[0])
                ny.update(maal)
            tilstand = ny
        slutt = sorted(tilstand)
        if slutt == [kode]:
            continue
        if len(slutt) == 1:
            kart[kode] = slutt[0]
            malnavn[slutt[0]] = tilstand[slutt[0]]
            if kode in antatt and antatt[kode][2] != slutt[0]:
                antatt.pop(kode)
        else:
            antatt.pop(kode, None)
            helt.pop(kode, None)
            delt[kode] = (startnavn, [(k, tilstand[k]) for k in slutt])
    return kart, delt, antatt, kandidater, helt, malnavn


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fra", type=int, default=1989, help="første år i dataene (standard 1989)")
    ap.add_argument("--til", type=int, default=2024, help="inndelingen det skal omkodes til (standard 2024)")
    ap.add_argument("--navn", default="kommune", help="variabelnavn i skriptet (standard kommune)")
    ap.add_argument("--norske-navn", action="store_true",
                    help="bare norsk navn i merkelappene (Hamarøy, ikke Hábmer - Hamarøy)")
    ap.add_argument("--splitt", choices=["behold", "forste"], default="behold",
                    help="koder som er delt i flere kommuner: behold uendret, eller bruk første kandidat")
    a = ap.parse_args()

    d = last()
    if a.fra < int(d["fra"][:4]):
        sys.exit(f"--fra kan ikke være før {d['fra'][:4]}. Henter fra Klass er satt til {d['fra']}.")
    fra, til = f"{a.fra}-01-01", f"{a.til}-12-31"
    siste = max(e["dato"] for e in d["endringer"])
    if a.til > int(siste[:4]):
        print(f"// Advarsel: Klass-uttrekket (hentet {d['hentet']}) har ingen endringer etter {siste}.", file=sys.stderr)

    kart, delt, antatt, kand, helt, malnavn = bygg(d, fra, til)
    if a.norske_navn:
        malnavn = {k: norsk_navn(n, d) for k, n in malnavn.items()}
    if a.splitt == "forste":
        for k, (_, mal) in delt.items():
            kart[k] = mal[0][0]
            malnavn[mal[0][0]] = mal[0][1]

    out = []
    out.append(f"// Kommunenumre {a.fra} -> inndelingen {a.til}. Kilde: SSB Klass 131 (hentet {d['hentet']}).")
    out.append(f"// {len(kart)} koder omkodes til {len(set(kart.values()))} kommuner. Øvrige koder står uendret.")
    konf = konflikter(kart)
    if konf:
        out.append(f"// {len(konf)} koder er både kilde og mål. De står samlet i første recode-kommando. Ikke del den linjen.")
    if delt:
        out.append("// Delte kommuner (kan ikke løses uten adresse), "
                   + ("står uendret:" if a.splitt == "behold" else "satt til første kandidat:"))
        for k in sorted(delt):
            navn, mal = delt[k]
            out.append(f"//   {k} {navn} -> " + ", ".join(f"{m} {n}" for m, n in mal))
    if antatt:
        out.append("// Valgt ved navnesammenligning etter en deling (kontroller):")
        for k in sorted(antatt):
            dato, kilde, m = antatt[k]
            out.append(f"//   {k} {kand[k][1]}: {dato[:4]} delt av {kilde}, satt til {m}")
    if helt:
        out.append("// Koder som selv ble delt, satt til delen med samme navn. Personer i de andre delene kommer")
        out.append("// med (riktig ved grensejusteringer, ellers ikke). Bruk eldre koder eller adresse om det er viktig:")
        for k in sorted(helt):
            dato, deler, m = helt[k]
            out.append(f"//   {k} {kand[k][1]}: {dato[:4]} delt i " + ", ".join(f"{x} {n}" for x, n in deler)
                       + f", satt til {kart.get(k, m)}")
    out += recode_linjer(a.navn, kart, malnavn)
    print("\n".join(out))


if __name__ == "__main__":
    main()
