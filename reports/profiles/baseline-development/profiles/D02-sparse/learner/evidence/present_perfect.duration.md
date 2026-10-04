# Learner State

Sessions: 1; accepted observations: 1

Facts below are deterministic. Interpretations are hypotheses, not diagnoses.

- Only supported grammatical attempts enter accuracy counts.
- Reports may be selective and attempts correlated: credible intervals are conditional on the independence model, not full real-world certainty.
- Opportunities and self-corrections are recorded separately; no inference of avoidance from a single event.

## Present perfect — duration (`present_perfect.duration`)

Sessions observed: 1; last seen: 2026-01-01

| Production mode | Successes | Failures | Posterior mean | 95% credible interval |
|---|---:|---:|---:|---|
| spontaneous | 1 | 0 | 0.667 | [0.158, 0.987] |
| prompted | 0 | 0 | prior only | [0.025, 0.975] |
| controlled | 0 | 0 | prior only | [0.025, 0.975] |
| unknown | 0 | 0 | prior only | [0.025, 0.975] |

Model: Beta(1,1) prior; posterior Beta(1+successes, 1+failures).
Opportunities: 0; self-corrections: 0; uncertain: 0
Trend: insufficient_data

Hypothesis: Observed successes in these contexts; transfer remains untested.

Unknowns:

- Insufficient evidence for negative forms (fewer than 3 attempts).
- Insufficient evidence for question forms (fewer than 3 attempts).
- Fewer than 5 spontaneous attempts; estimate is dominated by sparse evidence.

Recent evidence IDs: OBS-fdf82e28abb0b7a56556

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-fdf82e28abb0b7a56556

Session: SES-68807bcf6cdda8b5b3cc; construction: present_perfect.duration
Outcome: correct; mode: spontaneous; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [43, 182) (Python Unicode characters)

Learner:

> I've lived here since 2021.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "I've lived here since 2021." The sentence was correct in the reported context.
