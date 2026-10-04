# Learner State

Sessions: 3; accepted observations: 3

Facts below are deterministic. Interpretations are hypotheses, not diagnoses.

- Only supported grammatical attempts enter accuracy counts.
- Reports may be selective and attempts correlated: credible intervals are conditional on the independence model, not full real-world certainty.
- Opportunities and self-corrections are recorded separately; no inference of avoidance from a single event.

## Since vs. for (`duration.since_for`)

Sessions observed: 3; last seen: 2026-01-15

| Production mode | Successes | Failures | Posterior mean | 95% credible interval |
|---|---:|---:|---:|---|
| spontaneous | 0 | 0 | prior only | [0.025, 0.975] |
| prompted | 0 | 0 | prior only | [0.025, 0.975] |
| controlled | 0 | 0 | prior only | [0.025, 0.975] |
| unknown | 0 | 0 | prior only | [0.025, 0.975] |

Model: Beta(1,1) prior; posterior Beta(1+successes, 1+failures).
Opportunities: 3; self-corrections: 0; uncertain: 3
Trend: insufficient_data

Hypothesis: Insufficient spontaneous attempt evidence.
Mode comparison: Insufficient evidence of a prompted/controlled versus spontaneous gap.
Recent failed spontaneous evidence IDs: 

Unknowns:

- Insufficient evidence for spontaneous negative forms (fewer than 3 attempts).
- Insufficient evidence for spontaneous question forms (fewer than 3 attempts).
- Fewer than 5 spontaneous attempts; estimate is dominated by sparse evidence.

Recent evidence IDs: OBS-3cad12d69de173c4037f, OBS-06ba0bb3ee171e9c24ab, OBS-3c0acb9097e98e0ad64d

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-3cad12d69de173c4037f

Session: SES-9aa5fdb6abe9e341b94b; construction: duration.since_for
Outcome: uncertain; mode: spontaneous; evidence: opportunity
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [50, 207) (Python Unicode characters)

Learner:

> That happened earlier.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "That happened earlier." This was an opportunity for duration.since_for; target was not selected.

## OBS-06ba0bb3ee171e9c24ab

Session: SES-5710a7d8db39b9d7990d; construction: duration.since_for
Outcome: uncertain; mode: spontaneous; evidence: opportunity
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [50, 207) (Python Unicode characters)

Learner:

> That happened earlier.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "That happened earlier." This was an opportunity for duration.since_for; target was not selected.

## OBS-3c0acb9097e98e0ad64d

Session: SES-76119a4ad438af4a9dd3; construction: duration.since_for
Outcome: uncertain; mode: spontaneous; evidence: opportunity
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [50, 207) (Python Unicode characters)

Learner:

> That happened earlier.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "That happened earlier." This was an opportunity for duration.since_for; target was not selected.
