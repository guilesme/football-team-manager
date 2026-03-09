"""
app.py — Flask server for Football Team Management.
Serves the dashboard and provides JSON API endpoints.
"""

from flask import Flask, request, jsonify, render_template
from tools.db_json import load_db, save_db, next_id, next_str_id

app = Flask(__name__)


# ─── Dashboard ────────────────────────────────────────────────────────────────

VALOR_MENSALIDADE = 50.00

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
        "valor": VALOR_MENSALIDADE,
        "tipo": "receita",
        "status": "pago",
        "data": "2026-03-05" # Hoje simplificado
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
    for j in db["elenco"]:
        if j["id"] == jogador_id:
            j["nome"] = request.json.get("nome", j["nome"])
            j["posicao"] = request.json.get("posicao", j["posicao"])
            if "gols" in request.json:
                j["gols"] = request.json["gols"]
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
    if artilheiros and placar_casa < len(artilheiros):
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
    return jsonify(partida), 201


@app.route("/api/calendario/<match_id>", methods=["PUT"])
def update_partida(match_id):
    db = load_db()
    for p in db["calendario"]:
        if p["id"] == match_id:
            p["data"] = request.json.get("data", p["data"])
            p["adversario"] = request.json.get("adversario", p["adversario"])
            p["placar_casa"] = request.json.get("placar_casa", p["placar_casa"])
            p["placar_fora"] = request.json.get("placar_fora", p["placar_fora"])
            p["status"] = request.json.get("status", p["status"])

            # Handle goal scorers — update player goal counts
            new_artilheiros = request.json.get("artilheiros")
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
    tx = {
        "id": next_str_id(db["financeiro"], "tx"),
        "jogador_id": data.get("jogador_id"),
        "descricao": data.get("descricao", ""),
        "valor": float(data.get("valor", 0)),
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
    for tx in db["financeiro"]:
        if tx["id"] == tx_id:
            tx["jogador_id"] = request.json.get("jogador_id", tx["jogador_id"])
            tx["descricao"] = request.json.get("descricao", tx.get("descricao", ""))
            tx["valor"] = float(request.json.get("valor", tx["valor"]))
            tx["tipo"] = request.json.get("tipo", tx.get("tipo", "receita"))
            tx["status"] = request.json.get("status", tx["status"])
            tx["data"] = request.json.get("data", tx["data"])
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
        t["valor"] for t in db["financeiro"]
        if t.get("tipo") == "receita" and t["status"] == "pago"
    )
    despesas = sum(
        t["valor"] for t in db["financeiro"]
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
        "saldo": saldo,
        "receitas": receitas,
        "despesas": despesas,
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
    app.run(host="0.0.0.0", port=8080, debug=True)
