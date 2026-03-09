<div align="center">

# ⚽ Football Team Manager

**Aplicativo web para gestão de times de futebol amador**  
Controle seu elenco, calendário de jogos e finanças do clube — tudo em um único painel moderno.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge)

</div>

---

## 📖 Sobre o Projeto

Football Team Manager é uma aplicação web de página única (SPA) construída com **Flask** e **HTML/JS**. Os dados são persistidos localmente em um arquivo **JSON**, sem necessidade de banco de dados externo. Ideal para times amadores que querem um controle simples e elegante do clube.

### ✨ Funcionalidades

| Módulo | Descrição |
|---|---|
| **👥 Elenco** | Cadastro, edição e remoção de jogadores com posição e contagem de gols |
| **📅 Calendário** | Agendamento de partidas, registro de placares e artilheiros |
| **💰 Financeiro** | Controle de receitas (mensalidades) e despesas com saldo em tempo real |
| **📊 Estatísticas** | Ranking de artilharia, aproveitamento, próximo jogo e saldo financeiro |

---

## 🚀 Início Rápido

Escolha o método de instalação que preferir:

### Opção A — Docker (Recomendado, Windows/Linux/macOS)

> Pré-requisitos: [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e em execução.

```bash
# 1. Clone o repositório
git clone https://github.com/guilesme/football-team-manager.git
cd football-team-manager

# 2. Suba a aplicação
docker compose up --build -d

# 3. Acesse no navegador
#    http://localhost:8080
```

Para parar:
```bash
docker compose down
```

---

### Opção B — Python Puro (Windows/Linux/macOS)

> Pré-requisitos: [Python 3.11+](https://www.python.org/downloads/) instalado.

#### Linux / macOS

```bash
# 1. Clone o repositório
git clone https://github.com/guilesme/football-team-manager.git
cd football-team-manager

# 2. Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie o servidor
python app.py
```

#### Windows (PowerShell)

```powershell
# 1. Clone o repositório
git clone https://github.com/guilesme/football-team-manager.git
cd football-team-manager

# 2. Crie e ative o ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie o servidor
python app.py
```

> Se o PowerShell bloquear a execução de scripts, execute antes:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

Acesse: **http://localhost:8080**

---

## 🗂️ Estrutura do Projeto

```
football-team-manager/
├── app.py                  # Servidor Flask e rotas da API REST
├── requirements.txt        # Dependências Python com versões fixas
├── Dockerfile              # Imagem Docker da aplicação
├── docker-compose.yml      # Orquestração dos containers
├── .env.example            # Template de variáveis de ambiente
│
├── tools/
│   ├── __init__.py
│   └── db_json.py          # Camada de persistência JSON (cross-platform)
│
├── templates/
│   └── index.html          # Dashboard SPA (HTML/CSS/JS)
│
├── data/
│   ├── .gitkeep            # Mantém a pasta no repositório
│   └── db.json             # Banco de dados (gerado automaticamente, ignorado pelo git)
│
└── architecture/
    └── SOP_engine.md       # Regras de negócio e lógica do domínio
```

---

## ⚙️ Configuração (Opcional)

Copie o arquivo de exemplo e ajuste conforme necessário:

```bash
cp .env.example .env
```

| Variável | Padrão | Descrição |
|---|---|---|
| `FLASK_ENV` | `development` | Ambiente Flask |
| `FLASK_DEBUG` | `1` | Modo debug (desabilite em produção) |
| `APP_PORT` | `8080` | Porta da aplicação |
| `VALOR_MENSALIDADE` | `50.00` | Valor da mensalidade em BRL |
| `DB_PATH` | `data/db.json` | Caminho do banco de dados JSON |

---

## 📡 API Reference

Todos os endpoints retornam e aceitam `Content-Type: application/json`.  
A base URL padrão é `http://localhost:8080`.

### 👥 Elenco

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/elenco` | Lista todos os jogadores |
| `POST` | `/api/elenco` | Cria um novo jogador |
| `PUT` | `/api/elenco/{id}` | Atualiza dados do jogador |
| `DELETE` | `/api/elenco/{id}` | Remove um jogador |
| `POST` | `/api/pagar_mensalidade/{id}` | Registra pagamento de mensalidade |

**Exemplo — Criar jogador:**
```bash
curl -X POST http://localhost:8080/api/elenco \
  -H "Content-Type: application/json" \
  -d '{"nome": "Pelé", "posicao": "Atacante"}'
```

---

### 📅 Calendário

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/calendario` | Lista todas as partidas |
| `POST` | `/api/calendario` | Cria uma nova partida |
| `PUT` | `/api/calendario/{id}` | Atualiza dados/placar da partida |
| `DELETE` | `/api/calendario/{id}` | Remove uma partida |

**Exemplo — Registrar partida finalizada:**
```bash
curl -X POST http://localhost:8080/api/calendario \
  -H "Content-Type: application/json" \
  -d '{
    "data": "2026-03-15",
    "adversario": "Santos FC",
    "placar_casa": 2,
    "placar_fora": 1,
    "status": "finalizado",
    "artilheiros": [1, 1, 2]
  }'
```

> 💡 `artilheiros` é uma lista de `jogador_id`. Repetir um ID conta como gol extra do mesmo jogador.

---

### 💰 Financeiro

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/financeiro` | Lista todas as transações |
| `POST` | `/api/financeiro` | Cria uma transação manual |
| `PUT` | `/api/financeiro/{id}` | Atualiza uma transação |
| `DELETE` | `/api/financeiro/{id}` | Remove uma transação |

**Tipos de transação:** `receita` | `despesa`  
**Status:** `pendente` | `pago`

**Exemplo — Registrar despesa:**
```bash
curl -X POST http://localhost:8080/api/financeiro \
  -H "Content-Type: application/json" \
  -d '{
    "descricao": "Aluguel do campo",
    "valor": 200.00,
    "tipo": "despesa",
    "status": "pago",
    "data": "2026-03-15"
  }'
```

---

### 📊 Estatísticas

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/stats` | Retorna estatísticas consolidadas |

**Resposta:**
```json
{
  "total_jogadores": 10,
  "artilharia": [{ "id": 1, "nome": "Pelé", "gols": 5 }],
  "saldo": 150.00,
  "receitas": 200.00,
  "despesas": 50.00,
  "proximo_jogo": { "data": "2026-04-01", "adversario": "Corinthians" },
  "vitorias": 3,
  "empates": 1,
  "derrotas": 0
}
```

---

## 🗄️ Modelo de Dados

O banco de dados é um único arquivo `data/db.json` com a seguinte estrutura:

```json
{
  "config":    { "ano": 2026, "moeda": "BRL" },
  "elenco":    [ { "id": 1, "nome": "...", "posicao": "...", "gols": 0 } ],
  "calendario":[ { "id": "match_001", "data": "...", "adversario": "...",
                   "placar_casa": 0, "placar_fora": 0,
                   "status": "agendado", "artilheiros": [] } ],
  "financeiro":[ { "id": "tx_001", "jogador_id": 1, "descricao": "...",
                   "valor": 50.0, "tipo": "receita",
                   "status": "pago", "data": "..." } ]
}
```

> O arquivo `db.json` **não é versionado** (listado no `.gitignore`). Ele é criado automaticamente com dados vazios na primeira execução.

---

## 🧱 Regras de Negócio

Para detalhes sobre as regras de negócio do domínio, consulte [`architecture/SOP_engine.md`](architecture/SOP_engine.md).

**Resumo:**
- **Saldo** = Σ(receitas pagas) − Σ(despesas pagas)
- **Artilharia** = jogadores ordenados por `gols` DESC
- **Fluxo de Partida**: `agendado → finalizado` (ao finalizar, artilheiros têm gols incrementados)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para o guia completo.

**Resumo rápido:**
1. Fork este repositório
2. Crie uma branch: `git checkout -b feature/minha-feature`
3. Commit suas mudanças: `git commit -m 'feat: adiciona nova feature'`
4. Push para a branch: `git push origin feature/minha-feature`
5. Abra um Pull Request

---

## 📋 Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para o histórico de versões.

---

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
