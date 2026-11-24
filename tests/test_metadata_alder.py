"""Varsler når metadata som ikke hentes automatisk, er mer enn ett år gamle.

Den ukentlige workflowen henter variabler, manual og grunnkrets. Kommuneendringer, regioninndelinger og
kodeverket fra Kreftregisteret (ELVIS) hentes for hånd. Blir de gamle, mangler verktøyene nye endringer uten at
noe sier fra. Testen kjøres som eget steg til slutt i den ukentlige workflowen, så jobben blir rød uten å stoppe
pull requesten med nye metadata. Miljøvariabelen UTEN_ALDERSSJEKK hopper over selve alderskontrollen, både
i teststeget der og i tester.yml, så bidrag ikke stopper på noe bare vedlikeholderne kan rette.

`metadata/HENTET` og `grunnkrets/HENTET` er ikke med: de skrives bare når noe er endret, så datoen der er
siste endring, ikke siste henting.
"""

import json
import os
import unittest
from datetime import date, timedelta

from hjelp import METADATA

MAKS_ALDER = timedelta(days=365)


def hentet():
    """{fil: (dato for henting, kommando som oppdaterer)}. Kommandoene kjøres fra skills/microdata-no."""
    forste_ord = lambda sti: (METADATA / sti).read_text(encoding="utf-8").split()[0]
    return {
        "metadata/kommuneendringer.json": (
            json.loads((METADATA / "kommuneendringer.json").read_text(encoding="utf-8"))["hentet"],
            "python verktoy/hent_kommuneendringer.py"),
        "metadata/regioner/HENTET": (
            forste_ord("regioner/HENTET"),
            "python verktoy/hent_regioninndelinger.py, og se om filene i metadata/regioner/manuelt/ har nyere utgaver"),
        "metadata/fhi/kreftregisteret/HENTET": (
            forste_ord("fhi/kreftregisteret/HENTET"),
            "python verktoy/kreftregisteret.py hent"),
    }


class TestMetadataAlder(unittest.TestCase):
    def test_datoene_kan_leses(self):
        for fil, (dato, _) in hentet().items():
            with self.subTest(fil=fil):
                self.assertLessEqual(date.fromisoformat(dato), date.today())

    @unittest.skipIf(os.environ.get("UTEN_ALDERSSJEKK"), "UTEN_ALDERSSJEKK er satt")
    def test_hentet_siste_aar(self):
        gamle = [f"{fil} er hentet {dato}, over ett år siden. Oppdater med {kommando}."
                 for fil, (dato, kommando) in hentet().items()
                 if date.today() - date.fromisoformat(dato) > MAKS_ALDER]
        self.assertEqual(gamle, [], "\n".join(gamle))


if __name__ == "__main__":
    unittest.main()
