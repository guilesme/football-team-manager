import os
import json
from app import app
from models import db, Config, Jogador, Partida, Transacao

def migrate():
    json_path = os.path.join("data", "db.json")
    if not os.path.exists(json_path):
        print(f"File {json_path} not found. Nothing to migrate.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with app.app_context():
        # Clear existing data to avoid duplicates if run multiple times
        db.session.query(Transacao).delete()
        db.session.query(Partida).delete()
        db.session.query(Jogador).delete()
        db.session.query(Config).delete()

        # Config
        config_data = data.get('config', {})
        conf = Config(
            id=1,
            ano=config_data.get('ano', 2026),
            moeda=config_data.get('moeda', 'BRL')
        )
        db.session.add(conf)

        # Elenco
        for j in data.get('elenco', []):
            jogador = Jogador(
                id=j['id'],
                nome=j['nome'],
                posicao=j['posicao'],
                gols=j.get('gols', 0)
            )
            db.session.add(jogador)

        # Calendario
        for p in data.get('calendario', []):
            partida = Partida(
                id=p['id'],
                adversario=p.get('adversario', ''),
                placar_casa=p.get('placar_casa', 0),
                placar_fora=p.get('placar_fora', 0),
                data=p.get('data', ''),
                status=p.get('status', 'agendado'),
                artilheiros=p.get('artilheiros', [])
            )
            db.session.add(partida)

        # Financeiro
        for t in data.get('financeiro', []):
            tx = Transacao(
                id=t['id'],
                jogador_id=t.get('jogador_id'),
                descricao=t.get('descricao', ''),
                valor=t.get('valor', 0.0),
                tipo=t.get('tipo', 'receita'),
                status=t.get('status', 'pendente'),
                data=t.get('data', '')
            )
            db.session.add(tx)

        db.session.commit()
        print("Migration complete. Data from db.json has been ported to SQLite.")

if __name__ == "__main__":
    migrate()
