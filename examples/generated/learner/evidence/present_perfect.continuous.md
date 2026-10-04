# Learner State

Sessions: 3; accepted observations: 11

Facts below are deterministic. Interpretations are hypotheses, not diagnoses.

- Only supported grammatical attempts enter accuracy counts.
- Reports may be selective and attempts correlated: credible intervals are conditional on the independence model, not full real-world certainty.
- Opportunities and self-corrections are recorded separately; no inference of avoidance from a single event.

## Present perfect continuous (`present_perfect.continuous`)

Sessions observed: 1; last seen: 2026-01-01

| Production mode | Successes | Failures | Posterior mean | 95% credible interval |
|---|---:|---:|---:|---|
| spontaneous | 0 | 0 | prior only | [0.025, 0.975] |
| prompted | 1 | 0 | 0.667 | [0.158, 0.987] |
| controlled | 0 | 0 | prior only | [0.025, 0.975] |
| unknown | 0 | 0 | prior only | [0.025, 0.975] |

Model: Beta(1,1) prior; posterior Beta(1+successes, 1+failures).
Opportunities: 0; self-corrections: 0; uncertain: 0
Trend: insufficient_data

Hypothesis: Insufficient spontaneous attempt evidence.

Unknowns:

- Insufficient evidence for negative forms (fewer than 3 attempts).
- Insufficient evidence for question forms (fewer than 3 attempts).
- Fewer than 5 spontaneous attempts; estimate is dominated by sparse evidence.

Recent evidence IDs: OBS-e2f988d5ad06872c803b

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-e2f988d5ad06872c803b

Session: SES-c4462c73aa2ca6b30c67; construction: present_perfect.continuous
Outcome: correct; mode: prompted; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: a3d0d7229140bafff56838b22ca39ba29c7e8d28dafc0809899659575338cfee
Source offsets: [448, 618) (Python Unicode characters)

Learner:

> I've been working on this project for three months.

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> During a prompted speaking turn, the learner said: "I've been working on this project for three months." The sentence was grammatically correct. The work still continues.
