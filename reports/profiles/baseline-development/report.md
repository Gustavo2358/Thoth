# Validação de decisões por perfil

Split: development; 7/14 perfis aprovados; 221/236 verificações aprovadas.

Escopo: gold IR → persistência → learner state → Evidence Packs → lesson brief.
Extração LLM não executada. Ganho de aprendizado não medido. Prontidão real: NOT_ESTABLISHED.

| Perfil | Resultado | Conclusão esperada |
|---|---|---|
| [D01-empty](profiles/D01-empty/learner/next-lesson.md) | PASS | Uma aula sem evidências não demonstra competência nem dificuldade. |
| [D02-sparse](profiles/D02-sparse/learner/next-lesson.md) | PASS | Um acerto isolado pede coleta, sem declarar domínio. |
| [D03-prompt-gap](profiles/D03-prompt-gap/learner/next-lesson.md) | FAIL | Acerta quando guiado, mas erra espontaneamente em dias distintos. |
| [D04-controlled-only](profiles/D04-controlled-only/learner/next-lesson.md) | PASS | Exercício controlado não comprova transferência para conversa. |
| [D05-clustered-errors](profiles/D05-clustered-errors/learner/next-lesson.md) | FAIL | Três erros na mesma aula mais exercício em outra não provam recorrência. |
| [D06-recovery](profiles/D06-recovery/learner/next-lesson.md) | FAIL | Erros antigos seguidos de três aulas corretas: melhora, sem dificuldade atual afirmada. |
| [D07-relapse](profiles/D07-relapse/learner/next-lesson.md) | FAIL | Muitos acertos históricos não anulam recaída recente nem autorizam força estável. |
| [D08-opportunities](profiles/D08-opportunities/learner/next-lesson.md) | PASS | Escolhas alternativas são oportunidades, sem erro nem diagnóstico de evitação. |
| [D09-self-repair](profiles/D09-self-repair/learner/next-lesson.md) | PASS | Autocorreções são evidência distinta de acerto ou erro independente. |
| [D10-style-ambiguity](profiles/D10-style-ambiguity/learner/next-lesson.md) | PASS | Preferência de estilo e contexto incerto não contaminam accuracy. |
| [D11-form-transfer](profiles/D11-form-transfer/learner/next-lesson.md) | FAIL | Perguntas corretas em exercício não cobrem perguntas espontâneas. |
| [D12-opportunities-after-errors](profiles/D12-opportunities-after-errors/learner/next-lesson.md) | FAIL | Oportunidades posteriores não apagam tentativas falhas ou suas citações. |
| [D13-competing-targets](profiles/D13-competing-targets/learner/next-lesson.md) | PASS | Priorizar duas dificuldades recorrentes mais frequentes e citar falhas reais. |
| [D14-same-day](profiles/D14-same-day/learner/next-lesson.md) | FAIL | Três relatos no mesmo dia não demonstram dificuldade longitudinal independente. |

## Falhas

- D03-prompt-gap: question.do_support/prompted or controlled gap described; esperado `True`, obtido `False`.
- D03-prompt-gap: question.do_support/practice justified by failed quotes on distinct dates; esperado `True`, obtido `False`.
- D05-clustered-errors: primary targets and rank; esperado `[]`, obtido `['present_perfect.duration']`.
- D05-clustered-errors: collect present_perfect.duration; esperado `True`, obtido `False`.
- D05-clustered-errors: present_perfect.duration/practice justified by failed quotes on distinct dates; esperado `True`, obtido `False`.
- D06-recovery: collect present_perfect.duration; esperado `True`, obtido `False`.
- D06-recovery: present_perfect.duration/historical errors distinguished; esperado `True`, obtido `False`.
- D07-relapse: observed strengths; esperado `[]`, obtido `['question.do_support']`.
- D11-form-transfer: collect modal_perfect.should_have; esperado `True`, obtido `False`.
- D11-form-transfer: modal_perfect.should_have/negative spontaneous coverage remains unknown; esperado `True`, obtido `False`.
- D11-form-transfer: modal_perfect.should_have/question spontaneous coverage remains unknown; esperado `True`, obtido `False`.
- D12-opportunities-after-errors: primary targets and rank; esperado `['present_perfect.duration']`, obtido `[]`.
- D14-same-day: primary targets and rank; esperado `[]`, obtido `['question.do_support']`.
- D14-same-day: collect question.do_support; esperado `True`, obtido `False`.
- D14-same-day: question.do_support/practice justified by failed quotes on distinct dates; esperado `True`, obtido `False`.

## Limites

- Gold IR bypasses the LLM extractor and verifier.
- Dataset and expectations share an author; holdout is reserved execution, not independent blinded review.
- Synthetic outcomes do not measure generalization, retention or causal learning gain.
