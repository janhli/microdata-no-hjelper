"""Sjekker at evalueringene henger sammen: kriteriene er merket, poengene viser til kriterier som finnes, og svarene
er lagret. Svarene fra runde 1 ble ikke lagret og kan ikke vurderes på nytt."""

import csv
import re
import subprocess
import sys
import unittest

from hjelp import SKILL

EVALS = SKILL.parent.parent / "evals"
RESULTATER = EVALS / "resultater"
UTEN_SVAR = {"runde1"}


def les_csv(fil):
    with open(fil, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def kriterier():
    return les_csv(EVALS / "kriterier.csv")


def poengfiler():
    return sorted(RESULTATER.glob("*/poeng.csv"))


class TestEvals(unittest.TestCase):
    def test_alle_kriteriene_er_merket(self):
        filer = {(f.parent.parent.name, f.name[:2]) for f in EVALS.glob("*/graders/*.md")}
        merket = {(k["oppgave"], k["nr"]) for k in kriterier() if not k["nr"].startswith("r1-")}
        self.assertEqual(filer, merket)
        self.assertLessEqual({k["krav"] for k in kriterier()}, {"", "fil", "verktoy"})

    def test_kriterier_som_nevner_verktoyene_er_merket(self):
        krav = {(k["oppgave"], k["nr"]): k["krav"] for k in kriterier()}
        for f in EVALS.glob("*/graders/*.md"):
            if "verktoy/" in f.read_text(encoding="utf-8"):
                with self.subTest(kriterium=f"{f.parent.parent.name}/{f.name}"):
                    self.assertEqual(krav[(f.parent.parent.name, f.name[:2])], "verktoy")

    def test_poengene_er_gyldige(self):
        kjente = {(k["oppgave"], k["nr"]) for k in kriterier()}
        self.assertGreaterEqual(len(poengfiler()), 2)
        for fil in poengfiler():
            rader = les_csv(fil)
            with self.subTest(runde=fil.parent.name):
                self.assertEqual([r for r in rader if (r["oppgave"], r["nr"]) not in kjente], [])
                self.assertLessEqual({r["poeng"] for r in rader}, {"0", "1"})
                nokler = [(r["oppgave"], r["nr"], r["betingelse"], r["kjoring"]) for r in rader]
                self.assertEqual(len(nokler), len(set(nokler)))

    def test_svarene_er_lagret(self):
        mangler = []
        for fil in poengfiler():
            if fil.parent.name in UTEN_SVAR:
                continue
            for o, b, k in sorted({(r["oppgave"], r["betingelse"], r["kjoring"]) for r in les_csv(fil)}):
                svar = fil.parent / "svar" / o / f"{b}-{k}.md"
                if not svar.exists():
                    mangler.append(svar.relative_to(EVALS).as_posix())
        self.assertEqual(mangler, [])

    def test_svarene_har_ikke_lokale_stier(self):
        for svar in RESULTATER.glob("*/svar/**/*.md"):
            with self.subTest(svar=svar.name):
                self.assertNotRegex(svar.read_text(encoding="utf-8"), re.compile(r"[A-Z]:[\\/]Users|/Users/|t3-thread|AppData", re.I))


class TestPoeng(unittest.TestCase):
    def kjor(self, *args):
        r = subprocess.run([sys.executable, "-I", str(EVALS / "poeng.py"), *args], capture_output=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_runde_1(self):
        ut = " ".join(self.kjor("runde1").split())
        # Alle kriterier, som i runde1.md
        self.assertIn("| med | 50/53 (94 %) |", ut)
        self.assertIn("| uten | 34/53 (64 %) |", ut)
        # Uten de fire som krever skillens verktøy (kommune 01, region 01, næring r1-01 og r1-02)
        self.assertIn("| med | 50/53 (94 %) | 46/49 (94 %) |", ut)
        self.assertIn("| uten | 34/53 (64 %) | 34/49 (69 %) |", ut)

    def test_oppgavene_vises(self):
        self.assertIn("| andregradsledd | 2/2 | 1/2 |", self.kjor("runde1"))

    def test_andre_agenter(self):
        ut = " ".join(self.kjor("7_14").split())
        self.assertIn("| codex | 7/7 (100 %) |", ut)
        self.assertIn("| copilot | 6/7 (86 %) |", ut)

    def test_spredning_mellom_kjoringer(self):
        sys.path.insert(0, str(EVALS))
        try:
            from poeng import spredning
        finally:
            sys.path.remove(str(EVALS))
        rad = {"oppgave": "a", "nr": "01", "betingelse": "med"}
        rader = [{**rad, "kjoring": "1", "poeng": "1"}, {**rad, "kjoring": "2", "poeng": "0"},
                 {**rad, "nr": "02", "kjoring": "1", "poeng": "1"}, {**rad, "nr": "02", "kjoring": "2", "poeng": "1"}]
        self.assertEqual(spredning(rader), "50–100 % i 2 kjøringer")
        self.assertEqual(spredning(rader[:1]), "1 kjøring")


if __name__ == "__main__":
    unittest.main()
