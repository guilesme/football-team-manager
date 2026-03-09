"""
app.py — Flask server for Football Team Management.
Serves the dashboard and provides JSON API endpoints.
"""

import datetime
import os
from decimal import Decimal, InvalidOperation

from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from tools.db_json import load_db, save_db, next_id, next_str_id

# Load .env file if present (no-op if missing)
load_dotenv()

app = Flask(__name__)


# ─── Dashboard ────────────────────────────────────────────────────────────────

VALOR_MENSALIDADE = Decimal(os.environ.get("VALOR_MENSALIDADE", "50.00"))


def _decimal_to_float(val):
    """Safely convert Decimal (or any numeric) to float for JSON."""
    if isinstance(val, Decimal):
        return float(val)
    return val


@app.route("/")
def index():
    return render_template("index.html")

@app.route('/api/pagar_mensalidade/<int:jogador_id>', methods=['POST'])
def pagar_mensalidade(jogador_id):
    db = load_db()
    
    # Valida se jogador existe
    jog_existe = any(j["id"] == jogador_id for j in db["elenco"])
    if not jog_existe:
        return jsonify({"error": "Jogador não encontrado"}), 404
        
    pagamento = {
        "id": next_str_id(db["financeiro"], "tx"),
        "jogador_id": jogador_id,
        "descricao": "Mensalidade Fixa",
        "valor": float(VALOR_MENSALIDADE),
        "tipo": "receita",
        "status": "pago",
        "data": datetime.date.today().isoformat()
    }
    db['financeiro'].append(pagamento)
    save_db(db)
    return jsonify(pagamento), 201

# ─── Elenco (Squad) API ──────────────────────────────────────────────────────

@app.route("/api/elenco", methods=["GET"])
def get_elenco():
    db = load_db()
    return jsonify(db["elenco"])


@app.route("/api/elenco", methods=["POST"])
def add_jogador():
    db = load_db()
    data = request.get_json(force=True)
    jogador = {
        "id": next_id(db["elenco"]),
        "nome": data.get("nome", ""),
        "posicao": data.get("posicao", ""),
        "gols": 0
    }
    db["elenco"].append(jogador)
    save_db(db)
    return jsonify(jogador), 201


@app.route("/api/elenco/<int:jogador_id>", methods=["PUT"])
def update_jogador(jogador_id):
    db = load_db()
    data = request.get_json(force=True) or {}
    for j in db["elenco"]:
        if j["id"] == jogador_id:
            j["nome"] = data.get("nome", j["nome"])
            j["posicao"] = data.get("posicao", j["posicao"])
            if "gols" in data:
                j["gols"] = data["gols"]
            save_db(db)
            return jsonify(j)
    return jsonify({"error": "Jogador não encontrado"}), 404


@app.route("/api/elenco/<int:jogador_id>", methods=["DELETE"])
def delete_jogador(jogador_id):
    db = load_db()
    before = len(db["elenco"])
    db["elenco"] = [j for j in db["elenco"] if j["id"] != jogador_id]
    if len(db["elenco"]) == before:
        return jsonify({"error": "Jogador não encontrado"}), 404
    save_db(db)
    return jsonify({"ok": True})


# ─── Calendário (Matches) API ────────────────────────────────────────────────

@app.route("/api/calendario", methods=["GET"])
def get_calendario():
    db = load_db()
    return jsonify(db["calendario"])


@app.route("/api/calendario", methods=["POST"])
def add_partida():
    db = load_db()
    data = request.get_json(force=True)
    artilheiros = data.get("artilheiros", [])
    
    # Calculate goals for team
    placar_casa = data.get("placar_casa", 0)
    warning = None
    if artilheiros and placar_casa < len(artilheiros):
        warning = f"Placar ajustado de {placar_casa} para {len(artilheiros)} (quantidade de artilheiros marcados)"
        placar_casa = len(artilheiros)
        
    partida = {
        "id": next_str_id(db["calendario"], "match"),
        "data": data.get("data", ""),
        "adversario": data.get("adversario", ""),
        "placar_casa": placar_casa,
        "placar_fora": data.get("placar_fora", 0),
        "status": data.get("status", "agendado"),
        "artilheiros": artilheiros
    }
    
    # Increment goals for players
    if artilheiros:
        for jid in artilheiros:
            for j in db["elenco"]:
                if j["id"] == jid:
                    j["gols"] += 1
                    
    db["calendario"].append(partida)
    save_db(db)

    response = dict(partida)
    if warning:
        response["warning"] = warning
    return jsonify(response), 201


@app.route("/api/calendario/<match_id>", methods=["PUT"])
def update_partida(match_id):
    db = load_db()
    data = request.get_json(force=True) or {}
    for p in db["calendario"]:
        if p["id"] == match_id:
            p["data"] = data.get("data", p["data"])
            p["adversario"] = data.get("adversario", p["adversario"])
            p["placar_casa"] = data.get("placar_casa", p["placar_casa"])
            p["placar_fora"] = data.get("placar_fora", p["placar_fora"])
            p["status"] = data.get("status", p["status"])

            # Handle goal scorers — update player goal counts
            new_artilheiros = data.get("artilheiros")
            if new_artilheiros is not None:
                # Reset goals from previous artilheiros for this match
                for jid in p["artilheiros"]:
                    for j in db["elenco"]:
                        if j["id"] == jid:
                            j["gols"] = max(0, j["gols"] - 1)

                # Apply new artilheiros
                p["artilheiros"] = new_artilheiros
                for jid in new_artilheiros:
                    for j in db["elenco"]:
                        if j["id"] == jid:
                            j["gols"] += 1

            save_db(db)
            return jsonify(p)
    return jsonify({"error": "Partida não encontrada"}), 404


@app.route("/api/calendario/<match_id>", methods=["DELETE"])
def delete_partida(match_id):
    db = load_db()
    found = None
    for p in db["calendario"]:
        if p["id"] == match_id:
            found = p
            break
    if not found:
        return jsonify({"error": "Partida não encontrada"}), 404

    # Revert goal counts from artilheiros
    for jid in found.get("artilheiros", []):
        for j in db["elenco"]:
            if j["id"] == jid:
                j["gols"] = max(0, j["gols"] - 1)

    db["calendario"] = [p for p in db["calendario"] if p["id"] != match_id]
    save_db(db)
    return jsonify({"ok": True})


# ─── Financeiro (Finance) API ────────────────────────────────────────────────

@app.route("/api/financeiro", methods=["GET"])
def get_financeiro():
    db = load_db()
    return jsonify(db["financeiro"])


@app.route("/api/financeiro", methods=["POST"])
def add_transacao():
    db = load_db()
    data = request.get_json(force=True)
    try:
        valor = float(Decimal(str(data.get("valor", 0))))
    except (InvalidOperation, ValueError):
        valor = 0.0
    tx = {
        "id": next_str_id(db["financeiro"], "tx"),
        "jogador_id": data.get("jogador_id"),
        "descricao": data.get("descricao", ""),
        "valor": valor,
        "tipo": data.get("tipo", "receita"),  # receita | despesa
        "status": data.get("status", "pendente"),
        "data": data.get("data", "")
    }
    db["financeiro"].append(tx)
    save_db(db)
    return jsonify(tx), 201


@app.route("/api/financeiro/<tx_id>", methods=["PUT"])
def update_transacao(tx_id):
    db = load_db()
    data = request.get_json(force=True) or {}
    for tx in db["financeiro"]:
        if tx["id"] == tx_id:
            tx["jogador_id"] = data.get("jogador_id", tx["jogador_id"])
            tx["descricao"] = data.get("descricao", tx.get("descricao", ""))
            try:
                tx["valor"] = float(Decimal(str(data.get("valor", tx["valor"]))))
            except (InvalidOperation, ValueError):
                pass
            tx["tipo"] = data.get("tipo", tx.get("tipo", "receita"))
            tx["status"] = data.get("status", tx["status"])
            tx["data"] = data.get("data", tx["data"])
            save_db(db)
            return jsonify(tx)
    return jsonify({"error": "Transação não encontrada"}), 404


@app.route("/api/financeiro/<tx_id>", methods=["DELETE"])
def delete_transacao(tx_id):
    db = load_db()
    before = len(db["financeiro"])
    db["financeiro"] = [t for t in db["financeiro"] if t["id"] != tx_id]
    if len(db["financeiro"]) == before:
        return jsonify({"error": "Transação não encontrada"}), 404
    save_db(db)
    return jsonify({"ok": True})


# ─── Stats API ───────────────────────────────────────────────────────────────

@app.route("/api/stats", methods=["GET"])
def get_stats():
    db = load_db()

    # Artilharia ranking
    artilharia = sorted(db["elenco"], key=lambda j: j["gols"], reverse=True)

    # Saldo financeiro
    receitas = sum(
        Decimal(str(t["valor"])) for t in db["financeiro"]
        if t.get("tipo") == "receita" and t["status"] == "pago"
    )
    despesas = sum(
        Decimal(str(t["valor"])) for t in db["financeiro"]
        if t.get("tipo") == "despesa" and t["status"] == "pago"
    )
    saldo = receitas - despesas

    # Próximo jogo
    agendados = [p for p in db["calendario"] if p["status"] == "agendado"]
    agendados.sort(key=lambda p: p["data"])
    proximo_jogo = agendados[0] if agendados else None

    # Record
    finalizados = [p for p in db["calendario"] if p["status"] == "finalizado"]
    vitorias = sum(1 for p in finalizados if p["placar_casa"] > p["placar_fora"])
    empates = sum(1 for p in finalizados if p["placar_casa"] == p["placar_fora"])
    derrotas = sum(1 for p in finalizados if p["placar_casa"] < p["placar_fora"])

    return jsonify({
        "total_jogadores": len(db["elenco"]),
        "artilharia": artilharia[:10],
        "saldo": float(saldo),
        "receitas": float(receitas),
        "despesas": float(despesas),
        "proximo_jogo": proximo_jogo,
        "total_jogos": len(db["calendario"]),
        "jogos_finalizados": len(finalizados),
        "vitorias": vitorias,
        "empates": empates,
        "derrotas": derrotas,
        "ano": db["config"]["ano"]
    })


# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("APP_PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
