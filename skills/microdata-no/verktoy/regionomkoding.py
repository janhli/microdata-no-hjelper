"""Lager microdata.no-linjer som koder kommune om til en regioninndeling (helseregion, politidistrikt osv.).

Bruker tabellene i metadata/regioner/ (se INDEX.csv for tilgjengelige inndelinger). Tabellene gjelder
kommuneinndelingen som står i metadata/regioner/HENTET (standard 2024). Har dataene eldre kommunenumre,
kjør først verktoy/kommuneomkoding.py.

Eksempler (fra prosjektmappen):
  python verktoy/regionomkoding.py helseregioner
  python verktoy/regionomkoding.py okonomiske_regioner --fra kommune --til okonreg
  python verktoy/regionomkoding.py --liste

Utskriften er en generate-linje og noen recode-linjer (verdien får regionnavnet som merkelapp). Kommunekoder
som ikke står i tabellen (gamle kommunenumre, 9999) står uendret. Kontroller med tabulate.

Innen én recode-kommando kjører reglene i rekkefølge, og verdier som allerede er omkodet påvirkes ikke av
senere regler. Det gjelder IKKE mellom kommandoer. Derfor kan oppdeling i flere kommandoer ikke kombineres
med en sluttregel (* = ...). Med --ukjent legges sluttregelen som siste regel i én samlet kommando.
Linjen blir da lang (2 800–4 700 tegn). microdata.no har godtatt 2 789 tegn (helseregioner, versjon 59).
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent / "metadata" / "regioner"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recode_regler import konflikter, recode_linjer  # noqa: E402


def raa_kommunekoder():
    """Alle koder BEFOLKNING_KOMMNR_FORMELL har hatt (første kodeliste + innsettinger), eller tomt sett."""
    fil = DIR.parent / "variabler" / "BEFOLKNING_KOMMNR_FORMELL.json"
    if not fil.exists():
        return set()
    koder = set()
    for p in json.loads(fil.read_text(encoding="utf-8"))["measureVariable"]["representedVariables"]:
        vd = p["valueDomain"]
        koder |= {c["code"] for c in vd.get("codeList", [])}
        koder |= {c["code"] for c in vd.get("delta", {}).get("insert", {}).values()}
    return koder


def les_indeks():
    with open(DIR / "INDEX.csv", encoding="utf-8", newline="") as f:
        return {r["inndeling"]: r for r in csv.DictReader(f, delimiter=";")}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inndeling", nargs="?", help="navn fra INDEX.csv, f.eks. helseregioner")
    ap.add_argument("--fra", default="kommune", help="variabelen med kommunenummer (streng), standard kommune")
    ap.add_argument("--til", help="ny variabel (standard: inndelingens navn)")
    ap.add_argument("--liste", action="store_true", help="vis tilgjengelige inndelinger")
    ap.add_argument("--ukjent", action="store_true",
                    help="sett kommunekoder som ikke står i tabellen til 'xxxx' (gir én lang recode-kommando)")
    a = ap.parse_args()

    if not DIR.exists():
        sys.exit("Mangler metadata/regioner/. Kjør først: python verktoy/hent_regioninndelinger.py")
    indeks = les_indeks()
    if a.liste or not a.inndeling:
        for slug, r in indeks.items():
            print(f"{slug:32} {r['antall_regioner']:>4} regioner  {r['beskrivelse']}  [{r['kilde']}]")
        return
    if a.inndeling not in indeks:
        sys.exit(f"Ukjent inndeling «{a.inndeling}». Bruk --liste.")

    til = a.til or a.inndeling
    regioner = defaultdict(list)
    navn = {}
    with open(DIR / f"{a.inndeling}.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            regioner[r["regionkode"]].append(r["kommunenr"])
            navn[r["regionkode"]] = r["regionnavn"].replace("'", "’")

    r = indeks[a.inndeling]
    hentet = (DIR / "HENTET").read_text(encoding="utf-8").strip()
    kart = {k: kode for kode, ks in regioner.items() for k in ks}
    konf = konflikter(kart)
    linjer = recode_linjer(til, kart, navn, sluttregel=("xxxx", "Ukjent region") if a.ukjent else None)

    print(f"// {r['beskrivelse']}. Kilde: {r['kilde']}, tabell: {r['tabell']}. Hentet {hentet}.")
    if konf and not a.ukjent:
        print(f"// {len(konf)} regionkoder er også kommunekoder. Disse reglene står samlet i første recode-kommando.")
    # En rå kommunekode som ikke omkodes, men som er lik en regionkode, blir umulig å skille fra regionen.
    tvetydige = sorted(set(regioner) & (raa_kommunekoder() - set(kart)))
    if tvetydige and not a.ukjent:
        print(f"// Advarsel: regionkoden {' '.join(tvetydige)} er også en kode i kommunevariabelen som ikke omkodes."
              " Personer med den kommunekoden ser ut som regionen. Bruk --ukjent, eller kontroller med tabulate.")
    print(f"// Forutsetter kommunenumre i samme kommuneinndeling som tabellen ({r['antall_kommuner']} kommuner).")
    if r["oversatt_fra_eldre_kommuneinndeling"] == "ja":
        print("// Tabellen er oversatt fra en eldre kommuneinndeling med Klass' kommuneendringer.")
    if a.ukjent:
        print("// Alt som ikke står i tabellen får 'xxxx'. Alle regler står i én lang kommando.")
    else:
        print("// Kommunekoder som ikke står i tabellen (gamle kommunenumre, 9999 osv.) står uendret. Kontroller med tabulate.")
    print(f"generate {til} = {a.fra}")
    for linje in linjer:
        print(linje)


if __name__ == "__main__":
    main()
