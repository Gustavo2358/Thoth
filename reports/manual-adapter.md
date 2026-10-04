# Refinamento: ChatGPT manual como runtime do MVP

O runtime padrão passa a ser `ManualChatGPTAdapter`, usando a assinatura do ChatGPT pelo fluxo de copiar prompt e devolver a resposta original. API é opcional. O domínio depende de `LLMPort`; não conhece transporte, login ou credenciais.

## O que mudou

- Um único construtor de messages e schema estrito alimenta os adapters manual e OpenAI. Testes com transporte HTTP simulado verificam igualdade do payload lógico de extractor e verifier.
- `--llm manual` é alias de `--provider manual` e o padrão da CLI. `--interactive` permite copiar/colar com `END_JSON` ou Ctrl+D.
- `--export requests/` cria prompts numerados `.txt` e manifest sem gold. `--import responses/` aceita as respostas originais com os mesmos nomes, sem envelope manual.
- Todas as propostas que passam pelas verificações determinísticas têm seus verifier requests exportados em uma só execução. Os prompts dependem das propostas reais, por isso extraction vem primeiro.
- `response.txt` é preservado antes do parser, inclusive para conteúdo inválido. Não se removem fences nem se repara JSON. Tentativas de substituir uma resposta original ou alterações de hash são rejeitadas.
- O benchmark continua sobre outros casos pendentes ou inválidos. Pending aparece na cobertura e não recebe metrics artificiais. Resposta inválida é registrada e gera schema failure/FNs quando o caso é concluído.
- Cada caso de benchmark guarda request, raw response, parsing, gold, resultado, metadata e interações separadas de verificação. Os arquivos fornecidos ao ChatGPT não contêm gold.
- Modelo é uma declaração do operador, junto de `mode: manual-chat`, versões de prompt/schema/dataset e hashes. Trocar modelo/configuração exige outro exchange; mudar código invalida calibração/freeze anteriores.
- Qualificação manual é permitida sem API. O desenho independente e o modelo precisam estar identificados, e os mesmos gates quantitativos devem passar. O transporte manual não é uma razão para rejeitar a qualificação.

## Uso

```bash
source .venv/bin/activate
learner ingest minha-sessao.md --llm manual --interactive \
  --model "ChatGPT / MODELO_SELECIONADO" --responses-dir data/minhas-interacoes

learner benchmark --llm manual --model "ChatGPT / MODELO_SELECIONADO" \
  --responses-dir data/manual-benchmark --export requests/

# Use o ChatGPT, salve respostas sem editar, com os mesmos nomes:
learner benchmark --llm manual --model "ChatGPT / MODELO_SELECIONADO" \
  --responses-dir data/manual-benchmark --import responses/ --export requests/
```

O primeiro comando de benchmark pode retornar exit code 2: significa respostas pendentes, não falha de instalação. Preencha as respostas de extractor, importe e depois preencha os verifier prompts novos. O padrão de saída é `reports/manual`, separado dos resultados históricos.

## Evidência e limites

O fluxo manual, parser, preservação do raw, importação, retomada, provenance e avaliação foram verificados offline por testes de integração com respostas controladas. Nenhum desses testes é apresentado como uma nova inferência real no ChatGPT. A avaliação anterior de 100% e suas limitações foram preservadas nos relatórios originais; não foram requalificadas com o novo adapter nem promovidas a prova independente.

Validação desta revisão: **50 testes aprovados**. A execução da CLI exportou 8 prompts de development em `artifacts/manual-prepared/requests/`, com cópia ZIP. Os 8 casos estão pending, com zero sessões pontuadas e precision/recall/F1 `null`: não foram fornecidas respostas artificiais para preencher o ensaio. Os artefatos de ingestão anteriores continuam preservados.

Um benchmark preenchido com respostas reais do ChatGPT mede o runtime manual efetivamente usado pelo aluno. A calibração correspondente não garante comportamento idêntico de uma API futura. Use conversas sem gold e um verifier em contexto separado, com inputs reservados e labels independentes. O indicador `--evaluation-design independent` registra uma declaração do desenho experimental; não verifica automaticamente se esse procedimento foi seguido.
