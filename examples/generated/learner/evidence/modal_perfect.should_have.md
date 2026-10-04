# Learner State

Sessions: 3; accepted observations: 11

Facts below are deterministic. Interpretations are hypotheses, not diagnoses.

- Only supported grammatical attempts enter accuracy counts.
- Reports may be selective and attempts correlated: credible intervals are conditional on the independence model, not full real-world certainty.
- Opportunities and self-corrections are recorded separately; no inference of avoidance from a single event.

## Modal perfect — should have (`modal_perfect.should_have`)

Sessions observed: 3; last seen: 2026-01-15

| Production mode | Successes | Failures | Posterior mean | 95% credible interval |
|---|---:|---:|---:|---|
| spontaneous | 1 | 2 | 0.400 | [0.068, 0.806] |
| prompted | 0 | 0 | prior only | [0.025, 0.975] |
| controlled | 0 | 0 | prior only | [0.025, 0.975] |
| unknown | 0 | 0 | prior only | [0.025, 0.975] |

Model: Beta(1,1) prior; posterior Beta(1+successes, 1+failures).
Opportunities: 0; self-corrections: 0; uncertain: 0
Trend: insufficient_data

Hypothesis: Preliminary evidence of inconsistent spontaneous production; retrieval cause is unproven.

Unknowns:

- Insufficient evidence for negative forms (fewer than 3 attempts).
- Insufficient evidence for question forms (fewer than 3 attempts).
- Fewer than 5 spontaneous attempts; estimate is dominated by sparse evidence.

Recent evidence IDs: OBS-aa7b26cb11520adc5ce2, OBS-ef40ee5608ddd306df10, OBS-154ee0e2cb969084c190

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-aa7b26cb11520adc5ce2

Session: SES-c4462c73aa2ca6b30c67; construction: modal_perfect.should_have
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: a3d0d7229140bafff56838b22ca39ba29c7e8d28dafc0809899659575338cfee
Source offsets: [230, 446) (Python Unicode characters)

Learner:

> I should told my team before.

Reported correction (not automatically authoritative):

> I should have told my team before.

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> During spontaneous conversation about a release incident, the learner said: "I should told my team before." The teacher corrected this to: "I should have told my team before." We discussed regret about a past action.

## OBS-ef40ee5608ddd306df10

Session: SES-75258f2722c0123145b6; construction: modal_perfect.should_have
Outcome: correct; mode: spontaneous; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: a3d0d7229140bafff56838b22ca39ba29c7e8d28dafc0809899659575338cfee
Source offsets: [205, 386) (Python Unicode characters)

Learner:

> I should not have sent that message.

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> During spontaneous conversation about a delivery, the learner said: "I should not have sent that message." The speaker regrets a past action. The sentence was grammatically correct.

## OBS-154ee0e2cb969084c190

Session: SES-2802a620705d2ee889b3; construction: modal_perfect.should_have
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: a3d0d7229140bafff56838b22ca39ba29c7e8d28dafc0809899659575338cfee
Source offsets: [227, 423) (Python Unicode characters)

Learner:

> I should told my team earlier.

Reported correction (not automatically authoritative):

> I should have told my team earlier.

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> During spontaneous conversation about a release, the learner said: "I should told my team earlier." The teacher corrected this to: "I should have told my team earlier." We discussed a past regret.
