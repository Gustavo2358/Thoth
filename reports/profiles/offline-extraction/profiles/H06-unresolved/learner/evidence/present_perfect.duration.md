# Learner State

Sessions: 2; accepted observations: 2

Facts below are deterministic. Interpretations are hypotheses, not diagnoses.

- Only supported grammatical attempts enter accuracy counts.
- Reports may be selective and attempts correlated: credible intervals are conditional on the independence model, not full real-world certainty.
- Opportunities and self-corrections are recorded separately; no inference of avoidance from a single event.

## Present perfect — duration (`present_perfect.duration`)

Sessions observed: 2; last seen: 2026-01-08

| Production mode | Successes | Failures | Posterior mean | 95% credible interval |
|---|---:|---:|---:|---|
| spontaneous | 0 | 0 | prior only | [0.025, 0.975] |
| prompted | 0 | 0 | prior only | [0.025, 0.975] |
| controlled | 0 | 0 | prior only | [0.025, 0.975] |
| unknown | 0 | 0 | prior only | [0.025, 0.975] |

Model: Beta(1,1) prior; posterior Beta(1+successes, 1+failures).
Opportunities: 2; self-corrections: 0; uncertain: 2
Trend: insufficient_data

Hypothesis: Insufficient spontaneous attempt evidence.
Mode comparison: Insufficient evidence of a prompted/controlled versus spontaneous gap.
Recent failed spontaneous evidence IDs: 

Unknowns:

- Insufficient evidence for spontaneous negative forms (fewer than 3 attempts).
- Insufficient evidence for spontaneous question forms (fewer than 3 attempts).
- Fewer than 5 spontaneous attempts; estimate is dominated by sparse evidence.

Recent evidence IDs: OBS-a64ca2cb74be36e56279, OBS-4bcf67aa07ab394a45fb

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-a64ca2cb74be36e56279

Session: SES-31c3ec10597cc21765eb; construction: present_perfect.duration
Outcome: uncertain; mode: spontaneous; evidence: opportunity
Verifier: supported; support score: 3/4; pipeline: 6ed6b2e8bbec5ddf33c96acb75b84bdc30ddd0c724838a4eb939b1fa6555649a
Source offsets: [209, 374) (Python Unicode characters)

Learner:

> That happened earlier.

Verifier reason: Non-independent attempt; retain separately without accuracy counting

Source excerpt:

> Block 2. During spontaneous conversation, the learner said: "That happened earlier." This was an opportunity for present_perfect.continuous; target was not selected.

## OBS-4bcf67aa07ab394a45fb

Session: SES-db1cde0293b6f1f97854; construction: present_perfect.duration
Outcome: uncertain; mode: spontaneous; evidence: opportunity
Verifier: supported; support score: 3/4; pipeline: 6ed6b2e8bbec5ddf33c96acb75b84bdc30ddd0c724838a4eb939b1fa6555649a
Source offsets: [47, 212) (Python Unicode characters)

Learner:

> That happened earlier.

Verifier reason: Non-independent attempt; retain separately without accuracy counting

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "That happened earlier." This was an opportunity for present_perfect.continuous; target was not selected.
