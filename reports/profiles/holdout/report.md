# Validação de decisões por perfil

Split: holdout; 8/8 perfis aprovados; 133/133 verificações aprovadas.

Escopo: gold IR → persistência → learner state → Evidence Packs → lesson brief.
Extração LLM não executada. Ganho de aprendizado não medido. Prontidão real: NOT_ESTABLISHED.

| Perfil | Resultado | Conclusão esperada |
|---|---|---|
| [H01-repeated-mixed](profiles/H01-repeated-mixed/learner/next-lesson.md) | PASS | Erros em duas datas com algum sucesso: prática, apesar de exercícios perfeitos. |
| [H02-observed-strength](profiles/H02-observed-strength/learner/next-lesson.md) | PASS | Acertos distribuídos: força observada, mantendo lacunas de perguntas e negações. |
| [H03-recovered-modal](profiles/H03-recovered-modal/learner/next-lesson.md) | PASS | Recuperação em outra construção: reconhecer histórico sem insistir no erro antigo. |
| [H04-declining-duration](profiles/H04-declining-duration/learner/next-lesson.md) | PASS | Recaída em since/for deve sobrepor força histórica. |
| [H05-controlled-gap](profiles/H05-controlled-gap/learner/next-lesson.md) | PASS | Bom desempenho controlado com falhas espontâneas não prova causa cognitiva. |
| [H06-unresolved](profiles/H06-unresolved/learner/next-lesson.md) | PASS | Contexto ambíguo, paráfrases e autocorreção: coletar, sem inventar falhas. |
| [H07-single-failed-day](profiles/H07-single-failed-day/learner/next-lesson.md) | PASS | Uma aula ruim mais três aulas controladas não prova repetição espontânea. |
| [H08-negative-transfer](profiles/H08-negative-transfer/learner/next-lesson.md) | PASS | Negação controlada não elimina lacuna de negação em conversa. |

## Falhas

Nenhuma falha nos critérios pré-definidos.

## Limites

- Gold IR bypasses the LLM extractor and verifier.
- Dataset and expectations share an author; holdout is reserved execution, not independent blinded review.
- Synthetic outcomes do not measure generalization, retention or causal learning gain.
