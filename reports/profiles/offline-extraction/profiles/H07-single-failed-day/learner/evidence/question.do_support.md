# Learner State

Sessions: 4; accepted observations: 12

Facts below are deterministic. Interpretations are hypotheses, not diagnoses.

- Only supported grammatical attempts enter accuracy counts.
- Reports may be selective and attempts correlated: credible intervals are conditional on the independence model, not full real-world certainty.
- Opportunities and self-corrections are recorded separately; no inference of avoidance from a single event.

## Question formation — do support (`question.do_support`)

Sessions observed: 4; last seen: 2026-01-22

| Production mode | Successes | Failures | Posterior mean | 95% credible interval |
|---|---:|---:|---:|---|
| spontaneous | 0 | 3 | 0.200 | [0.006, 0.602] |
| prompted | 0 | 0 | prior only | [0.025, 0.975] |
| controlled | 9 | 0 | 0.909 | [0.692, 0.997] |
| unknown | 0 | 0 | prior only | [0.025, 0.975] |

Model: Beta(1,1) prior; posterior Beta(1+successes, 1+failures).
Opportunities: 0; self-corrections: 0; uncertain: 0
Trend: insufficient_data

Hypothesis: Errors concentrated on one recent date; collect more independent spontaneous evidence.
Mode comparison: Prompted/controlled successes exceed spontaneous accuracy in the observed contexts. Task and context differences may explain this; no retrieval diagnosis.
Recent failed spontaneous evidence IDs: OBS-98588c9a58ea44b9ea51, OBS-b59860b1d3c140c95936, OBS-f5968d1e2e3a5feb8cb3

Unknowns:

- Insufficient evidence for spontaneous negative forms (fewer than 3 attempts).
- Fewer than 5 spontaneous attempts; estimate is dominated by sparse evidence.

Recent evidence IDs: OBS-f191369a669dd390aa27, OBS-e58d6fcb6de4071cd63a, OBS-fdd7a8ad1d27f30508ad, OBS-e9f3869a51fec2fe7d10, OBS-57596588a937472c29c7

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-98588c9a58ea44b9ea51

Session: SES-7b0ac8a69af07c0aa313; construction: question.do_support
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: 6ed6b2e8bbec5ddf33c96acb75b84bdc30ddd0c724838a4eb939b1fa6555649a
Source offsets: [54, 214) (Python Unicode characters)

Learner:

> Where you work?

Reported correction (not automatically authoritative):

> Where do you work?

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "Where you work?" The teacher corrected this to: "Where do you work?" The situation still continues.

## OBS-b59860b1d3c140c95936

Session: SES-7b0ac8a69af07c0aa313; construction: question.do_support
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: 6ed6b2e8bbec5ddf33c96acb75b84bdc30ddd0c724838a4eb939b1fa6555649a
Source offsets: [216, 376) (Python Unicode characters)

Learner:

> Where you work?

Reported correction (not automatically authoritative):

> Where do you work?

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> Block 2. During spontaneous conversation, the learner said: "Where you work?" The teacher corrected this to: "Where do you work?" The situation still continues.

## OBS-f5968d1e2e3a5feb8cb3

Session: SES-7b0ac8a69af07c0aa313; construction: question.do_support
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: 6ed6b2e8bbec5ddf33c96acb75b84bdc30ddd0c724838a4eb939b1fa6555649a
Source offsets: [378, 538) (Python Unicode characters)

Learner:

> Where you work?

Reported correction (not automatically authoritative):

> Where do you work?

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> Block 3. During spontaneous conversation, the learner said: "Where you work?" The teacher corrected this to: "Where do you work?" The situation still continues.

## OBS-0992b6751de504509ae2

Session: SES-ac202a796e39647486d3; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: 6ed6b2e8bbec5ddf33c96acb75b84bdc30ddd0c724838a4eb939b1fa6555649a
Source offsets: [54, 183) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> Block 1. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-b18b42ece6a1c83ee2dd

Session: SES-ac202a796e39647486d3; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: 6ed6b2e8bbec5ddf33c96acb75b84bdc30ddd0c724838a4eb939b1fa6555649a
Source offsets: [185, 314) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> Block 2. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-22dfc8cb421e42a3dc46

Session: SES-ac202a796e39647486d3; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: 6ed6b2e8bbec5ddf33c96acb75b84bdc30ddd0c724838a4eb939b1fa6555649a
Source offsets: [316, 445) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> Block 3. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-90a5beb6627a62eb69a2

Session: SES-970ae27f38fc8a59f85b; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: 6ed6b2e8bbec5ddf33c96acb75b84bdc30ddd0c724838a4eb939b1fa6555649a
Source offsets: [54, 183) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> Block 1. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-f191369a669dd390aa27

Session: SES-970ae27f38fc8a59f85b; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: 6ed6b2e8bbec5ddf33c96acb75b84bdc30ddd0c724838a4eb939b1fa6555649a
Source offsets: [185, 314) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> Block 2. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-e58d6fcb6de4071cd63a

Session: SES-970ae27f38fc8a59f85b; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: 6ed6b2e8bbec5ddf33c96acb75b84bdc30ddd0c724838a4eb939b1fa6555649a
Source offsets: [316, 445) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> Block 3. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-fdd7a8ad1d27f30508ad

Session: SES-6d0d71d80c58c8157961; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: 6ed6b2e8bbec5ddf33c96acb75b84bdc30ddd0c724838a4eb939b1fa6555649a
Source offsets: [54, 183) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> Block 1. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-e9f3869a51fec2fe7d10

Session: SES-6d0d71d80c58c8157961; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: 6ed6b2e8bbec5ddf33c96acb75b84bdc30ddd0c724838a4eb939b1fa6555649a
Source offsets: [185, 314) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> Block 2. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-57596588a937472c29c7

Session: SES-6d0d71d80c58c8157961; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: 6ed6b2e8bbec5ddf33c96acb75b84bdc30ddd0c724838a4eb939b1fa6555649a
Source offsets: [316, 445) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Independent grammatical predicate and source agree

Source excerpt:

> Block 3. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.
