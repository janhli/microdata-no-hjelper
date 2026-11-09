"""Laster ned kommuneendringer fra SSB Klass (klassifikasjon 131, Standard for kommuneinndeling).

Lagrer til metadata/kommuneendringer.json:
  hentet       dato for nedlasting
  fra          første dato i uttrekket
  koder_ved_fra  kommunekoder som var gyldige på startdatoen (kode, navn)
  endringer    alle kodeendringer siden startdatoen (oldCode, newCode, changeOccurred, navn)

Brukes av verktoy/kommuneomkoding.py. Kjøres fra prosjektmappen:  python verktoy/hent_kommuneendringer.py
"""

import json
import urllib.request
from datetime import date
from pathlib import Path

FRA = "1989-01-01"  # eldste kommunevariabel for bosted (BEFOLKNING_KOMMNR_FORMELL) starter her
BASE = "https://data.ssb.no/api/klass/v1/classifications/131"
UT = Path(__file__).resolve().parent.parent / "metadata" / "kommuneendringer.json"


def hent(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    koder = hent(f"{BASE}/codesAt?date={FRA}&language=nb")["codes"]
    endr = hent(f"{BASE}/changes?from={FRA}&language=nb")["codeChanges"]
    ut = {
        "kilde": "SSB Klass 131, Standard for kommuneinndeling (https://www.ssb.no/klass/klassifikasjoner/131)",
        "hentet": date.today().isoformat(),
        "fra": FRA,
        "koder_ved_fra": [{"kode": c["code"], "navn": c["name"].strip()} for c in koder],
        "endringer": [
            {
                "gammel": c["oldCode"],
                "gammelt_navn": c["oldName"].strip(),
                "ny": c["newCode"],
                "nytt_navn": c["newName"].strip(),
                "dato": c["changeOccurred"],
            }
            for c in sorted(endr, key=lambda c: (c["changeOccurred"], c["oldCode"], c["newCode"]))
        ],
    }
    UT.write_text(json.dumps(ut, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    siste = max(e["dato"] for e in ut["endringer"])
    print(f"Skrev {UT}: {len(ut['koder_ved_fra'])} koder ved {FRA}, {len(ut['endringer'])} endringer til og med {siste}.")


if __name__ == "__main__":
    main()
