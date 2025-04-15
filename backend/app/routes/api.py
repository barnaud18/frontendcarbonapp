from flask import Blueprint, jsonify, request
from flask_restful import Resource, Api
from ..models.calculo_carbono import CalculoCarbono, db, calcular_creditos

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

class CalcularCreditosResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data:
                return {'error': 'Dados não fornecidos'}, 400
                
            # Validar e converter os dados
            try:
                area_pastagem = float(data.get('area_pastagem', 0))
                area_florestal = float(data.get('area_florestal', 0))
                area_renovacao = float(data.get('area_renovacao_cultura', 0))
                area_integracao = float(data.get('area_integracao_lavoura', 0))
            except ValueError:
                return {'error': 'Valores inválidos fornecidos'}, 400
                
            # Validar se pelo menos uma área foi fornecida
            if area_pastagem == 0 and area_florestal == 0 and area_renovacao == 0 and area_integracao == 0:
                return {'error': 'Pelo menos uma área deve ser maior que zero'}, 400
                
            resultados = calcular_creditos(
                area_pastagem=area_pastagem,
                area_florestal=area_florestal,
                area_renovacao_cultura=area_renovacao,
                area_integracao_lavoura=area_integracao
            )
            
            return resultados
            
        except Exception as e:
            return {'error': str(e)}, 500

class CalcularCreditosHifenResource(Resource):
    def post(self):
        # Chama o mesmo método da classe principal
        return CalcularCreditosResource().post()

class CenariosListResource(Resource):
    def get(self):
        try:
            cenarios = CalculoCarbono.query.order_by(CalculoCarbono.data_calculo.desc()).all()
            return [c.to_dict() for c in cenarios]
        except Exception as e:
            return {'error': str(e)}, 500

class CenarioDetailResource(Resource):
    def get(self, id):
        try:
            cenario = CalculoCarbono.query.get_or_404(id)
            return cenario.to_dict()
        except Exception as e:
            return {'error': str(e)}, 500
            
    def delete(self, id):
        try:
            cenario = CalculoCarbono.query.get_or_404(id)
            db.session.delete(cenario)
            db.session.commit()
            return {'message': 'Cenário excluído com sucesso'}, 200
        except Exception as e:
            return {'error': str(e)}, 500

# Registrar os recursos
api.add_resource(CalcularCreditosResource, '/calcular')
api.add_resource(CalcularCreditosHifenResource, '/calcular-creditos')
api.add_resource(CenariosListResource, '/cenarios')
api.add_resource(CenarioDetailResource, '/cenarios/<int:id>') 