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
Linjen blir da lang (flere tusen tegn), og det er ikke prøvd om microdata.no tåler det.
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent / "metadata" / "regioner"
MAKS_KODER = 25  # kommunekoder per regel
MAKS_TEGN = 600  # omtrentlig makslengde på en recode-linje


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
    # En regel per region. Store regioner deles i biter på ``MAKS_KODER`` koder, og merkelappen settes
    # bare på første bit (samme verdi, så senere biter arver den).
    regler = []
    for kode in sorted(regioner):
        kommuner = sorted(regioner[kode])
        for i in range(0, len(kommuner), MAKS_KODER):
            bit = " ".join(f"'{k}'" for k in kommuner[i : i + MAKS_KODER])
            merkelapp = f" '{navn[kode]}'" if i == 0 else ""
            regler.append(f"({bit} = '{kode}'{merkelapp})")
    # Oppdeling i flere recode-kommandoer er bare trygg når ingen regionkode også er en kommunekode:
    # en senere kommando ville da omkodet verdier den tidligere kommandoen allerede har satt.
    alle_kommuner = {k for ks in regioner.values() for k in ks}
    overlapp = sorted(set(regioner) & alle_kommuner)
    # En sluttregel (* = ...) må stå i SAMME kommando som de andre reglene. I en egen kommando treffer
    # den alle verdier, også regionkodene som allerede er satt.
    en_kommando = a.ukjent or bool(overlapp)
    if overlapp and not a.ukjent:
        print(f"// Advarsel: regionkodene {' '.join(overlapp)} er også kommunekoder. Alle regler er derfor samlet i én kommando.",
              file=sys.stderr)

    if en_kommando:
        if a.ukjent:
            regler.append("(* = 'xxxx' 'Ukjent region')")
        linjer = [" ".join(regler)]
    else:
        linjer, naa = [], ""
        for regel in regler:
            if naa and len(naa) + len(regel) > MAKS_TEGN:
                linjer.append(naa)
                naa = ""
            naa = f"{naa} {regel}" if naa else regel
        if naa:
            linjer.append(naa)

    print(f"// {r['beskrivelse']}. Kilde: {r['kilde']}, tabell: {r['tabell']}. Hentet {hentet}.")
    print(f"// Forutsetter kommunenumre i samme kommuneinndeling som tabellen ({r['antall_kommuner']} kommuner).")
    if r["oversatt_fra_eldre_kommuneinndeling"] == "ja":
        print("// Tabellen er oversatt fra en eldre kommuneinndeling med Klass' kommuneendringer.")
    if a.ukjent:
        print("// Alt som ikke står i tabellen får 'xxxx'. Alle regler står i én lang kommando (ikke prøvd mot lengdegrense).")
    else:
        print("// Kommunekoder som ikke står i tabellen (gamle kommunenumre, 9999 osv.) står uendret. Kontroller med tabulate.")
    print(f"generate {til} = {a.fra}")
    for linje in linjer:
        print(f"recode {til} {linje}")


if __name__ == "__main__":
    main()
