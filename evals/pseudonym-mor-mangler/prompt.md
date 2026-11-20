---
tags: [microdata-no, data]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Jeg vil lage et datasett med barn født 2015–2020 og fjerne barna der mor ikke er kjent. Skriv skriptet. Jeg tenkte på `drop if sysmiss(fnr_mor)`.
