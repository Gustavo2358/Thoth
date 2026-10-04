# Learner State

Sessions: 3; accepted observations: 11

Facts below are deterministic. Interpretations are hypotheses, not diagnoses.

- Only supported grammatical attempts enter accuracy counts.
- Reports may be selective and attempts correlated: credible intervals are conditional on the independence model, not full real-world certainty.
- Opportunities and self-corrections are recorded separately; no inference of avoidance from a single event.

## Question formation — do support (`question.do_support`)

Sessions observed: 1; last seen: 2026-01-08

| Production mode | Successes | Failures | Posterior mean | 95% credible interval |
|---|---:|---:|---:|---|
| spontaneous | 0 | 0 | prior only | [0.025, 0.975] |
| prompted | 0 | 0 | prior only | [0.025, 0.975] |
| controlled | 1 | 0 | 0.667 | [0.158, 0.987] |
| unknown | 0 | 0 | prior only | [0.025, 0.975] |

Model: Beta(1,1) prior; posterior Beta(1+successes, 1+failures).
Opportunities: 0; self-corrections: 0; uncertain: 0
Trend: insufficient_data

Hypothesis: Insufficient spontaneous attempt evidence.

Unknowns:

- Insufficient evidence for negative forms (fewer than 3 attempts).
- Insufficient evidence for question forms (fewer than 3 attempts).
- Fewer than 5 spontaneous attempts; estimate is dominated by sparse evidence.

Recent evidence IDs: OBS-dfe18696dc5bcaa33879

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-dfe18696dc5bcaa33879

Session: SES-75258f2722c0123145b6; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: a3d0d7229140bafff56838b22ca39ba29c7e8d28dafc0809899659575338cfee
Source offsets: [388, 521) (Python Unicode characters)

Learner:

> Where does he work?

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> During a controlled drill, the learner said: "Where does he work?" This is a direct question. The sentence was grammatically correct.
