---
type: llm
focus: trace
weight: 1
---

Grupperingen bruker ikke en konstruksjon der manglende verdi blir 0 eller faller i laveste gruppe (f.eks. `generate g = 1` fulgt av `replace` med betingelser uten håndtering av `sysmiss`).
