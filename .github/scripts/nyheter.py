"""Oppretter én GitHub-issue per nytt innlegg på microdata.no/nyheter-og-informasjon.

Leser RSS-feeden (https://www.microdata.no/feed/, de ti siste innleggene). Innlegg publisert før
--fra-dato, eller som allerede har en issue med etiketten «nyhet» (lenken står i issue-teksten),
hoppes over. Innleggene går ikke rett inn i skillen. Issuen er en påminnelse om å vurdere dem.

Kjøres av .github/workflows/nyheter.yml. Lokalt (krever gh og innlogging):
  python .github/scripts/nyheter.py --fra-dato 2026-11-05 --torrkjoring
"""

import argparse
import email.utils
import html
import json
import re
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET

FEED = "https://www.microdata.no/feed/"
ETIKETT = "nyhet"
INNHOLD = "{http://purl.org/rss/1.0/modules/content/}encoded"


def hent_feed():
    req = urllib.request.Request(FEED, headers={"User-Agent": "microdata-no-hjelper/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        rot = ET.fromstring(r.read())
    innlegg = []
    for item in rot.iter("item"):
        tekst = html.unescape(re.sub(r"<[^>]+>", " ", item.findtext(INNHOLD) or item.findtext("description") or ""))
        tekst = re.sub(r"\s+", " ", tekst).split(" Innlegget ")[0].strip()  # WordPress-hale fjernes
        innlegg.append({
            "tittel": (item.findtext("title") or "").strip(),
            "lenke": (item.findtext("link") or "").strip(),
            "dato": email.utils.parsedate_to_datetime(item.findtext("pubDate")).date().isoformat(),
            "kategorier": [c.text for c in item.findall("category") if c.text],
            "utdrag": tekst[:800] + (" …" if len(tekst) > 800 else ""),
        })
    if not innlegg:
        sys.exit("Fant ingen innlegg i feeden. Er formatet endret?")
    return innlegg


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, encoding="utf-8").stdout


def kjente_lenker():
    ut = gh("issue", "list", "--label", ETIKETT, "--state", "all", "--limit", "500", "--json", "body")
    return {lenke for i in json.loads(ut) for lenke in re.findall(r"https?://\S+", i["body"] or "")}


def issue_tekst(n):
    versjon = re.search(r"versjon", n["tittel"], re.I)
    return f"""Nytt innlegg på microdata.no ({n['dato']}): {n['lenke']}

> {n['utdrag']}

Kategorier: {', '.join(n['kategorier']) or '–'}

Vurder (kryss av og lukk issuen):
- [ ] Ny eller endret fallgruve i `referanser/fallgruver.md`
- [ ] Ny kodesnutt, eller endring i en eksisterende
- [ ] Endring i `SKILL.md` (nye kommandoer, nye datakilder, versjonsråd)
- [ ] Bør testes i microdata.no først (legg i `TESTLISTE.md`)
- [ ] Ingen handling
{"" if not versjon else chr(10) + "Versjonsinnlegg: endrede variabler kommer også med den ukentlige metadata-PR-en."}
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fra-dato", required=True, help="ta bare med innlegg publisert denne datoen eller senere")
    ap.add_argument("--torrkjoring", action="store_true", help="vis hva som ville blitt opprettet")
    a = ap.parse_args()

    nye = [n for n in hent_feed() if n["dato"] >= a.fra_dato]
    if nye:
        kjent = kjente_lenker()
        nye = [n for n in nye if n["lenke"] not in kjent]
    print(f"{len(nye)} nye innlegg siden {a.fra_dato}.")
    if nye and not a.torrkjoring:
        gh("label", "create", ETIKETT, "--color", "1D76DB", "--description", "Nytt innlegg på microdata.no", "--force")
    for n in sorted(nye, key=lambda n: n["dato"]):
        tittel = f"Nyhet: {n['tittel']}"
        if a.torrkjoring:
            print(f"--- {tittel}\n{issue_tekst(n)}")
        else:
            print(gh("issue", "create", "--title", tittel, "--label", ETIKETT, "--body", issue_tekst(n)).strip())


if __name__ == "__main__":
    main()
