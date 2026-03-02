HUF-DOC: HUF.REL.LRN.INDEX.LEARNING_TRACK | HUF:1.1.8 | DOC:v0.1.0 | STATUS:draft | LANE:release | RO:Peter Higgins
CODES: LRN, INDEX | ART: CM, AS, TR, EB | EVID:E1 | POSTURE:OP | WEIGHTS: OP=0.80 TOOL=0.20 PEER=0.00 | CAP: OP_MIN=0.51 TOOL_MAX=0.49 | CANON:docs/learning/index.md

## Learning dashboard

**Progress legend:** 🟡 draft · 🔵 reviewed · 🟢 release · ⚫ deprecated  
**How this page stays honest:** module status should match `docs/learning/**/module.json`. When you promote a module, update `status` there first.

| Module | Status | Prereqs | Overview | Quiz | Answers |
|---|---:|---|---|---|---|
| 00 Orientation | 🟡 | — | [Start](00_orientation/) | [Quiz](00_orientation/quiz.md) | [Answers](00_orientation/answers.md) |
| 01 Foundations | 🟡 | 00 | [Start](01_foundations/) | [Quiz](01_foundations/quiz.md) | [Answers](01_foundations/answers.md) |
| 02 Formal Core | 🟡 | 01 | [Start](02_formal_core/) | [Quiz](02_formal_core/quiz.md) | [Answers](02_formal_core/answers.md) |
| 03 Artifacts | 🟡 | 02 | [Start](03_artifacts/) | [Quiz](03_artifacts/quiz.md) | [Answers](03_artifacts/answers.md) |
| 04 Running Examples | 🟡 | 03 | [Start](04_running_examples/) | [Quiz](04_running_examples/quiz.md) | [Answers](04_running_examples/answers.md) |
| 05 Case Studies | 🟡 | 04 | [Start](05_case_studies/) | [Quiz](05_case_studies/quiz.md) | [Answers](05_case_studies/answers.md) |
| 06 Partner Pilots | 🟡 | 05 | [Start](06_partner_pilots/) | [Quiz](06_partner_pilots/quiz.md) | [Answers](06_partner_pilots/answers.md) |
| 07 Advanced Math | 🟡 | 06 | [Start](07_advanced_math/) | [Quiz](07_advanced_math/quiz.md) | [Answers](07_advanced_math/answers.md) |

### Checklist (operator gate)

Use this as a lightweight “done / not done” tracker.  
When you tick a box here, also update the module’s `module.json` (`status: reviewed` or `status: release`) so the dashboard stays consistent.

- [ ] **00 Orientation** — I can explain CM/AS/TR/EB in plain language and run one example.
- [ ] **01 Foundations** — I can define regimes, mass accounting, retention, and normalization invariance.
- [ ] **02 Formal Core** — I can state the formal core claims vs interpretive extensions (and label them).
- [ ] **03 Artifacts** — I can read CM/AS/TR/EB and explain “why it stayed / what was discarded”.
- [ ] **04 Running Examples** — I can run Markham/Traffic/Planck demos and interpret outputs.
- [ ] **05 Case Studies** — I can map a real case narrative to artifacts + reproducible commands.
- [ ] **06 Partner Pilots** — I can explain scope boundaries for partner work (audit layer, not domain modeling).
- [ ] **07 Advanced Math** — I can connect the advanced math text back to core definitions and artifacts.

# Learning Track (Graduated)

This is the structured learning path for HUF, arranged from orientation to advanced mathematics.

What this track is:
- A **stable** front door for new readers (keeps the docs site navigable).
- A place where each module has a **quiz** and **answers** page.

Why it matters:
- Most people don’t struggle with the code — they struggle with the **conceptual inversion**:
  retention can strengthen what remains, and discarded mass must stay visible.

What you’ll see:
- A pipeline view (regimes → mass accounting → retention → coherence → artifacts).
- A conservative “formal core” that avoids overclaiming.
- Hands-on commands you can run in minutes.

Artifacts / outputs (recurring):
- **CM** Coherence Map (`artifact_1_coherence_map.csv`)
- **AS** Active Set (`artifact_2_active_set.csv`)
- **TR** Trace Report (`artifact_3_trace_report.jsonl`)
- **EB** Error Budget (`artifact_4_error_budget.json`)

Next steps:
- Start at **00 Orientation** and keep moving forward.
