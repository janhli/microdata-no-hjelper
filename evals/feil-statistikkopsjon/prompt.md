---
tags: [microdata-no, data]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Dette skriptet stopper. Hva er feil?

```
require no.ssb.fdb:60 as fdb
create-dataset p
import fdb/BEFOLKNING_KOMMNR_FORMELL 2025-01-01 as kommune
import fdb/INNTEKT_WLONN 2024-12-31 as lonn
generate fylke = substr(kommune, 1, 2)
tabulate fylke, summarize(lonn) median
```
