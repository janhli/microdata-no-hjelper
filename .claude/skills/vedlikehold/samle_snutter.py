"""Setter sammen kodesnuttene til ett testskript for microdata.no.

Hver snutt tas med ordrett, men uten toppkommentar og require. Etter hver snutt slettes datasettene den
har laget, så neste snutt kan bruke samme navn (personer, barn, mor). Snutter som allerede er testet med
gjeldende versjon hoppes over, med mindre de nevnes eksplisitt.

  python .claude/skills/vedlikehold/samle_snutter.py > testskript.txt
  python .claude/skills/vedlikehold/samle_snutter.py alder.txt mor_barn.txt > testskript.txt
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

ROT = Path(__file__).resolve().parents[3]
SNUTTER = ROT / "skills" / "microdata-no" / "kodesnutter"
DATALAGER = ROT / "skills" / "microdata-no" / "metadata" / "datalager.json"

# Enkle og sikre først, utkast og de mest sammensatte sist (en feil stopper resten av skriptet)
REKKEFOLGE = ["alder", "innvandringskategori", "landbakgrunn_region", "samlivsstatus", "arbeidsstyrkestatus",
              "utdanningsniva", "mal_analyse", "forlop_til_person", "mor_barn", "verdi_ved_hendelse",
              "lavinntekt_eu60", "sektor_lonnstakere", "lavinntekt_vedvarende"]


def status(tekst):
    m = re.search(r"^// Status:\s*(.+)$", tekst, re.M)
    return m.group(1).strip() if m else "ukjent"


def tittel(tekst):
    for linje in tekst.splitlines()[1:]:
        if linje.startswith("// ") and not linje.startswith("// ="):
            return linje[3:].strip()
    return ""


def kode(tekst):
    """Alt etter toppkommentaren, uten require."""
    linjer = tekst.splitlines()
    slutt = max(i for i, l in enumerate(linjer[:80]) if l.startswith("// ====="))
    return [l for l in linjer[slutt + 1:] if not l.startswith("require ")]


def main():
    versjon = json.loads(DATALAGER.read_text(encoding="utf-8"))["versions"][0]["version"].split(".")[0]
    valgt = sys.argv[1:]
    filer = {p.stem: p for p in SNUTTER.glob("*.txt")}
    navn = [n.removesuffix(".txt") for n in valgt] or [n for n in REKKEFOLGE if n in filer] + sorted(set(filer) - set(REKKEFOLGE))

    deler = []
    for n in navn:
        tekst = filer[n].read_text(encoding="utf-8")
        st = status(tekst)
        if not valgt and st.startswith("testet (") and f"fdb:{versjon}," in st:
            continue  # allerede testet frittstående med gjeldende versjon
        deler.append((n, tekst, st))

    sys.stdout.reconfigure(encoding="utf-8")
    print(f"// Samlet testskript for {len(deler)} kodesnutter, laget {date.today().isoformat()} av samle_snutter.py.")
    print("// Kjør hele skriptet. Stopper det med feil, noter snutten (overskriften «Snutt N») og feilmeldingen.")
    print(f"require no.ssb.fdb:{versjon} as fdb\n")
    print("textblock")
    print(f"# Test av {len(deler)} kodesnutter, no.ssb.fdb:{versjon}")
    print("Hver snutt kjøres ordrett etter hverandre, og datasettene slettes mellom dem. En snutt er bestått når")
    print("den kjører uten feil og tabellene ser rimelige ut (ingen tomme kategorier som skulle hatt innhold).")
    print("endblock\n")
    for i, (n, tekst, st) in enumerate(deler, 1):
        linjer = kode(tekst)
        alt = "\n".join(linjer)
        datasett = list(dict.fromkeys(re.findall(r"^[ \t]*create-dataset[ \t]+(\S+)", alt, re.M)
                                      + re.findall(r"^[ \t]*clone-dataset[ \t]+\S+[ \t]+(\S+)", alt, re.M)))
        slettet = set(re.findall(r"^[ \t]*delete-dataset[ \t]+(\S+)", alt, re.M))
        print(f"// {'=' * 69}\n// Snutt {i}: {n}.txt\n// {'=' * 69}")
        print("textblock")
        print(f"# Snutt {i}/{len(deler)}: {n}.txt")
        print(f"{tittel(tekst)}. Status før test: {st}.")
        print("endblock")
        print("\n".join(linjer).strip())
        rest = [d for d in datasett if d not in slettet and not d.startswith("$")]
        if rest and i < len(deler):
            print("\n// Rydd før neste snutt")
            for d in rest:
                print(f"delete-dataset {d}")
        print()


if __name__ == "__main__":
    main()
