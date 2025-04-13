from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
import os
import logging
from datetime import datetime
from utils.pdf_generator import gerar_pdf_relatorio_creditos, gerar_pdf_relatorio_emissoes

# Auxiliar para templates
def now():
    """Retorna a data/hora atual para uso nos templates"""
    return datetime.now()

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Configurar banco de dados
class Base(DeclarativeBase):
    pass

# Inicializar app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "chave_secreta_temporaria")

# Adicionar função auxiliar aos templates
app.jinja_env.globals['now'] = now

# Configurar a conexão com o banco de dados
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Inicializar o banco de dados
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Calculadora de créditos simplificada
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

def calcular_creditos(area_pastagem=0.0, area_florestal=0.0, area_renovacao_cultura=0.0, area_integracao_lavoura=0.0):
    """
    Calcula o potencial de créditos de carbono com base em diferentes metodologias
    
    Referências científicas:
    - Recuperação de pastagens: Método VCS VM0032 (Verified Carbon Standard)
    - Florestamento: AR-ACM0003 (CDM - Clean Development Mechanism)
    - Práticas agrícolas: CDM AMS-III.AU (Small-scale Methodology)
    - Integração lavoura-pecuária: VCS VM0017
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
    app.logger.debug("Renderizando o template da página inicial")
    return render_template('index.html')

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

@app.route('/dashboard')
def dashboard():
    try:
        app.logger.debug("Acessando dashboard de análise")
        
        # Buscar todos os cenários do banco de dados
        cenarios = CalculoCarbono.query.order_by(CalculoCarbono.data_calculo.desc()).all()
        
        # Cálculos para estatísticas
        total_cenarios = len(cenarios)
        total_creditos = sum(c.total_creditos for c in cenarios) if cenarios else 0
        valor_estimado = sum(c.valor_estimado for c in cenarios) if cenarios else 0
        area_total = sum((c.area_pastagem + c.area_florestal + c.area_renovacao_cultura + c.area_integracao_lavoura) for c in cenarios) if cenarios else 0
        
        # Calcular totais por metodologia
        totais = {
            'credito_pastagem': sum(c.credito_pastagem for c in cenarios) if cenarios else 0,
            'credito_florestal': sum(c.credito_florestal for c in cenarios) if cenarios else 0,
            'credito_renovacao': sum(c.credito_renovacao for c in cenarios) if cenarios else 0,
            'credito_integracao': sum(c.credito_integracao for c in cenarios) if cenarios else 0
        }
        
        # Dados para o gráfico de séries temporais
        datas = []
        creditos_acumulados = []
        acumulado = 0
        
        # Ordenar cenários por data para o gráfico de séries temporais
        cenarios_ordenados = sorted(cenarios, key=lambda x: x.data_calculo)
        for c in cenarios_ordenados:
            acumulado += c.total_creditos
            datas.append(f"'{c.data_calculo.strftime('%d/%m/%Y')}'" if c.data_calculo else "'Data desconhecida'")
            creditos_acumulados.append(acumulado)
        
        return render_template(
            'dashboard.html',
            cenarios=cenarios,
            total_cenarios=total_cenarios,
            total_creditos=total_creditos,
            valor_estimado=valor_estimado,
            area_total=area_total,
            totais=totais,
            datas=datas,
            creditos_acumulados=creditos_acumulados
        )
    except Exception as e:
        app.logger.error(f"Erro ao renderizar dashboard: {str(e)}")
        flash(f"Erro ao carregar dashboard: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/detalhes/<int:id>')
def detalhes_cenario(id):
    try:
        app.logger.debug(f"Acessando detalhes do cenário {id}")
        
        # Buscar cenário do banco de dados
        cenario = CalculoCarbono.query.get_or_404(id)
        
        return render_template(
            'detalhes.html',
            cenario=cenario
        )
    except Exception as e:
        app.logger.error(f"Erro ao acessar detalhes do cenário {id}: {str(e)}")
        flash(f"Erro ao carregar detalhes: {str(e)}", 'error')
        return redirect(url_for('dashboard'))

# Funcionalidade de comparação de cenários removida conforme solicitado pelo usuário

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
        
        # Nome do cenário (opcional)
        nome_cenario = request.form.get('nome_cenario', 'Cenário sem nome')
        
        # Salvar no banco de dados
        try:
            novo_calculo = CalculoCarbono(
                nome_cenario=nome_cenario,
                area_pastagem=area_pastagem,
                area_florestal=area_florestal,
                area_renovacao_cultura=area_renovacao_cultura,
                area_integracao_lavoura=area_integracao_lavoura,
                credito_pastagem=resultados.get("pastagem", {}).get("creditos", 0),
                credito_florestal=resultados.get("florestal", {}).get("creditos", 0),
                credito_renovacao=resultados.get("renovacao", {}).get("creditos", 0),
                credito_integracao=resultados.get("integracao", {}).get("creditos", 0),
                total_creditos=total_creditos,
                valor_estimado=valor_estimado
            )
            db.session.add(novo_calculo)
            db.session.commit()
            app.logger.debug(f"Cálculo salvo no banco de dados com ID: {novo_calculo.id}")
        except Exception as e:
            app.logger.error(f"Erro ao salvar cálculo no banco de dados: {str(e)}")
            db.session.rollback()
            
        # Renderizar template
        return render_template(
            'creditos.html',
            area_pastagem=area_pastagem,
            area_florestal=area_florestal,
            area_renovacao_cultura=area_renovacao_cultura,
            area_integracao_lavoura=area_integracao_lavoura,
            resultados=resultados,
            potencial_credito=total_creditos,
            valor_estimado=valor_estimado,
            nome_cenario=nome_cenario
        )
        
    except Exception as e:
        app.logger.error(f"Erro em /creditos: {str(e)}")
        flash(f"Erro ao calcular créditos: {str(e)}", 'error')
        return redirect(url_for('creditos'))

# Servir arquivos estáticos
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Exclusão de cenário
@app.route('/apagar-cenario/<int:id>', methods=['POST'])
def apagar_cenario(id):
    """Apaga um cenário específico do banco de dados"""
    try:
        app.logger.debug(f"Apagando cenário {id}")
        
        # Buscar cenário
        cenario = CalculoCarbono.query.get_or_404(id)
        
        # Apagar do banco de dados
        db.session.delete(cenario)
        db.session.commit()
        
        flash(f"Cenário '{cenario.nome_cenario}' apagado com sucesso!", 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        app.logger.error(f"Erro ao apagar cenário {id}: {str(e)}")
        flash(f"Erro ao apagar cenário: {str(e)}", 'error')
        return redirect(url_for('dashboard'))

# Exclusão de todos os cenários
@app.route('/apagar-todos-cenarios', methods=['POST'])
def apagar_todos_cenarios():
    """Apaga todos os cenários do banco de dados"""
    try:
        app.logger.debug("Apagando todos os cenários")
        
        # Contar cenários antes de apagar
        total = CalculoCarbono.query.count()
        
        # Apagar todos os registros da tabela
        CalculoCarbono.query.delete()
        db.session.commit()
        
        flash(f"{total} cenários foram apagados com sucesso!", 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        app.logger.error(f"Erro ao apagar todos os cenários: {str(e)}")
        flash(f"Erro ao apagar cenários: {str(e)}", 'error')
        return redirect(url_for('dashboard'))

# Visualização de Impacto Real
@app.route('/impacto-real/<int:id>')
def visualizar_impacto_real(id):
    """Exibe visualização do impacto real dos créditos de carbono"""
    try:
        app.logger.debug(f"Acessando visualização de impacto real para cenário {id}")
        
        # Importar calculadora de impacto
        from utils.impact_calculator import calcular_impacto_real
        
        # Buscar cenário
        cenario = CalculoCarbono.query.get_or_404(id)
        
        # Calcular impacto real
        impacto_real = calcular_impacto_real(cenario.total_creditos)
        
        # Renderizar template
        return render_template(
            'impacto_real.html',
            cenario=cenario,
            impacto_real=impacto_real
        )
    except Exception as e:
        app.logger.error(f"Erro ao visualizar impacto real: {str(e)}")
        flash(f"Erro ao visualizar impacto real: {str(e)}", 'error')
        return redirect(url_for('detalhes_cenario', id=id))

# Exportação de PDF
@app.route('/exportar-pdf/creditos/<int:id>')
def exportar_pdf_creditos(id):
    """Exporta relatório de créditos de carbono em PDF"""
    try:
        app.logger.debug(f"Exportando relatório PDF de créditos para cenário {id}")
        
        # Buscar cenário
        cenario = CalculoCarbono.query.get_or_404(id)
        
        # Gerar PDF
        pdf_path = gerar_pdf_relatorio_creditos(cenario)
        
        # Enviar arquivo
        return send_file(pdf_path, download_name=f"relatorio_creditos_{id}.pdf", as_attachment=True)
    except Exception as e:
        app.logger.error(f"Erro ao gerar PDF de créditos: {str(e)}")
        flash(f"Erro ao gerar relatório PDF: {str(e)}", 'error')
        return redirect(url_for('detalhes_cenario', id=id))

# Configuração da API RESTful
api = Api(app, prefix='/api')

# Endpoints da API
class CalcularCreditosResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            
            nome_cenario = data.get('nome_cenario', 'Cenário sem nome')
            area_pastagem = float(data.get('area_pastagem', 0) or 0)
            area_florestal = float(data.get('area_florestal', 0) or 0)
            area_renovacao_cultura = float(data.get('area_renovacao_cultura', 0) or 0)
            area_integracao_lavoura = float(data.get('area_integracao_lavoura', 0) or 0)
            
            # Calcular créditos de carbono
            total_creditos, resultados = calcular_creditos(
                area_pastagem=area_pastagem,
                area_florestal=area_florestal,
                area_renovacao_cultura=area_renovacao_cultura,
                area_integracao_lavoura=area_integracao_lavoura
            )
            
            # Valor estimado em reais (R$ 50/tCO2e)
            valor_estimado = total_creditos * 50
            
            # Salvar no banco de dados
            novo_calculo = CalculoCarbono(
                nome_cenario=nome_cenario,
                area_pastagem=area_pastagem,
                area_florestal=area_florestal,
                area_renovacao_cultura=area_renovacao_cultura,
                area_integracao_lavoura=area_integracao_lavoura,
                credito_pastagem=resultados.get("pastagem", {}).get("creditos", 0),
                credito_florestal=resultados.get("florestal", {}).get("creditos", 0),
                credito_renovacao=resultados.get("renovacao", {}).get("creditos", 0),
                credito_integracao=resultados.get("integracao", {}).get("creditos", 0),
                total_creditos=total_creditos,
                valor_estimado=valor_estimado
            )
            db.session.add(novo_calculo)
            db.session.commit()
            
            # Retornar resultado
            return {
                'id': novo_calculo.id,
                'total_creditos': total_creditos,
                'resultados': resultados,
                'valor_estimado': valor_estimado
            }, 200
            
        except Exception as e:
            app.logger.error(f"Erro na API /calcular-creditos: {str(e)}")
            return {'error': str(e)}, 400

class CenariosListResource(Resource):
    def get(self):
        try:
            calculos = CalculoCarbono.query.order_by(CalculoCarbono.data_calculo.desc()).all()
            return [
                {
                    'id': calculo.id,
                    'nome_cenario': calculo.nome_cenario,
                    'total_creditos': calculo.total_creditos,
                    'valor_estimado': calculo.valor_estimado,
                    'data_calculo': calculo.data_calculo.strftime('%Y-%m-%d %H:%M') if calculo.data_calculo else None
                } for calculo in calculos
            ], 200
        except Exception as e:
            app.logger.error(f"Erro na API /cenarios: {str(e)}")
            return {'error': str(e)}, 500

class CenarioDetailResource(Resource):
    def get(self, id):
        try:
            calculo = CalculoCarbono.query.get(id)
            if not calculo:
                return {'error': 'Cenário não encontrado'}, 404
            
            return calculo.to_dict(), 200
        except Exception as e:
            app.logger.error(f"Erro na API /cenarios/{id}: {str(e)}")
            return {'error': str(e)}, 500

class ReferenciasResource(Resource):
    def get(self):
        return {
            'metodologias': [
                {
                    'codigo': 'VCS-VM0032',
                    'nome': 'Recuperação de pastagens degradadas',
                    'descricao': 'Metodologia para quantificação de emissões reduzidas por recuperação de pastagens degradadas',
                    'fator': 0.5,
                    'referencia': 'Verified Carbon Standard (VCS) VM0032',
                    'url': 'https://verra.org/methodology/vm0032-methodology-for-the-adoption-of-sustainable-grasslands-through-adjustment-of-fire-and-grazing-v1-0/'
                },
                {
                    'codigo': 'AR-ACM0003',
                    'nome': 'Florestamento e reflorestamento',
                    'descricao': 'Metodologia para quantificação de remoções de carbono por atividades de florestamento e reflorestamento',
                    'fator': 8.0,
                    'referencia': 'Clean Development Mechanism (CDM) AR-ACM0003',
                    'url': 'https://cdm.unfccc.int/methodologies/DB/C7TYXBQJ7JJXON44AV71HBQXVSJ46V'
                },
                {
                    'codigo': 'CDM-AMS-III.AU',
                    'nome': 'Práticas agrícolas de baixo carbono',
                    'descricao': 'Metodologia para redução de emissões de práticas agrícolas sustentáveis',
                    'fator': 1.2,
                    'referencia': 'Clean Development Mechanism (CDM) AMS-III.AU',
                    'url': 'https://cdm.unfccc.int/methodologies/DB/13LQNV5A5EKORXUG3607N7ROBX6J6K'
                },
                {
                    'codigo': 'VCS-VM0017',
                    'nome': 'Sistemas de integração lavoura-pecuária',
                    'descricao': 'Metodologia para adoção de agricultura sustentável com sistemas de manejo de terras e pastagens',
                    'fator': 3.0,
                    'referencia': 'Verified Carbon Standard (VCS) VM0017',
                    'url': 'https://verra.org/methodology/vm0017-adoption-of-sustainable-agricultural-land-management-v1-0/'
                }
            ]
        }

class EstudosCasoResource(Resource):
    def get(self):
        return [
            {
                'id': 1,
                'titulo': 'Recuperação de Pastagens na Fazenda Modelo, MG',
                'localizacao': 'Minas Gerais, Brasil',
                'metodologias': ['VCS-VM0032'],
                'resultados': 'Recuperação de 500 hectares de pastagens degradadas, com sequestro médio de 0,7 tCO2e/ha/ano',
                'ano': 2022
            },
            {
                'id': 2,
                'titulo': 'Projeto de Reflorestamento em Áreas Degradadas',
                'localizacao': 'Paraná, Brasil',
                'metodologias': ['AR-ACM0003'],
                'resultados': 'Reflorestamento de 200 hectares com espécies nativas, sequestro médio de 10 tCO2e/ha/ano nos primeiros 5 anos',
                'ano': 2021
            },
            {
                'id': 3,
                'titulo': 'Integração Lavoura-Pecuária em Larga Escala',
                'localizacao': 'Mato Grosso, Brasil',
                'metodologias': ['VCS-VM0017', 'CDM-AMS-III.AU'],
                'resultados': 'Implementação em 1.200 hectares, redução de uso de fertilizantes e aumento da produtividade em 25%',
                'ano': 2023
            }
        ]

# Registrar endpoints na API
api.add_resource(CalcularCreditosResource, '/calcular-creditos')
api.add_resource(CenariosListResource, '/cenarios')
api.add_resource(CenarioDetailResource, '/cenarios/<int:id>')
api.add_resource(ReferenciasResource, '/referencias')
api.add_resource(EstudosCasoResource, '/estudos-caso')

# Configuração do Swagger UI
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.yml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "API de Calculadora de Créditos de Carbono Agrícola"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Endpoint para servir a especificação Swagger
@app.route('/static/swagger.yml')
def serve_swagger_spec():
    return send_from_directory('.', 'swagger.yml')

# Criar tabelas quando o app iniciar
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)