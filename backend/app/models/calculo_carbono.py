from datetime import datetime
from .. import db

class CalculoCarbono(db.Model):
    """Modelo para armazenar cálculos de créditos de carbono"""
    id = db.Column(db.Integer, primary_key=True)
    nome_cenario = db.Column(db.String(100), nullable=True)
    area_pastagem = db.Column(db.Float, nullable=True, default=0)
    area_florestal = db.Column(db.Float, nullable=True, default=0)
    area_renovacao_cultura = db.Column(db.Float, nullable=True, default=0)
    area_integracao_lavoura = db.Column(db.Float, nullable=True, default=0)
    credito_pastagem = db.Column(db.Float, nullable=True, default=0)
    credito_florestal = db.Column(db.Float, nullable=True, default=0)
    credito_renovacao = db.Column(db.Float, nullable=True, default=0)
    credito_integracao = db.Column(db.Float, nullable=True, default=0)
    total_creditos = db.Column(db.Float, nullable=True, default=0)
    valor_estimado = db.Column(db.Float, nullable=True, default=0)
    data_calculo = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_cenario': self.nome_cenario,
            'area_pastagem': self.area_pastagem,
            'area_florestal': self.area_florestal,
            'area_renovacao_cultura': self.area_renovacao_cultura,
            'area_integracao_lavoura': self.area_integracao_lavoura,
            'credito_pastagem': self.credito_pastagem,
            'credito_florestal': self.credito_florestal,
            'credito_renovacao': self.credito_renovacao, 
            'credito_integracao': self.credito_integracao,
            'total_creditos': self.total_creditos,
            'valor_estimado': self.valor_estimado,
            'data_calculo': self.data_calculo.strftime('%Y-%m-%d %H:%M') if self.data_calculo else None
        }

def calcular_creditos(area_pastagem=0, area_florestal=0, area_renovacao_cultura=0, area_integracao_lavoura=0):
    """
    Calcula o potencial de créditos de carbono com base em diferentes metodologias
    """
    # Fatores de conversão por metodologia
    credito_pastagem = area_pastagem * 0.5  # VCS VM0032
    credito_florestal = area_florestal * 8.0  # AR-ACM0003
    credito_renovacao = area_renovacao_cultura * 1.2  # CDM AMS-III.AU
    credito_integracao = area_integracao_lavoura * 3.0  # VCS VM0017
    
    total_creditos = credito_pastagem + credito_florestal + credito_renovacao + credito_integracao
    valor_estimado = total_creditos * 50  # R$50 por tCO2e
    
    resultados = {
        "pastagem": {
            "area": area_pastagem,
            "fator": 0.5,
            "creditos": credito_pastagem,
            "metodologia": "VCS VM0032 - Recuperação de pastagens degradadas"
        },
        "florestal": {
            "area": area_florestal,
            "fator": 8.0,
            "creditos": credito_florestal,
            "metodologia": "AR-ACM0003 - Florestamento e reflorestamento"
        },
        "renovacao": {
            "area": area_renovacao_cultura,
            "fator": 1.2,
            "creditos": credito_renovacao,
            "metodologia": "CDM AMS-III.AU - Práticas agrícolas de baixo carbono"
        },
        "integracao": {
            "area": area_integracao_lavoura,
            "fator": 3.0,
            "creditos": credito_integracao,
            "metodologia": "VCS VM0017 - Sistemas de integração lavoura-pecuária"
        }
    }
    
    # Salvar no banco de dados
    cenario = CalculoCarbono(
        area_pastagem=area_pastagem,
        area_florestal=area_florestal,
        area_renovacao_cultura=area_renovacao_cultura,
        area_integracao_lavoura=area_integracao_lavoura,
        credito_pastagem=credito_pastagem,
        credito_florestal=credito_florestal,
        credito_renovacao=credito_renovacao,
        credito_integracao=credito_integracao,
        total_creditos=total_creditos,
        valor_estimado=valor_estimado
    )
    
    db.session.add(cenario)
    db.session.commit()
    
    # Adicionar o ID do cenário ao resultado
    resultados['id'] = cenario.id
    
    return {
        "total_creditos": total_creditos,
        "valor_estimado": valor_estimado,
        "resultados": resultados
    } 