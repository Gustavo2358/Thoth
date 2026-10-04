# Final benchmark qualification

Recommendation: **NOT_READY_FOR_PERSONAL_PILOT**

Run: EVAL-8fb1e72f16384f09; created: 2026-10-04T19:26:18.677832+00:00
Provider: text-input; extractor: codex-session; verifier: codex-session
Pipeline: `98148675ec2bb27b6df2c0407e0a30c98e1b103c73d5648df5f504119f682aa3`; dataset: `synthetic-1`

This report measures a frozen pipeline on synthetic holdout sessions. Offline rule results do not qualify an LLM or arbitrary real reports.

## Composition

- development: 8 sessions; 128 narrative blocks; 128 gold observations; 72 negative error controls; 56 adversarial blocks.
- calibration: 8 sessions; 128 narrative blocks; 128 gold observations; 72 negative error controls; 56 adversarial blocks.
- holdout_test: 8 sessions; 128 narrative blocks; 128 gold observations; 72 negative error controls; 56 adversarial blocks.

## Holdout results

| Metric | Result |
|---|---:|
| Exact-match precision | 100.0% |
| Recall | 100.0% |
| F1 | 100.0% |
| False positive observations | 0 |
| False negatives | 0 |
| Grammar-attempt precision | 100.0% |
| Accepted hallucinated provenance | 0 |
| Rejected invalid provenance proposals | 0 |
| Uncertain accepted observations | 24 |
| Abstention rate (uncertain / accepted) | 18.8% |
| Negative control blocks with false grammar error | 0 / 72 |
| Ambiguous blocks with uncertainty or no grammar fact | 100.0% |

## By construction

| Construction | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| article.indefinite | 16 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| auxiliary.chain | 12 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| duration.since_for | 8 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| modal_perfect.should_have | 16 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| present_perfect.continuous | 8 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| present_perfect.duration | 36 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| present_perfect.vs_simple_past | 12 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| question.do_support | 12 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| unclassified | 8 | 0 | 0 | 100.0% | 100.0% | 100.0% |

## By evidence type

| Evidence | Precision | Recall | FP | FN |
|---|---:|---:|---:|---:|
| explicit_correction | 100.0% | 100.0% | 0 | 0 |
| opportunity | 100.0% | 100.0% | 0 | 0 |
| other | 100.0% | 100.0% | 0 | 0 |
| self_correction | 100.0% | 100.0% | 0 | 0 |
| successful_use | 100.0% | 100.0% | 0 | 0 |

## Ambiguous and adversarial categories

| Category | Precision | Recall | FP | FN |
|---|---:|---:|---:|---:|
| ambiguous | 100.0% | 100.0% | 0 | 0 |
| correct_control | 100.0% | 100.0% | 0 | 0 |
| ended_context | 100.0% | 100.0% | 0 | 0 |
| irrelevant | n/a | n/a | 0 | 0 |
| multiple | 100.0% | 100.0% | 0 | 0 |
| negative_form | 100.0% | 100.0% | 0 | 0 |
| opportunity | 100.0% | 100.0% | 0 | 0 |
| paraphrase | n/a | n/a | 0 | 0 |
| positive | 100.0% | 100.0% | 0 | 0 |
| question | 100.0% | 100.0% | 0 | 0 |
| self_correction | 100.0% | 100.0% | 0 | 0 |
| style | 100.0% | 100.0% | 0 | 0 |
| successful | 100.0% | 100.0% | 0 | 0 |
| teacher_only | n/a | n/a | 0 | 0 |
| teacher_wrong | 100.0% | 100.0% | 0 | 0 |
| vocabulary | 100.0% | 100.0% | 0 | 0 |

## Outcome confusion matrix

Rows/columns use exact learner utterance + construction alignment; missed and extra are explicit.

- correct->correct: 60
- incorrect->incorrect: 44
- uncertain->uncertain: 24

## Support calibration

Calibration is fitted only on calibration, never development or holdout. Scores are tiers, not individual probabilities.

| Raw score | Calibration N | Calibration correct | Calibration precision | Wilson 95% interval | Holdout N | Holdout actual precision |
|---|---:|---:|---:|---|---:|---:|
| 1 | 8 | 8 | 100.0% | [0.676, 1.000] | 8 | 100.0% |
| 2 | 8 | 8 | 100.0% | [0.676, 1.000] | 8 | 100.0% |
| 3 | 68 | 68 | 100.0% | [0.947, 1.000] | 68 | 100.0% |
| 4 | 44 | 44 | 100.0% | [0.920, 1.000] | 44 | 100.0% |

Support scores are tiers, not calibrated individual probabilities; Brier and ECE deliberately not asserted.

### Verifier utility (calibration split)

```json
{
  "provenance_only": {
    "precision": 1.0,
    "recall": 1.0,
    "false_positives": 0,
    "negative_blocks_with_false_error": 0
  },
  "with_verifier": {
    "precision": 1.0,
    "recall": 1.0,
    "false_positives": 0,
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

Unmatched/missing observations: 0. The complete list is retained in benchmark-final.json. Below are examples; none were used to tune the frozen pipeline.


## Qualification

- Chat-assisted text responses were evaluated, but the same assistant authored the synthetic experiment; independent blinded real-model validation remains unproven.

To qualify an actual LLM, configure credentials securely, run development first, freeze that provider/pipeline separately, calibrate and evaluate a new untouched holdout. Human review remains advisable before longitudinal ingestion.
