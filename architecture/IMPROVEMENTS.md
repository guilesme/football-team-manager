# 📋 Backlog de Melhorias — Gestão do Time 2026

> **Gerado em:** 2026-03-09  
> **Prioridade:** 🔴 Crítica · 🟠 Alta · 🟡 Média · 🟢 Baixa

---

## 1. 🔴 Sanitização contra XSS no Frontend

**Tipo:** Bug / Segurança  
**Esforço:** Baixo  
**Arquivos afetados:** `templates/index.html`

### Problema
Nomes de jogadores são injetados diretamente via `innerHTML` em todas as tabelas e na lista de artilheiros. Um jogador cadastrado como `<script>alert(1)</script>` (já presente no `db.json`) executa JavaScript arbitrário no navegador.

### Implementação

1. Criar função helper no `<script>` do `index.html`:
```javascript
function escapeHtml(str) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}
```

2. Substituir **toda** interpolação `${j.nome}`, `${best.nome}`, `${jog.nome}`, `${t.descricao}` e similares por `${escapeHtml(j.nome)}`, etc.

3. Pontos de renderização a corrigir:
   - `table-elenco` (linha ~1046)
   - `dash-artilharia` (linha ~1037)
   - `kpi-artilheiro` (linha ~1011)
   - `scorer-list-container` (linha ~979)
   - `tx-jogador` select options (linha ~975)
   - `table-financeiro` (linha ~1082)
   - `lista-mensalidades` (seção de mensalidades)

### Validação
- Cadastrar jogador com nome `<img src=x onerror=alert(1)>` e verificar que renderiza como texto plano.

---

## 2. 🔴 Corrigir Data Fixa no Pagamento de Mensalidade

**Tipo:** Bug  
**Esforço:** Mínimo  
**Arquivos afetados:** `app.py`

### Problema
Na rota `/api/pagar_mensalidade/<id>` (linha 36), a data está hardcoded como `"2026-03-05"`.

### Implementação

1. Adicionar import no topo de `app.py`:
```python
from datetime import date
```

2. Substituir a linha 36:
```diff
- "data": "2026-03-05" # Hoje simplificado
+ "data": date.today().isoformat()
```

### Validação
- Chamar `POST /api/pagar_mensalidade/1` e verificar que `data` retorna a data de hoje.

---

## 3. 🟡 Suporte a Múltiplos Gols por Artilheiro

**Tipo:** Melhoria de lógica  
**Esforço:** Médio  
**Arquivos afetados:** `app.py`, `templates/index.html`, `architecture/SOP_engine.md`

### Problema
O modelo atual registra artilheiros como uma lista de IDs (`[3, 4]`), limitando cada jogador a exatamente 1 gol por partida. Na realidade, um jogador pode fazer múltiplos gols.

### Implementação

**Modelo de dados** — substituir `artilheiros: [jogador_id]` por:
```json
"artilheiros": [
    {"jogador_id": 3, "gols": 2},
    {"jogador_id": 4, "gols": 1}
]
```

**Backend (`app.py`):**
1. Na `add_partida`: processar `artilheiros` como lista de objetos `{jogador_id, gols}`.
2. Incrementar `j["gols"] += artilheiro["gols"]` ao invés de `+= 1`.
3. Na `update_partida`: reverter gols usando o valor antigo de `gols`, aplicar novo.
4. Na `delete_partida`: reverter usando `artilheiro["gols"]`.
5. Manter retrocompatibilidade: se receber lista de IDs simples, tratar cada como `gols: 1`.

**Frontend (`index.html`):**
1. Substituir checkboxes por `<input type="number" min="0" value="0">` ao lado de cada jogador.
2. Ao salvar, coletar apenas jogadores com `gols > 0` e montar o array de objetos.
3. Na tabela do calendário, exibir artilheiros detalhados: `Ronaldo (2), Romário (1)`.

**SOP_engine.md:** Atualizar regra de artilharia e contagem de gols.

### Validação
- Registrar partida com jogador fazendo 3 gols. Verificar que o campo `gols` do jogador incrementa em 3.
- Editar partida mudando de 3 para 1 gol. Verificar que decrementa corretamente.

---

## 4. 🟢 Gráfico de Evolução Financeira Mensal

**Tipo:** Nova Feature  
**Esforço:** Médio  
**Arquivos afetados:** `templates/index.html`, `app.py` (novo endpoint opcional)

### Descrição
Adicionar gráfico de barras empilhadas ou linhas mostrando receitas vs. despesas por mês no dashboard.

### Implementação

**Dependência:** Adicionar Chart.js via CDN no `<head>`:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

**Backend (opcional)** — novo endpoint `/api/stats/mensal`:
```python
@app.route("/api/stats/mensal", methods=["GET"])
def get_stats_mensal():
    db = load_db()
    meses = {}
    for t in db["financeiro"]:
        if t["status"] != "pago" or not t.get("data"):
            continue
        chave = t["data"][:7]  # "2026-03"
        if chave not in meses:
            meses[chave] = {"receitas": 0, "despesas": 0}
        meses[chave][t["tipo"] + "s"] += t["valor"]
    return jsonify(meses)
```

**Frontend:**
1. Na tab `#tab-dashboard`, adicionar um `<canvas id="chart-financeiro">` dentro de um novo card na `grid-2`.
2. Na `updateUI()`, chamar `fetchAPI('/stats/mensal')` e renderizar gráfico com barras verdes (receitas) vs. vermelhas (despesas).
3. Usar cores do design system (`var(--success)`, `var(--danger)`).

### Validação
- Com dados financeiros em pelo menos 2 meses diferentes, verificar que o gráfico renderiza corretamente.

---

## 5. 🟢 Layout Responsivo para Mobile

**Tipo:** Melhoria UX  
**Esforço:** Médio  
**Arquivos afetados:** `templates/index.html`

### Descrição
A sidebar fixa de 280px torna o app inutilizável em telas < 768px.

### Implementação

1. Adicionar botão hambúrguer no topo do `<main>`:
```html
<button class="hamburger-btn" id="menu-toggle" onclick="toggleSidebar()">
    <i class="fa-solid fa-bars"></i>
</button>
```

2. CSS — Media queries:
```css
@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
        transition: transform 0.3s ease;
    }
    .sidebar.open {
        transform: translateX(0);
    }
    .main-content {
        margin-left: 0;
        width: 100%;
        padding: 1rem;
    }
    .hamburger-btn {
        display: block;
    }
    .grid-2 {
        grid-template-columns: 1fr;
    }
    .kpi-grid {
        grid-template-columns: 1fr 1fr;
    }
}

@media (min-width: 769px) {
    .hamburger-btn { display: none; }
}
```

3. JavaScript:
```javascript
function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('open');
}
```

4. Adicionar overlay que fecha a sidebar ao clicar fora.

### Validação
- Testar em viewport de 375px (iPhone) e 768px (tablet). Sidebar deve estar escondida e acessível via botão.

---

## 6. 🟢 Controle de Mensalidades por Mês/Competência

**Tipo:** Nova Feature  
**Esforço:** Alto  
**Arquivos afetados:** `app.py`, `templates/index.html`, `data/db.json`, `architecture/SOP_engine.md`

### Descrição
Adicionar uma **tabela-calendário de mensalidades** que mostra, para cada jogador, se cada mês está pago, pendente ou inadimplente.

### Implementação

**Modelo de dados** — Nova propriedade em `financeiro`:
```json
{
    "id": "tx_008",
    "jogador_id": 3,
    "descricao": "Mensalidade Mar/2026",
    "valor": 50.0,
    "tipo": "receita",
    "status": "pago",
    "data": "2026-03-09",
    "competencia": "2026-03"   // ← NOVO
}
```

**Backend (`app.py`):**
1. Ajustar `pagar_mensalidade` para receber e gravar `competencia` (mês/ano).
2. Novo endpoint `GET /api/mensalidades/grid` que retorna, para cada jogador, o status de cada mês do ano:
```json
{
    "meses": ["2026-01", "2026-02", "2026-03", ...],
    "jogadores": [
        {"id": 1, "nome": "Ronaldo", "status": {"2026-01": "pago", "2026-02": "pendente", ...}}
    ]
}
```
3. Impedir pagamento duplicado do mesmo mês/jogador (validação).

**Frontend:**
1. Nova seção no tab Financeiro (ou nova tab "Mensalidades") com grid visual estilo calendário.
2. Cada célula: verde (pago), amarelo (pendente), vermelha (inadimplente = mês passado e não pago).
3. Clicar na célula → registrar pagamento diretamente.

**SOP_engine.md:** Adicionar regras de competência de mensalidade.

### Validação
- Registrar pagamento de março para 2 jogadores. Verificar grid mostra verde nesses e vermelho/amarelo nos outros.
- Tentar pagar março de novo para mesmo jogador → deve retornar erro 409.

---

## 7. 🟢 Exportação de Dados (CSV / PDF)

**Tipo:** Nova Feature  
**Esforço:** Baixo  
**Arquivos afetados:** `templates/index.html`

### Descrição
Permitir exportar tabelas (elenco, financeiro, calendário) para CSV e/ou imprimir como PDF.

### Implementação

**CSV (JavaScript puro, sem dependência):**
```javascript
function exportCSV(data, headers, filename) {
    const csvHeader = headers.join(',');
    const csvRows = data.map(row => headers.map(h => `"${row[h] ?? ''}"`).join(','));
    const csv = [csvHeader, ...csvRows].join('\n');
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}
```

1. Adicionar botão "Exportar CSV" no header de cada tab (elenco, financeiro, calendário).
2. Para elenco: `exportCSV(elencoData, ['id','nome','posicao','gols'], 'elenco.csv')`.
3. Para financeiro: incluir `['data','descricao','tipo','valor','status']`.

**PDF (via CSS Print):**
1. Adicionar `<style media="print">` que esconde sidebar, botões e mostra só a tab ativa.
2. Botão "Imprimir" que chama `window.print()`.

### Validação
- Exportar CSV do elenco, abrir no Excel/Google Sheets. Verificar acentos corretos (BOM UTF-8).
- Imprimir via navegador: layout limpo sem sidebar.

---

## 8. 🟢 Busca e Filtro nas Tabelas

**Tipo:** Melhoria UX  
**Esforço:** Baixo  
**Arquivos afetados:** `templates/index.html`

### Descrição
Campo de busca em tempo real para filtrar conteúdo das tabelas de elenco e financeiro.

### Implementação

1. Adicionar campo de busca no header de cada tab:
```html
<input type="text" id="search-elenco" class="form-control"
       placeholder="Buscar jogador..."
       oninput="filterTable('elenco')"
       style="max-width: 300px;">
```

2. Função de filtro:
```javascript
function filterTable(tabName) {
    const query = document.getElementById(`search-${tabName}`).value.toLowerCase();
    const rows = document.querySelectorAll(`#table-${tabName} tr`);
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(query) ? '' : 'none';
    });
}
```

3. Aplicar em:
   - Tab Elenco: filtrar por nome/posição.
   - Tab Financeiro: filtrar por descrição/jogador/tipo.
   - Tab Calendário: filtrar por adversário/data.

4. Estilizar o input com ícone de lupa (`fa-magnifying-glass`) à esquerda.

### Validação
- Com 5+ jogadores cadastrados, digitar parte do nome e verificar que a tabela filtra em tempo real.

---

## 9. 🟡 Campos "Local do Jogo" e "Mando de Campo"

**Tipo:** Enriquecimento de dados  
**Esforço:** Baixo  
**Arquivos afetados:** `app.py`, `templates/index.html`, `architecture/SOP_engine.md`

### Descrição
Adicionar campos `local` (string) e `mando` (enum: `casa` | `fora`) ao modelo de partida.

### Implementação

**Modelo de dados:**
```json
{
    "id": "match_003",
    "data": "2026-04-10",
    "adversario": "Corinthians",
    "local": "Campo do Bairro",
    "mando": "casa",
    "placar_casa": 0,
    "placar_fora": 0,
    "status": "agendado",
    "artilheiros": []
}
```

**Backend (`app.py`):**
1. `add_partida`: ler `data.get("local", "")` e `data.get("mando", "casa")`.
2. `update_partida`: permitir atualizar `local` e `mando`.
3. `get_stats`: calcular aproveitamento em casa vs. fora:
```python
vitorias_casa = sum(1 for p in finalizados if p.get("mando") == "casa" and p["placar_casa"] > p["placar_fora"])
vitorias_fora = sum(1 for p in finalizados if p.get("mando") == "fora" and p["placar_casa"] > p["placar_fora"])
```

**Frontend:**
1. No modal de partida, adicionar campos:
   - Select "Mando" com opções `Casa` / `Fora`
   - Input texto "Local do Jogo"
2. Na tabela do calendário, exibir ícone de casa/avião e o local.
3. No dashboard, exibir card "Aproveitamento Casa vs. Fora".

**SOP_engine.md:** Adicionar regra de mando e local.

### Validação
- Criar partida como visitante. Verificar que stats diferenciam casa vs. fora.

---

## 10. 🟠 Backup e Restauração do Banco de Dados

**Tipo:** Segurança de dados  
**Esforço:** Baixo  
**Arquivos afetados:** `app.py`, `templates/index.html`

### Descrição
Permitir download do `db.json` atual e restauração a partir de upload, protegendo contra perda de dados.

### Implementação

**Backend (`app.py`):**

1. Endpoint de download:
```python
from flask import send_file

@app.route("/api/backup", methods=["GET"])
def backup_db():
    return send_file(
        DB_PATH,
        mimetype="application/json",
        as_attachment=True,
        download_name=f"backup_{date.today().isoformat()}.json"
    )
```

2. Endpoint de restauração:
```python
@app.route("/api/restore", methods=["POST"])
def restore_db():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    try:
        data = json.load(file)
        # Validar estrutura mínima
        required_keys = {"config", "elenco", "calendario", "financeiro"}
        if not required_keys.issubset(data.keys()):
            return jsonify({"error": "Estrutura inválida"}), 400
        # Backup do atual antes de sobrescrever
        save_db(load_db())  # garante .tmp existe
        save_db(data)
        return jsonify({"ok": True, "message": "Banco restaurado com sucesso"})
    except json.JSONDecodeError:
        return jsonify({"error": "Arquivo JSON inválido"}), 400
```

**Frontend:**
1. Adicionar seção "Configurações" na sidebar (ou botões no rodapé da sidebar).
2. Botão "Baixar Backup" → `window.location = '/api/backup'`.
3. Botão "Restaurar Backup" → abre file input, envia via `FormData` com `fetch`.
4. Confirmação obrigatória antes de restaurar ("Tem certeza? Todos os dados atuais serão sobrescritos").

### Validação
- Baixar backup, deletar todos os jogadores, restaurar backup. Verificar que dados voltaram.

---

## Ordem de Implementação Sugerida

| Fase | Issues | Justificativa |
|------|--------|---------------|
| **Sprint 1** | #1, #2 | Bugs e segurança — zero esforço, alto impacto |
| **Sprint 2** | #8, #7, #10 | Quick wins de UX e segurança de dados |
| **Sprint 3** | #5, #4 | Visual e responsividade |
| **Sprint 4** | #3, #9 | Enriquecimento do modelo de dados |
| **Sprint 5** | #6 | Feature mais complexa, depende de modelo estável |
