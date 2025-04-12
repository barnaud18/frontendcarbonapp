import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure PostgreSQL database using environment variables
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Define models
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
            'data_registro': self.data_registro.isoformat(),
            'agricultura': self.agricultura.to_dict() if self.agricultura else {},
            'pecuaria': self.pecuaria.to_dict() if self.pecuaria else {},
            'emissao': self.emissao.to_dict() if self.emissao else {},
            'recomendacoes': [r.to_dict() for r in self.recomendacoes] if self.recomendacoes else []
        }

class Agricultura(db.Model):
    """Model for agricultural data"""
    id = db.Column(db.Integer, primary_key=True)
    propriedade_id = db.Column(db.Integer, db.ForeignKey('propriedade.id'), nullable=False)
    area_agricola = db.Column(db.Float, nullable=False)  # Agricultural area in hectares
    uso_fertilizante = db.Column(db.Float, nullable=False)  # Fertilizer use in kg/ha/year
    consumo_combustivel = db.Column(db.Float, nullable=False)  # Fuel consumption in liters/year
    area_pastagem = db.Column(db.Float, nullable=True)  # Pasture area in hectares
    area_florestal = db.Column(db.Float, nullable=True, default=0)  # Forest area in hectares
    area_renovacao_cultura = db.Column(db.Float, nullable=True, default=0)  # Crop rotation area in hectares
    area_integracao_lavoura = db.Column(db.Float, nullable=True, default=0)  # Integrated crop-livestock area in hectares
    
    def to_dict(self):
        return {
            'id': self.id,
            'propriedade_id': self.propriedade_id,
            'area_agricola': self.area_agricola,
            'uso_fertilizante': self.uso_fertilizante,
            'consumo_combustivel': self.consumo_combustivel,
            'area_pastagem': self.area_pastagem,
            'area_florestal': self.area_florestal,
            'area_renovacao_cultura': self.area_renovacao_cultura,
            'area_integracao_lavoura': self.area_integracao_lavoura
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
            'data_calculo': self.data_calculo.isoformat()
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

# Utility functions 
def calcular_emissoes(area_agricola, uso_fertilizante, num_bovinos, consumo_combustivel):
    """
    Calculate carbon emissions using IPCC Tier 1 methodology
    
    Parameters:
    - area_agricola: Agricultural area in hectares
    - uso_fertilizante: Fertilizer use in kg/ha/year
    - num_bovinos: Number of cattle
    - consumo_combustivel: Fuel consumption in liters/year
    
    Returns:
    - Dictionary with emission details
    """
    # Constants from IPCC methodology
    # N2O from fertilizer (kg CO2e per kg N)
    fator_n2o = 44/28 * 0.01 * 298  # N to N2O conversion * emission factor * GWP
    
    # CH4 from cattle (kg CO2e per head per year)
    fator_ch4_bovino = 56 * 25  # kg CH4 per head per year * GWP
    
    # CO2 from diesel (kg CO2e per liter)
    fator_diesel = 2.68  # kg CO2e per liter
    
    # Calculate emissions
    # Agricultural emissions - N2O from fertilizer application
    emissao_agricultura = area_agricola * uso_fertilizante * fator_n2o
    
    # Livestock emissions - CH4 from enteric fermentation
    emissao_pecuaria = num_bovinos * fator_ch4_bovino
    
    # Fuel emissions - CO2 from diesel consumption
    emissao_combustivel = consumo_combustivel * fator_diesel
    
    # Total emissions
    total = emissao_agricultura + emissao_pecuaria + emissao_combustivel
    
    return {
        'total': total,
        'agricultura': emissao_agricultura,
        'pecuaria': emissao_pecuaria,
        'combustivel': emissao_combustivel
    }

def calcular_creditos_carbono(area_pastagem=0.0, area_florestal=0.0, area_renovacao_cultura=0.0, area_integracao_lavoura=0.0, metodologia=None):
    """
    Calculate carbon credit potential for multiple methodologies
    
    Parameters:
    - area_pastagem: Pasture area in hectares
    - area_florestal: Forest area in hectares
    - area_renovacao_cultura: Crop rotation area in hectares
    - area_integracao_lavoura: Integrated crop-livestock area in hectares
    - metodologia: Specific methodology to use (if None, calculates all)
    
    Returns:
    - Carbon credit potential in tCO2e/year or dictionary with details by methodology
    """
    resultados = {}
    
    # Conservative carbon sequestration factors (tCO2e/ha/year) for each methodology
    # 1. Pasture recovery (VCS VM0032)
    fator_pastagem = 0.5  # tCO2e/ha/year
    
    # 2. Forestry (AR-ACM0003 - Afforestation and Reforestation of Lands)
    fator_florestal = 8.0  # tCO2e/ha/year
    
    # 3. Crop rotation (CDM AMS-III.AU - Small-scale methodology for low carbon farming practices)
    fator_renovacao = 1.2  # tCO2e/ha/year
    
    # 4. Integrated crop-livestock-forest systems (VCS VM0017)
    fator_integracao = 3.0  # tCO2e/ha/year
    
    # Calculate credits for each methodology
    if metodologia == "pastagem" or metodologia is None:
        resultados["pastagem"] = {
            "area": area_pastagem,
            "fator": fator_pastagem,
            "creditos": area_pastagem * fator_pastagem,
            "metodologia": "VCS VM0032 - Recuperação de pastagens degradadas"
        }
        
    if metodologia == "florestal" or metodologia is None:
        resultados["florestal"] = {
            "area": area_florestal,
            "fator": fator_florestal,
            "creditos": area_florestal * fator_florestal,
            "metodologia": "AR-ACM0003 - Florestamento e reflorestamento"
        }
        
    if metodologia == "renovacao" or metodologia is None:
        resultados["renovacao"] = {
            "area": area_renovacao_cultura,
            "fator": fator_renovacao,
            "creditos": area_renovacao_cultura * fator_renovacao,
            "metodologia": "CDM AMS-III.AU - Práticas agrícolas de baixo carbono"
        }
        
    if metodologia == "integracao" or metodologia is None:
        resultados["integracao"] = {
            "area": area_integracao_lavoura,
            "fator": fator_integracao,
            "creditos": area_integracao_lavoura * fator_integracao,
            "metodologia": "VCS VM0017 - Sistemas de integração lavoura-pecuária"
        }
    
    # If only one methodology requested, return a dictionary with the credit value
    if metodologia is not None:
        credit_value = resultados.get(metodologia, {}).get("creditos", 0)
        return {"total": credit_value}
    
    # Calculate total credits (sum from all methodologies)
    total_creditos = sum(metodo["creditos"] for metodo in resultados.values())
    
    # Add total to results
    resultados["total"] = total_creditos
    
    return resultados

def gerar_recomendacoes(emissao_agricultura, emissao_pecuaria, emissao_combustivel, num_bovinos, uso_fertilizante):
    """
    Generate mitigation recommendations based on emission sources
    
    Parameters:
    - emissao_agricultura: Agricultural emissions in kg CO2e
    - emissao_pecuaria: Livestock emissions in kg CO2e
    - emissao_combustivel: Fuel emissions in kg CO2e
    - num_bovinos: Number of cattle
    - uso_fertilizante: Fertilizer use in kg/ha/year
    
    Returns:
    - List of recommendation dictionaries
    """
    recomendacoes = []
    
    # Agricultural recommendations
    if emissao_agricultura > 0 and uso_fertilizante > 0:
        reducao_potencial = emissao_agricultura * 0.2  # 20% reduction potential
        recomendacoes.append({
            'acao': 'Manejo eficiente de fertilizantes',
            'descricao': 'Implementar técnicas de aplicação fracionada de fertilizantes e utilizar inibidores de nitrificação.',
            'potencial_reducao': reducao_potencial
        })
        
    # Livestock recommendations
    if emissao_pecuaria > 0 and num_bovinos > 0:
        reducao_potencial = emissao_pecuaria * 0.15  # 15% reduction potential
        recomendacoes.append({
            'acao': 'Suplementação alimentar para bovinos',
            'descricao': 'Adicionar aditivos na dieta animal para reduzir a emissão de metano entérico.',
            'potencial_reducao': reducao_potencial
        })
        
    # Fuel recommendations
    if emissao_combustivel > 0:
        reducao_potencial = emissao_combustivel * 0.3  # 30% reduction potential
        recomendacoes.append({
            'acao': 'Eficiência no uso de combustível',
            'descricao': 'Otimizar o uso de maquinário agrícola e implementar técnicas de plantio direto.',
            'potencial_reducao': reducao_potencial
        })
    
    # General recommendations
    recomendacoes.append({
        'acao': 'Recuperação de pastagens degradadas',
        'descricao': 'Recuperar pastagens degradadas para aumentar o sequestro de carbono no solo.',
        'potencial_reducao': 500  # Fixed value in kg CO2e
    })
    
    recomendacoes.append({
        'acao': 'Implementação de sistemas agroflorestais',
        'descricao': 'Combinar a produção agrícola com espécies florestais para aumentar o sequestro de carbono.',
        'potencial_reducao': 1000  # Fixed value in kg CO2e
    })
    
    return recomendacoes

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    try:
        # Get form data
        nome = request.form.get('nome', 'Propriedade Teste')
        tamanho_total = float(request.form.get('tamanho_total', 0))
        area_agricola = float(request.form.get('area_agricola', 0))
        uso_fertilizante = float(request.form.get('uso_fertilizante', 0))
        area_pastagem = float(request.form.get('area_pastagem', 0))
        num_bovinos = int(request.form.get('num_bovinos', 0))
        consumo_combustivel = float(request.form.get('consumo_combustivel', 0))
        
        # Debug logging
        app.logger.debug(f"Form data: nome={nome}, tamanho_total={tamanho_total}, area_agricola={area_agricola}, " +
                        f"uso_fertilizante={uso_fertilizante}, area_pastagem={area_pastagem}, " +
                        f"num_bovinos={num_bovinos}, consumo_combustivel={consumo_combustivel}")
        
        # Calculate emissions
        resultado_emissoes = calcular_emissoes(
            area_agricola=area_agricola,
            uso_fertilizante=uso_fertilizante,
            num_bovinos=num_bovinos,
            consumo_combustivel=consumo_combustivel
        )
        
        # Debug logging
        app.logger.debug(f"Resultado emissões: {resultado_emissoes}")
        app.logger.debug(f"Calculando potencial de crédito. area_pastagem={area_pastagem}, tipo={type(area_pastagem)}")
        
        # Calculate carbon credits if pasture area is provided
        # Garantindo que area_pastagem é um float
        area_pastagem_float = float(area_pastagem)
        potencial_credito = 0
        
        try:
            if area_pastagem_float > 0:
                app.logger.debug(f"Área de pastagem > 0, chamando calcular_creditos_carbono com area_pastagem={area_pastagem_float}")
                potencial_credito_resultado = calcular_creditos_carbono(area_pastagem=area_pastagem_float)
                app.logger.debug(f"Resultado do cálculo de créditos: {potencial_credito_resultado}")
                
                if isinstance(potencial_credito_resultado, dict) and "total" in potencial_credito_resultado:
                    potencial_credito = potencial_credito_resultado["total"]
                    app.logger.debug(f"Potencial de crédito extraído: {potencial_credito}")
                else:
                    app.logger.error(f"Resultado inesperado do cálculo de créditos: {potencial_credito_resultado}")
                    potencial_credito = 0
            else:
                app.logger.debug("Área de pastagem <= 0, crédito=0")
        except Exception as erro_credito:
            app.logger.error(f"Erro ao calcular créditos de carbono: {str(erro_credito)}")
            potencial_credito = 0
        
        # Generate recommendations
        recomendacoes = gerar_recomendacoes(
            emissao_agricultura=resultado_emissoes['agricultura'],
            emissao_pecuaria=resultado_emissoes['pecuaria'],
            emissao_combustivel=resultado_emissoes['combustivel'],
            num_bovinos=num_bovinos,
            uso_fertilizante=uso_fertilizante
        )
        
        # Render template with results
        return render_template(
            'resultado.html',
            nome=nome,
            tamanho_total=tamanho_total,
            area_agricola=area_agricola,
            uso_fertilizante=uso_fertilizante,
            area_pastagem=area_pastagem,
            num_bovinos=num_bovinos,
            consumo_combustivel=consumo_combustivel,
            total_emissao=resultado_emissoes['total'],
            emissao_agricultura=resultado_emissoes['agricultura'],
            emissao_pecuaria=resultado_emissoes['pecuaria'],
            emissao_combustivel=resultado_emissoes['combustivel'],
            potencial_credito=potencial_credito,
            recomendacoes=recomendacoes
        )
    except Exception as e:
        # Log the error
        app.logger.error(f"Error in calculation: {str(e)}")
        
        # Redirect back with error message
        flash(f"Erro ao calcular: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    try:
        # Get form data
        nome = request.form.get('nome')
        tamanho_total = float(request.form.get('tamanho_total'))
        area_agricola = float(request.form.get('area_agricola'))
        uso_fertilizante = float(request.form.get('uso_fertilizante'))
        area_pastagem = float(request.form.get('area_pastagem', 0))
        num_bovinos = int(request.form.get('num_bovinos'))
        consumo_combustivel = float(request.form.get('consumo_combustivel'))
        
        # Get optional form data for new carbon credit methodologies
        area_florestal = float(request.form.get('area_florestal', 0))
        area_renovacao_cultura = float(request.form.get('area_renovacao_cultura', 0))
        area_integracao_lavoura = float(request.form.get('area_integracao_lavoura', 0))
        
        # Create property
        nova_propriedade = Propriedade(
            nome=nome,
            tamanho_total=tamanho_total
        )
        db.session.add(nova_propriedade)
        db.session.flush()  # Get ID without committing
        
        # Create agriculture data
        agricultura = Agricultura(
            propriedade_id=nova_propriedade.id,
            area_agricola=area_agricola,
            uso_fertilizante=uso_fertilizante,
            consumo_combustivel=consumo_combustivel,
            area_pastagem=area_pastagem,
            area_florestal=area_florestal,
            area_renovacao_cultura=area_renovacao_cultura,
            area_integracao_lavoura=area_integracao_lavoura
        )
        db.session.add(agricultura)
        
        # Create livestock data
        pecuaria = Pecuaria(
            propriedade_id=nova_propriedade.id,
            num_bovinos=num_bovinos
        )
        db.session.add(pecuaria)
        
        # Calculate emissions
        resultado_emissoes = calcular_emissoes(
            area_agricola=area_agricola,
            uso_fertilizante=uso_fertilizante,
            num_bovinos=num_bovinos,
            consumo_combustivel=consumo_combustivel
        )
        
        # Calculate carbon credits if areas are provided
        resultados_creditos = calcular_creditos_carbono(
            area_pastagem=area_pastagem,
            area_florestal=area_florestal,
            area_renovacao_cultura=area_renovacao_cultura,
            area_integracao_lavoura=area_integracao_lavoura
        )
        
        # Create emission record
        emissao = Emissao(
            propriedade_id=nova_propriedade.id,
            total_emissao=resultado_emissoes['total'],
            emissao_agricultura=resultado_emissoes['agricultura'],
            emissao_pecuaria=resultado_emissoes['pecuaria'],
            emissao_combustivel=resultado_emissoes['combustivel'],
            potencial_credito=resultados_creditos['total']
        )
        db.session.add(emissao)
        
        # Create recommendations
        recomendacoes = gerar_recomendacoes(
            emissao_agricultura=resultado_emissoes['agricultura'],
            emissao_pecuaria=resultado_emissoes['pecuaria'],
            emissao_combustivel=resultado_emissoes['combustivel'],
            num_bovinos=num_bovinos,
            uso_fertilizante=uso_fertilizante
        )
        
        for recomendacao in recomendacoes:
            nova_recomendacao = Recomendacao(
                propriedade_id=nova_propriedade.id,
                acao=recomendacao['acao'],
                descricao=recomendacao['descricao'],
                potencial_reducao=recomendacao['potencial_reducao']
            )
            db.session.add(nova_recomendacao)
        
        # Commit all changes
        db.session.commit()
        
        # Redirect with success message
        flash("Propriedade cadastrada com sucesso!", 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        # Log the error
        app.logger.error(f"Error in registration: {str(e)}")
        
        # Rollback the transaction
        db.session.rollback()
        
        # Redirect back with error message
        flash(f"Erro ao cadastrar: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/creditos', methods=['GET', 'POST'])
def creditos():
    if request.method == 'GET':
        # Display the carbon credits calculator form
        app.logger.debug("GET request to /creditos - rendering calculadora_creditos.html")
        return render_template('calculadora_creditos.html')
        
    try:
        # For POST requests, process the form data
        app.logger.debug("POST request to /creditos - processing form data")
        
        # Get form data
        area_pastagem = float(request.form.get('area_pastagem', 0))
        area_florestal = float(request.form.get('area_florestal', 0))
        area_renovacao_cultura = float(request.form.get('area_renovacao_cultura', 0))
        area_integracao_lavoura = float(request.form.get('area_integracao_lavoura', 0))
        
        # Check if at least one area is provided
        if area_pastagem <= 0 and area_florestal <= 0 and area_renovacao_cultura <= 0 and area_integracao_lavoura <= 0:
            app.logger.error("Validation error: at least one area must be greater than zero")
            raise ValueError("Pelo menos uma área deve ser maior que zero")
        
        # Calculate credits for all methodologies
        resultados_creditos = calcular_creditos_carbono(
            area_pastagem=area_pastagem,
            area_florestal=area_florestal,
            area_renovacao_cultura=area_renovacao_cultura,
            area_integracao_lavoura=area_integracao_lavoura
        )
        
        # Total credits and estimated value
        total_creditos = resultados_creditos['total']
        valor_estimado = total_creditos * 50  # Assuming R$50 per tCO2e
        
        app.logger.debug(f"Credits calculation successful. Total credits: {total_creditos}")
        
        # Render template with results
        return render_template(
            'creditos.html',
            area_pastagem=area_pastagem,
            area_florestal=area_florestal,
            area_renovacao_cultura=area_renovacao_cultura,
            area_integracao_lavoura=area_integracao_lavoura,
            resultados=resultados_creditos,
            potencial_credito=total_creditos,
            valor_estimado=valor_estimado
        )
        
    except Exception as e:
        # Log the error
        app.logger.error(f"Error in credit calculation: {str(e)}")
        
        # Redirect back with error message
        flash(f"Erro ao calcular créditos: {str(e)}", 'error')
        return redirect(url_for('creditos'))

@app.route('/propriedades')
def listar_propriedades():
    # Get all properties
    propriedades = Propriedade.query.all()
    
    # Render template with properties
    return render_template('propriedades.html', propriedades=propriedades)

# API routes - keeping for compatibility
@app.route('/api/calcular', methods=['POST'])
def api_calcular():
    try:
        data = request.get_json()
        
        area_agricola = data.get('area_agricola', 0)
        uso_fertilizante = data.get('uso_fertilizante', 0)
        num_bovinos = data.get('num_bovinos', 0)
        consumo_combustivel = data.get('consumo_combustivel', 0)
        area_pastagem = data.get('area_pastagem', 0)
        
        # Calculate emissions
        resultado = calcular_emissoes(
            area_agricola=area_agricola,
            uso_fertilizante=uso_fertilizante,
            num_bovinos=num_bovinos,
            consumo_combustivel=consumo_combustivel
        )
        
        # Calculate carbon credits if pasture area is provided
        try:
            # Garantindo que area_pastagem é um float
            area_pastagem_float = float(area_pastagem)
            potencial_credito = 0
            
            if area_pastagem_float > 0:
                app.logger.debug(f"API: Área de pastagem > 0, chamando calcular_creditos_carbono com area_pastagem={area_pastagem_float}")
                potencial_credito_resultado = calcular_creditos_carbono(area_pastagem=area_pastagem_float)
                app.logger.debug(f"API: Resultado do cálculo de créditos: {potencial_credito_resultado}")
                
                if isinstance(potencial_credito_resultado, dict) and "total" in potencial_credito_resultado:
                    potencial_credito = potencial_credito_resultado["total"]
                    app.logger.debug(f"API: Potencial de crédito extraído: {potencial_credito}")
                else:
                    app.logger.error(f"API: Resultado inesperado do cálculo de créditos: {potencial_credito_resultado}")
                    potencial_credito = 0
            else:
                app.logger.debug("API: Área de pastagem <= 0, crédito=0")
        except Exception as erro_credito:
            app.logger.error(f"API: Erro ao calcular créditos de carbono: {str(erro_credito)}")
            potencial_credito = 0
        
        # Generate recommendations
        recomendacoes = gerar_recomendacoes(
            emissao_agricultura=resultado['agricultura'],
            emissao_pecuaria=resultado['pecuaria'],
            emissao_combustivel=resultado['combustivel'],
            num_bovinos=num_bovinos,
            uso_fertilizante=uso_fertilizante
        )
        
        return jsonify({
            "pegada_total_kg_co2e": resultado['total'],
            "detalhes": {
                "agricultura": resultado['agricultura'],
                "pecuaria": resultado['pecuaria'],
                "combustivel": resultado['combustivel']
            },
            "potencial_credito_tco2e": potencial_credito,
            "recomendacoes": recomendacoes
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/cadastrar_propriedade', methods=['POST'])
def api_cadastrar_propriedade():
    try:
        data = request.get_json()
        
        # Property data
        nome = data.get('nome')
        tamanho_total = data.get('tamanho_total')
        
        # Agricultural data
        area_agricola = data.get('area_agricola')
        uso_fertilizante = data.get('uso_fertilizante')
        consumo_combustivel = data.get('consumo_combustivel')
        area_pastagem = data.get('area_pastagem', 0)
        
        # New carbon credit methodology data
        area_florestal = data.get('area_florestal', 0)
        area_renovacao_cultura = data.get('area_renovacao_cultura', 0)
        area_integracao_lavoura = data.get('area_integracao_lavoura', 0)
        
        # Livestock data
        num_bovinos = data.get('num_bovinos', 0)
        
        # Create property
        nova_propriedade = Propriedade(
            nome=nome,
            tamanho_total=tamanho_total
        )
        db.session.add(nova_propriedade)
        db.session.flush()  # Get ID without committing
        
        # Create agriculture data
        agricultura = Agricultura(
            propriedade_id=nova_propriedade.id,
            area_agricola=area_agricola,
            uso_fertilizante=uso_fertilizante,
            consumo_combustivel=consumo_combustivel,
            area_pastagem=area_pastagem,
            area_florestal=area_florestal,
            area_renovacao_cultura=area_renovacao_cultura,
            area_integracao_lavoura=area_integracao_lavoura
        )
        db.session.add(agricultura)
        
        # Create livestock data
        pecuaria = Pecuaria(
            propriedade_id=nova_propriedade.id,
            num_bovinos=num_bovinos
        )
        db.session.add(pecuaria)
        
        # Calculate emissions
        resultado_emissoes = calcular_emissoes(
            area_agricola=area_agricola,
            uso_fertilizante=uso_fertilizante,
            num_bovinos=num_bovinos,
            consumo_combustivel=consumo_combustivel
        )
        
        # Calculate carbon credits
        resultados_creditos = calcular_creditos_carbono(
            area_pastagem=area_pastagem,
            area_florestal=area_florestal,
            area_renovacao_cultura=area_renovacao_cultura,
            area_integracao_lavoura=area_integracao_lavoura
        )
        
        # Create emission record
        emissao = Emissao(
            propriedade_id=nova_propriedade.id,
            total_emissao=resultado_emissoes['total'],
            emissao_agricultura=resultado_emissoes['agricultura'],
            emissao_pecuaria=resultado_emissoes['pecuaria'],
            emissao_combustivel=resultado_emissoes['combustivel'],
            potencial_credito=resultados_creditos['total']
        )
        db.session.add(emissao)
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            "message": "Propriedade cadastrada com sucesso",
            "propriedade_id": nova_propriedade.id,
            "pegada_carbono": {
                "total_emissao_kg_co2e": resultado_emissoes['total'],
                "detalhes_emissao": resultado_emissoes,
                "potencial_credito_tco2e": resultados_creditos['total'],
                "detalhes_creditos": {
                    k: v for k, v in resultados_creditos.items() if k != 'total'
                }
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/api/calcular-creditos', methods=['POST'])
def api_calcular_creditos():
    try:
        data = request.get_json()
        area_pastagem = data.get('area_pastagem', 0)
        area_florestal = data.get('area_florestal', 0)
        area_renovacao_cultura = data.get('area_renovacao_cultura', 0)
        area_integracao_lavoura = data.get('area_integracao_lavoura', 0)
        
        # Calculate credits for all methodologies
        resultados = calcular_creditos_carbono(
            area_pastagem=area_pastagem,
            area_florestal=area_florestal,
            area_renovacao_cultura=area_renovacao_cultura,
            area_integracao_lavoura=area_integracao_lavoura
        )
        
        # Get total credits
        total_creditos = resultados['total']
        
        # Format response
        response = {
            "areas": {
                "pastagem_ha": area_pastagem,
                "florestal_ha": area_florestal,
                "renovacao_cultura_ha": area_renovacao_cultura,
                "integracao_lavoura_ha": area_integracao_lavoura
            },
            "resultados_por_metodologia": {
                k: {
                    "creditos": v["creditos"],
                    "metodologia": v["metodologia"]
                } for k, v in resultados.items() if k != 'total'
            },
            "potencial_credito_total_tco2e": round(total_creditos, 2),
            "valor_estimado_reais": round(total_creditos * 50, 2)  # Assuming R$50 per tCO2e
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
