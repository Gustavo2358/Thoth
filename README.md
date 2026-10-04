# Thoth

MVP local para transformar relatórios de speaking em evidências rastreáveis, acumular o histórico de produção e preparar a próxima aula. A interface é uma CLI em Python; não há frontend, áudio, autenticação, vector database ou framework de agentes.

**Status: `NOT_READY_FOR_PERSONAL_PILOT`.** O software funciona, mas a avaliação assistida por esta conversa compartilha autor com os dados sintéticos. Os resultados não demonstram generalização para relatórios reais. Consulte [o relatório final](reports/benchmark-final.md) e [a análise do experimento](reports/experiment.md).

## Instalação e quickstart

Requer Python 3.11+; instalação e testes verificados com Python 3.12 em Linux. Execute na raiz deste checkout:

```bash
bash scripts/setup.sh
source .venv/bin/activate
learner ingest examples/session-01.md --provider offline --date 2026-01-01
learner ingest examples/session-02.md --provider offline --date 2026-01-08
learner ingest examples/session-03.md --provider offline --date 2026-01-15
learner state
learner next-lesson
pytest -q
```

`requirements.lock` fixa as versões usadas. A instalação não altera esse arquivo nem as declarações do projeto. O baseline offline aceita um dialeto restrito de relatórios com blocos narrativos e citações atribuídas (`The learner said: "..."`). Serve para demonstrar o fluxo e testar a infraestrutura; não interpreta arbitrariamente toda a língua inglesa. O provider padrão agora é **`manual`**: o runtime real do MVP usa sua assinatura do ChatGPT, sem API key ou chamadas pagas. `--provider` e `--llm` são aliases.

Os exemplos resultam em 3 sessões e 11 observações, com dificuldades preliminares em duração no present perfect e modal perfect. Os produtos incluem intervalos largos e `insufficient_data` para tendência. Exemplos de saída persistidos para revisão estão em [examples/generated](examples/generated).

Os argumentos globais precedem o comando:

```bash
learner --db data/experiment.db --artifacts artifacts/experiment ingest examples/session-01.md --provider offline
learner history SES-<id>
learner reprocess SES-<id> --provider offline
```

Reprocessar acrescenta uma run e muda somente o ponteiro ativo. O raw e todas as extrações anteriores permanecem auditáveis; uma falha de extração não troca a run ativa. Reingerir o mesmo conteúdo não duplica sessões ou tentativas. Duas aulas com texto byte-a-byte idêntico são consideradas a mesma sessão; diferencie o conteúdo com o cabeçalho da aula. A data padrão é a data local na primeira ingestão; para um histórico reproduzível, informe `--date`.

## Arquitetura

```text
arquivo UTF-8 preservado
  → LLMPort (ManualChatGPTAdapter, OpenAIAdapter ou baseline offline)
  → prompt / JSON schema / Proposal[]
  → normalização de IDs + provenance literal
  → verifier com prompt separado
  → Observation IR + sinais determinísticos de suporte
  → SQLite (raw imutável, runs imutáveis, ponteiro ativo)
  → engine determinístico
  → learner-state.json/.md + Evidence Packs + next-lesson.md
```

`contracts.py` contém contratos Pydantic estritos. Campos inesperados, incluindo `confidence`, são rejeitados. `pipeline.py` não consulta o learner state para classificar uma observação. `engine.py` consome apenas Observations e datas das sessões; não depende de provider, relatório, rede ou LLM. `storage.py` usa SQLite e triggers de imutabilidade, sem ORM ou migrações desnecessárias. A versão da base é verificada com `PRAGMA user_version`.

Oito famílias canônicas e `unclassified` estão em `contracts.py`. São versionados schema, taxonomia, prompts e implementações; hashes invalidam calibração após mudanças no pipeline. Aliases conhecidos são normalizados; strings livres desconhecidas viram `unclassified` e não geram contagens gramaticais.

`llm.py` constrói um único payload lógico: messages e JSON schema estrito. Manual e OpenAI usam esse mesmo construtor, com testes de igualdade tanto para extractor quanto para verifier. O arquivo manual renderiza esses mesmos messages e o contrato de saída para copiar no ChatGPT; os campos HTTP de transporte (modelo API, temperatura) são específicos do provider. A experiência do ChatGPT não oferece necessariamente os mesmos controles de amostragem, contexto ou versão do modelo da API.

## OpenAI e endpoints compatíveis

Configure `THOTH_API_KEY` de forma segura no ambiente. Não coloque a chave no repositório, em respostas de benchmark ou em relatórios. Uma `OPENAI_API_KEY` já existente também é aceita. Variáveis opcionais:

| Variável | Padrão | Uso |
|---|---|---|
| `THOTH_MODEL` | `gpt-4.1-mini` | Extractor |
| `THOTH_VERIFIER_MODEL` | Modelo do extractor | Verifier |
| `THOTH_BASE_URL` | `https://api.openai.com/v1` | Endpoint compatível com Chat Completions e JSON schema |

```bash
learner ingest minha-sessao.md --provider openai --date 2026-10-04
learner ingest minha-sessao.md --provider openai --model MODELO --verifier-model OUTRO_MODELO
```

São usados structured outputs, schema estrito, temperatura zero, TLS verificado e chamadas separadas. O verifier recebe somente excerpt e fatos propostos, sem raciocínio do extractor ou histórico do aluno. Concordância entre chamadas é um sinal, não prova absoluta. Nem todo endpoint/modelo compatível suporta o mesmo formato; refusals, truncamento e erros interrompem a run. Não há fallback silencioso. O adapter foi testado com transporte HTTP simulado; nenhuma chamada paga à API foi executada neste trabalho.

## ManualChatGPTAdapter: uso real com sua assinatura

Não precisa de API key. A aplicação gera o prompt; você o copia para o ChatGPT e devolve a resposta original. Use conversas novas, sem gold, learner state ou correções suas. Para a verificação, envie somente o novo prompt independente; não acrescente o raciocínio do extractor. Informe em `--model` o nome do modelo que aparece na experiência que está usando; o sistema registra esse nome como declaração do operador, sem inventar uma identidade de modelo.

```bash
learner ingest minha-sessao.md --llm manual --interactive \
  --model "ChatGPT / MODELO_SELECIONADO" --responses-dir data/minhas-interacoes
```

O terminal mostra messages, documento e schema. Primeiro devolva a resposta do extractor `{"observations": [...]}`; depois responda aos prompts de verifier (`supported`/`unsupported`/`uncertain` e reason). Termine cada paste com uma linha `END_JSON`, ou Ctrl+D. Sem resposta, o request permanece pending. Sem `--interactive`, os prompts são salvos para preencher por arquivos, e o comando retorna pending em vez de chamar API.

**Nunca edite a resposta do ChatGPT antes da avaliação.** O adapter salva `response.txt` antes de fazer parsing, inclusive para JSON inválido, campos extras ou markdown fences. Não remove fences, não repara JSON e não sobrescreve uma resposta existente com conteúdo diferente. A validação exige o mesmo schema emitido para a API, inclusive campos opcionais explicitamente `null`. Para uma nova tentativa, preserve o ensaio anterior e use um novo diretório de interações. Uma resposta errada é um resultado medido, não algo a consertar silenciosamente.

### Benchmark por arquivos, com retomada

```bash
learner benchmark --llm manual --model "ChatGPT / MODELO_SELECIONADO" \
  --responses-dir data/manual-benchmark --export requests/
```

Gera arquivos como `requests/001-extractor.txt`, `002-extractor.txt` e `manifest.json`, sem labels. Copie cada prompt para o ChatGPT e salve a **resposta original** em `responses/001-extractor.txt` etc., mantendo os nomes. Não há envelope JSON para criar à mão.

```bash
learner benchmark --llm manual --model "ChatGPT / MODELO_SELECIONADO" \
  --responses-dir data/manual-benchmark --import responses/ --export requests/
```

Essa execução importa as respostas e exporta todos os verifier prompts necessários para as extrações já disponíveis. Copie os novos `NNN-verifier.txt` para conversas independentes, salve as respectivas respostas em `responses/`, e reexecute o mesmo comando. Respostas já importadas são idempotentes. Se há respostas ainda pendentes, o exit code é 2; falhas de schema concluídas dão 1; uma avaliação completa sem falhas de schema dá 0. A documentação de métricas distingue pending de abstenção do modelo.

Não é possível preparar verifier prompts antes de existir a extração, pois eles contêm as observations efetivamente propostas. Não usamos gold para fabricar propostas. Se a extração é inválida, aquela sessão é registrada como falha, sem gerar observations artificiais ou pular a sessão no denominador. JSON inválido em um verifier também invalida a sessão para persistência/contagens, preservando todas as interações e falhas. Na aplicação, uma run incompleta/inválida não troca a run ativa do histórico.

Trocar `--model`, verifier ou desenho de avaliação exige um diretório de exchange diferente. O diretório padrão é `data/manual-chat`, ignorado pelo Git. A assinatura do ChatGPT não é integrada automaticamente: o transporte é sua cópia e colagem no ChatGPT, sem automação de login ou consumo de API.

### Auditoria

```text
data/manual-benchmark/
  exchange.json
  cases/<request-hash>/
    request.json          # payload lógico, modelo, mode, versões e hashes
    request.txt           # texto exato para o ChatGPT
    response.txt          # resposta original, inclusive inválida
    capture.json          # hash da resposta original
    parsed.json           # apenas quando o parsing/contrato passa
    validation.json       # sucesso ou erros do contrato

reports/manual/runs/<run>/cases/<session>/
  metadata.json           # modelo/mode, pipeline e dataset
  request.txt
  response.txt
  parsed.json             # observations aceitas pelo pipeline
  gold.json
  result.json
  interactions/           # cada extractor/verifier com seu raw e parsing
```

Pending não entra nos denominadores de qualidade; aparece em case_counts/coverage, sem calibração ou recomendação final até completar o split. Respostas inválidas entram como falhas de schema e observações gold perdidas, com FN/recall reportados. Arquivos de gold ficam somente nos artifacts internos de avaliação, separados do diretório exportado para o modelo.

Calibração via manual-chat valida **este pipeline + estes prompts + o modelo disponível nessa experiência do ChatGPT**. Ela não se transfere automaticamente para API ou outro modelo. Um ensaio manual com gold independente pode qualificar o runtime sem nenhuma API. `--evaluation-design independent` registra sua declaração sobre o desenho experimental; não certifica automaticamente cegamento. Use essa declaração somente quando os labels forem independentes da inferência e o holdout realmente reservado. O padrão é `unverified`.

O adapter `text` antigo continua disponível para compatibilidade com os envelopes de `benchmark/chat-evaluation/qualified/`. Esse arquivo registra o ensaio anterior assistido nesta conversa, com decisões compartilhando autor e templates com gold. Não constitui avaliação independente. `scripts/assemble_chat_responses.py` é um formatter daquele ensaio e **não deve preencher novas respostas de ChatGPT manual**. Os resultados antigos foram preservados; seus freezes/calibrações foram invalidados pelo hash da implementação nova e não são reutilizados silenciosamente.

## Provenance, fatos e incerteza

Cada observação aceita tem offsets Unicode exatos para excerpt e fala do aluno. Apenas diferenças de whitespace são normalizadas; não há fuzzy matching, normalização semântica ou correção inventada. Excerpts ausentes/ambíguos, fala inexistente, correção ausente e comentários sem origem são rejeitados antes de persistir. A origem é verificada novamente ao reconstruir o estado.

A presença da frase não prova sozinha que a interpretação ou a atribuição de speaker esteja correta: essa qualidade depende do verifier e do benchmark. As Observations incertas permanecem auditáveis sem contaminar a contagem de tentativas. Oportunidades e autocorreções são contadas separadamente. Uma paráfrase correta não é failure da construção que o professor esperava.

O `raw_support_score` é a soma de quatro sinais booleanos do código:

1. Provenance válido.
2. Classificação canônica conhecida.
3. Verifier retornou `supported`.
4. Correção explícita presente no excerpt para `explicit_correction`.

O score **não é uma probabilidade** e não é escolhido pela LLM. Um ponto adicional por correção explícita mede um sinal disponível, não a autoridade infalível do professor. O report de calibração mede a precisão observada por bucket, com N e intervalo Wilson. Não reutilizamos mappings entre pipelines; `validate_calibration` rejeita hashes diferentes. Essas frequências são qualidade da classificação, não capacidade do aluno. Não entram no learner state como `confidence`.

Somente tentativas gramaticais apoiadas pelo verifier contam em acertos/erros. O modelo de accuracy é Beta(1,1) + successes/failures separados para spontaneous, prompted, controlled e unknown. Uma média 0,4 com 1 sucesso e 2 falhas significa posterior Beta(2,3), com intervalo 95% aproximadamente [0,068, 0,806]; não significa domínio estabelecido. A independência das tentativas e a representatividade dos relatórios são suposições, frequentemente imperfeitas.

Trend é descritivo: exige pelo menos 4 datas distintas e 5 tentativas espontâneas em cada metade temporal. Delta de accuracy >=0,20 indica improving; <=-0,20 declining; caso contrário stable. Dados insuficientes dão insufficient_data. Isso não é teste de significância.

Targets para a próxima aula exigem >=3 tentativas espontâneas, >=2 sessões observadas e >=2 falhas espontâneas nas últimas 3 sessões da construção. A ordenação considera falhas recentes. Construções com menos de 5 tentativas ou intervalo de largura >0,5 viram alvos de coleta, separados dos alvos de prática. Regras completas constam nos artifacts, junto aos IDs que sustentam as hipóteses.

## Dados e artifacts

```text
data/app.db                               # local, ignorado pelo Git
artifacts/sessions/<id>/raw.md             # fonte preservada
artifacts/sessions/<id>/runs/<run>/        # observations, audit, evidence-pack
artifacts/sessions/<id>/active-run.json
artifacts/learner/learner-state.json
artifacts/learner/learner-state.md
artifacts/learner/evidence/<construction>.md
artifacts/learner/next-lesson.md
benchmark/datasets/{development,calibration,holdout_test}/
benchmark/manifest.json                   # versão e hashes dos inputs/gold
reports/runs/<eval>/                      # qualification arquivada
reports/{benchmark-final.md,benchmark-final.json,calibration.json}
```

O source e a auditoria também ficam no SQLite. Os packs globais são produtos atuais regeneráveis; packs de sessões/runs permanecem históricos. Para responder “por que existe essa dificuldade?”, abra o pack da construção: ele contém contagens, quotes, correções reportadas, decisões do verifier, IDs e offsets. A reconstrução usa somente a run ativa de cada sessão, evitando duplicar tentativas em reprocessamentos.

## Benchmark e calibração

Existem 24 sessões, 384 gold observations e 384 blocos narrativos: 8 sessões/128 observations por split. Cada split tem 40 blocos com erros gold, 72 controles negativos de erro e 56 blocos adversariais; categorias se sobrepõem. Os golds são fixtures linguísticas explicitamente definidas, nunca inferência do pipeline. Há 8 famílias, múltiplos erros, controle de estilo/vocabulário, perguntas/negação, oportunidade, teacher-only, ambiguidade, teacher errado, irrelevância e emprego encerrado.

Os documentos e valores lexicais/temporais são diferentes entre splits, mas os templates gramaticais se repetem. O holdout não foi executado antes do congelamento; isso não o torna um estudo externo cego, especialmente no ensaio de chat solicitado. O escopo de anotação considera famílias-alvo locais; não pretende catalogar toda construção correta incidental.

```bash
# development: pode revelar problemas e orientar alterações
learner benchmark --provider offline --split development --output reports/my-development

# Somente depois de finalizar código/prompts/dataset:
learner freeze --provider offline --freeze-file reports/my-freeze.json
learner benchmark --provider offline --split qualify --freeze-file reports/my-freeze.json --output reports/my-qualification

# Para qualificação manual: use uma versão com casos novos reservados e
# mantenha modelo, desenho e diretório de exchange iguais em todas as etapas.
learner freeze --llm manual --dataset CAMINHO_DATASET_NOVO \
  --model "ChatGPT / MODELO_SELECIONADO" --evaluation-design independent \
  --responses-dir data/qualificacao-manual --freeze-file reports/manual-freeze.json
learner benchmark --llm manual --dataset CAMINHO_DATASET_NOVO \
  --model "ChatGPT / MODELO_SELECIONADO" --evaluation-design independent \
  --responses-dir data/qualificacao-manual --split qualify \
  --freeze-file reports/manual-freeze.json --export requests/qualificacao/
# Importe os raws e reexecute para completar calibration e depois holdout.
```

`qualify` ajusta buckets exclusivamente em calibration e depois avalia holdout_test. Exige freeze compatível e manifest intacto; outputs são arquivados por run, e os arquivos finais são ponteiros/cópias de conveniência. Não execute novamente o gerador de dataset para mascarar alteração de fixtures já qualificadas. Após expor os erros de um holdout, não use aquele split como novo teste cego de uma versão ajustada: crie uma nova versão e casos reservados diferentes.

API é opcional. Se futuramente mudar para API, faça development com `--provider openai`, configure modelos, congele esse pipeline com outro `--freeze-file` e qualifique com as mesmas flags/modelos. Não reutilize a calibração manual ou do baseline. Não há API key nem gasto de API no fluxo manual, offline ou nos testes.

Matching é um multiset one-to-one por sessão: posição exata da utterance + texto normalizado apenas em whitespace + construção + outcome + modo + evidence_type + issue_kind + feature + correção. Não há correspondência aproximada. O report distingue metrics de todas as observações das tentativas gramaticais; mostra FP/FN, provenance, abstenções, grupos, matriz de confusão e accuracy de outcome nos exemplos alinhados (JSON). Recall mede cobertura; sessões com zero predictions não são “testes aprovados”. Abstenção é uncertain / accepted, com missing gold reportado à parte.

Na avaliação assistida, todos os buckets tiveram 100% de precisão observada, mas dois possuem somente N=8. Isso não demonstra separação útil de suporte nem confiança generalizável. Brier/ECE estão explicitamente `null`: não apresentamos tiers como probabilidades individuais calibradas.

## Testes e limites atuais

Unitários e integração funcionam sem internet e sem LLM: schema, parsing HTTP simulado, provenance, deduplicação, speaker teacher-only, estatística, modes, trend, persistência, reprocessamento, artifacts, matching, calibração, freeze e CLI. Há testes metamórficos de ruído, ordem, texto irrelevante, formatação e remoção de correções.

O baseline offline perdeu cobertura fora de números/formatos estreitos, e concordar com a correção errada do professor é uma classe importante que o verifier precisa conter. O ensaio de chat foi perfeito nesse gold conhecido, mas não mediu generalização. Ainda faltam avaliação externa com inputs novos, gold revisado independentemente e um modelo/provider identificável. Use os dados de exemplo para explorar o software; mantenha revisão humana das evidências antes de construir histórico real.
