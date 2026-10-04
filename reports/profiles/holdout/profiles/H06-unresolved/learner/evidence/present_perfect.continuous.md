# Learner State

Sessions: 2; accepted observations: 4

Facts below are deterministic. Interpretations are hypotheses, not diagnoses.

- Only supported grammatical attempts enter accuracy counts.
- Reports may be selective and attempts correlated: credible intervals are conditional on the independence model, not full real-world certainty.
- Opportunities and self-corrections are recorded separately; no inference of avoidance from a single event.

## Present perfect continuous (`present_perfect.continuous`)

Sessions observed: 2; last seen: 2026-01-08

| Production mode | Successes | Failures | Posterior mean | 95% credible interval |
|---|---:|---:|---:|---|
| spontaneous | 0 | 0 | prior only | [0.025, 0.975] |
| prompted | 0 | 0 | prior only | [0.025, 0.975] |
| controlled | 0 | 0 | prior only | [0.025, 0.975] |
| unknown | 0 | 0 | prior only | [0.025, 0.975] |

Model: Beta(1,1) prior; posterior Beta(1+successes, 1+failures).
Opportunities: 2; self-corrections: 1; uncertain: 4
Trend: insufficient_data

Hypothesis: Insufficient spontaneous attempt evidence.
Mode comparison: Insufficient evidence of a prompted/controlled versus spontaneous gap.
Recent failed spontaneous evidence IDs: 

Unknowns:

- Insufficient evidence for spontaneous negative forms (fewer than 3 attempts).
- Insufficient evidence for spontaneous question forms (fewer than 3 attempts).
- Fewer than 5 spontaneous attempts; estimate is dominated by sparse evidence.

Recent evidence IDs: OBS-5c21a5badf553964da4f, OBS-aad7f0c900f528ba7c91, OBS-cef3eb0ae88f9a098652, OBS-2c6464bab21c84cd1b8a

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-5c21a5badf553964da4f

Session: SES-31c3ec10597cc21765eb; construction: present_perfect.continuous
Outcome: uncertain; mode: spontaneous; evidence: other
Verifier: uncertain; support score: 2/4; pipeline: gold-ir-profiles-1
Source offsets: [47, 207) (Python Unicode characters)

Learner:

> I've been studying all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "I've been studying all morning." Context is missing; grammatical interpretation remains unresolved.

## OBS-aad7f0c900f528ba7c91

Session: SES-31c3ec10597cc21765eb; construction: present_perfect.continuous
Outcome: uncertain; mode: spontaneous; evidence: opportunity
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [209, 374) (Python Unicode characters)

Learner:

> That happened earlier.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During spontaneous conversation, the learner said: "That happened earlier." This was an opportunity for present_perfect.continuous; target was not selected.

## OBS-cef3eb0ae88f9a098652

Session: SES-db1cde0293b6f1f97854; construction: present_perfect.continuous
Outcome: uncertain; mode: spontaneous; evidence: opportunity
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [47, 212) (Python Unicode characters)

Learner:

> That happened earlier.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "That happened earlier." This was an opportunity for present_perfect.continuous; target was not selected.

## OBS-2c6464bab21c84cd1b8a

Session: SES-db1cde0293b6f1f97854; construction: present_perfect.continuous
Outcome: uncertain; mode: spontaneous; evidence: self_correction
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [214, 401) (Python Unicode characters)

Learner:

> I've studying all morning. Sorry, I've been studying all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During spontaneous conversation, the learner said: "I've studying all morning. Sorry, I've been studying all morning." The learner repaired the sentence without a teacher prompt.
