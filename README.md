# Thoth

Thoth é um learner model local para produção de inglês em speaking. Ele observa relatórios de conversas e descobre padrões específicos daquela pessoa. As habilidades linguísticas são descritas livremente; nenhuma lista de construções existe no runtime.

O loop é:

```text
relatório → observations revisadas → embedding local → candidatos
          → resolução semântica → padrões recorrentes
          → learner state → brief para a próxima conversa
```

O banco começa vazio. Exemplos e benchmarks sintéticos não são carregados automaticamente. O software não mede ganho de aprendizado nem está qualificado para uso sem revisão. A recomendação atual é um piloto pessoal supervisionado: [relatório experimental](reports/final.md).

## Instalação

Python 3.12+ em Linux/macOS, com acesso à internet durante a instalação:

```bash
bash scripts/setup.sh
source .venv/bin/activate
thoth state
```

O setup instala dependências fixadas, o modelo oficial `en_core_web_md` do spaCy e roda os testes. O download do modelo tem aproximadamente 33,5 MB. A instalação limpa foi testada com Python 3.12. Embeddings e consultas posteriores funcionam localmente, sem rede. A rede continua necessária para usar ChatGPT ou a API opcional.

O modelo fornece vetores de palavras de 300 dimensões. Thoth calcula a média dos tokens conhecidos e normaliza o vetor. É uma solução simples, com limitações de representação contextual medidas no benchmark. O fingerprint combina a capacidade de produção e a intenção comunicativa normalizadas; não inclui a frase bruta nem o resultado da tentativa. Não há segundo modelo ou fallback remoto.

SQLite guarda relatórios, observations, memberships, decisões e vetores float32. A busca é um produto escalar exato sobre os poucos vetores locais. Isso dispensa extensão SQLite, servidor vetorial e índices adicionais. O hash dos pesos permite detectar uma troca acidental de modelo. Copiar o banco, os arquivos de intercâmbio e reinstalar as mesmas dependências basta para continuar; artifacts podem ser regenerados.

## Sessões com sua assinatura do ChatGPT

Prepare um relatório depois da conversa contendo trechos atribuídos ao aluno, contexto/intenção, indicação de produção espontânea ou guiada e correções realmente feitas. Inclua produções bem-sucedidas, além de dificuldades. O relatório pode ser em português ou inglês; as descrições pedagógicas estruturadas devem ser em inglês para o embedding local.

Não precisa de transcrição exata do áudio. Preserve o relatório como fonte pedagógica e indique quando a atribuição ou o modo forem desconhecidos. [Um exemplo](examples/session-01.md) mostra o formato livre; não existe template obrigatório.

```bash
thoth ingest minha-sessao.md --date 2026-10-04 --model 'ChatGPT / nome do modelo usado'
```

O comando informa um `request.txt` e um `response.txt` pendentes em `data/exchange/<hash>/`. A primeira chamada faz extração; depois vêm revisão e resolução, conforme necessário.

1. Copie o conteúdo completo de `request.txt` para ChatGPT.
2. Salve a resposta original em `response.txt`, sem editar nem remover cercas Markdown se o modelo as produziu. O contrato exige JSON puro; uma resposta inválida deve aparecer como falha.
3. Repita o mesmo comando. Respostas anteriores são reutilizadas e a próxima interação fica pendente.
4. Continue até a sessão terminar. Uma pendência retorna código 2; validação inválida retorna 1; sucesso retorna 0.

A sessão inteira só é gravada quando todas as etapas terminam. Repetir o mesmo relatório/data é idempotente. Ingira em ordem cronológica. Relatórios diferentes na mesma data não contam como recorrência longitudinal independente.

Também é possível colar respostas no terminal:

```bash
thoth ingest minha-sessao.md --date 2026-10-04 --model 'ChatGPT / nome do modelo usado' --interactive
```

Finalize cada resposta com `END_JSON`. Para importar arquivos, nomeie cada resposta `<hash-da-request>.txt` e use:

```bash
thoth import respostas/ --model 'ChatGPT / nome do modelo usado'
```

Depois retome o comando de ingestão. O modo por arquivos e o interativo usam o mesmo adapter e o mesmo payload lógico. A identidade do modelo é uma declaração do operador, não uma identificação automática. Não existe integração programática com sua assinatura ChatGPT.

Requests, respostas originais, SHA-256 e parsed JSON ficam disponíveis para auditoria. Respostas anteriores não podem ser sobrescritas. Se quiser repetir uma interação inválida, use outra pasta `--exchange`. Uma associação já gravada não tem comando de edição: um erro confirmado exige reconstruir um banco novo a partir dos relatórios, com outro intercâmbio. Revise as respostas antes de concluir a ingestão durante o piloto.

## Estado, padrões e próxima conversa

```bash
thoth patterns
thoth state
thoth next-lesson
```

Os comandos escrevem:

```text
artifacts/
  learner-state.json
  learner-state.md
  next-lesson.md
  patterns/PAT-<id>.md
  sessions/SES-<id>/
    report.md
    audit.json
    evidence-pack.md
```

O Session Evidence Pack aponta trechos da fonte. O Pattern Evidence Pack mostra significado proposto, todas as observations, datas, modalidades, sucessos/dificuldades, justificativas das associações e lacunas. Contagens e memberships vêm do sistema; a descrição linguística é uma hipótese da LLM.

Uma observation separa intenção comunicativa, dimensão de produção e comportamento nesta ocorrência. Modo, performance e tipo de evidência são conceitos pequenos da aplicação. A dificuldade linguística é texto livre. O verifier pode rejeitar uma preferência estilística, uma alternativa regional legítima ou uma afirmação infundada sobre tradução mental. Casos incertos continuam isolados.

A busca recupera até três grupos de evidências pelos seus exemplares mais próximos. O resolver examina seus membros e decide `same_pattern`, `related_but_different`, `new_pattern` ou `insufficient_evidence`. Similaridade nunca decide membership. `new_pattern` é uma decisão de separação: não cria automaticamente um Pattern.

A política calibrada exige evidência revisada em pelo menos duas datas para materializar um padrão emergente. A prioridade exige pelo menos três datas e dificuldades espontâneas em pelo menos duas das três últimas datas com tentativas. Duas datas recentes com sucessos espontâneos e sem dificuldades nelas sinalizam recuperação, preservando o histórico. Esses critérios são heurísticas conservadoras de organização, não medidas de domínio ou verdades pedagógicas universais.

O brief distingue prática, coleta e força/recuperação recente. Sugere contextos comunicativos naturais, com até duas prioridades por bloco. O agente usa o brief para conduzir uma conversa, sem exigir uma expressão-alvo antes de observar produção espontânea. Formas sugeridas e evidências completas ficam nos packs para feedback posterior.

Opportunities e self-corrections permanecem eventos incertos; não contam automaticamente como falhas. Sucessos controlados não provam disponibilidade espontânea. Hipóteses de transferência do português ou dificuldade de recuperação continuam hipóteses.

## API opcional

Configure `OPENAI_API_KEY` fora do chat e selecione explicitamente um modelo compatível com Chat Completions e Structured Outputs:

```bash
thoth ingest minha-sessao.md --date 2026-10-04 --provider openai --model MODELO
```

Os contratos e mensagens são os mesmos do adapter manual. A API é cobrada separadamente da assinatura. Os experimentos deste repositório não fizeram chamadas pagas. O adapter foi testado com HTTP simulado; seu comportamento com um modelo remoto ainda não foi qualificado.

## Experimentos

[Resultados e limitações](reports/final.md), [calibração](reports/calibration.json), [holdout original](reports/holdout/result.json) e [diagnóstico posterior](reports/holdout/diagnostics.json) estão disponíveis. O benchmark principal isola retrieval e agrupamento usando observations sintéticas já revisadas. O teste completo de ingestão cobre três relatórios adicionais. Isso não equivale a uma avaliação independente de extração sobre conversas reais.

O runtime não recebe o gold, que mora em arquivos separados de `benchmark/data/`. Development serviu para corrigir implementação; calibration escolheu parâmetros; código, dados, política, dependências e identidade declarada dos modelos foram congelados antes do holdout. `benchmark/freeze.json` é um registro experimental, não um formato versionado do produto.

Para novas avaliações, use diretórios de saída/intercâmbio próprios:

```bash
thoth benchmark --split development --output reports/experimento-development --exchange data/experimento-development --model 'ChatGPT / modelo'
thoth benchmark --split calibrate --output reports
thoth benchmark --split calibration --output reports/experimento-calibration --exchange data/experimento-calibration --model 'ChatGPT / modelo'
thoth benchmark --split review --output reports/experimento-review --exchange data/experimento-review --model 'ChatGPT / modelo'
thoth benchmark --split freeze --freeze-file benchmark/experimento-freeze.json --model 'ChatGPT / modelo'
thoth benchmark --split holdout --freeze-file benchmark/experimento-freeze.json --output reports/experimento-holdout --exchange data/experimento-holdout --model 'ChatGPT / modelo'
```

Responda prompts pelo mesmo fluxo manual. Um resultado concluído não é sobrescrito. O freeze entregue registra caminhos do ambiente desta execução; em outro checkout gere um freeze próprio para reproduzir os casos já conhecidos. Reproduzir respostas salvas não constitui um novo holdout. Para qualificar uma alteração após estudar estes resultados, prepare novos casos reservados.

Os scripts `benchmark/build_dataset.py` e `benchmark/build_reviews.py` são a autoria explícita das fixtures. Não os execute sobre um experimento congelado. O script `benchmark/analyze_run.py` verifica hashes e produz diagnósticos posteriores, sem alterar previsões nem o resultado primário.

Para exercitar a ingestão com os intercâmbios originais já salvos, use um banco separado:

```bash
thoth --db /tmp/thoth-demo.db --artifacts /tmp/thoth-demo-artifacts ingest examples/session-01.md --date 2026-03-01 --model 'Codex / modelo desta conversa' --exchange reports/ingest-demo/exchange
thoth --db /tmp/thoth-demo.db --artifacts /tmp/thoth-demo-artifacts ingest examples/session-02.md --date 2026-03-08 --model 'Codex / modelo desta conversa' --exchange reports/ingest-demo/exchange
thoth --db /tmp/thoth-demo.db --artifacts /tmp/thoth-demo-artifacts ingest examples/session-03.md --date 2026-03-15 --model 'Codex / modelo desta conversa' --exchange reports/ingest-demo/exchange
```
