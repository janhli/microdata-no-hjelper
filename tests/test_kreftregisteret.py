"""Tester kreftregisteret.py (uten nett): grupperingen bruker metadata/fhi/kreftregisteret/, og hent simuleres."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from hjelp import avvik, kjor, recode_linjer_i, simuler

import kreftregisteret as kr


def grupper(*args):
    return kjor("kreftregisteret.py", "grupper", *args)


class TestGrupper(unittest.TestCase):
    def test_nivaa1_gir_hovedgrupper(self):
        tekst = grupper("--variabel", "S_TOPOGRAFIICD10", "--nivaa", "1", "--var", "topo")
        self.assertIn("generate kreftform = substr(topo, 1, 3)", tekst)
        self.assertEqual(avvik(tekst), [])
        ut = simuler(recode_linjer_i(tekst), ["C18", "C50", "C34", "D47", "D45", "C78", "D05"])
        self.assertEqual(ut, ["C15-C26", "C50", "C30-C39", "C81-C96", "C81-C96", "C78", "D05"])  # D45 mangler i kodelisten
        self.assertIn("'C15-C26' 'Fordøyelsesorganer'", tekst)
        self.assertIn("('C50' = 'C50' 'Bryst')", tekst)  # gruppe og kode er like, men skal ha navn
        self.assertIn("C77 C78 C79 C97", tekst)  # spredning og flere svulster står uendret, og det sies fra

    def test_nivaa2_gir_merkelapper_uten_recode(self):
        tekst = grupper("--variabel", "S_TOPOGRAFIICD10", "--nivaa", "2", "--navn", "kreft3", "--var", "topo")
        self.assertEqual(recode_linjer_i(tekst), [])
        self.assertIn("'C18' 'Tykktarm'", tekst)
        self.assertIn("assign-labels kreft3 kreft3txt", tekst)

    def test_ukjent_bruker_betingelse_ikke_sluttregel(self):
        # Diagnosevariabelen har nesten 20 000 koder. Med --ukjent skal det bli to linjer, ikke en lang recode
        tekst = grupper("--variabel", "SOM_EP_HOVEDTILSTAND1", "--nivaa", "2", "--var", "diag", "--ukjent")
        self.assertIn("generate kreftform = 'annet' if !sysmiss(diag)", tekst)
        self.assertIn("!inlist(substr(diag, 1, 3), ", tekst)
        self.assertNotIn("(* =", tekst)
        self.assertEqual(recode_linjer_i(tekst), [])

    def test_utelat_tar_ut_gruppe(self):
        tekst = grupper("--variabel", "S_TOPOGRAFIICD10", "--nivaa", "1", "--utelat", "C40-C41")
        self.assertNotIn("= 'C40-C41'", tekst)
        self.assertIn("C40 C41", tekst)
        self.assertEqual(simuler(recode_linjer_i(tekst), ["C40", "C18"]), ["C40", "C15-C26"])


class TestHent(unittest.TestCase):
    """hent med simulerte svar: skal ikke skrive filer når formatet er endret."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ut = Path(self._tmp.name) / "kreftregisteret"
        self._orig = kr.UT, kr.hent_json
        kr.UT = self.ut

    def tearDown(self):
        kr.UT, kr.hent_json = self._orig
        self._tmp.cleanup()

    def kjor(self, svar):
        kr.hent_json = svar
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            try:
                kr.kommando_hent(None)
                return 0, err.getvalue()
            except SystemExit as e:
                return e.code, err.getvalue()

    @staticmethod
    def sites(n=102):
        topp = {"id": 1, "name": "Fordøyelsesorganer", "icdCode": "C15-C26"}
        return [topp] + [{"id": i + 2, "name": f"Kode {i}", "icdCode": f"C{i:02d}", "parent": topp} for i in range(n - 1)]

    def test_vellykket(self):
        def svar(sti):
            if sti.endswith("cancer-sites"):
                return self.sites()
            return [{"value": "1", "description": "Ja", "valueCancerSites": [
                {"cancerSite": {"icdCode": "C18"}}, {"cancerSite": {"icdCode": "C19"}, "validTo": "01.01.2010"}]}]
        kode, err = self.kjor(svar)
        self.assertEqual(kode, 0, err[-500:])
        verdier = (self.ut / "verdier.csv").read_text(encoding="utf-8").splitlines()
        self.assertIn(";1;Ja;C18", verdier[1])  # utgått kreftform (validTo) er ikke med

    def test_endret_format_skriver_ingenting(self):
        def svar(sti):
            if sti.endswith("cancer-sites"):
                return self.sites(30)
            return {"feil": "nytt format"}
        kode, err = self.kjor(svar)
        self.assertNotEqual(kode, 0)
        self.assertIn("kreftformer", err)
        self.assertIn("ikke en liste", err)
        self.assertFalse(self.ut.exists())


if __name__ == "__main__":
    unittest.main()
