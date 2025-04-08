from backend.app import db
from datetime import datetime

class Propriedade(db.Model):
    """Model for property (farm) data"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tamanho_total = db.Column(db.Float, nullable=False)  # Total size in hectares
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    agricultura = db.relationship('Agricultura', backref='propriedade', lazy=True, uselist=False)
    pecuaria = db.relationship('Pecuaria', backref='propriedade', lazy=True, uselist=False)
    emissao = db.relationship('Emissao', backref='propriedade', lazy=True, uselist=False)
    recomendacoes = db.relationship('Recomendacao', backref='propriedade', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tamanho_total': self.tamanho_total,
            'data_registro': self.data_registro.isoformat() if self.data_registro else None,
            'agricultura': self.agricultura.to_dict() if self.agricultura else None,
            'pecuaria': self.pecuaria.to_dict() if self.pecuaria else None,
            'emissao': self.emissao.to_dict() if self.emissao else None,
            'recomendacoes': [rec.to_dict() for rec in self.recomendacoes] if self.recomendacoes else []
        }


class Agricultura(db.Model):
    """Model for agricultural data"""
    id = db.Column(db.Integer, primary_key=True)
    propriedade_id = db.Column(db.Integer, db.ForeignKey('propriedade.id'), nullable=False)
    area_agricola = db.Column(db.Float, nullable=False)  # Agricultural area in hectares
    uso_fertilizante = db.Column(db.Float, nullable=False)  # Fertilizer use in kg/ha/year
    consumo_combustivel = db.Column(db.Float, nullable=False)  # Fuel consumption in liters/year
    area_pastagem = db.Column(db.Float, nullable=True)  # Pasture area in hectares for carbon credit calculation
    
    def to_dict(self):
        return {
            'id': self.id,
            'propriedade_id': self.propriedade_id,
            'area_agricola': self.area_agricola,
            'uso_fertilizante': self.uso_fertilizante,
            'consumo_combustivel': self.consumo_combustivel,
            'area_pastagem': self.area_pastagem
        }


class Pecuaria(db.Model):
    """Model for livestock data"""
    id = db.Column(db.Integer, primary_key=True)
    propriedade_id = db.Column(db.Integer, db.ForeignKey('propriedade.id'), nullable=False)
    num_bovinos = db.Column(db.Integer, nullable=False)  # Number of cattle
    
    def to_dict(self):
        return {
            'id': self.id,
            'propriedade_id': self.propriedade_id,
            'num_bovinos': self.num_bovinos
        }


class Emissao(db.Model):
    """Model for emission calculation results"""
    id = db.Column(db.Integer, primary_key=True)
    propriedade_id = db.Column(db.Integer, db.ForeignKey('propriedade.id'), nullable=False)
    total_emissao = db.Column(db.Float, nullable=False)  # Total emissions in kg CO2e
    emissao_agricultura = db.Column(db.Float, nullable=False)  # Agricultural emissions in kg CO2e
    emissao_pecuaria = db.Column(db.Float, nullable=False)  # Livestock emissions in kg CO2e
    emissao_combustivel = db.Column(db.Float, nullable=False)  # Fuel emissions in kg CO2e
    potencial_credito = db.Column(db.Float, nullable=True)  # Potential carbon credits in tCO2e
    data_calculo = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'propriedade_id': self.propriedade_id,
            'total_emissao': self.total_emissao,
            'emissao_agricultura': self.emissao_agricultura,
            'emissao_pecuaria': self.emissao_pecuaria,
            'emissao_combustivel': self.emissao_combustivel,
            'potencial_credito': self.potencial_credito,
            'data_calculo': self.data_calculo.isoformat() if self.data_calculo else None
        }


class Recomendacao(db.Model):
    """Model for mitigation recommendations"""
    id = db.Column(db.Integer, primary_key=True)
    propriedade_id = db.Column(db.Integer, db.ForeignKey('propriedade.id'), nullable=False)
    acao = db.Column(db.String(255), nullable=False)  # Recommendation action
    descricao = db.Column(db.Text, nullable=True)  # Detailed description
    potencial_reducao = db.Column(db.Float, nullable=False)  # Potential reduction in kg CO2e
    
    def to_dict(self):
        return {
            'id': self.id,
            'propriedade_id': self.propriedade_id,
            'acao': self.acao,
            'descricao': self.descricao,
            'potencial_reducao': self.potencial_reducao
        }
