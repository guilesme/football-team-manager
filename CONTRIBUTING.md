# Contributing Guide

Obrigado por considerar contribuir com o **Football Team Manager**! ❤️

## Como contribuir

1. **Fork** o repositório e clone localmente
2. **Crie uma branch** descritiva:
   ```bash
   git checkout -b feat/nome-da-feature
   # ou
   git checkout -b fix/descricao-do-bug
   ```
3. **Faça suas mudanças** e teste localmente (veja abaixo)
4. **Commit** seguindo [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` — nova funcionalidade
   - `fix:` — correção de bug
   - `docs:` — apenas documentação
   - `refactor:` — refatoração sem mudança funcional
   - `chore:` — manutenção, build, CI
5. **Push** e abra um **Pull Request** com descrição clara do que foi feito

## Testando localmente

```bash
# Via Docker (recomendado)
docker compose up --build

# Ou via Python diretamente
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
python app.py
```

## Padrões de código

- Python: siga o estilo do projeto (sem linter externo configurado, use bom senso)
- Use docstrings em funções novas
- Não commita `data/db.json` (está no `.gitignore`)
- Não quebre compatibilidade da API sem versionar

## Reportando bugs

Abra uma [Issue](../../issues/new) com:
- Passos para reproduzir
- Comportamento esperado vs. observado
- Versão do Python/Docker utilizada
- Sistema operacional
