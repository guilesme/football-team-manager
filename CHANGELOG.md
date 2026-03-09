# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.0] — 2026-03-09

### Added
- **Multi-goal support**: replaced binary goal checkboxes with numeric inputs per player. The backend now associates goal quantities with each player per match instead of a flat list, automatically migrating old data.
- **API Pagination**: added `?limit=` and `?offset=` query string parameters to all `GET` routes (`/api/elenco`, `/api/calendario`, `/api/financeiro`) for scalable data fetching.

---

## [1.1.1] — 2026-03-09

### Fixed
- **Delete functions without error handling**: `delElenco`, `delPartida`, and `delTransacao` now wrapped in `try/catch` with user-visible error toasts
- **Import in the middle of the file**: moved `from tools.db_json import ...` to the top of `app.py` (PEP 8)
- **`DB_PATH` relative path failure**: wrapped with `os.path.abspath()` so relative paths from `.env` resolve correctly

---

## [1.1.0] — 2026-03-09

### Security
- **XSS prevention**: added `esc()` HTML escape helper and applied to all `innerHTML` template literals in the frontend
- **`debug=True` removed**: Flask debug mode now reads from `FLASK_DEBUG` env var (defaults to off)
- **Docker non-root user**: container now runs as `appuser` instead of `root`
- **`.dockerignore` added**: prevents `.git`, `data/db.json`, docs, and caches from leaking into the Docker image

### Fixed
- **Mensalidade date hardcoded**: now uses `datetime.date.today().isoformat()` instead of a fixed date
- **`request.json` crash on PUT routes**: replaced with `request.get_json(force=True) or {}` to prevent `AttributeError` when `Content-Type` is not JSON
- **Race condition in `save_db`**: `os.replace()` moved inside the exclusive file lock to prevent data corruption
- **Score silently overwritten**: when `placar_casa < artilheiros`, the backend now returns a `warning` field in the response
- **Artilheiro checkboxes not reset**: checkboxes are now cleared when the match modal is closed or re-opened
- **`saveElenco/Partida/Transacao` without error handling**: all save functions now wrapped in `try/catch` with user-visible error toasts
- **`loadData` silent failure**: errors during initial data load now display a toast notification instead of a blank screen
- **Fragile regex in form reset helper**: `.match()` result is now null-checked before accessing
- **`next_str_id` fragile prefix parsing**: uses `sid[len(prefix)+1:]` instead of `split("_")[1]`
- **`showToast` XSS**: toast messages are now escaped via `esc()`

### Changed
- **Environment variables**: `FLASK_DEBUG`, `APP_PORT`, `VALOR_MENSALIDADE`, and `DB_PATH` are now read from environment/`.env` file with sensible defaults
- **`load_dotenv()` activated**: `python-dotenv` (already in `requirements.txt`) is now called on startup
- **Monetary precision**: financial calculations use `decimal.Decimal` internally, converting to `float` only for JSON serialization

---

## [1.0.0] — 2026-03-09

### Added
- Dashboard SPA com design dark glassmorphic
- Módulo **Elenco**: cadastro, edição e remoção de jogadores com posição e gols
- Módulo **Calendário**: agendamento e resultado de partidas com artilheiros
- Módulo **Financeiro**: controle de receitas e despesas com saldo em tempo real
- Módulo **Estatísticas**: ranking de artilharia, aproveitamento e próximo jogo
- API REST completa com endpoints para elenco, calendário, financeiro e stats
- Persistência em JSON com file locking cross-platform (Windows & Unix)
- Suporte a Docker e Docker Compose
- Documentação completa (README, CONTRIBUTING, CHANGELOG)
- `.gitignore`, `.env.example` e `LICENSE` (MIT)
