# Final benchmark qualification

Recommendation: **NOT_READY_FOR_PERSONAL_PILOT**

Run: EVAL-11bb6295e9364519; created: 2026-10-04T19:26:19.735806+00:00
Provider: offline-rules; extractor: narrative-baseline-1; verifier: independent-grammar-checks-1
Pipeline: `a3d0d7229140bafff56838b22ca39ba29c7e8d28dafc0809899659575338cfee`; dataset: `synthetic-1`

This report measures a frozen pipeline on synthetic holdout sessions. Offline rule results do not qualify an LLM or arbitrary real reports.

## Composition

- development: 8 sessions; 128 narrative blocks; 128 gold observations; 72 negative error controls; 56 adversarial blocks.
- calibration: 8 sessions; 128 narrative blocks; 128 gold observations; 72 negative error controls; 56 adversarial blocks.
- holdout_test: 8 sessions; 128 narrative blocks; 128 gold observations; 72 negative error controls; 56 adversarial blocks.

## Holdout results

| Metric | Result |
|---|---:|
| Exact-match precision | 95.8% |
| Recall | 71.9% |
| F1 | 82.1% |
| False positive observations | 4 |
| False negatives | 36 |
| Grammar-attempt precision | 100.0% |
| Accepted hallucinated provenance | 0 |
| Rejected invalid provenance proposals | 0 |
| Uncertain accepted observations | 24 |
| Abstention rate (uncertain / accepted) | 25.0% |
| Negative control blocks with false grammar error | 0 / 72 |
| Ambiguous blocks with uncertainty or no grammar fact | 100.0% |

## By construction

| Construction | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| article.indefinite | 12 | 0 | 4 | 100.0% | 75.0% | 85.7% |
| auxiliary.chain | 12 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| duration.since_for | 4 | 0 | 4 | 100.0% | 50.0% | 66.7% |
| modal_perfect.should_have | 16 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| present_perfect.continuous | 0 | 0 | 8 | n/a | 0.0% | 0.0% |
| present_perfect.duration | 20 | 0 | 16 | 100.0% | 55.6% | 71.4% |
| present_perfect.vs_simple_past | 8 | 0 | 4 | 100.0% | 66.7% | 80.0% |
| question.do_support | 12 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| unclassified | 8 | 4 | 0 | 66.7% | 100.0% | 80.0% |

## By evidence type

| Evidence | Precision | Recall | FP | FN |
|---|---:|---:|---:|---:|
| explicit_correction | 100.0% | 81.8% | 0 | 8 |
| opportunity | 100.0% | 100.0% | 0 | 0 |
| other | 75.0% | 75.0% | 4 | 4 |
| self_correction | 100.0% | 100.0% | 0 | 0 |
| successful_use | 100.0% | 60.0% | 0 | 24 |

## Ambiguous and adversarial categories

| Category | Precision | Recall | FP | FN |
|---|---:|---:|---:|---:|
| ambiguous | 50.0% | 50.0% | 4 | 4 |
| correct_control | 100.0% | 100.0% | 0 | 0 |
| ended_context | n/a | 0.0% | 0 | 4 |
| irrelevant | n/a | n/a | 0 | 0 |
| multiple | 100.0% | 66.7% | 0 | 8 |
| negative_form | 100.0% | 100.0% | 0 | 0 |
| opportunity | 100.0% | 100.0% | 0 | 0 |
| paraphrase | n/a | n/a | 0 | 0 |
| positive | 100.0% | 80.0% | 0 | 4 |
| question | 100.0% | 100.0% | 0 | 0 |
| self_correction | 100.0% | 100.0% | 0 | 0 |
| style | 100.0% | 100.0% | 0 | 0 |
| successful | 100.0% | 50.0% | 0 | 8 |
| teacher_only | n/a | n/a | 0 | 0 |
| teacher_wrong | n/a | 0.0% | 0 | 8 |
| vocabulary | 100.0% | 100.0% | 0 | 0 |

## Outcome confusion matrix

Rows/columns use exact learner utterance + construction alignment; missed and extra are explicit.

- correct->correct: 36
- correct->missed: 24
- extra->uncertain: 4
- incorrect->incorrect: 36
- incorrect->missed: 8
- uncertain->missed: 4
- uncertain->uncertain: 20

## Support calibration

Calibration is fitted only on calibration, never development or holdout. Scores are tiers, not individual probabilities.

| Raw score | Calibration N | Calibration correct | Calibration precision | Wilson 95% interval | Holdout N | Holdout actual precision |
|---|---:|---:|---:|---|---:|---:|
| 1 | 12 | 8 | 66.7% | [0.391, 0.862] | 12 | 66.7% |
| 2 | 4 | 4 | 100.0% | [0.510, 1.000] | 4 | 100.0% |
| 3 | 44 | 44 | 100.0% | [0.920, 1.000] | 44 | 100.0% |
| 4 | 36 | 36 | 100.0% | [0.904, 1.000] | 36 | 100.0% |

Support scores are tiers, not calibrated individual probabilities; Brier and ECE deliberately not asserted.

### Verifier utility (calibration split)

```json
{
  "provenance_only": {
    "precision": 0.8846153846153846,
    "recall": 0.71875,
    "false_positives": 12,
    "negative_blocks_with_false_error": 8
  },
  "with_verifier": {
    "precision": 0.9583333333333334,
    "recall": 0.71875,
    "false_positives": 4,
    "negative_blocks_with_false_error": 0
  },
  "interpretation": "Same-pipeline comparison on calibration data; agreement is an observable signal, not independent proof. A different verifier model is configurable."
}
```

## Matching and limitations

One-to-one multiset match within each session on exact learner character offset, whitespace-normalized utterance and correction, canonical construction, outcome, production mode, evidence type, issue kind, and feature. Predictions first undergo independent source-offset validation. No fuzzy matching. Identical quotes in different contexts cannot match each other. Per-construction precision/recall, not an inflated true-negative accuracy. Teacher-correction semantics must match too.

- Hand-authored gold and fixed narrative templates; lexical/time values and session documents are disjoint across splits, but grammatical templates overlap.
- The holdout is untouched by execution until pipeline freeze, but is not an independently blinded human study.
- Observations in a session are correlated. Bucket sample sizes are not independent students or real speaking sessions.
- Exact provenance prevents nonexistent utterances, but source presence alone cannot prove semantic or speaker attribution accuracy.
- Statistical learner accuracy is conditional on observed attempts; missing opportunities and selective teacher reporting cause sampling bias.
- No generalization to ASR/transcripts, arbitrary report phrasing, real student speech, or different pipeline versions has been demonstrated.

## Failures

Unmatched/missing observations: 40. The complete list is retained in benchmark-final.json. Below are examples; none were used to tune the frozen pipeline.

- holdout_test-00-0 / missing_observation: `present_perfect.duration` / correct / successful_use: “I've worked here for ten years.”
- holdout_test-00-0 / missing_observation: `present_perfect.continuous` / incorrect / explicit_correction: “I have working on the project for ten months.”
- holdout_test-00-0 / missing_observation: `present_perfect.continuous` / correct / successful_use: “I've been working on the project for ten months.”
- holdout_test-00-0 / missing_observation: `duration.since_for` / incorrect / explicit_correction: “I have lived here since ten years.”
- holdout_test-00-0 / missing_observation: `present_perfect.duration` / correct / successful_use: “I've worked here for 2012.”
- holdout_test-00-1 / unmatched_prediction: `unclassified` / uncertain / other: “I worked there for ten years.”
- holdout_test-00-1 / missing_observation: `present_perfect.duration` / uncertain / other: “I worked there for ten years.”
- holdout_test-00-1 / missing_observation: `present_perfect.duration` / correct / successful_use: “I've lived here since 2012.”
- holdout_test-00-1 / missing_observation: `present_perfect.vs_simple_past` / correct / successful_use: “I worked there for ten years.”
- holdout_test-00-1 / missing_observation: `article.indefinite` / correct / successful_use: “She is an engineer in Tokyo.”

## Qualification

- No actual LLM evaluation was executed: offline baseline quality is not evidence of real-model or real-report readiness.

To qualify an actual LLM, configure credentials securely, run development first, freeze that provider/pipeline separately, calibrate and evaluate a new untouched holdout. Human review remains advisable before longitudinal ingestion.
