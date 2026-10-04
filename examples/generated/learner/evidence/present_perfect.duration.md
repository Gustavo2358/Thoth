# Learner State

Sessions: 3; accepted observations: 11

Facts below are deterministic. Interpretations are hypotheses, not diagnoses.

- Only supported grammatical attempts enter accuracy counts.
- Reports may be selective and attempts correlated: credible intervals are conditional on the independence model, not full real-world certainty.
- Opportunities and self-corrections are recorded separately; no inference of avoidance from a single event.

## Present perfect — duration (`present_perfect.duration`)

Sessions observed: 3; last seen: 2026-01-15

| Production mode | Successes | Failures | Posterior mean | 95% credible interval |
|---|---:|---:|---:|---|
| spontaneous | 1 | 2 | 0.400 | [0.068, 0.806] |
| prompted | 0 | 0 | prior only | [0.025, 0.975] |
| controlled | 0 | 0 | prior only | [0.025, 0.975] |
| unknown | 0 | 0 | prior only | [0.025, 0.975] |

Model: Beta(1,1) prior; posterior Beta(1+successes, 1+failures).
Opportunities: 1; self-corrections: 0; uncertain: 1
Trend: insufficient_data

Hypothesis: Preliminary evidence of inconsistent spontaneous production; retrieval cause is unproven.

Unknowns:

- Insufficient evidence for negative forms (fewer than 3 attempts).
- Insufficient evidence for question forms (fewer than 3 attempts).
- Fewer than 5 spontaneous attempts; estimate is dominated by sparse evidence.

Recent evidence IDs: OBS-337d0a646c6a5bfa2e6c, OBS-1098f3d4b36cf7d470be, OBS-e3a6ddbdf18fb3c307f3, OBS-09f6c1211a33c8350522

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-337d0a646c6a5bfa2e6c

Session: SES-c4462c73aa2ca6b30c67; construction: present_perfect.duration
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: a3d0d7229140bafff56838b22ca39ba29c7e8d28dafc0809899659575338cfee
Source offsets: [38, 228) (Python Unicode characters)

Learner:

> I live here since 2021.

Reported correction (not automatically authoritative):

> I've lived here since 2021.

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> During spontaneous conversation about my current home, the learner said: "I live here since 2021." The teacher corrected this to: "I've lived here since 2021." The situation still continues.

## OBS-1098f3d4b36cf7d470be

Session: SES-c4462c73aa2ca6b30c67; construction: present_perfect.duration
Outcome: uncertain; mode: prompted; evidence: opportunity
Verifier: supported; support score: 3/4; pipeline: a3d0d7229140bafff56838b22ca39ba29c7e8d28dafc0809899659575338cfee
Source offsets: [872, 1089) (Python Unicode characters)

Learner:

> I started three years ago.

Verifier reason: Non-independent attempt; retain separately without accuracy counting

Source excerpt:

> During a prompted turn, the teacher asked: "How long have you worked there?" The learner answered: "I started three years ago." This was an opportunity; the target was not selected. The answer was grammatically valid.

## OBS-e3a6ddbdf18fb3c307f3

Session: SES-75258f2722c0123145b6; construction: present_perfect.duration
Outcome: correct; mode: spontaneous; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: a3d0d7229140bafff56838b22ca39ba29c7e8d28dafc0809899659575338cfee
Source offsets: [35, 203) (Python Unicode characters)

Learner:

> I've lived here for four years.

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> During spontaneous conversation about travel, the learner said: "I've lived here for four years." The situation still continues. The sentence was grammatically correct.

## OBS-09f6c1211a33c8350522

Session: SES-2802a620705d2ee889b3; construction: present_perfect.duration
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: a3d0d7229140bafff56838b22ca39ba29c7e8d28dafc0809899659575338cfee
Source offsets: [37, 225) (Python Unicode characters)

Learner:

> I work here since 2022.

Reported correction (not automatically authoritative):

> I've worked here since 2022.

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> During spontaneous conversation about ongoing work, the learner said: "I work here since 2022." The teacher corrected this to: "I've worked here since 2022." The situation still continues.
