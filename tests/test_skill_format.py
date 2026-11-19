"""Sjekker at skillene følger Agent Skills-spesifikasjonen (https://agentskills.io/specification).

Spesifikasjonen er det Copilot, Codex, Cursor, Gemini CLI og Claude leser. Brytes den, kan skillen bli
borte i noen agenter uten at det merkes i Claude. Testen sjekker også at filene SKILL.md viser til, finnes
inne i skill-mappen, så mappen virker når den lenkes eller kopieres alene.
"""

import re
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
SKILLS = sorted(ROT.glob("skills/*/SKILL.md")) + sorted(ROT.glob(".claude/skills/*/SKILL.md"))
FELT = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAVN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Relative stier i backticks, f.eks. `metadata/variabler.csv` og `verktoy/klass.py`
STI = re.compile(r"`((?:metadata|referanser|kodesnutter|verktoy)/[^`*<>\s]+\.(?:md|csv|json|py|txt))`")


def les(fil):
    """(frontmatter som dict, brødtekst). Bare enkle «nøkkel: verdi»-linjer, innrykkede linjer hører til
    nøkkelen over (metadata)."""
    tekst = fil.read_text(encoding="utf-8")
    deler = tekst.split("---", 2)
    if not tekst.startswith("---") or len(deler) < 3:
        return None, tekst
    felt = {}
    for linje in deler[1].strip().splitlines():
        if linje.startswith((" ", "\t")) or not linje.strip():
            continue
        nokkel, _, verdi = linje.partition(":")
        felt[nokkel.strip()] = verdi.strip().strip('"').strip("'")
    return felt, deler[2]


class TestSkillFormat(unittest.TestCase):
    def test_finner_skills(self):
        self.assertIn(ROT / "skills" / "microdata-no" / "SKILL.md", SKILLS)

    def test_frontmatter(self):
        for fil in SKILLS:
            with self.subTest(skill=fil.parent.name):
                felt, _ = les(fil)
                self.assertIsNotNone(felt, "mangler YAML-frontmatter mellom ---")
                self.assertLessEqual(set(felt), FELT, "ukjente felt i frontmatter")
                navn = felt.get("name", "")
                self.assertRegex(navn, NAVN, "name: små bokstaver, tall og enkle bindestreker")
                self.assertLessEqual(len(navn), 64)
                self.assertEqual(navn, fil.parent.name, "name må være lik mappenavnet")
                beskrivelse = felt.get("description", "")
                self.assertTrue(1 <= len(beskrivelse) <= 1024, f"description er {len(beskrivelse)} tegn (1–1024)")
                if "compatibility" in felt:
                    self.assertLessEqual(len(felt["compatibility"]), 500)

    def test_lengde(self):
        for fil in SKILLS:
            with self.subTest(skill=fil.parent.name):
                _, brodtekst = les(fil)
                self.assertLessEqual(len(brodtekst.splitlines()), 500, "SKILL.md bør være under 500 linjer")

    def test_stier_finnes_i_skill_mappen(self):
        fil = ROT / "skills" / "microdata-no" / "SKILL.md"
        mangler = sorted({s for s in STI.findall(fil.read_text(encoding="utf-8")) if not (fil.parent / s).exists()})
        self.assertEqual(mangler, [], "SKILL.md viser til filer som ikke finnes i skill-mappen")


if __name__ == "__main__":
    unittest.main()
