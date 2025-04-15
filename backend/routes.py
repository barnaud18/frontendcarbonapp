from flask import request, jsonify, send_file
import json
import os
from backend.app import app, db
from backend.models import Propriedade, Agricultura, Pecuaria, Emissao, Recomendacao
from backend.utils import calcular_emissoes, gerar_recomendacoes
from backend.app.models.calculo_carbono import calcular_creditos
from datetime import datetime


@app.route('/')
def index():
    """Serve the frontend main page"""
    app.logger.debug("Serving index.html")
    return send_file('../frontend/index.html')

@app.route('/js/<path:path>')
def serve_js(path):
    """Serve JavaScript files"""
    app.logger.debug(f"Serving JS file: {path}")
    return send_file(f'../frontend/js/{path}')

@app.route('/css/<path:path>')
def serve_css(path):
    """Serve CSS files"""
    app.logger.debug(f"Serving CSS file: {path}")
    return send_file(f'../frontend/css/{path}')

@app.route('/api')
def api_index():
    """API root endpoint"""
    return jsonify({"message": "API de Calculadora de Pegada de Carbono Agrícola"})


@app.route('/static/swagger.json')
def swagger_spec():
    """Serve the swagger specification file"""
    with open('swagger.yml', 'r') as f:
        return f.read()


@app.route('/cadastrar_propriedade', methods=['POST'])
def cadastrar_propriedade():
    """
    Register a new property with agricultural and livestock data
    ---
    """
    try:
        data = request.get_json()
        
        # Create property
        nova_propriedade = Propriedade(
            nome=data.get('nome'),
            tamanho_total=data.get('tamanho_total')
        )
        db.session.add(nova_propriedade)
        db.session.flush()  # Get ID without committing
        
        # Create agriculture data
        agricultura = Agricultura(
            propriedade_id=nova_propriedade.id,
            area_agricola=data.get('area_agricola'),
            uso_fertilizante=data.get('uso_fertilizante'),
            consumo_combustivel=data.get('consumo_combustivel'),
            area_pastagem=data.get('area_pastagem', 0)
        )
        db.session.add(agricultura)
        
        # Create livestock data
        pecuaria = Pecuaria(
            propriedade_id=nova_propriedade.id,
            num_bovinos=data.get('num_bovinos', 0)
        )
        db.session.add(pecuaria)
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            "message": "Propriedade cadastrada com sucesso",
            "propriedade_id": nova_propriedade.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/calcular', methods=['POST'])
def calcular():
    """
    Calculate carbon footprint based on property data
    ---
    """
    try:
        data = request.get_json()
        
        # Check if property ID is provided for existing property
        propriedade_id = data.get('propriedade_id')
        
        if propriedade_id:
            # Find existing property
            propriedade = Propriedade.query.get(propriedade_id)
            if not propriedade:
                return jsonify({"error": "Propriedade não encontrada"}), 404
                
            # Update agricultural data
            if propriedade.agricultura:
                propriedade.agricultura.area_agricola = data.get('area_agricola', propriedade.agricultura.area_agricola)
                propriedade.agricultura.uso_fertilizante = data.get('uso_fertilizante', propriedade.agricultura.uso_fertilizante)
                propriedade.agricultura.consumo_combustivel = data.get('consumo_combustivel', propriedade.agricultura.consumo_combustivel)
                propriedade.agricultura.area_pastagem = data.get('area_pastagem', propriedade.agricultura.area_pastagem)
            
            # Update livestock data
            if propriedade.pecuaria:
                propriedade.pecuaria.num_bovinos = data.get('num_bovinos', propriedade.pecuaria.num_bovinos)
        else:
            # Create temporary objects for calculation without saving
            propriedade = Propriedade(
                nome="Cálculo Avulso",
                tamanho_total=data.get('area_agricola', 0) + data.get('area_pastagem', 0)
            )
            
            agricultura = Agricultura(
                propriedade_id=None,
                area_agricola=data.get('area_agricola', 0),
                uso_fertilizante=data.get('uso_fertilizante', 0),
                consumo_combustivel=data.get('consumo_combustivel', 0),
                area_pastagem=data.get('area_pastagem', 0)
            )
            propriedade.agricultura = agricultura
            
            pecuaria = Pecuaria(
                propriedade_id=None,
                num_bovinos=data.get('num_bovinos', 0)
            )
            propriedade.pecuaria = pecuaria
        
        # Calculate emissions
        resultado_emissoes = calcular_emissoes(
            area_agricola=propriedade.agricultura.area_agricola,
            uso_fertilizante=propriedade.agricultura.uso_fertilizante,
            num_bovinos=propriedade.pecuaria.num_bovinos,
            consumo_combustivel=propriedade.agricultura.consumo_combustivel
        )
        
        # Calculate carbon credits if pasture area is provided
        potencial_credito = calcular_creditos(
            area_pastagem=propriedade.agricultura.area_pastagem
        ) if propriedade.agricultura.area_pastagem else 0
        
        # Generate recommendations
        recomendacoes = gerar_recomendacoes(
            emissao_agricultura=resultado_emissoes['agricultura'],
            emissao_pecuaria=resultado_emissoes['pecuaria'],
            emissao_combustivel=resultado_emissoes['combustivel'],
            num_bovinos=propriedade.pecuaria.num_bovinos,
            uso_fertilizante=propriedade.agricultura.uso_fertilizante
        )
        
        # Save emission results if it's an existing property
        if propriedade_id:
            # Delete old emission record if exists
            if propriedade.emissao:
                db.session.delete(propriedade.emissao)
                
            # Delete old recommendations if exist
            for rec in propriedade.recomendacoes:
                db.session.delete(rec)
            
            # Create new emission record
            emissao = Emissao(
                propriedade_id=propriedade_id,
                total_emissao=resultado_emissoes['total'],
                emissao_agricultura=resultado_emissoes['agricultura'],
                emissao_pecuaria=resultado_emissoes['pecuaria'],
                emissao_combustivel=resultado_emissoes['combustivel'],
                potencial_credito=potencial_credito
            )
            db.session.add(emissao)
            
            # Create new recommendations
            for rec in recomendacoes:
                recomendacao = Recomendacao(
                    propriedade_id=propriedade_id,
                    acao=rec['acao'],
                    descricao=rec['descricao'],
                    potencial_reducao=rec['potencial_reducao']
                )
                db.session.add(recomendacao)
            
            db.session.commit()
        
        # Prepare response
        response = {
            "pegada_total_kg_co2e": round(resultado_emissoes['total'], 2),
            "detalhes": {
                "agricultura": round(resultado_emissoes['agricultura'], 2),
                "pecuaria": round(resultado_emissoes['pecuaria'], 2),
                "combustivel": round(resultado_emissoes['combustivel'], 2)
            },
            "potencial_credito_tco2e": round(potencial_credito, 2),
            "recomendacoes": recomendacoes
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/buscar_usuario/<int:propriedade_id>', methods=['GET'])
def buscar_usuario(propriedade_id):
    """
    Retrieve property data by ID
    ---
    """
    try:
        propriedade = Propriedade.query.get(propriedade_id)
        if not propriedade:
            return jsonify({"error": "Propriedade não encontrada"}), 404
            
        return jsonify(propriedade.to_dict()), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/calcular-creditos', methods=['POST'])
def calcular_creditos_route():
    """
    Calculate carbon credits potential
    ---
    """
    try:
        data = request.get_json()
        
        # Extrair e validar áreas
        try:
            area_pastagem = float(data.get('area_pastagem', 0) or 0)
            area_florestal = float(data.get('area_florestal', 0) or 0)
            area_renovacao_cultura = float(data.get('area_renovacao_cultura', 0) or 0)
            area_integracao_lavoura = float(data.get('area_integracao_lavoura', 0) or 0)
        except (ValueError, TypeError):
            return jsonify({"error": "Valores inválidos fornecidos para as áreas"}), 400
        
        # Verificar se pelo menos uma área foi fornecida
        if area_pastagem <= 0 and area_florestal <= 0 and area_renovacao_cultura <= 0 and area_integracao_lavoura <= 0:
            return jsonify({"error": "Pelo menos uma área deve ser maior que zero"}), 400
        
        # Calcular créditos
        resultados = calcular_creditos(
            area_pastagem=area_pastagem,
            area_florestal=area_florestal,
            area_renovacao_cultura=area_renovacao_cultura,
            area_integracao_lavoura=area_integracao_lavoura
        )
        
        return jsonify(resultados), 200
        
    except Exception as e:
        app.logger.error(f"Erro ao calcular créditos: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/propriedades', methods=['GET'])
def listar_propriedades():
    """
    List all registered properties
    ---
    """
    try:
        propriedades = Propriedade.query.all()
        return jsonify([p.to_dict() for p in propriedades]), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/cenarios', methods=['GET'])
def listar_cenarios():
    """
    List all calculation scenarios
    ---
    """
    try:
        # Por enquanto, retornar dados de exemplo
        cenarios = [
            {
                "id": 1,
                "nome": "Cenário Base",
                "data_calculo": datetime.now().strftime("%Y-%m-%d"),
                "area_pastagem": 100.0,
                "area_florestal": 50.0,
                "area_renovacao_cultura": 30.0,
                "area_integracao_lavoura": 20.0,
                "credito_pastagem": 50.0,
                "credito_florestal": 400.0,
                "credito_renovacao": 36.0,
                "credito_integracao": 60.0,
                "total_creditos": 546.0,
                "valor_estimado": 27300.0
            },
            {
                "id": 2,
                "nome": "Cenário Otimizado",
                "data_calculo": datetime.now().strftime("%Y-%m-%d"),
                "area_pastagem": 150.0,
                "area_florestal": 80.0,
                "area_renovacao_cultura": 50.0,
                "area_integracao_lavoura": 40.0,
                "credito_pastagem": 75.0,
                "credito_florestal": 640.0,
                "credito_renovacao": 60.0,
                "credito_integracao": 120.0,
                "total_creditos": 895.0,
                "valor_estimado": 44750.0
            }
        ]
        return jsonify(cenarios), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/cenarios/<int:id>', methods=['GET'])
def obter_cenario(id):
    """
    Retrieve a specific scenario by ID
    ---
    """
    try:
        # Buscar o cenário no banco de dados
        cenario = db.session.query(CalculoCarbono).filter_by(id=id).first()
        
        if not cenario:
            return jsonify({"error": "Cenário não encontrado"}), 404
            
        # Converter para dict
        cenario_dict = {
            "id": cenario.id,
            "nome_cenario": cenario.nome_cenario,
            "area_pastagem": cenario.area_pastagem,
            "area_florestal": cenario.area_florestal,
            "area_renovacao_cultura": cenario.area_renovacao_cultura,
            "area_integracao_lavoura": cenario.area_integracao_lavoura,
            "credito_pastagem": cenario.credito_pastagem,
            "credito_florestal": cenario.credito_florestal,
            "credito_renovacao": cenario.credito_renovacao,
            "credito_integracao": cenario.credito_integracao,
            "total_creditos": cenario.total_creditos,
            "valor_estimado": cenario.valor_estimado,
            "data_calculo": cenario.data_calculo.isoformat() if cenario.data_calculo else None
        }
        
        return jsonify(cenario_dict), 200
        
    except Exception as e:
        app.logger.error(f"Erro ao buscar cenário: {str(e)}")
        return jsonify({"error": "Erro ao buscar cenário"}), 500
