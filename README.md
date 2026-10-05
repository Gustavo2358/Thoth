# Thoth

Thoth compila o histórico de aprendizagem em **um prompt para o professor da próxima conversa**. É um persistent pedagogical brain local: aprende como seu inglês está evoluindo, como você pede para ser ensinado e quais objetivos definiu. Você continua praticando inglês falado no ChatGPT Voice ou em outro agente externo.

```text
conversa completa exportada em Markdown
  → análise com provenance
  → Learner Model + Teaching Model + Goals
  → teacher-prompt.md
  → colar numa conversa nova e praticar
  → exportar a conversa completa → repetir
```

O output é o produto. Não existe tutor dentro do Thoth, dashboard, integração com a UI do ChatGPT ou relatório especial obrigatório no final da aula. O banco pessoal começa vazio; nenhum exemplo é carregado automaticamente.

A implementação é uma aplicação local modular, com SQLite e embeddings spaCy locais. Não há versões paralelas, migrações de bancos experimentais ou pipeline alternativo. O Git preserva o histórico. [Modelo conceitual](docs/product-model.md), [qualificação e limitações](reports/final.md) e [rubrica de qualidade do prompt](benchmark/prompt-rubric.md).

## Instalar

Python 3.12+ em Linux/macOS:

```bash
bash scripts/setup.sh
source .venv/bin/activate
thoth state
```

O setup instala dependências fixadas, o modelo `en_core_web_md` 3.8.0 (aproximadamente 33,5 MB) e executa testes. Após a instalação, embeddings, SQLite e o compiler funcionam sem rede. O trabalho interno de interpretação ainda precisa de uma LLM, pelo adapter manual ou pela API interna opcional já existente.

## Entrada: conversa completa com papéis

Não há samples de exportação real do ChatGPT no repositório. Portanto o contrato canônico é explícito:

```markdown
# Conversation

## User
Yesterday I needed to explain a difficult decision...

## Assistant
What made the decision difficult?

## User
Please always explain why you changed my wording.
```

Use `## User` / `## Assistant` ou `## Learner` / `## Teacher`, sem diferenciar maiúsculas. Cada heading abre um turno completo. Só um título Markdown de nível um e linhas vazias podem preceder os turnos. Dentro do corpo, headings de conteúdo usam nível três ou maior. Blocos cercados são preservados e não criam turnos. Ambos os papéis precisam existir; papéis desconhecidos, conteúdo sem atribuição, turnos vazios e cercas não fechadas falham explicitamente.

Preserve a conversa completa, incluindo intervenções e pedidos pedagógicos. Não precisa de áudio, pronúncia ou transcrição forense. O Markdown disponível é a fonte. [Três exemplos completos](examples/).

## O loop principal

```bash
thoth goals add "Explain technical design trade-offs naturally in spoken English"
thoth ingest conversation.md --date 2026-10-04 --model 'ChatGPT / nome do modelo interno'
thoth prepare > teacher-prompt.md
```

A data deve ser a data real da sessão; sem `--date`, usa hoje. Ingira sessões antigas em ordem cronológica. Várias conversas na mesma data não contam como recorrência independente.

`ingest` solicita trabalho **interno** da LLM:

1. O comando informa um `request.txt` e `response.txt` pendentes em `data/exchange/<hash>/`.
2. Copie o request completo para uma conversa de análise no ChatGPT e salve a resposta original em `response.txt`. O contrato interno exige JSON puro; uma resposta inválida é preservada e rejeitada.
3. Repita o mesmo comando. A resposta anterior é reutilizada e outra revisão/resolução pode ficar pendente.
4. Continue até sucesso. Código 2 significa resposta pendente; 1 significa erro; 0 significa conclusão.

A sessão só altera os modelos quando todas as etapas terminam. Repetir a mesma fonte/data é idempotente. O modo `--interactive` aceita respostas no terminal, terminadas por `END_JSON`. Para importar arquivos `<hash-da-request>.txt`, use `thoth import respostas/ --model 'ChatGPT / nome' --exchange data/exchange` e retome a ingestão.

Depois de `prepare`, copie **somente `teacher-prompt.md`** para uma conversa nova e pratique. Esse é outro uso do ChatGPT: professor externo, sem acesso ao banco, fontes anteriores ou audit. Não peça um report ou JSON no final; exporte a conversa inteira para a próxima ingestão.

## Inspeção e artifacts

```bash
thoth state
thoth patterns
thoth teaching
thoth goals
thoth goals remove GOAL-<id>
```

Os caminhos globais `--db`, `--artifacts` e `--policy` vêm antes do comando. `prepare` imprime somente o prompt em stdout, permitindo redirecionar. Artifacts são regenerados em:

```text
artifacts/
  teacher-prompt.md
  teacher-prompt.audit.json
  learner-state.json
  learner-state.md
  teaching-model.json
  goals.json
  patterns/PAT-<id>.md
  sessions/SES-<id>/
    conversation.md
    audit.json
    evidence-pack.md
```

O raw Markdown fica imutável no SQLite e é exportado byte-for-byte. Locators incluem sessão, speaker, turno, offsets em code points e linhas da fonte UTF-8 original. O prompt fica limpo; o audit explica cada seleção, suas evidências, turnos de suporte, estratégia, objetivos e omissões por limite/budget. Intercâmbios guardam requests, respostas originais, SHA-256 e JSON validado.

## O que os modelos significam

**Learner Model:** dimensões de produção abertas, com sucesso, dificuldade, incerteza e oportunidade. Produção espontânea, guiada e controlada permanecem distintas. Uma frase repetida após um modelo não conta como recuperação espontânea. A mesma capacidade pode reunir tentativas difíceis e sucessos posteriores. Cosine recupera candidatos; só a resolução semântica decide membership.

**Teaching Model:** evidência sobre pedidos e respostas a intervenções. Instruções duráveis explicitamente declaradas pelo aluno entram imediatamente. Um pedido local fica tentativo; recorrência em duas datas pode sustentar uma hipótese inferida, identificada como tal. Uma reação positiva isolada não vira “melhor método”. Uma afirmação do professor sobre a preferência do aluno não basta. Não há perfil psicológico.

**Goals:** objetivos explicitamente definidos pelo usuário ou declarados na conversa e revisados. Erros não inventam objetivos. Os goals orientam os assuntos da próxima sessão; patterns não monopolizam a agenda.

O compiler seleciona poucos itens. Prática pede tentativa antes do modelo, feedback seletivo, nova produção e variação posterior. Observação cria oportunidade natural sem diagnosticar fraqueza. Recuperação testa transferência em outro contexto sem lembrar a resposta. Evidência antiga perde prioridade de prática. Os defaults gerais são identificados separadamente das preferências pessoais.

A política usa datas/contagens e um budget aproximado de 8.000 caracteres, com limites simples em `src/thoth/policy.json`. Omissões são de itens inteiros. Não há scores de domínio ou confiança inventada. Detalhes das heurísticas estão no [modelo](docs/product-model.md).

## Corrigir interpretações e reconstruir

Fontes e respostas consumidas são imutáveis. Para corrigir extração ou associação, use um intercâmbio novo e reprocessamento:

```bash
thoth ingest conversation.md --date DATA_ORIGINAL --reprocess \
  --exchange data/reanalysis --model 'ChatGPT / nome do modelo interno'
```

O arquivo precisa ser uma fonte já ingerida, sem alterações. O comando reanalisa **todo o histórico armazenado**, em ordem cronológica, e troca o estado derivado atomicamente após conclusão. Enquanto faltar uma resposta, o estado existente permanece intacto. Não duplica evidência. Goals manuais são preservados; um goal declarado na fonte pode ser registrado de novo pelo replay. Para começar outro experimento, use um SQLite novo, sem migrações.

## API interna opcional

O adapter OpenAI existente permanece apenas para análise interna, com os mesmos contratos. Não importa chats nem controla o professor externo. Configure `OPENAI_API_KEY` fora do chat e selecione explicitamente um modelo com Structured Outputs:

```bash
thoth ingest conversation.md --date 2026-10-04 --provider openai --model MODELO
```

Não houve chamadas pagas nesta campanha. O contrato HTTP tem teste simulado; comportamento semântico de modelos remotos continua sem qualificação independente.

## Reproduzir a campanha

```bash
python -m pytest -q
PYTHONPATH=src python benchmark/run_campaign.py \
  --output /tmp/thoth-campaign --exchange reports/continuity/exchange
```

A campanha usa a CLI de produção, SQLite vazio e embeddings reais. São oito conversas em três históricos, gold separado, respostas originais de extração/revisão/resolução e prompts gerados após cada sessão. O harness só lê o gold depois da ingestão. Use outro diretório de saída para um replay independente; um novo intercâmbio pede novas respostas internas.

Fluxo demonstrado:

- [Sessão 1](examples/session-01.md) → [prompt 2](reports/continuity/continuity/after-01/teacher-prompt.md): prefere razões para reformulações, evita excesso de correção, observa capacidades emergentes; chunking local ainda fica fora.
- [Sessão 2](examples/session-02.md) → [prompt 3](reports/continuity/continuity/after-02/teacher-prompt.md): transferência sem priming para incerteza reutilizada sem ajuda; prática para duração ainda difícil.
- [Sessão 3](examples/session-03.md) → [prompt 4](reports/continuity/continuity/after-03/teacher-prompt.md): duas intenções de transferência e chunking como hipótese recorrente, além de rejeição explícita a aulas de gramática.

[Resultados](reports/continuity/result.json) e [análise final](reports/final.md) distinguem prova técnica de eficácia pedagógica. A mesma assistência autorou conversas, respostas semânticas e gold: o replay não mede uma taxa populacional de extração. A recomendação é um piloto pessoal supervisionado, com revisão inicial das evidências e observação do comportamento real de um professor novo.
