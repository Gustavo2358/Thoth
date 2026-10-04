# Relatório do MVP Thoth

## Implemented

Aplicação Python instalável com CLI `learner`, contratos Pydantic, SQLite, extração estruturada, provenance literal com offsets Unicode, verifier separado, suporte computado, reprocessamento auditável e artifacts Markdown/JSON. Adapters: OpenAI-compatible, entrada de JSON por texto/arquivos e baseline offline restrito.

O estado usa somente Observations ativas. Não consulta LLM nem histórico para decidir o outcome de uma nova observação. Raw e runs antigas são preservados, inclusive quando uma nova extração fica vazia ou falha. Correções estilísticas, sugestões de vocabulário, autocorreções, oportunidades e ambiguidade não entram como erros gramaticais.

## Architecture

`raw → adapter/prompt/schema → Proposal[] → canonical IDs/provenance → verifier → Observation IR → SQLite → engine Beta-Binomial por modo → Learner State/Evidence Packs/Next Lesson Brief`.

A CLI funciona sem servidor. O adapter OpenAI usa HTTP/JSON schema direto, sem framework de IA. Verifier e extractor podem ter modelos diferentes. A separação de prompts é testada; não tratamos concordância como certeza. A entrada por texto registra o prompt completo, a resposta, autor e hashes para reprodução.

## Commands

Na raiz `/workspace/Thoth`:

```bash
bash scripts/setup.sh
source .venv/bin/activate
learner ingest examples/session-01.md --provider offline --date 2026-01-01
learner state
learner next-lesson
learner ingest examples/session-01.md --provider text --interactive --responses-dir data/manual
pytest -q
learner benchmark --provider text --responses-dir benchmark/chat-evaluation/qualified \
  --split qualify --freeze-file reports/chat-freeze.json --output reports/replay
```

O setup foi exercitado em um venv limpo, com dependências fixadas no lock, instalação editable e **37 testes aprovados**. Foram verificados casos de schema, provenance, deduplicação, conflitos/modos, Beta-Binomial, trend, persistência, reprocessamento, artifacts, CLI, matching, calibração, freeze, HTTP simulado e metamórficos. Não houve chamadas à API externa; o adapter OpenAI foi validado por transporte HTTP simulado.

## Synthetic benchmark

Dataset `synthetic-1`: **24 sessões, 384 blocos narrativos e 384 gold observations**, 8 famílias canônicas mais unclassified. Cada split (development, calibration, holdout_test) tem 8 sessões e 128 observations: 60 correct, 44 incorrect, 24 uncertain. Por split: 40 blocos contendo erros gold, 72 controles negativos de erro, 56 blocos adversariais. As categorias se sobrepõem.

Golds são decisões explícitas em fixtures linguísticas, não output inferido pelo pipeline. Incluem contextos encerrados, reformulações legítimas, professor errado, teacher-only, oportunidade não selecionada, autocorreção, múltiplos erros, questions/negation e ruído. Templates gramaticais se repetem entre splits, mas documentos, cidades, anos, durações e tópicos são diferentes. Isso reduz drasticamente a independência estatística e a validade externa.

O benchmark usa matching one-to-one estrito por posição exata da fala, texto, correção, construção, outcome, modo, evidence type, issue kind e feature. Presença de texto é revalidada. Frases idênticas em contextos diferentes não podem corresponder entre si. As métricas completas por construção/evidence_type/categoria e matriz de confusão constam no JSON final.

## Results

Pipeline/dataset congelados antes da execução do holdout. O extractor e o verifier não foram ajustados depois de ler as falhas do holdout. Correções posteriores limitaram-se à exportação de raw com CRLF e limpeza de packs atuais obsoletos, sem alterar extração, scoring, matching ou métricas congeladas.

| Avaliação no holdout | Precision | Recall | F1 | FP | FN | Provenance inválido aceito |
|---|---:|---:|---:|---:|---:|---:|
| Respostas assistidas por esta conversa | 100% | 100% | 100% | 0 | 0 | 0 |
| Baseline offline | 95,83% | 71,88% | 82,14% | 4 | 36 | 0 |

Ensaio assistido: 128 predictions, 104 tentativas gramaticais e 24 observações uncertain. Precision das tentativas: 100%; uncertain/accepted: 18,75%; controles negativos com erro gramatical falso: 0/72. Todas as ambiguidades tiveram uncertainty, sem outcome gramatical definido.

Baseline offline: 96 predictions, 72 tentativas gramaticais alinhadas corretamente, 24 uncertain. Precision de tentativas: 100%; recall de tentativas: 69,23%; uncertain/accepted: 25%; controles negativos com erro gramatical falso: 0/72. Seus 4 FPs são classificação unclassified em observações incertas, não failures adicionados ao estado.

O ensaio de chat usa minhas decisões como a LLM solicitada pelo usuário, com formatter mecânico para variantes repetidas. O assembler não lê gold nem usa o baseline para gerar outcomes. Porém **eu também escrevi os casos e seus labels**: portanto o ensaio não é independente, blind ou representativo de um provider/modelo de API. Reprodução do transcript prova replay e funcionamento do instrumento; não constitui nova inferência ou generalização. A limitação é explícita nos envelopes, nos artifacts e na recomendação automática.

## Calibration

Calibração ajustada exclusivamente no split calibration. Não há confidence inventado pela LLM. O raw score soma quatro booleanos: provenance, construção conhecida, verifier supported e presença de correção explícita no source.

| Score | N calibração assistida | Precisão observada | Wilson 95% |
|---|---:|---:|---|
| 1 | 8 | 100% | [0,676; 1,000] |
| 2 | 8 | 100% | [0,676; 1,000] |
| 3 | 68 | 100% | [0,947; 1,000] |
| 4 | 44 | 100% | [0,920; 1,000] |

Todos os buckets tiveram igual precisão observada. Logo o ensaio **não demonstrou que mais pontos distinguem qualidade melhor**. Os buckets de N=8 são especialmente fracos. As variantes correlacionadas também tornam esses intervalos otimistas. Não convertemos tiers em probabilidades individuais; Brier/ECE são `null` com justificativa. O artifact versionado contém pipeline, dataset, hashes, contagens, data e método, e o código rejeita reutilização em pipeline diferente.

No baseline, score 1 teve precisão de 66,67% (8/12); os outros buckets tiveram 100% em amostras pequenas. O verifier elevou a precisão de propostas provenance-valid de 88,46% para 95,83% no calibration e reduziu os blocos negativos com erro de 8 para 0. A avaliação assistida já começava em 100%, então não mediu ganho de precisão do verifier.

Accuracy do aluno é um conceito separado: Beta(1,1) + successes/failures, por production_mode. Em cada uma das duas famílias difíceis do exemplo, 1 sucesso e 2 falhas produzem Beta(2,3), média 0,4 e intervalo 95% [0,068; 0,806]. Isso exprime baixa quantidade de dados, sem afirmar mastery ou diagnóstico causal de retrieval.

## Failure analysis

O baseline reconhece somente uma gramática e um dialeto narrativo estreitos. Variações de números fora de `one` a `five`, como `ten years`, derrubaram a cobertura de duração/continuous e de since/for. Frases corretas acompanhadas de uma correção errada do professor foram conservadoramente rejeitadas, perdendo sucessos válidos. Isso ajudou a precisão gramatical, mas limitou recall e deixou o perfil incompleto.

Exemplos mantidos no report offline: uso correto “I've worked here for ten years.” ausente; erro “I have working on the project for ten months.” ausente; since/for em “I have lived here since ten years.” não reconhecido; ambiguidade “I worked there for ten years.” classificada como unclassified em vez da família-alvo incerta. Não alterei o pipeline congelado para corrigir essas falhas após o holdout.

Mesmo com provenance literal zero, um modelo pode atribuir ao aluno uma frase real dita pelo professor ou interpretar uma correção de estilo como erro. Presence/offsets garantem origem, não verdade semântica. Testes e verifier tratam essas classes, mas a taxa em sessões reais ainda não foi medida. Relatórios seletivos e tentativas correlacionadas também impedem usar o posterior como certeza objetiva sobre a capacidade global do aluno.

## Generated artifacts

As três sessões de exemplo foram realmente ingeridas e geraram 11 observações, estado reconstruído, packs e lesson brief. Snapshot versionável:

- [Learner state JSON](../examples/generated/learner/learner-state.json)
- [Learner state Markdown](../examples/generated/learner/learner-state.md)
- [Evidence Pack de duração](../examples/generated/learner/evidence/present_perfect.duration.md)
- [Next Lesson Brief](../examples/generated/learner/next-lesson.md)
- [Sessões, fontes e auditorias](../examples/generated/sessions)
- [Relatório final assistido](benchmark-final.md), [JSON](benchmark-final.json), [calibração](calibration.json)
- [Relatório offline](offline/benchmark-final.md)
- [Prompts e respostas do ensaio assistido](../benchmark/chat-evaluation/qualified)

São 544 arquivos selados de requests/responses: 16 prompts de extraction + 256 prompts de verification e suas respectivas respostas, entre calibration e holdout. As respostas têm schema validation e hashes de conteúdo. Runs de benchmark ficam arquivadas em `reports/runs`, permitindo inspecionar respostas, rejeições e falhas sem depender da apresentação final.

O lesson brief escolheu modal perfect e duração como prática principal por falhas espontâneas recentes repetidas em três sessões, e continuous/questions como coleta adicional. Ainda não declarou forças estáveis ou tendência.

## Recommendation

**`NOT_READY_FOR_PERSONAL_PILOT`** para construção automática de um histórico longitudinal real sem revisão.

O fluxo técnico e sua reprodução estão funcionais. A qualidade do baseline é limitada; a avaliação assistida compartilha autor e templates com o gold e não é uma validação externa. O próximo passo é reservar novos inputs variados, revisar labels independentemente e executar o adapter OpenAI (ou uma avaliação textual por outro operador/modelo), com pipeline congelado e calibração próprios. Até isso existir, o software pode ser explorado com exemplos e evidências revisadas manualmente, sem tratar os números observados no ensaio como confiança em sessões reais.
