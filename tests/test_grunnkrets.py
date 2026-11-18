"""Tester grunnkrets.py mot metadata/grunnkrets/ og kodelistehistorikken til BEFOLKNING_GRUNNKRETS (uten nett)."""

import contextlib
import csv
import io
import re
import tempfile
import unittest
from pathlib import Path

from hjelp import METADATA, avvik, kjor, recode_linjer_i, simuler

import grunnkrets as gk

ALESUND_2019 = "15040101"  # Ålesund 1504 -> 1507 (2020) -> 1508 (2024): grunnkrets 15080101 i 2026


def kjor_gk(*args):
    return kjor("grunnkrets.py", *args)


def substr_steg(tekst, verdier):
    """Utfører replace-linjen med substr() slik microdata.no gjør, etter recode-linjene."""
    linje = next((l for l in tekst.splitlines() if l.startswith("replace ")), None)
    if not linje:
        return verdier
    unntak = set(re.findall(r"'(\d{8})'", linje))
    return [v[:6] if len(v) == 8 and v[4:] != "9999" and v not in unntak else v for v in verdier]


def inndeling(navn):
    with open(METADATA / "grunnkrets" / "inndelinger.csv", encoding="utf-8", newline="") as f:
        return {r["grunnkrets"]: r["kode"] for r in csv.DictReader(f, delimiter=";") if r["inndeling"] == navn}


class TestGrunnkrets(unittest.TestCase):
    def test_lks_gjeldende_aar_er_tabellen(self):
        tekst = kjor_gk("--til", "lks", "--aar", "2026", "--var", "gk")
        self.assertEqual(avvik(tekst), [])
        tab = inndeling("lks")
        kilder = sorted(tab)
        self.assertEqual(simuler(recode_linjer_i(tekst), kilder), [tab[k] for k in kilder])
        self.assertIn("'Ålesund LKS 03'", tekst)

    def test_gammel_kode_folges_gjennom_to_reformer(self):
        tekst = kjor_gk("--til", "lks", "--aar", "2019", "--kommune", "1508")
        self.assertEqual(simuler(recode_linjer_i(tekst), [ALESUND_2019]), ["1508000003"])
        # Utenfor --kommune og utenfor inndelingen står uendret
        self.assertEqual(simuler(recode_linjer_i(tekst), ["03010101", "15049999"]), ["03010101", "15049999"])

    def test_regel_tar_med_alle_grunnkretser_i_enheten(self):
        # Avsløringskontrollen ser på hver målverdi. Regelen for en levekårssone skal derfor ha med alle
        # grunnkretsene i sonen, ikke bare dem som har endret kode.
        r = gk.bygg(2024, "lks")
        tab = inndeling("lks")
        for mal in {"1508000003", "3201000054"}:
            self.assertEqual({k for k, m in r["kart"].items() if m == mal}, {g for g, m in tab.items() if m == mal})

    def test_delomrade_med_substr_gir_samme_som_full_omkoding(self):
        for aar in (2015, 2020, 2024):
            with self.subTest(aar=aar):
                tekst = kjor_gk("--til", "delomrade", "--aar", str(aar))
                self.assertEqual(avvik(tekst), [])
                koder = sorted(k for k in gk.kodeliste_aar(gk.kodelister(), aar) if len(k) == 8)
                ut = substr_steg(tekst, simuler(recode_linjer_i(tekst), koder))
                per_dato = gk.les_endringer()
                for kode, verdi in zip(koder, ut):
                    if kode.endswith("9999"):
                        self.assertEqual(verdi, kode)
                        continue
                    mal = {n[:6] for n in gk.folg(kode, f"{aar}-01-01", per_dato)}
                    self.assertEqual(verdi, mal.pop() if len(mal) == 1 else kode, kode)

    def test_delomrade_2026_er_bare_substr(self):
        tekst = kjor_gk("--til", "delomrade", "--aar", "2026")
        self.assertEqual(recode_linjer_i(tekst), [])
        self.assertIn("replace delomrade = substr(delomrade, 1, 6) if length(delomrade) == 8", tekst)

    def test_delt_grunnkrets_star_uendret_eller_forste(self):
        r = gk.bygg(1990, "delomrade", {"3101"})
        self.assertIn("01010104", r["delt"])
        self.assertNotIn("01010104", r["kart"])
        r = gk.bygg(1990, "delomrade", {"3101"}, splitt="forste")
        self.assertIn(r["kart"]["01010104"], {"310101", "310102"})

    def test_egne_omrader_fra_fil(self):
        with tempfile.TemporaryDirectory() as d:
            fil = Path(d) / "sentrum.csv"
            fil.write_text("grunnkrets;kode;navn\n15080101;S;Sentrum\n15080102;S;Sentrum\n", encoding="utf-8")
            tekst = kjor_gk("--til", str(fil), "--aar", "2019", "--var", "gk")
        self.assertIn("generate sentrum = gk", tekst)
        self.assertEqual(simuler(recode_linjer_i(tekst), [ALESUND_2019, "15040103"]), ["S", "15040103"])

    def test_utelat(self):
        tekst = kjor_gk("--til", "lks", "--aar", "2026", "--kommune", "1508", "--utelat", "1508000003")
        self.assertNotIn("= '1508000003'", tekst)
        self.assertIn("= '1508000002'", tekst)


class TestHent(unittest.TestCase):
    """hent_grunnkrets med simulerte Klass-svar."""

    def setUp(self):
        import hent_grunnkrets as hg
        self.hg = hg
        self._tmp = tempfile.TemporaryDirectory()
        self._orig = hg.UT, hg.hent, hg.MIN_ENDRINGER, dict(hg.TABELLER)
        hg.UT = Path(self._tmp.name) / "grunnkrets"
        hg.MIN_ENDRINGER = 1
        for k in hg.TABELLER:
            hg.TABELLER[k] = (hg.TABELLER[k][0], 1)

    def tearDown(self):
        self.hg.UT, self.hg.hent, self.hg.MIN_ENDRINGER, tab = self._orig
        self.hg.TABELLER.clear()
        self.hg.TABELLER.update(tab)
        self._tmp.cleanup()

    def svar(self, mangler=None):
        tabeller = {"lks": "Levekårssoner (LKS) 2026-05", "bydel": "Bydelsinndeling 2020", "delbydel": "Delbydeler i Oslo 2017"}

        def hent(url):
            if "/changes" in url:
                return {"codeChanges": [{"oldCode": "15070101", "newCode": "15080101", "changeOccurred": "2024-01-01"},
                                        {"oldCode": "150701", "newCode": "150801", "changeOccurred": "2024-01-01"}]}
            if url.endswith("/classifications/1"):
                return {"versions": [{"validFrom": "2026-01-01", "_links": {"self": {"href": "V"}}}]}
            if url == "V":
                return {"name": "Grunnkrets 2026", "correspondenceTables": [
                    {"name": f"{n} - Grunnkrets 2026", "_links": {"self": {"href": k}}}
                    for k, n in tabeller.items() if k != mangler]}
            return {"name": url, "correspondenceMaps": [
                {"sourceCode": "S1", "sourceName": "Sone 1", "targetCode": "15080101"}]}
        return hent

    def kjor(self, svar):
        self.hg.hent = svar
        err, out = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            try:
                self.hg.main()
                return 0, out.getvalue() + err.getvalue()
            except SystemExit as e:
                return e.code, out.getvalue() + err.getvalue()

    def test_skriver_og_lar_uendrede_filer_sta(self):
        kode, tekst = self.kjor(self.svar())
        self.assertIn(kode, (0, None), tekst)
        self.assertEqual((self.hg.UT / "endringer.csv").read_text(encoding="utf-8"),
                         "dato;gammel;ny\n2024-01-01;15070101;15080101\n")  # bare 8 sifre
        (self.hg.UT / "HENTET").write_text("gammel dato\n", encoding="utf-8")
        _, tekst = self.kjor(self.svar())
        self.assertIn("Ingen endringer", tekst)
        self.assertEqual((self.hg.UT / "HENTET").read_text(encoding="utf-8"), "gammel dato\n")

    def test_manglende_tabell_skriver_ingenting(self):
        kode, tekst = self.kjor(self.svar(mangler="lks"))
        self.assertEqual(kode, 1)
        self.assertIn("lks: 0 tabeller", tekst)
        self.assertFalse(self.hg.UT.exists())


if __name__ == "__main__":
    unittest.main()
