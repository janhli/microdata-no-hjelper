"""Tester kreftregisteret.py (uten nett): grupperingen bruker metadata/fhi/kreftregisteret/, og hent simuleres."""

import contextlib
import io
import re
import tempfile
import unittest
from pathlib import Path

from hjelp import avvik, kjor, recode_linjer_i, simuler

import kreftregisteret as kr
from recode_regler import q


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


def cin_utfall(tekst, koder, ukjent=False):
    """Kjører generate/replace/recode fra --nivaa cin slik microdata.no gjør (uten kjønn og morfologi)."""
    fire = set(re.findall(r"'([CD]\d{3})'", next(l for l in tekst.splitlines() if l.startswith("replace ") and "1, 4)" in l)))
    tre = None
    if ukjent:
        tre = set(re.findall(r"'([CD]\d{2})'", next(l for l in tekst.splitlines() if "1, 3)" in l and l.startswith("replace "))))
    verdier = []
    for k in koder:
        v = k[:3] if not ukjent else ("annet" if k[:3] not in tre else k[:3])
        if k[:4] in fire:
            v = k[:4]
        verdier.append(v)
    return simuler(recode_linjer_i(tekst), verdier)


class TestCancerInNorway(unittest.TestCase):
    def setUp(self):
        self.tekst = grupper("--variabel", "S_TOPOGRAFIICD10", "--nivaa", "cin", "--var", "topo")

    def test_kjente_koder(self):
        koder = ["C000", "C003", "C008", "C050", "C051", "C09", "C189", "C20", "C341", "C482", "C570", "C577",
                 "C57", "D090", "D353", "D350", "D443", "D47", "C780", "C97", "D050"]
        fasit = ["C00", "C02-06", "C02-06", "C02-06", "C09-10,C01,C14", "C09-10,C01,C14", "C18", "C19-20",
                 "C33-34", "C48-49", "C56,C57.0-4,C48.2", "C51-52,C57.7-9", "C51-52,C57.7-9", "C65-68",
                 "C37,C74-75", "D35", "C37,C74-75", "C91-95", "C78", "C97", "D05"]
        self.assertEqual(cin_utfall(self.tekst, koder), fasit)

    def test_alle_kreftkoder_faar_en_kreftform(self):
        cin = kr.les_cin()
        grupper_ = {g["gruppe"] for g in cin}
        self.assertEqual(len(cin), 48)
        prefikser = [k for g in cin for k in g["koder"].split()]
        self.assertEqual(len(prefikser), len(set(prefikser)), "en kode står i to kreftformer")
        koder = kr.kodeliste("S_TOPOGRAFIICD10")
        ut = dict(zip(koder, cin_utfall(self.tekst, koder)))
        for k, v in ut.items():
            if k.startswith("C") and k[:3] not in ("C46", "C77", "C78", "C79", "C97"):
                self.assertIn(v, grupper_, k)
        # Alle kreftformene har navn
        for g in grupper_:
            self.assertIn(f"= {q(g)} {q(next(x['navn'] for x in cin if x['gruppe'] == g))}", self.tekst)

    def test_ukjent(self):
        tekst = grupper("--variabel", "SOM_EP_HOVEDTILSTAND1", "--nivaa", "cin", "--var", "diag", "--ukjent")
        self.assertIn("generate kreftform = 'annet' if !sysmiss(diag)", tekst)
        self.assertEqual(cin_utfall(tekst, ["C189", "D353", "D350", "I10", "C482"], ukjent=True),
                         ["C18", "C37,C74-75", "annet", "annet", "C48-49"])

    def test_kjonn_og_morfologi(self):
        self.assertNotIn("== '2'", self.tekst)
        self.assertIn("--kjonn", self.tekst)  # sier fra om C48.2 uten kjønn
        tekst = grupper("--variabel", "S_TOPOGRAFIICD10", "--nivaa", "cin", "--var", "topo", "--kjonn", "kjonn",
                        "--morfologi", "morf")
        self.assertIn("replace kreftform = 'C56,C57.0-4,C48.2' if substr(topo, 1, 4) == 'C482' & kjonn == '2'", tekst)
        self.assertIn("replace kreftform = 'basal' if substr(morf, 1, 3) == '809'", tekst)

    def test_leppe_fra_icdo3_foer_recode(self):
        self.assertIn("--topografi", self.tekst)  # sier fra om leppekreft uten ICD-O-3
        tekst = grupper("--variabel", "S_TOPOGRAFIICD10", "--nivaa", "cin", "--var", "topo", "--topografi", "topo3")
        linjer = tekst.splitlines()
        leppe = linjer.index("replace kreftform = 'C00' if inlist(substr(topo, 1, 3), 'C43', 'C44') & "
                             "inlist(substr(topo3, 1, 3), '000', '001', '002', '006', '009')")
        forste_recode = next(i for i, l in enumerate(linjer) if l.startswith("recode "))
        self.assertLess(leppe, forste_recode)  # så recode gir C00 navnet Leppe
        # 'C00' og 'C02-06' er ikke kilde i noen regel, så recode endrer dem ikke
        self.assertEqual(simuler(recode_linjer_i(tekst), ["C00", "C02-06"]), ["C00", "C02-06"])

    def test_linjelengde(self):
        self.assertEqual(avvik(self.tekst), [])
        self.assertTrue(all(len(l) < 2700 for l in self.tekst.splitlines()))


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
