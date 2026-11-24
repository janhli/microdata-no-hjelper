"""Summerer poengene i en evalueringsrunde, med og uten kriteriene som krever noe bare skillen har.

  python evals/poeng.py            alle rundene
  python evals/poeng.py runde1     én runde

Leser resultater/<runde>/poeng.csv og kriterier.csv. Kriterier merket `verktoy` kan ikke oppfylles uten skillen
(de krever et av verktøyene i den). Kriterier merket `fil` viser til filer i skillen, men kan oppfylles med
det samme oppslaget på nettet.
"""

import csv
import sys
from pathlib import Path

EVALS = Path(__file__).resolve().parent


def les_csv(fil):
    with open(fil, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def poeng(rader):
    return sum(int(r["poeng"]) for r in rader), len(rader)


def vis(rader):
    sum_, antall = poeng(rader)
    return f"{sum_}/{antall} ({100 * sum_ / antall:.0f} %)" if antall else "–"


def spredning(rader):
    """Laveste og høyeste andel når hver kjøring regnes for seg. Med én kjøring vet vi ikke hvor mye som er støy."""
    kjoringer = sorted({r["kjoring"] for r in rader})
    if len(kjoringer) == 1:
        return "1 kjøring"
    andeler = []
    for k in kjoringer:
        sum_, antall = poeng([r for r in rader if r["kjoring"] == k])
        andeler.append(100 * sum_ / antall)
    return f"{min(andeler):.0f}–{max(andeler):.0f} % i {len(kjoringer)} kjøringer"


def skriv(runde, krav):
    rader = les_csv(EVALS / "resultater" / runde / "poeng.csv")
    betingelser = list(dict.fromkeys(r["betingelse"] for r in rader))

    def uten(fjern):
        return [r for r in rader if krav[(r["oppgave"], r["nr"])] not in fjern]

    utvalg = [rader, uten({"verktoy"}), uten({"verktoy", "fil"})]
    print(f"## {runde}\n")
    print("| Betingelse | Alle kriterier | Uten `verktoy` | Uten `verktoy` og `fil` | Spredning |")
    print("|---|---|---|---|---|")
    for b in betingelser:
        deler = [[r for r in u if r["betingelse"] == b] for u in utvalg]
        print(f"| {b} | {' | '.join(vis(d) for d in deler)} | {spredning(deler[0])} |")
    print(f"\n| Oppgave | {' | '.join(betingelser)} |")
    print("|---|" + "---|" * len(betingelser))
    for o in dict.fromkeys(r["oppgave"] for r in rader):
        celler = [poeng([r for r in rader if r["oppgave"] == o and r["betingelse"] == b]) for b in betingelser]
        print(f"| {o} | {' | '.join(f'{s}/{n}' for s, n in celler)} |")
    print()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    krav = {(k["oppgave"], k["nr"]): k["krav"] for k in les_csv(EVALS / "kriterier.csv")}
    finnes = sorted(f.parent.name for f in (EVALS / "resultater").glob("*/poeng.csv"))
    for runde in sys.argv[1:] or finnes:
        if runde not in finnes:
            sys.exit(f"finner ikke resultater/{runde}/poeng.csv. Rundene som finnes: {', '.join(finnes)}")
        skriv(runde, krav)


if __name__ == "__main__":
    main()
