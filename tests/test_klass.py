"""Tester klass.py mot SSB Klass (krever nett). Hoppes over uten nett eller med UTEN_NETT=1."""

import unittest

from hjelp import avvik, har_nett, kjor, recode_linjer_i, simuler


@unittest.skipUnless(har_nett(), "SSB Klass svarer ikke (eller UTEN_NETT er satt)")
class TestKlass(unittest.TestCase):
    def test_grupper(self):
        for args in [("grupper", "7", "--nivaa", "1", "--variabel", "REGSYS_ARB_YRKE_STYRK08"),
                     ("grupper", "36", "--nivaa", "1", "--variabel", "NUDB_BU"),
                     ("grupper", "545", "--nivaa", "2", "--variabel", "BEFOLKNING_LANDBAK3GEN"),
                     ("grupper", "6", "--nivaa", "1", "--dato", "2024-01-01", "--variabel", "REGSYS_NARING_SN2007")]:
            with self.subTest(args=args):
                tekst = kjor("klass.py", *args)
                self.assertIn("generate ", tekst)
                self.assertTrue(recode_linjer_i(tekst))
                self.assertEqual(avvik(tekst), [])

    def test_styrk_til_hovedgruppe(self):
        tekst = kjor("klass.py", "grupper", "7", "--nivaa", "1", "--variabel", "REGSYS_ARB_YRKE_STYRK08")
        self.assertEqual(simuler(recode_linjer_i(tekst), ["2511", "XXXX"]), ["2", "XXXX"])

    def test_kobling_sn2002_til_sn2007(self):
        tekst = kjor("klass.py", "kobling", "6", "--dato", "2005-01-01", "--tabell", "SN 2007", "--navn", "naring")
        self.assertIn("kobles til flere mål", tekst)
        self.assertIn("både kilde og mål", tekst)
        self.assertEqual(avvik(tekst), [])

    def test_kobling_sn2025_til_sn2007_med_tomme_maal(self):
        # Krasjet før: Klass har rader uten mål (targetCode null), f.eks. 46.890.
        tekst = kjor("klass.py", "kobling", "6", "--dato", "2025-06-01", "--tabell", "SN 2007")
        self.assertIn("ingen motpart", tekst)
        self.assertEqual(avvik(tekst), [])

    def test_kobling_sn2007_til_sn2025(self):
        self.assertEqual(avvik(kjor("klass.py", "kobling", "6", "--dato", "2024-01-01", "--tabell", "SN) 2025")), [])

    def test_kobling_nus_til_isced(self):
        self.assertEqual(avvik(kjor("klass.py", "kobling", "36", "--tabell", "ISCED 2011 Attainment")), [])


if __name__ == "__main__":
    unittest.main()
