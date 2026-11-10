"""Tester recode-utskriften fra recode_regler.py, kommuneomkoding.py og regionomkoding.py (uten nett).

Utskriften kjøres med simulatoren i recode_regler.py, som følger manualens beskrivelse av recode. Om
microdata.no faktisk oppfører seg slik, er punkt 1.9 i TESTLISTE.md.
"""

import csv
import unittest

from hjelp import METADATA, avvik, kjor, recode_linjer_i, simuler, tiltenkt
from recode_regler import MAKS_TEGN, konflikter, q, recode_linjer


def utfall(tekst, *verdier):
    return dict(zip(verdier, simuler(recode_linjer_i(tekst), list(verdier))))


class LinjelengdeMixin:
    def sjekk_linjelengde(self, tekst):
        """Vanlige linjer holder seg under MAKS_TEGN. Bare konfliktkommandoen (første linje) kan være lengre."""
        linjer = recode_linjer_i(tekst)
        kart, slutt = tiltenkt(linjer)
        if slutt is not None:
            self.assertEqual(len(linjer), 1, "med sluttregel skal alt stå i én kommando")
            return
        start = 1 if konflikter(kart) else 0
        for linje in linjer[start:]:
            regler = linje.split(" ", 2)[2]
            self.assertLessEqual(len(regler), MAKS_TEGN, linje[:120])


class TestRecodeRegler(unittest.TestCase, LinjelengdeMixin):
    KART = {"a": "b", "b": "c", "p": "q", "q": "p", "x": "y", "z": "z",
            **{f"k{i:03d}": f"r{i % 7}" for i in range(200)}}

    def test_kjede_bytte_identitet_med_smale_linjer(self):
        tekst = "\n".join(recode_linjer("v", self.KART, maks_tegn=80))
        self.assertEqual(avvik(tekst), [])
        self.assertNotIn("'z' = 'z'", tekst)
        self.assertEqual(utfall(tekst, "a", "b", "p", "q"), {"a": "b", "b": "c", "p": "q", "q": "p"})

    def test_konfliktregler_i_forste_kommando(self):
        linjer = recode_linjer("v", self.KART, maks_tegn=80)
        for kode in ("'a'", "'b'", "'p'", "'q'"):
            self.assertIn(kode, linjer[0])
        for linje in linjer[1:]:
            for kode in ("'a'", "'b'", "'p'", "'q'"):
                self.assertNotIn(kode, linje)

    def test_sluttregel_gir_en_kommando_med_stjerne_sist(self):
        linjer = recode_linjer("v", self.KART, sluttregel=("xxxx", "Ukjent"))
        self.assertEqual(len(linjer), 1)
        self.assertTrue(linjer[0].endswith("(* = 'xxxx' 'Ukjent')"))
        self.assertEqual(avvik("\n".join(linjer)), [])

    def test_simulatoren_gjenkjenner_sluttregel_i_egen_kommando(self):
        gammel = recode_linjer("v", {"a": "b"}) + ["recode v (* = 'xxxx')"]
        self.assertEqual(simuler(gammel, ["a"]), ["xxxx"])

    def test_simulatoren_gjenkjenner_kjede_over_kommandoer(self):
        delt = ["recode v ('a' = 'b')", "recode v ('b' = 'c')"]
        self.assertEqual(simuler(delt, ["a"]), ["c"])

    def test_linjelengde(self):
        self.sjekk_linjelengde("\n".join(recode_linjer("v", self.KART)))

    def test_merkelapp_bare_paa_forste_bit_og_apostrof_byttes(self):
        kart = {f"k{i:02d}": "m" for i in range(30)}
        linjer = recode_linjer("v", kart, {"m": "Jan's"})
        tekst = " ".join(linjer)
        self.assertEqual(tekst.count("'Jan’s'"), 1)
        self.assertEqual(q("a'b"), "'a’b'")

    def test_tomt_kart(self):
        self.assertEqual(recode_linjer("v", {}), [])
        self.assertEqual(recode_linjer("v", {"a": "a"}, sluttregel=("x", "")), ["recode v (* = 'x')"])


class TestKommuneomkoding(unittest.TestCase, LinjelengdeMixin):
    def test_varianter(self):
        for args in [(), ("--fra", "2015"), ("--til", "2020"), ("--til", "2026"), ("--splitt", "forste")]:
            with self.subTest(args=args):
                tekst = kjor("kommuneomkoding.py", *args)
                self.assertEqual(avvik(tekst), [])
                self.sjekk_linjelengde(tekst)

    def test_kjente_omkodinger(self):
        tekst = kjor("kommuneomkoding.py")
        ut = utfall(tekst, "0301", "3001", "1534", "1523", "1529", "1546", "0114", "0720", "1850", "9999", "3000")
        self.assertEqual(ut["0301"], "0301")  # Oslo er uendret
        self.assertEqual(ut["3001"], "3101")  # Halden: Viken -> Østfold
        self.assertEqual(ut["1534"], "1580")  # Haram
        for kode in ("1523", "1529", "1546"):  # Ørskog, Skodje, Sandøy -> Ålesund
            self.assertEqual(ut[kode], "1508")
        for kode in ("0114", "0720", "1850", "9999", "3000"):  # delte kommuner og spesialkoder
            self.assertEqual(ut[kode], kode)
        self.assertIn("0114 Varteig", tekst)

    def test_splitt_forste_omkoder_delte(self):
        ut = utfall(kjor("kommuneomkoding.py", "--splitt", "forste"), "0720")
        self.assertNotEqual(ut["0720"], "0720")


class TestRegionomkoding(unittest.TestCase, LinjelengdeMixin):
    @classmethod
    def setUpClass(cls):
        cls.inndelinger = [l.split()[0] for l in kjor("regionomkoding.py", "--liste").splitlines() if l.strip()]

    def test_alle_inndelinger_med_og_uten_ukjent(self):
        self.assertGreaterEqual(len(self.inndelinger), 11)
        for inn in self.inndelinger:
            for args in [(inn,), (inn, "--ukjent")]:
                with self.subTest(args=args):
                    tekst = kjor("regionomkoding.py", *args)
                    self.assertEqual(avvik(tekst), [])
                    self.sjekk_linjelengde(tekst)

    def test_alle_kommuner_i_tabellen_faar_region(self):
        for inn in self.inndelinger:
            with self.subTest(inndeling=inn):
                with open(METADATA / "regioner" / f"{inn}.csv", encoding="utf-8", newline="") as f:
                    rader = list(csv.DictReader(f, delimiter=";"))
                ut = utfall(kjor("regionomkoding.py", inn), *[r["kommunenr"] for r in rader])
                for r in rader:
                    self.assertEqual(ut[r["kommunenr"]], r["regionkode"], r["kommunenr"])

    def test_ukjent_gir_xxxx_for_resten(self):
        ut = utfall(kjor("regionomkoding.py", "helseregioner", "--ukjent"), "0301", "9999", "0101")
        self.assertEqual(ut["0301"], "H12")
        self.assertEqual(ut["9999"], "xxxx")
        self.assertEqual(ut["0101"], "xxxx")

    def test_advarsel_naar_regionkode_er_kommunekode(self):
        self.assertIn("Advarsel: regionkoden 0300", kjor("regionomkoding.py", "barnevernsregioner"))
        self.assertNotIn("Advarsel", kjor("regionomkoding.py", "helseregioner"))


if __name__ == "__main__":
    unittest.main()
