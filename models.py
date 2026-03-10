from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, default=2026)
    moeda = db.Column(db.String(10), default="BRL")

    def to_dict(self):
        return {
            "ano": self.ano,
            "moeda": self.moeda
        }

class Jogador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    posicao = db.Column(db.String(50), nullable=False)
    gols = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "posicao": self.posicao,
            "gols": self.gols
        }

class Partida(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    adversario = db.Column(db.String(100), nullable=False)
    placar_casa = db.Column(db.Integer, default=0)
    placar_fora = db.Column(db.Integer, default=0)
    data = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="agendado")
    artilheiros = db.Column(db.JSON, default=list)

    def to_dict(self):
        return {
            "id": self.id,
            "adversario": self.adversario,
            "placar_casa": self.placar_casa,
            "placar_fora": self.placar_fora,
            "data": self.data,
            "status": self.status,
            "artilheiros": self.artilheiros if self.artilheiros is not None else []
        }

class Transacao(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    jogador_id = db.Column(db.Integer, db.ForeignKey('jogador.id'), nullable=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, default=0.0)
    tipo = db.Column(db.String(50), default="receita")
    status = db.Column(db.String(50), default="pendente")
    data = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "jogador_id": self.jogador_id,
            "descricao": self.descricao,
            "valor": self.valor,
            "tipo": self.tipo,
            "status": self.status,
            "data": self.data
        }
