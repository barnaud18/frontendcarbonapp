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
    app.logger.debug("Renderizando página inicial")
    return render_template('creditos_inicio.html')

@app.route('/somente-creditos')
def novo_index():
    app.logger.debug("Renderizando página inicial apenas de créditos")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Calculadora de Créditos de Carbono Agrícola</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #1e1e1e;
                color: #f8f9fa;
            }
            
            .container {
                max-width: 1000px;
                margin: 0 auto;
            }
            
            h1 {
                color: #0d6efd;
                margin-bottom: 20px;
            }
            
            h2 {
                color: #0dcaf0;
            }
            
            .card {
                background-color: #2c2c2c;
                border-radius: 5px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            
            form {
                margin-bottom: 0;
            }
            
            .form-group {
                margin-bottom: 15px;
            }
            
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            
            input[type="text"],
            input[type="number"] {
                width: 100%;
                padding: 10px;
                border: 1px solid #444;
                border-radius: 4px;
                background-color: #333;
                color: #fff;
                box-sizing: border-box;
            }
            
            button {
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                margin-right: 10px;
                font-weight: bold;
            }
            
            .btn-primary {
                background-color: #0d6efd;
                color: white;
            }
            
            .btn-success {
                background-color: #198754;
                color: white;
            }
            
            .btn-info {
                background-color: #0dcaf0;
                color: white;
                text-decoration: none;
                display: inline-block;
            }
            
            .row {
                display: flex;
                flex-wrap: wrap;
                margin: 0 -10px;
            }
            
            .col-md-6 {
                flex: 0 0 100%;
                padding: 0 10px;
                box-sizing: border-box;
            }
            
            @media (min-width: 768px) {
                .col-md-6 {
                    flex: 0 0 50%;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Calculadora de Créditos de Carbono Agrícola</h1>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <h2>Calculadora de Créditos de Carbono</h2>
                        <p>Calcule os potenciais créditos de carbono baseados em diferentes metodologias:</p>
                        
                        <a href="/creditos" class="btn-success" style="text-align: center; text-decoration: none; display: block; padding: 10px; margin-bottom: 15px;">
                            Calculadora Multi-Metodologias
                        </a>
                        
                        <form action="/creditos" method="post">
                            <div class="form-group">
                                <label for="area_pastagem">Cálculo Rápido - Área de Pastagem (ha):</label>
                                <input type="number" id="area_pastagem" name="area_pastagem" min="0.1" step="0.1" required>
                            </div>
                            <button type="submit" class="btn-success">Calcular Créditos de Carbono</button>
                        </form>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card">
                        <h2>Metodologia</h2>
                        <p>Os cálculos de créditos de carbono são baseados nas seguintes metodologias reconhecidas:</p>
                        <ul>
                            <li><strong>VCS VM0032:</strong> Recuperação de pastagens degradadas (0,5 tCO2e/ha/ano)</li>
                            <li><strong>AR-ACM0003:</strong> Florestamento e reflorestamento (8,0 tCO2e/ha/ano)</li>
                            <li><strong>CDM AMS-III.AU:</strong> Práticas agrícolas de baixo carbono (1,2 tCO2e/ha/ano)</li>
                            <li><strong>VCS VM0017:</strong> Sistemas de integração lavoura-pecuária (3,0 tCO2e/ha/ano)</li>
                        </ul>
                        <p>Estes valores representam estimativas conservadoras do potencial de sequestro de carbono para cada atividade.</p>
                    </div>
                    
                    <div class="card">
                        <h2>Instruções</h2>
                        <p>Para utilizar a calculadora:</p>
                        <ol>
                            <li>Acesse a <strong>Calculadora Multi-Metodologias</strong> para inserir dados de diferentes práticas sustentáveis.</li>
                            <li>Ou utilize o <strong>Cálculo Rápido</strong> para estimar créditos baseados apenas na área de pastagem.</li>
                            <li>Informe as áreas em hectares para cada tipo de atividade que implementa em sua propriedade.</li>
                            <li>Obtenha estimativas do potencial de créditos de carbono e valor financeiro aproximado.</li>
                        </ol>
                        <p>Lembre-se que para monetizar créditos de carbono, é necessário seguir protocolos específicos e obter certificação por entidades credenciadas.</p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/propriedades')
def listar_propriedades():
    propriedades = [
        {
            'id': 1,
            'nome': 'Fazenda Exemplo',
            'tamanho_total': 100.0,
            'data_registro': '2025-04-10'
        }
    ]
    return render_template('propriedades.html', propriedades=propriedades)

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