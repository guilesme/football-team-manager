# 📋 Análise e Novas Sugestões (Fase 2)

> **Data da Análise:** 2026-03-10
> **Estado Atual do Projeto:** O projeto sofreu um mega upgrade arquitetural. O banco JSON foi substituído pelo **SQLite via SQLAlchemy**, as listas agora possuem **paginação server-side**, e o backend conta com validação mais robusta e conversão de valores (`Decimal`).

---

## 🔍 Status das Melhorias Anteriores (Fase 1)

**✅ Implementadas com Sucesso:**
- **2. Data Dinâmica em Mensalidades:** Agora o `pagar_mensalidade` puxa `datetime.date.today().isoformat()`.
- **3. Suporte a Múltiplos Gols:** Implementado no backend (`_normalize_artilheiros`) e no frontend (inputs numéricos substituindo checkboxes).

**❌ Ainda Pendentes (Recomendado manter no backlog):**
- **1. Sanitização de XSS no Frontend:** (Risco de Segurança) O innerHTML ainda é usado e vulnerável.
- **4. Gráfico de Evolução Financeira Mensal:** Ainda não adicionamos o ChartJS no dashboard.
- **5. Layout Mobile Responsivo:** A sidebar fixa continua quebrando o uso via celular.
- **6. Controle de Mensalidades por Mês/Competência:** O `Transacao` atual ainda não tem o campo `competencia`.
- **7. Exportação de Dados (CSV/PDF).**
- **9. Local do Jogo e Mando de Campo na tabela `Partida`.**

---

## 💡 NOVO BACKLOG: Baseado em SQLite e Paginação

Como o sistema evoluiu para usar **SQL Relacional puro** com paginação e classes ORM isoladas em `models.py`, um novo leque de potenciais melhorias foi desbloqueado:

### 11. 🟡 Soft Delete (Inativar Jogador)
**Por que:** Num banco relacional, usar `DELETE` em um jogador apaga-o fisicamente, mas pode gerar *Orphan Records* ou erros de Constraint se houver transações financeiras ligadas ao `jogador_id`.
**Como implementar:**
- Adicionar `ativo = db.Column(db.Boolean, default=True)` em `Jogador`.
- Na rota `DELETE /api/elenco/<id>`, ao invés de `db.session.delete()`, fazemos `jogador.ativo = False`.
- Os _endpoints_ GET filtram apenas `ativo == True`, e mostramos inativos apenas numa tela "Histórico do Clube".

### 12. 🟢 Filtros Server-Side Integrados à Paginação
**Por que:** Antes sugeri busca no frontend. Mas agora que há `limit` e `offset` (paginação), se o frontend buscar apenas na tabela renderizada, ele buscará apenas na página atual (ex: 1 a 10).
**Como implementar:**
- Passar um parâmetro `?q=Buscado` nas rotas do `app.py`.
- No SQLAlchemy, usar `Jogador.query.filter(Jogador.nome.ilike(f"%{q}%"))` ou equivalente para Partidas e Finanças.

### 13. 🟠 Backup e Restore do Banco SQLite (`app.db`)
**Por que:** O sistema agora guarda dados num binário `data/app.db`. Copiar `db.json` não funciona mais, e sem backup, perder o contêiner Docker/Volume zera os dados.
**Como implementar:**
- `/api/backup`: `send_file("data/app.db", as_attachment=True)`.
- `/api/restore`: Upload de arquivo sobrescrevendo `app.db` (exigirá restart do banco via SQLAlchemy para invalidar as antigas conexões de sessão).

### 14. 🟡 Aggregations (Métricas mais Rápidas)
**Por que:** Hoje o `/api/stats` ainda puxa `Transacao.query.all()` para depois somar num loop Python e puxa `Partida.query.all()` para calcular vitórias. Para 10 mil transações, isso começa a consumir RAM atoa.
**Como implementar:**
- Mudar para lógica de banco: `db.session.query(db.func.sum(Transacao.valor)).filter_by(...)` que delega o cálculo ao motor DB, trazendo performance imediata.

### 15. 🟢 Configurações Globais Gerenciáveis
**Por que:** Foi criada a tabela `Config` (`ano` e `moeda`), mas não há tela para o usuário manipular os valores do clube.
**Como implementar:**
- Rota GET e PUT `/api/config`.
- Painel estético de "Configurações" no Frontend (ícone de engrenagem) permitindo mudar moeda base (ex: $, R$, €) e nome oficial do time (ex: adicionar na tabela Config um campo `nome_time`). O Dashboard trocaria o logo para o nome customizado.

---

### 🚀 Plano de Ataque (Sprints Sugeridas Atualizadas)

1. **Sprint 1 (Robustez)**: Sanitização XSS (#1), Soft Delete no elenco (#11).
2. **Sprint 2 (Busca)**: Implementar Filtros e Buscas Server-Side junto da paginação atual (#12).
3. **Sprint 3 (UX & Visual)**: Layout responsivo Mobile (#5), Gráfico de evolução Financeiro (#4).
4. **Sprint 4 (Novas Features)**: Controle de mensalidade por Competência (#6) e Configurações Globais (#15).
