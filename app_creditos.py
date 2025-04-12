from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Inicializar app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "chave_secreta_temporaria")

# Calculadora de créditos simplificada
def calcular_creditos(area_pastagem=0, area_florestal=0, area_renovacao_cultura=0, area_integracao_lavoura=0):
    """
    Calcula o potencial de créditos de carbono com base em diferentes metodologias
    """
    credito_pastagem = area_pastagem * 0.5  # VCS VM0032
    credito_florestal = area_florestal * 8.0  # AR-ACM0003
    credito_renovacao = area_renovacao_cultura * 1.2  # CDM AMS-III.AU
    credito_integracao = area_integracao_lavoura * 3.0  # VCS VM0017
    
    total_creditos = credito_pastagem + credito_florestal + credito_renovacao + credito_integracao
    
    resultados = {}
    
    if area_pastagem > 0:
        resultados["pastagem"] = {
            "area": area_pastagem,
            "fator": 0.5,
            "creditos": credito_pastagem,
            "metodologia": "VCS VM0032 - Recuperação de pastagens degradadas"
        }
        
    if area_florestal > 0:
        resultados["florestal"] = {
            "area": area_florestal,
            "fator": 8.0,
            "creditos": credito_florestal,
            "metodologia": "AR-ACM0003 - Florestamento e reflorestamento"
        }
        
    if area_renovacao_cultura > 0:
        resultados["renovacao"] = {
            "area": area_renovacao_cultura,
            "fator": 1.2,
            "creditos": credito_renovacao,
            "metodologia": "CDM AMS-III.AU - Práticas agrícolas de baixo carbono"
        }
        
    if area_integracao_lavoura > 0:
        resultados["integracao"] = {
            "area": area_integracao_lavoura,
            "fator": 3.0,
            "creditos": credito_integracao,
            "metodologia": "VCS VM0017 - Sistemas de integração lavoura-pecuária"
        }
    
    return total_creditos, resultados

# Rotas
@app.route('/')
def index():
    app.logger.debug("Renderizando página inicial da calculadora de créditos")
    return render_template('creditos_inicio.html')

@app.route('/creditos', methods=['GET', 'POST'])
def creditos():
    if request.method == 'GET':
        app.logger.debug("Acessando página de calculadora de créditos (GET)")
        return render_template('calculadora_creditos.html')
        
    try:
        app.logger.debug("Processando cálculo de créditos (POST)")
        # Processar formulário
        try:
            area_pastagem = float(request.form.get('area_pastagem', 0) or 0)
        except:
            area_pastagem = 0
            
        try:
            area_florestal = float(request.form.get('area_florestal', 0) or 0)
        except:
            area_florestal = 0
            
        try:
            area_renovacao_cultura = float(request.form.get('area_renovacao_cultura', 0) or 0)
        except:
            area_renovacao_cultura = 0
            
        try:
            area_integracao_lavoura = float(request.form.get('area_integracao_lavoura', 0) or 0)
        except:
            area_integracao_lavoura = 0
        
        # Verificar se pelo menos uma área foi fornecida
        if area_pastagem <= 0 and area_florestal <= 0 and area_renovacao_cultura <= 0 and area_integracao_lavoura <= 0:
            raise ValueError("Pelo menos uma área deve ser maior que zero")
            
        # Calcular créditos
        total_creditos, resultados = calcular_creditos(
            area_pastagem=area_pastagem,
            area_florestal=area_florestal,
            area_renovacao_cultura=area_renovacao_cultura,
            area_integracao_lavoura=area_integracao_lavoura
        )
        
        valor_estimado = total_creditos * 50  # R$50 por tCO2e
            
        # Renderizar template
        return render_template(
            'creditos.html',
            area_pastagem=area_pastagem,
            area_florestal=area_florestal,
            area_renovacao_cultura=area_renovacao_cultura,
            area_integracao_lavoura=area_integracao_lavoura,
            resultados=resultados,
            potencial_credito=total_creditos,
            valor_estimado=valor_estimado
        )
        
    except Exception as e:
        app.logger.error(f"Erro em /creditos: {str(e)}")
        flash(f"Erro ao calcular créditos: {str(e)}", 'error')
        return redirect(url_for('creditos'))

# Servir arquivos estáticos
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)