"""Tester recode-utskriften fra recode_regler.py, kommuneomkoding.py og regionomkoding.py (uten nett).

Utskriften kjøres med simulatoren i recode_regler.py, som følger manualens beskrivelse av recode. Om
microdata.no faktisk oppfører seg slik, er punkt 1.9 i TESTLISTE.md.
"""

import csv
import re
import subprocess
import sys
import unittest

from hjelp import METADATA, VERKTOY, avvik, kjor, recode_linjer_i, simuler, tiltenkt
from kommuneomkoding import koder_ved, last
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

    def test_fra_tar_med_koder_opprettet_etter_1989(self):
        # Før: startkodene var alltid 1989-kodene, så --fra 2019 lot 25 koder stå uendret (Klæbu, Sarpsborg ...)
        tekst = kjor("kommuneomkoding.py", "--fra", "2019")
        ut = utfall(tekst, "5030", "0105", "0710", "1903")
        self.assertEqual(ut, {"5030": "5001", "0105": "3105", "0710": "3907", "1903": "5503"})
        # Generelt: en kode som er gyldig ved --fra, ender likt som når man starter i 1989
        standard = kjor("kommuneomkoding.py")
        for aar in ("2002", "2013", "2018", "2019", "2020"):
            with self.subTest(fra=aar):
                koder = sorted(koder_ved(last(), f"{aar}-01-01"))
                fra_aar = utfall(kjor("kommuneomkoding.py", "--fra", aar), *koder)
                self.assertEqual({k: v for k, v in fra_aar.items() if v != utfall(standard, k)[k]}, {})

    def test_maalkodene_faar_navn_fra_inndelingen(self):
        # Nye koder står ellers uten navn i gamle årganger (TESTLISTE 2.8)
        tekst = kjor("kommuneomkoding.py")
        for regel in ("= '1108' 'Sandnes')", "= '1580' 'Haram')", "= '3101' 'Halden')", "= '1508' 'Ålesund')"):
            self.assertIn(regel, tekst)
        self.assertIn("= '3905' 'Tønsberg')", kjor("kommuneomkoding.py", "--splitt", "forste"))

    def test_norske_navn_uten_samiske_og_kvenske(self):
        tekst = kjor("kommuneomkoding.py", "--norske-navn")
        recode = "\n".join(l for l in tekst.splitlines() if l.startswith("recode"))
        self.assertNotIn(" - ", recode)
        for regel in ("= '1875' 'Hamarøy')", "= '5001' 'Trondheim')", "= '5540' 'Kåfjord')",
                      "= '5612' 'Kautokeino')", "= '5636' 'Nesseby')"):
            self.assertIn(regel, recode)
        self.assertIn("= '1875' 'Hábmer - Hamarøy')", kjor("kommuneomkoding.py"))  # standard: Klass-navnet

    def test_varsler_naar_koden_selv_ble_delt(self):
        # 1507 Ålesund (2020–2023) omfatter Haram, som ble skilt ut i 2024 (TESTLISTE 2.4)
        tekst = kjor("kommuneomkoding.py")
        self.assertEqual(utfall(tekst, "1507")["1507"], "1508")
        varsel = tekst.split("selv ble delt")[1].split("\nrecode")[0]
        self.assertIn("1507 Ålesund: 2024 delt i 1508 Ålesund, 1580 Haram, satt til 1508", varsel)
        self.assertIn("0412 Ringsaker: 1992 delt i 0403 Hamar, 0412 Ringsaker, satt til 3411", varsel)
        self.assertNotIn("1504", varsel)  # gamle Ålesund lå bare i dagens 1508

    def test_splitt_forste_omkoder_delte(self):
        ut = utfall(kjor("kommuneomkoding.py", "--splitt", "forste"), "0720")
        self.assertNotEqual(ut["0720"], "0720")


def med_grunnkrets(tekst, par):
    """Kjører utskriften fra kommuneomkoding.py --grunnkrets slik microdata.no gjør: recode på kommunen,
    recode på hjelpevariabelen (grunnkretsen) og replace der hjelpevariabelen fikk fire tegn.
    par: [(kommune, grunnkrets), ...]. Returnerer kommunene."""
    linjer = recode_linjer_i(tekst)
    kom = simuler([l for l in linjer if l.startswith("recode kommune ")], [k for k, _ in par])
    gk = simuler([l for l in linjer if l.startswith("recode kommune_gk ")], [g for _, g in par])
    if gk and "replace kommune = kommune_gk if length(kommune_gk) == 4" not in tekst:
        return kom
    return [g if len(g) == 4 else k for k, g in zip(kom, gk)]


class TestKommuneGrunnkrets(unittest.TestCase, LinjelengdeMixin):
    def test_stokke_fordeles_etter_grunnkrets(self):
        tekst = kjor("kommuneomkoding.py", "--fra", "2015", "--til", "2024", "--grunnkrets", "gk")
        self.sjekk_linjelengde(tekst)
        ut = med_grunnkrets(tekst, [("0720", "07200104"), ("0720", "07200103"), ("0720", "07209999"),
                                    ("1850", "18500101"), ("0301", "03010101"), ("1504", "15040101")])
        # Stokke-krets til Sandefjord. Delt krets og uoppgitt står som 0720. Oslo og Ålesund som før.
        self.assertEqual(ut, ["3907", "0720", "0720", "1806", "0301", "1508"])
        self.assertIn("Delte grunnkretser: 07200103 07200301", tekst)
        self.assertIn("generate kommune_gk = gk", tekst)
        self.assertTrue(tekst.rstrip().endswith("drop kommune_gk"))

    def test_haram_skilles_ut_fra_alesund_2023(self):
        tekst = kjor("kommuneomkoding.py", "--fra", "2023", "--til", "2024", "--grunnkrets", "gk")
        ut = med_grunnkrets(tekst, [("1507", "15071101"), ("1507", "15070101"), ("1507", "15079999")])
        self.assertEqual(ut, ["1580", "1508", "1508"])
        # Bare grunnkretsene som får en annen kommune enn recode gir, har regler (Haram, ikke Ålesund)
        self.assertNotIn("'15070101'", tekst)
        # 1580 finnes ikke i kodelisten 2023 og får ikke navn fra recode (TESTLISTE 2.9 c)
        self.assertIn("Uten navn i tabellen (finnes ikke i kodelisten 1.1.2023): 1580 Haram", tekst)

    def test_grensejustering_uten_regler(self):
        # Indre Østfold 2026: grunnkretsene som ble flyttet, er selv delt. Ingen regler trengs.
        tekst = kjor("kommuneomkoding.py", "--fra", "2025", "--til", "2026", "--grunnkrets", "gk")
        self.assertIn("Delte grunnkretser: 31181206 31181303 31181401", tekst)
        self.assertNotIn("kommune_gk", tekst)

    def test_mal_er_kommune_i_inndelingen(self):
        d = last()
        for fra, til in ((1990, 2024), (2015, 2026), (2019, 2020)):
            tekst = kjor("kommuneomkoding.py", "--fra", str(fra), "--til", str(til), "--grunnkrets", "gk")
            gyldige = set(koder_ved(d, f"{til + 1}-01-01"))
            mal = {m for l in recode_linjer_i(tekst) if l.startswith("recode kommune_gk ")
                   for m in re.findall(r"= '(\d{4})'", l)}
            self.assertTrue(mal <= gyldige, (fra, til, mal - gyldige))

    def test_for_tidlig_aar(self):
        r = subprocess.run([sys.executable, "-I", str(VERKTOY / "kommuneomkoding.py"), "--fra", "1989",
                            "--grunnkrets", "gk"], capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("1990", r.stderr)


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
