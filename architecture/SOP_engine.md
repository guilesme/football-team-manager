# SOP Engine — Regras de Negócio

## Financeiro
- **Saldo** = Σ(valor onde status = "pago") 
- Cada transação pertence a um `jogador_id`
- Status possíveis: `pendente`, `pago`

## Artilharia
- Ranking = jogadores ordenados por `gols` DESC
- Gols são incrementados ao registrar artilheiros em uma partida finalizada

## Calendário
- Status de partida: `agendado` → `finalizado`
- Ao finalizar, registrar `placar_casa`, `placar_fora` e `artilheiros[]`
- Cada item de `artilheiros` é um `jogador_id`; incrementa o campo `gols` do jogador

## Elenco
- Cada jogador tem: `id`, `nome`, `posicao`, `gols`
- Posições válidas: Goleiro, Zagueiro, Lateral, Volante, Meia, Atacante
