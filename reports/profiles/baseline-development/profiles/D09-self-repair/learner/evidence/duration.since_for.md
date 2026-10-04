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
Opportunities: 0; self-corrections: 3; uncertain: 3
Trend: insufficient_data

Hypothesis: Insufficient spontaneous attempt evidence.

Unknowns:

- Insufficient evidence for negative forms (fewer than 3 attempts).
- Insufficient evidence for question forms (fewer than 3 attempts).
- Fewer than 5 spontaneous attempts; estimate is dominated by sparse evidence.

Recent evidence IDs: OBS-c1c22b48912148e50692, OBS-699adaad4e9a265b407c, OBS-f4806b2990079604c832

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-c1c22b48912148e50692

Session: SES-589775c7ba57de630988; construction: duration.since_for
Outcome: uncertain; mode: spontaneous; evidence: self_correction
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [48, 246) (Python Unicode characters)

Learner:

> I've worked here since three years. Sorry, I've worked here for three years.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "I've worked here since three years. Sorry, I've worked here for three years." The learner repaired the sentence without a teacher prompt.

## OBS-699adaad4e9a265b407c

Session: SES-bf2ff166c20b9eefe107; construction: duration.since_for
Outcome: uncertain; mode: spontaneous; evidence: self_correction
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [48, 246) (Python Unicode characters)

Learner:

> I've worked here since three years. Sorry, I've worked here for three years.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "I've worked here since three years. Sorry, I've worked here for three years." The learner repaired the sentence without a teacher prompt.

## OBS-f4806b2990079604c832

Session: SES-c24bb8ab976044f0bb30; construction: duration.since_for
Outcome: uncertain; mode: spontaneous; evidence: self_correction
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [48, 246) (Python Unicode characters)

Learner:

> I've worked here since three years. Sorry, I've worked here for three years.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "I've worked here since three years. Sorry, I've worked here for three years." The learner repaired the sentence without a teacher prompt.
