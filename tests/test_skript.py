"""Kjører `verktoy/sjekk_skript.py` på kodesnuttene og testskriptene, og tester sjekken selv.

Snuttene og testskriptene er kjørt i microdata.no. Finner sjekken en feil i dem, er det enten en feil i filen
(f.eks. en variabel som er slettet i en ny versjon av datalageret) eller en regel i sjekken som slår ut feil.
Advarsler er tillatt. Snutter med status UTGÅTT hoppes over, fordi variablene deres kan være slettet.
Kravene til levering (ansvarslinje og `citation`) gjelder skript agenten skriver, ikke snuttene.
"""

import os
import re
import subprocess
import sys
import unittest

from hjelp import SKILL, VERKTOY  # hjelp legger verktoy/ på sys.path
from sjekk_skript import (ANSVARSLINJE, TEMAFILER, analysekommandoer, er_pseudonym, geografivariabler,
                          les_datalagre, les_funksjoner, sjekk, temafiler)

ROT = SKILL.parent.parent
SKRIPT = sorted(
    list((SKILL / "kodesnutter").glob("*.txt"))
    + list((ROT / ".claude" / "skills" / "vedlikehold" / "testskript").glob("*.txt"))
)
# Testskript som har feilen med vilje, for å vise hva microdata.no gjør med den.
FORVENTET = {("del8_11_interaksjoner.txt", "c.alder#c.alder")}  # TESTLISTE 8.11: leddet utelates


def utgatt(tekst):
    return re.search(r"^// Status:\s*UTGÅTT", tekst, re.MULTILINE) is not None


class TestSkriptene(unittest.TestCase):
    def test_ingen_feil_i_snutter_og_testskript(self):
        feil = []
        for fil in SKRIPT:
            tekst = fil.read_text(encoding="utf-8")
            if utgatt(tekst):
                continue
            for f in sjekk(tekst, levering=False):
                if f.niva == "feil" and not any(fil.name == n and m in f.melding for n, m in FORVENTET):
                    feil.append(f"{fil.relative_to(ROT)}:{f.linje}: {f.melding}")
        self.assertEqual(feil, [], "\n".join(feil))

    def test_finner_skript(self):
        self.assertTrue(any(f.parent.name == "kodesnutter" for f in SKRIPT))
        self.assertTrue(any(f.parent.name == "testskript" for f in SKRIPT))

    def test_ansvarslinjen_er_lik_i_skill_md(self):
        self.assertIn(f"`{ANSVARSLINJE}`", (SKILL / "SKILL.md").read_text(encoding="utf-8"))


class TestSjekken(unittest.TestCase):
    """Sjekken må finne feilene den skal finne, ellers består testen over uansett."""

    VARIABLER = {
        "FAST": {"navn": "FAST", "temporalitet": "FIXED", "fra": "1900-01-01", "til": "2025-12-31",
                 "datalager": "no.ssb.fdb"},
        "STATUS": {"navn": "STATUS", "temporalitet": "STATUS", "fra": "2015-01-01", "til": "2024-01-01",
                   "datalager": "no.ssb.fdb"},
        "MORFNR": {"navn": "MORFNR", "temporalitet": "FIXED", "fra": "1900-01-01", "til": "2025-12-31",
                   "datalager": "no.ssb.fdb"},
        "KREFT": {"navn": "KREFT", "temporalitet": "FIXED", "fra": "1953-01-01", "til": "2024-12-31",
                  "datalager": "no.fhi.kreftregisteret"},
    }
    HODE = "require no.ssb.fdb:60 as fdb\nrequire no.fhi.kreftregisteret:1 as krg\nimport fdb/MORFNR as mor\n"

    def funn(self, *linjer, levering=False):
        return sjekk(self.HODE + "\n".join(linjer), self.VARIABLER, levering=levering,
                     datalagre={"no.ssb.fdb", "no.fhi.kreftregisteret", "no.fhi.npr"},
                     funksjoner={"t", "year", "sysmiss"}, pseudonym=lambda navn: navn == "MORFNR")

    def meldinger(self, *linjer, levering=False):
        return [f.melding for f in self.funn(*linjer, levering=levering) if f.niva == "feil"]

    def test_riktige_linjer_gir_ingen_funn(self):
        self.assertEqual(self.funn(
            "import fdb/FAST as f",
            "import fdb/STATUS 2020-01-01 as s",
            "  import fdb/STATUS $dato as $var",
            "import krg/KREFT as k",
            'import fdb/FAST as f, values("2")',
            "import-event fdb/STATUS 2010-01-01 to 2016-01-01 as e",
            "import-panel fdb/STATUS fdb/FAST 2016-01-01 2017-01-01",
            "summarize mor",
            "collapse (count) f -> antall (median) s -> med, by(mor)",
            "merge antall into barn on mor",
            "tabulate f, summarize(s) mean std p50",
            "regress s alder c.alder#c.lonn i.kjonn",
            "for i in 1 2",
            "  let v = tid_ ++ $i",
            "  generate $v = 0",
            "end",
            "generate gr = '1'",
            "replace gr = '2' if s >= 20",
            "replace gr = '9' if sysmiss(s)",
            "// generate t = sysmiss(mor) og import fdb/FINNESIKKE as x i en kommentar",
            "textblock",
            "import fdb/FINNESIKKE as x, if sysmiss(mor) og c.x#c.x i en tekstblokk",
            "endblock",
            "generate tekst = 'if mor'",
        ), [])

    def test_finner_feil(self):
        for linje, forventet in [
            ("import fdb/FINNESIKKE 2020-01-01 as x", "finnes ikke"),
            ("import fdb/FAST 2020-01-01 as f", "skal importeres uten dato"),
            ("import fdb/STATUS as s", "må ha dato"),
            ("import fdb/STATUS 2025-01-01 as s", "utenfor dekningen"),
            ("import fdb/KREFT as k", "ligger i no.fhi.kreftregisteret"),
            ("import npr/STATUS 2020-01-01 as s", "ingen require"),
            ("import-event fdb/STATUS 2000-01-01 to 2010-01-01 as e", "overlapper ikke"),
            ("import-panel fdb/STATUS 2016-01-01 2026-01-01", "utenfor dekningen"),
            ("import fdb/STATUS 2020-01-01", "kan ikke tolke"),
            ("require no.ssb.fdb:latest as fdb2", "require må ha formen"),
            ("require no.ssb.fbd:60 as fdb2", "finnes ikke"),
            ("drop if sysmiss(mor)", "pseudonymisert"),
            ("generate harmor = !sysmiss(mor)", "pseudonymisert"),
            ("tabulate f if mor == 1", "pseudonymisert"),
            ("tabulate f, summarize(s) median", "Bruk `p50`"),
            ("tabulate f, summarize(s) mean sd", "Bruk `std`"),
            ("regress s alder c.alder#c.alder", "utelates fra modellen"),
            ("logit s c.alder##c.alder", "utelates fra modellen"),
            ("generate t$i = 0", "kan ikke limes inn"),
            ("let t = tid_ ++ $i", "samme navn som en funksjon"),
            ("generate year = 2024", "samme navn som en funksjon"),
            ("import fdb/FAST as t", "samme navn som en funksjon"),
        ]:
            with self.subTest(linje=linje):
                meldinger = self.meldinger(linje)
                self.assertEqual(len(meldinger), 1, meldinger)
                self.assertIn(forventet, meldinger[0])

    def test_advarsel_for_gruppering_uten_sysmiss(self):
        funn = self.funn("import fdb/STATUS 2020-01-01 as s", "generate gr = '1'", "replace gr = '2' if s >= 20")
        self.assertEqual([(f.niva, f.linje) for f in funn], [("advarsel", 5)])

    def test_krav_til_levering(self):
        self.assertEqual(len(self.meldinger(levering=True)), 2)  # ansvarslinje og citation
        funn = self.funn(ANSVARSLINJE, "citation", "tabulate f", levering=True)
        self.assertEqual([(f.niva, "citation" in f.melding) for f in funn], [("advarsel", True)])
        self.assertEqual(self.funn(ANSVARSLINJE, "tabulate f", "citation", levering=True), [])


class TestMetadataenSjekkenBruker(unittest.TestCase):
    """Testene over gir sjekken egne lister. Disse fanger at de ekte listene blir tomme etter en ny henting
    (f.eks. hvis manualen får andre overskrifter), så sjekkene ikke slutter å virke uten at det merkes."""

    def test_funksjonene_fra_manualen(self):
        funksjoner = les_funksjoner()
        self.assertGreater(len(funksjoner), 50)
        self.assertLessEqual({"t", "year", "sysmiss", "substr"}, funksjoner)

    def test_pseudonymer_fra_variabelfilene(self):
        self.assertTrue(er_pseudonym("BEFOLKNING_MOR_FNR"))
        self.assertTrue(er_pseudonym("ARBEIDSFORHOLD_PERSON"))
        self.assertFalse(er_pseudonym("BEFOLKNING_KJOENN"))

    def test_datalagrene(self):
        self.assertLessEqual({"no.ssb.fdb", "no.fhi.kreftregisteret", "no.fhi.npr"}, les_datalagre())


class TestTemafiler(unittest.TestCase):
    """Sjekken sier hvilke temafiler skriptet trenger, så agenten ikke må vurdere det selv."""

    HODE = "require no.ssb.fdb:60 as fdb\ncreate-dataset p\n"

    def tema(self, *linjer):
        return {fil.removeprefix("fallgruver_").removesuffix(".md") for fil in temafiler(self.HODE + "\n".join(linjer))}

    def test_temaene_er_filene_som_finnes(self):
        self.assertEqual(set(TEMAFILER), {f.name for f in (SKILL / "referanser").glob("fallgruver_*.md")})

    def test_skript_uten_tema(self):
        self.assertEqual(self.tema("import fdb/BEFOLKNING_KJOENN as kjonn", "tabulate kjonn", "summarize kjonn"), set())

    def test_tema_i_kode(self):
        for linjer, forventet in [
            (["import fdb/BEFOLKNING_KOMMNR_FORMELL 2024-01-01 as kommune", "tabulate kommune"], {"geografi"}),
            (["import fdb/BEFOLKNING_GRUNNKRETS 2024-01-01 as gk", "generate del = substr(gk, 1, 6)"], {"geografi"}),
            (["import fdb/BEFOLKNING_BYDEL 2024-01-01 as bydel", "keep if bydel == '030101'"], {"geografi"}),
            (["import fdb/KRIMINALITET_SIKTEDE_GJFYLKE 2020-01-01 as fylke", "collapse (count) x, by(fylke)"], {"geografi"}),
            (["import-event fdb/BOSATTEFDT_BOSTED 2010-01-01 to 2016-01-01 as e"], {"geografi"}),
            (["import-panel fdb/BEFOLKNING_KOMMNR_FORMELL 2016-01-01 2017-01-01"], {"geografi", "analyse"}),
            (["regress lonn alder mann"], {"analyse"}),
            (["  cox tid hendelse alder"], {"analyse"}),
            (["logit-predict y x"], {"analyse"}),
            (["correlate a b"], {"analyse"}),
            (["coefplot regress lonn alder mann"], {"analyse"}),
            (["import fdb/REGSYS_VIRK_NACE1_SN07 2019-11-16 as naring"], {"klass"}),
            (["import fdb/NUDB_BU 2024-07-01 as bu", "recode bu ('1' = '1')"], {"klass"}),
            (["import fdb/BEFOLKNING_LANDBAK3GEN as lb", "// Klass 545 (2026-11-24): koder omkodet"], {"klass"}),
            (["import fdb/NUDB_BU 2024-07-01 as bu"], set()),
            (["require no.fhi.npr:1 as npr", "import npr/SOM_EP_AAR as aar"], {"fhi"}),
        ]:
            with self.subTest(linjer=linjer):
                self.assertEqual(self.tema(*linjer), forventet)

    def test_kommune_bare_for_aa_avgrense_til_bosatte_er_ikke_geografi(self):
        importen = "import fdb/BEFOLKNING_KOMMNR_FORMELL 2024-01-01 as kommune"
        for linje in ("drop if sysmiss(kommune)", "keep if !sysmiss(kommune)", "keep if sysmiss(kommune) == 0",
                      "generate kommunetall = 1", "drop kommune"):
            with self.subTest(linje=linje):
                self.assertEqual(self.tema(importen, linje), set())
        self.assertEqual(self.tema(importen), set())
        self.assertEqual(self.tema(importen, "drop if sysmiss(kommune) | kommune == '2100'"), {"geografi"})
        self.assertEqual(self.tema(importen.replace("kommune", "$var"), "tabulate kjonn"), {"geografi"})

    def test_kommentarer_og_tekst_gir_ikke_tema(self):
        self.assertEqual(self.tema("// regress lonn alder", "// require no.fhi.npr:1 as npr", "textblock",
                                   "import fdb/BEFOLKNING_KOMMNR_FORMELL 2024-01-01 as k", "cox", "endblock"), set())

    def test_variabler_som_ligner_er_ikke_geografi(self):
        for navn in ("SKATT_INNTEKT_KOMMUNE", "BEFOLKNING_TETTNR", "ARBLONN_LONN_BONUS", "NUDB_UTVEKSL_STUDIEPROGRAM"):
            with self.subTest(navn=navn):
                self.assertEqual(self.tema(f"import fdb/{navn} 2020-01-01 as x", "recode x ('1' = '1')"), set())

    def test_listene_fra_metadata_er_ikke_tomme(self):
        self.assertGreater(len(geografivariabler()), 15)
        self.assertLessEqual({"regress", "rdd", "oaxaca", "kaplan-meier", "ci", "import-panel"}, analysekommandoer())
        self.assertFalse({"tabulate", "summarize", "import", "collapse"} & analysekommandoer())


class TestKommandolinjen(unittest.TestCase):
    def kjor(self, *args, inn=""):
        return subprocess.run([sys.executable, "-I", str(VERKTOY / "sjekk_skript.py"), *args], input=inn,
                              capture_output=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"})

    def test_feil_gir_kode_1(self):
        r = self.kjor("-", inn="require no.ssb.fdb:60 as fdb\nimport fdb/FINNESIKKE as x\n")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("linje 2: FEIL: FINNESIKKE finnes ikke", r.stdout)

    def test_pseudonym_i_uttrykk_med_ekte_metadata(self):
        r = self.kjor("--snutt", "-", inn="require no.ssb.fdb:60 as fdb\ncreate-dataset p\n"
                                          "import fdb/BEFOLKNING_MOR_FNR as mor\ndrop if sysmiss(mor)\n")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("linje 4: FEIL: mor (BEFOLKNING_MOR_FNR) er en pseudonymisert ID", r.stdout)

    def test_snutt_uten_feil_gir_kode_0(self):
        r = self.kjor("--snutt", str(SKILL / "kodesnutter" / "alder.txt"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Ingen feil funnet", r.stdout)

    def test_temafilene_skrives_ut_ogsaa_nar_skriptet_har_feil(self):
        kode = "require no.ssb.fdb:60 as fdb\nimport fdb/BEFOLKNING_KOMMNR_FORMELL 2024-01-01 as k\ntabulate k\n"
        for inn, args, returkode in [(kode, ["--snutt", "-"], 0), (kode, ["-"], 1)]:
            r = self.kjor(*args, inn=inn)
            self.assertEqual(r.returncode, returkode, r.stderr)
            self.assertIn("referanser/fallgruver_geografi.md (BEFOLKNING_KOMMNR_FORMELL)", r.stdout)
            self.assertNotIn("fallgruver_fhi.md", r.stdout)


if __name__ == "__main__":
    unittest.main()
