"""
app.py — Flask server for Football Team Management.
Serves the dashboard and provides JSON API endpoints.
"""

import datetime
import os
from decimal import Decimal, InvalidOperation

from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template

from models import db, Config, Jogador, Partida, Transacao

# Load .env file if present (no-op if missing)
load_dotenv()

app = Flask(__name__)

# Database configuration
_DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "data", "app.db")
db_path = os.path.abspath(os.environ.get("DB_PATH", _DEFAULT_DB_PATH))

# Use SQLite for the database
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db.create_all()
    # Initialize config if it doesn't exist
    if not Config.query.first():
        db.session.add(Config(id=1, ano=2026, moeda="BRL"))
        db.session.commit()

# ─── Configuration ────────────────────────────────────────────────────────────

VALOR_MENSALIDADE = Decimal(os.environ.get("VALOR_MENSALIDADE", "50.00"))

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _decimal_to_float(val):
    if isinstance(val, Decimal):
        return float(val)
    return val

def _generate_string_id(model_class, prefix):
    # Retrieve all IDs
    items = model_class.query.with_entities(model_class.id).all()
    # Extract numbers
    nums = []
    for (item_id,) in items:
        if isinstance(item_id, str) and item_id.startswith(prefix + "_"):
            try:
                nums.append(int(item_id[len(prefix) + 1:]))
            except ValueError:
                pass
    n = max(nums) + 1 if nums else 1
    return f"{prefix}_{n:03d}"

def _normalize_artilheiros(raw):
    """Convert artilheiros to the new format [{jogador_id, gols}].
    Accepts both:
      - Old format: [1, 3]           → [{jogador_id:1, gols:1}, {jogador_id:3, gols:1}]
      - New format: [{jogador_id:1, gols:2}, ...]  → passed through
    """
    if not raw:
        return []
    result = []
    for item in raw:
        if isinstance(item, dict):
            result.append({
                "jogador_id": item.get("jogador_id"),
                "gols": item.get("gols", 1)
            })
        else:
            # Old format: plain integer ID
            result.append({"jogador_id": item, "gols": 1})
    return result

def _total_gols_artilheiros(artilheiros):
    """Sum all goals from normalized artilheiros list."""
    return sum(a.get("gols", 1) for a in artilheiros)

def _paginate(query):
    """Paginate a collection based on ?limit= and ?offset= query params.
    If neither param is present, returns the raw list (backward compatible).
    If params are present, returns {data, total, limit, offset}.
    """
    limit = request.args.get("limit", type=int)
    offset = request.args.get("offset", 0, type=int)

    if limit is None:
        items = query.all()
        return jsonify([item.to_dict() for item in items])

    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return jsonify({
        "data": [item.to_dict() for item in items],
        "total": total,
        "limit": limit,
        "offset": offset
    })


# ─── Dashboard ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/api/pagar_mensalidade/<int:jogador_id>', methods=['POST'])
def pagar_mensalidade(jogador_id):
    jogador = db.session.get(Jogador, jogador_id)
    if not jogador:
        return jsonify({"error": "Jogador não encontrado"}), 404
        
    tx_id = _generate_string_id(Transacao, "tx")
    pagamento = Transacao(
        id=tx_id,
        jogador_id=jogador_id,
        descricao="Mensalidade Fixa",
        valor=float(VALOR_MENSALIDADE),
        tipo="receita",
        status="pago",
        data=datetime.date.today().isoformat()
    )
    db.session.add(pagamento)
    db.session.commit()
    return jsonify(pagamento.to_dict()), 201

# ─── Elenco (Squad) API ──────────────────────────────────────────────────────

@app.route("/api/elenco", methods=["GET"])
def get_elenco():
    return _paginate(Jogador.query)

@app.route("/api/elenco", methods=["POST"])
def add_jogador():
    data = request.get_json(force=True)
    jogador = Jogador(
        nome=data.get("nome", ""),
        posicao=data.get("posicao", ""),
        gols=0
    )
    db.session.add(jogador)
    db.session.commit()
    return jsonify(jogador.to_dict()), 201

@app.route("/api/elenco/<int:jogador_id>", methods=["PUT"])
def update_jogador(jogador_id):
    data = request.get_json(force=True) or {}
    jogador = db.session.get(Jogador, jogador_id)
    if not jogador:
        return jsonify({"error": "Jogador não encontrado"}), 404
        
    jogador.nome = data.get("nome", jogador.nome)
    jogador.posicao = data.get("posicao", jogador.posicao)
    if "gols" in data:
        jogador.gols = data["gols"]
        
    db.session.commit()
    return jsonify(jogador.to_dict())

@app.route("/api/elenco/<int:jogador_id>", methods=["DELETE"])
def delete_jogador(jogador_id):
    jogador = db.session.get(Jogador, jogador_id)
    if not jogador:
        return jsonify({"error": "Jogador não encontrado"}), 404
        
    db.session.delete(jogador)
    db.session.commit()
    return jsonify({"ok": True})

# ─── Calendário (Matches) API ────────────────────────────────────────────────

@app.route("/api/calendario", methods=["GET"])
def get_calendario():
    return _paginate(Partida.query)


@app.route("/api/calendario", methods=["POST"])
def add_partida():
    data = request.get_json(force=True)
    artilheiros = _normalize_artilheiros(data.get("artilheiros", []))
    
    placar_casa = data.get("placar_casa", 0)
    total_gols = _total_gols_artilheiros(artilheiros)
    warning = None
    if artilheiros and placar_casa < total_gols:
        warning = f"Placar ajustado de {placar_casa} para {total_gols} (soma dos gols dos artilheiros)"
        placar_casa = total_gols
        
    partida_id = _generate_string_id(Partida, "match")
    partida = Partida(
        id=partida_id,
        data=data.get("data", ""),
        adversario=data.get("adversario", ""),
        placar_casa=placar_casa,
        placar_fora=data.get("placar_fora", 0),
        status=data.get("status", "agendado"),
        artilheiros=artilheiros
    )
    
    # Increment goals for players
    if artilheiros:
        for a in artilheiros:
            jid = a.get("jogador_id")
            gols = a.get("gols", 1)
            j = db.session.get(Jogador, jid)
            if j:
                j.gols += gols
                
    db.session.add(partida)
    db.session.commit()

    response = partida.to_dict()
    if warning:
        response["warning"] = warning
    return jsonify(response), 201


@app.route("/api/calendario/<match_id>", methods=["PUT"])
def update_partida(match_id):
    data = request.get_json(force=True) or {}
    p = db.session.get(Partida, match_id)
    if not p:
        return jsonify({"error": "Partida não encontrada"}), 404
        
    p.data = data.get("data", p.data)
    p.adversario = data.get("adversario", p.adversario)
    p.placar_casa = data.get("placar_casa", p.placar_casa)
    p.placar_fora = data.get("placar_fora", p.placar_fora)
    p.status = data.get("status", p.status)

    raw_artilheiros = data.get("artilheiros")
    if raw_artilheiros is not None:
        # Reset goals from previous artilheiros
        old_artilheiros = _normalize_artilheiros(p.artilheiros)
        if old_artilheiros:
            for a in old_artilheiros:
                jid = a.get("jogador_id")
                gols = a.get("gols", 1)
                j = db.session.get(Jogador, jid)
                if j:
                    j.gols = max(0, j.gols - gols)

        # Apply new goals
        new_artilheiros = _normalize_artilheiros(raw_artilheiros)
        p.artilheiros = new_artilheiros
        for a in new_artilheiros:
            jid = a.get("jogador_id")
            gols = a.get("gols", 1)
            j = db.session.get(Jogador, jid)
            if j:
                j.gols += gols

    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(p, "artilheiros")

    db.session.commit()
    return jsonify(p.to_dict())

@app.route("/api/calendario/<match_id>", methods=["DELETE"])
def delete_partida(match_id):
    p = db.session.get(Partida, match_id)
    if not p:
        return jsonify({"error": "Partida não encontrada"}), 404

    # Revert goal counts from artilheiros
    old_artilheiros = _normalize_artilheiros(p.artilheiros)
    if old_artilheiros:
        for a in old_artilheiros:
            jid = a.get("jogador_id")
            gols = a.get("gols", 1)
            j = db.session.get(Jogador, jid)
            if j:
                j.gols = max(0, j.gols - gols)

    db.session.delete(p)
    db.session.commit()
    return jsonify({"ok": True})

# ─── Financeiro (Finance) API ────────────────────────────────────────────────

@app.route("/api/financeiro", methods=["GET"])
def get_financeiro():
    return _paginate(Transacao.query)

@app.route("/api/financeiro", methods=["POST"])
def add_transacao():
    data = request.get_json(force=True)
    try:
        valor = float(Decimal(str(data.get("valor", 0))))
    except (InvalidOperation, ValueError):
        valor = 0.0
        
    tx_id = _generate_string_id(Transacao, "tx")
    tx = Transacao(
        id=tx_id,
        jogador_id=data.get("jogador_id"),
        descricao=data.get("descricao", ""),
        valor=valor,
        tipo=data.get("tipo", "receita"),
        status=data.get("status", "pendente"),
        data=data.get("data", "")
    )
    db.session.add(tx)
    db.session.commit()
    return jsonify(tx.to_dict()), 201

@app.route("/api/financeiro/<tx_id>", methods=["PUT"])
def update_transacao(tx_id):
    data = request.get_json(force=True) or {}
    tx = db.session.get(Transacao, tx_id)
    if not tx:
        return jsonify({"error": "Transação não encontrada"}), 404
        
    tx.jogador_id = data.get("jogador_id", tx.jogador_id)
    tx.descricao = data.get("descricao", tx.descricao or "")
    try:
        tx.valor = float(Decimal(str(data.get("valor", tx.valor))))
    except (InvalidOperation, ValueError):
        pass
    tx.tipo = data.get("tipo", tx.tipo or "receita")
    tx.status = data.get("status", tx.status)
    tx.data = data.get("data", tx.data)
    
    db.session.commit()
    return jsonify(tx.to_dict())

@app.route("/api/financeiro/<tx_id>", methods=["DELETE"])
def delete_transacao(tx_id):
    tx = db.session.get(Transacao, tx_id)
    if not tx:
        return jsonify({"error": "Transação não encontrada"}), 404
        
    db.session.delete(tx)
    db.session.commit()
    return jsonify({"ok": True})

# ─── Stats API ───────────────────────────────────────────────────────────────

@app.route("/api/stats", methods=["GET"])
def get_stats():
    config = Config.query.first()
    ano = config.ano if config else 2026
    
    # Artilharia ranking
    jogadores = Jogador.query.order_by(Jogador.gols.desc()).all()
    artilharia = [j.to_dict() for j in jogadores]

    # Saldo financeiro
    txs_receita = Transacao.query.filter_by(tipo="receita", status="pago").all()
    txs_despesa = Transacao.query.filter_by(tipo="despesa", status="pago").all()
    
    receitas = sum(Decimal(str(t.valor)) for t in txs_receita)
    despesas = sum(Decimal(str(t.valor)) for t in txs_despesa)
    saldo = receitas - despesas

    # Próximo jogo
    agendados = Partida.query.filter_by(status="agendado").order_by(Partida.data).all()
    proximo_jogo = agendados[0].to_dict() if agendados else None

    # Record
    finalizados = Partida.query.filter_by(status="finalizado").all()
    vitorias = sum(1 for p in finalizados if p.placar_casa > p.placar_fora)
    empates = sum(1 for p in finalizados if p.placar_casa == p.placar_fora)
    derrotas = sum(1 for p in finalizados if p.placar_casa < p.placar_fora)

    return jsonify({
        "total_jogadores": len(jogadores),
        "artilharia": artilharia[:10],
        "saldo": float(saldo),
        "receitas": float(receitas),
        "despesas": float(despesas),
        "proximo_jogo": proximo_jogo,
        "total_jogos": Partida.query.count(),
        "jogos_finalizados": len(finalizados),
        "vitorias": vitorias,
        "empates": empates,
        "derrotas": derrotas,
        "ano": ano
    })

# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("APP_PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
