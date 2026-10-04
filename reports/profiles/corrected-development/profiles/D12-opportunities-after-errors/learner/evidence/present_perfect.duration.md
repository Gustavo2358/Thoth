# Learner State

Sessions: 6; accepted observations: 12

Facts below are deterministic. Interpretations are hypotheses, not diagnoses.

- Only supported grammatical attempts enter accuracy counts.
- Reports may be selective and attempts correlated: credible intervals are conditional on the independence model, not full real-world certainty.
- Opportunities and self-corrections are recorded separately; no inference of avoidance from a single event.

## Present perfect — duration (`present_perfect.duration`)

Sessions observed: 6; last seen: 2026-02-05

| Production mode | Successes | Failures | Posterior mean | 95% credible interval |
|---|---:|---:|---:|---|
| spontaneous | 4 | 5 | 0.455 | [0.187, 0.738] |
| prompted | 0 | 0 | prior only | [0.025, 0.975] |
| controlled | 0 | 0 | prior only | [0.025, 0.975] |
| unknown | 0 | 0 | prior only | [0.025, 0.975] |

Model: Beta(1,1) prior; posterior Beta(1+successes, 1+failures).
Opportunities: 3; self-corrections: 0; uncertain: 3
Trend: insufficient_data

Hypothesis: Preliminary evidence of inconsistent spontaneous production; retrieval cause is unproven.
Mode comparison: Insufficient evidence of a prompted/controlled versus spontaneous gap.
Recent failed spontaneous evidence IDs: OBS-1e81635282bbd7765b75, OBS-528f9a2f2308c02fe006, OBS-1f5013240009978083ac, OBS-ce7116919b0ac91944de, OBS-69b3d692fa904a2e6544

Unknowns:

- Insufficient evidence for spontaneous negative forms (fewer than 3 attempts).
- Insufficient evidence for spontaneous question forms (fewer than 3 attempts).

Recent evidence IDs: OBS-ce7116919b0ac91944de, OBS-69b3d692fa904a2e6544, OBS-07d375df6c5c0e657315, OBS-fe303112397e5d3defa7, OBS-6822fe3b2eb42676103c

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-1e81635282bbd7765b75

Session: SES-ff894204705ec987a7f2; construction: present_perfect.duration
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [63, 240) (Python Unicode characters)

Learner:

> I live here since 2021.

Reported correction (not automatically authoritative):

> I've lived here since 2021.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "I live here since 2021." The teacher corrected this to: "I've lived here since 2021." The situation still continues.

## OBS-3a8fd38e09803c6c22ca

Session: SES-ff894204705ec987a7f2; construction: present_perfect.duration
Outcome: correct; mode: spontaneous; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [242, 381) (Python Unicode characters)

Learner:

> I've lived here since 2021.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During spontaneous conversation, the learner said: "I've lived here since 2021." The sentence was correct in the reported context.

## OBS-f4b7276a37f2d71b33e4

Session: SES-ff894204705ec987a7f2; construction: present_perfect.duration
Outcome: correct; mode: spontaneous; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [383, 522) (Python Unicode characters)

Learner:

> I've lived here since 2021.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 3. During spontaneous conversation, the learner said: "I've lived here since 2021." The sentence was correct in the reported context.

## OBS-a28588faacebb148c5f1

Session: SES-d0d08b80b4affe5aa9d6; construction: present_perfect.duration
Outcome: correct; mode: spontaneous; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [63, 202) (Python Unicode characters)

Learner:

> I've lived here since 2021.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "I've lived here since 2021." The sentence was correct in the reported context.

## OBS-eaf3bef15be49fea71bb

Session: SES-d0d08b80b4affe5aa9d6; construction: present_perfect.duration
Outcome: correct; mode: spontaneous; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [204, 343) (Python Unicode characters)

Learner:

> I've lived here since 2021.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During spontaneous conversation, the learner said: "I've lived here since 2021." The sentence was correct in the reported context.

## OBS-528f9a2f2308c02fe006

Session: SES-d0d08b80b4affe5aa9d6; construction: present_perfect.duration
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [345, 522) (Python Unicode characters)

Learner:

> I live here since 2021.

Reported correction (not automatically authoritative):

> I've lived here since 2021.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 3. During spontaneous conversation, the learner said: "I live here since 2021." The teacher corrected this to: "I've lived here since 2021." The situation still continues.

## OBS-1f5013240009978083ac

Session: SES-479dfefd906a0378fee3; construction: present_perfect.duration
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [63, 240) (Python Unicode characters)

Learner:

> I live here since 2021.

Reported correction (not automatically authoritative):

> I've lived here since 2021.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "I live here since 2021." The teacher corrected this to: "I've lived here since 2021." The situation still continues.

## OBS-ce7116919b0ac91944de

Session: SES-479dfefd906a0378fee3; construction: present_perfect.duration
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [242, 419) (Python Unicode characters)

Learner:

> I live here since 2021.

Reported correction (not automatically authoritative):

> I've lived here since 2021.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During spontaneous conversation, the learner said: "I live here since 2021." The teacher corrected this to: "I've lived here since 2021." The situation still continues.

## OBS-69b3d692fa904a2e6544

Session: SES-479dfefd906a0378fee3; construction: present_perfect.duration
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [421, 598) (Python Unicode characters)

Learner:

> I live here since 2021.

Reported correction (not automatically authoritative):

> I've lived here since 2021.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 3. During spontaneous conversation, the learner said: "I live here since 2021." The teacher corrected this to: "I've lived here since 2021." The situation still continues.

## OBS-07d375df6c5c0e657315

Session: SES-280b83307a5abda3dbb0; construction: present_perfect.duration
Outcome: uncertain; mode: spontaneous; evidence: opportunity
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [63, 226) (Python Unicode characters)

Learner:

> That happened earlier.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "That happened earlier." This was an opportunity for present_perfect.duration; target was not selected.

## OBS-fe303112397e5d3defa7

Session: SES-65e2747dc7ef31f91c07; construction: present_perfect.duration
Outcome: uncertain; mode: spontaneous; evidence: opportunity
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [63, 226) (Python Unicode characters)

Learner:

> That happened earlier.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "That happened earlier." This was an opportunity for present_perfect.duration; target was not selected.

## OBS-6822fe3b2eb42676103c

Session: SES-cca719f3d8da2d3faf66; construction: present_perfect.duration
Outcome: uncertain; mode: spontaneous; evidence: opportunity
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [63, 226) (Python Unicode characters)

Learner:

> That happened earlier.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "That happened earlier." This was an opportunity for present_perfect.duration; target was not selected.
