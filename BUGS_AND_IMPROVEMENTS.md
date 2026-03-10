# 🔍 Relatório de Bugs e Melhorias

> Gerado em: 2026-03-09  
> Re-analisado em: 2026-03-09 e 2026-03-10  
> Analisado por: Revisão automatizada completa de código  
> Status geral: **Quase Completo** — 20/22 antigos corrigidos, mas há novos bugs de sintaxe introduzidos.

---

## Legenda de Status

| Símbolo | Significado |
|---|---|
| `[ ]` | Pendente |
| `[/]` | Em progresso |
| `[x]` | Concluído |

---

## 🔴 Crítico — Corrigir com Urgência

- [x] **`debug=True` em produção** (`app.py:288`)  
  O Flask roda com o Werkzeug debugger ativo. Expõe execução remota de código Python (RCE) e o código-fonte completo.  
  **Fix:** Ler `FLASK_DEBUG` de variável de ambiente em vez de hardcodar.

- [x] **XSS via `innerHTML`** (`templates/index.html` — múltiplos locais)  
  Dados vindos da API são inseridos com `innerHTML` sem nenhum escape. Um nome como `<script>alert(1)</script>` executa código no browser.  
  **Fix:** Criar função `esc(s)` de escape HTML e usá-la em todos os template literals.

---

## 🟠 Alta Prioridade

- [x] **Data de mensalidade hardcoded** (`app.py:36`)  
  Toda mensalidade registrada tem data fixa `"2026-03-05"` em vez da data real.  
  **Fix:** `datetime.date.today().isoformat()`

- [x] **`request.json` pode ser `None`** (`app.py:70, 136, 216`)  
  Nas rotas `PUT`, `request.json` retorna `None` se o `Content-Type` não for JSON, causando `AttributeError` (500).  
  **Fix:** Substituir por `request.get_json(force=True) or {}` como já feito nas rotas `POST`.

- [x] **Race condition no `save_db`** (`tools/db_json.py:96-100`)  
  O lock exclusivo é aplicado no arquivo `.tmp`, mas o `os.replace()` acontece **fora** do lock. Em ambiente multi-processo, pode corromper dados.  
  **Fix:** Redesenhar o lock para cobrir todo o ciclo de escrita + replace.

- [x] **Container Docker rodando como `root`** (`Dockerfile`)  
  Sem instrução `USER`, o processo Flask roda como root. Se explorado, o atacante tem privilégios máximos.  
  **Fix:** Adicionar `RUN adduser ... && USER appuser` no Dockerfile.

- [x] **Ausência de `.dockerignore`** (raiz do projeto)  
  `COPY . .` inclui `.git`, `data/db.json` e arquivos desnecessários na imagem Docker, aumentando tamanho e expondo dados.  
  **Fix:** Criar `.dockerignore` excluindo `.git`, `data/db.json`, `*.md`, `__pycache__`.

---

## 🟡 Média Prioridade

- [x] **Variáveis do `.env.example` não são lidas pelo app**  
  `FLASK_DEBUG`, `VALOR_MENSALIDADE`, `DB_PATH` e `APP_PORT` estão documentadas no `.env.example` mas o código as ignora completamente.  
  **Fix:** Implementar leitura com `os.environ.get()` em `app.py` e `db_json.py`.

- [x] **`python-dotenv` no `requirements.txt` mas nunca usado**  
  A dependência está listada mas `load_dotenv()` nunca é chamada.  
  **Fix:** Ou remover a dependência, ou implementar `load_dotenv()` no início de `app.py`.

- [x] **`float` para valores monetários** (`app.py:201`)  
  Ponto flutuante causa imprecisão: `0.1 + 0.2 == 0.30000000000000004`.  
  **Fix:** Usar `decimal.Decimal` para cálculos e só converter para `float` ao serializar JSON.

- [x] **`db.json` com dados reais commitado no Git** (`data/db.json`)  
  O banco de dados com nomes e transações está versionado. Se dados sensíveis forem adicionados, ficam expostos no histórico.  
  **Fix:** Adicionar `data/db.json` ao `.gitignore` (manter apenas `data/.gitkeep`).

- [x] **Placar sobrescrito silenciosamente** (`app.py:105-107`)  
  Se `placar_casa < len(artilheiros)`, o backend altera o placar sem avisar o usuário.  
  **Fix:** Remover a lógica de sobrescrita ou retornar warning ao frontend.

- [x] **Checkboxes de artilheiros não resetados ao fechar modal** (`index.html:1222`)  
  Ao fechar e reabrir o modal de nova partida, os checkboxes da partida anterior ficam marcados.  
  **Fix:** Desmarcar todos os checkboxes `input[name="artilheiros"]` ao resetar o formulário.

---

## 🟢 Baixa Prioridade / Qualidade de Código

- [x] **`saveElenco/Partida/Transacao` sem `try/catch`** (`index.html`)  
  Se a chamada à API falhar, o modal fecha como se o salvamento tivesse funcionado.  
  **Fix:** Envolver cada `fetchAPI` em `try/catch` e exibir `showToast(...)` em caso de erro.

- [x] **Regex frágil no helper de reset de formulários** (`index.html:1306`)  
  `.match()` pode retornar `null` causando `TypeError` se o atributo `onclick` tiver formato inesperado.  
  **Fix:** Verificar resultado do `.match()` antes de acessar `[1]`.

- [x] **`next_str_id` frágil com underscores no prefixo** (`db_json.py:119`)  
  `sid.split("_")[1]` pode retornar valor errado se o prefixo contiver underscores.  
  **Fix:** Usar `sid[len(prefix)+1:]` para extrair a parte numérica.

- [x] **Contagem de gols não suporta múltiplos gols por partida** (bug de design)  
  O sistema é binário (marcou/não marcou). Um jogador que fez 3 gols recebe apenas +1.  
  **Fix (design):** Substituir checkbox por campo numérico de quantidade de gols por jogador na interface HTML, assim como no backend as operações suportarão uma lista de identificadores. [Implementado na UI em v1.2]

- [x] **Sem tratamento de erro visível ao usuário em `loadData`** (`index.html:986-988`)  
  Erros de rede no carregamento inicial são logados só no console. O usuário vê a tela em branco.  
  **Fix:** Chamar `showToast(...)` no `catch` de `loadData`.

- [x] **Sem paginação nas rotas de listagem** (`app.py:44-47, 92-95, 187-190`)  
  Todas as coleções são retornadas inteiras. Não escala com crescimento de dados.  
  **Fix:** Foram adicionados parâmetros `?limit=` e `?offset=` no backend, como também a UI agora gerencia paginação. [Implementado em v1.2]

---

## 🆕 Novos Issues (encontrados na re-análise de 2026-03-09)

- [x] **`delElenco/delPartida/delTransacao` sem `try/catch`** (`index.html:1180, 1250, 1298`)  
  As funções de **save** ganharam `try/catch`, mas as de **delete** não. Se o servidor retornar erro, a exceção não é tratada e `loadData()`/`updateUI()` não executam.  
  **Fix:** Envolver cada `fetchAPI` de delete em `try/catch` com `showToast(...)` de erro.

- [x] **Import no meio do arquivo** (`app.py:23`)  
  `from tools.db_json import ...` ficou após a constante `VALOR_MENSALIDADE` em vez de no topo com os demais imports (viola PEP 8).  
  **Fix:** Mover o import para o bloco de imports no topo do arquivo (linhas 6-11).

- [x] **`DB_PATH` relativo pode falhar fora do Docker** (`tools/db_json.py:15`)  
  Se `DB_PATH=data/db.json` for definido via `.env` (caminho relativo), o arquivo será gravado relativo ao working directory, não ao diretório do projeto.  
  **Fix:** `DB_PATH = os.path.abspath(os.environ.get("DB_PATH", _DEFAULT_DB_PATH))`

---

## 🚨 Bugs Introduzidos na Correção (Encontrados em 2026-03-10)

- [ ] **Rotas da API quebradas por espaços na URL** (`index.html:1245, 1263, 1333, 1355, 1390, 1408, 1429`)  
  Um formatador de código adicionou espaços indevidos nas template strings das URLs. Em vez de ``/elenco/${id}``, o código chama ``/ elenco / ${id}``. Isso fará o servidor retornar erro `404 Not Found` em **TODAS** as operações de edição, exclusão e pagamento de mensalidade.  
  **Fix:** Remover os espaços: ``/elenco/${id}``, ``/calendario/${id}``, ``/financeiro/${id}``, ``/pagar_mensalidade/${id}``.

- [ ] **Tags HTML inválidas no Toast** (`index.html:1422`)  
  O formatador também corrompeu a tag do ícone do toast. O código tem `< i class= "fa-solid ${icon}" ></i >`. O HTML não reconhece a tag `< i>` (com espaço após o `<`).  
  **Fix:** Corrigir para `<i class="fa-solid ${icon}"></i>`.

---

## 📊 Resumo

| Categoria | Total | Pendentes |
|---|---|---|
| 🔴 Crítico | 2 | 0 |
| 🟠 Alta | 5 | 0 |
| 🟡 Média | 6 | 0 |
| 🟢 Baixa | 6 | 0 |
| 🆕 Novos | 3 | 0 |
| 🚨 Erros de Formatação | 2 | 2 |
| **Total** | **24** | **2** |
