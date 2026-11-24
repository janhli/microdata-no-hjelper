"""Sjekker at TESTLISTE.md (åpne punkter) og TESTLOGG.md (avklarte) henger sammen.

Numrene er felles for de to filene. En henvisning som «TESTLOGG 8.12» må peke på filen raden står i. Testskriptene
og evals er historikk og beholder «TESTLISTE», men numrene må finnes.
"""

import re
import unittest

from hjelp import SKILL

ROT = SKILL.parent.parent
FILER = {navn: ROT / f"{navn}.md" for navn in ("TESTLISTE", "TESTLOGG")}
RAD = re.compile(r"^\| (\d+\.\d+) \|(.*)$", re.MULTILINE)
NR = r"\d+\.\d+"
HENVISNING = re.compile(rf"\b(TESTLISTE|TESTLOGG)(?:\.md)?`?\]?(?:\([^)\s]*\))?\s+({NR}(?:(?:,\s*|\s+og\s+|–){NR})*)")
DEL = re.compile(r"\b(TESTLISTE|TESTLOGG)(?:\.md)?`?\]?(?:\([^)\s]*\))?\s+del\s+(\d+)")


def les(fil):
    return fil.read_text(encoding="utf-8")


def rader(navn):
    return RAD.findall(les(FILER[navn]))


def flat(tekst):
    """Uten linjeskift og kommentartegn, så en henvisning delt over to linjer finnes."""
    return re.sub(r"\s*\n\s*(?://|#|[-*>])?\s*", " ", tekst)


def filer():
    monstre = ["*.md", "skills/microdata-no/*.md", "skills/microdata-no/referanser/*.md",
               "skills/microdata-no/kodesnutter/*", "skills/microdata-no/verktoy/*.py", "arkiv/**/*", "tests/*.py",
               ".claude/skills/**/*.md", ".claude/skills/**/*.py", ".github/**/*.py", ".github/**/*.yml"]
    ut = {f for m in monstre for f in ROT.glob(m) if f.is_file()}
    return sorted(ut - {ROT / "tests" / "test_testliste.py"})


class TestTestliste(unittest.TestCase):
    def test_avklarte_punkter_staar_i_loggen(self):
        self.assertEqual([nr for nr, tekst in rader("TESTLISTE") if "~~" in tekst or "✓" in tekst], [])
        self.assertEqual([nr for nr, tekst in rader("TESTLOGG") if "~~" not in tekst or "Avklart" not in tekst], [])
        self.assertGreater(len(rader("TESTLOGG")), 90)

    def test_numrene_er_unike(self):
        numre = [nr for navn in FILER for nr, _ in rader(navn)]
        self.assertEqual(sorted({nr for nr in numre if numre.count(nr) > 1}), [])

    def test_henvisninger_peker_paa_riktig_fil(self):
        plass = {nr: navn for navn in FILER for nr, _ in rader(navn)}
        deler = {navn: set(re.findall(r"^## (\d+)\.", les(fil), re.MULTILINE)) for navn, fil in FILER.items()}
        feil, antall = [], 0
        for f in filer():
            tekst = flat(les(f))
            for navn, numre in HENVISNING.findall(tekst):
                for nr in re.findall(NR, numre):
                    antall += 1
                    if plass.get(nr) != navn:
                        feil.append(f"{f.relative_to(ROT)}: {navn} {nr} (står i {plass.get(nr)})")
            feil += [f"{f.relative_to(ROT)}: {navn} del {d}" for navn, d in DEL.findall(tekst) if d not in deler[navn]]
        self.assertEqual(feil, [], "\n".join(feil))
        self.assertGreater(antall, 40)

    def test_numrene_i_testskriptene_finnes(self):
        alle = {nr for navn in FILER for nr, _ in rader(navn)}
        feil = [f"{f.name}: {nr}" for f in sorted((ROT / ".claude/skills/vedlikehold/testskript").glob("*.txt"))
                for _, numre in HENVISNING.findall(flat(les(f))) for nr in re.findall(NR, numre) if nr not in alle]
        self.assertEqual(feil, [])


if __name__ == "__main__":
    unittest.main()
