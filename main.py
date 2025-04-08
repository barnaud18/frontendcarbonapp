import os
import logging
from flask import Flask, send_from_directory, jsonify, request, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
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

# Enable CORS
CORS(app)

# Initialize the app with the extension
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Configure Swagger
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Calculadora de Pegada de Carbono Agrícola API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

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

def calcular_creditos_carbono(area_pastagem):
    """
    Calculate carbon credit potential for pasture recovery
    
    Parameters:
    - area_pastagem: Pasture area in hectares
    
    Returns:
    - Carbon credit potential in tCO2e/year
    """
    # Conservative carbon sequestration factor for pasture recovery (tCO2e/ha/year)
    # Based on VCS VM0032 methodology
    fator_sequestro = 0.5  # tCO2e/ha/year
    
    return area_pastagem * fator_sequestro

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
    """Serve the frontend main page"""
    app.logger.debug("Serving index.html")
    return send_file('frontend/index.html')

@app.route('/js/<path:path>')
def serve_js(path):
    """Serve JavaScript files"""
    app.logger.debug(f"Serving JS file: {path}")
    return send_file(f'frontend/js/{path}')

@app.route('/css/<path:path>')
def serve_css(path):
    """Serve CSS files"""
    app.logger.debug(f"Serving CSS file: {path}")
    return send_file(f'frontend/css/{path}')

@app.route('/api')
def api_index():
    """API root endpoint"""
    return jsonify({"message": "API de Calculadora de Pegada de Carbono Agrícola"})


@app.route('/static/swagger.json')
def swagger_spec():
    """Serve the swagger specification file"""
    with open('swagger.yml', 'r') as f:
        return f.read()


@app.route('/api/cadastrar_propriedade', methods=['POST'])
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


@app.route('/api/calcular', methods=['POST'])
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
        potencial_credito = calcular_creditos_carbono(
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


@app.route('/api/buscar_usuario/<int:propriedade_id>', methods=['GET'])
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


@app.route('/api/calcular-creditos', methods=['POST'])
def calcular_creditos():
    """
    Calculate carbon credits potential
    ---
    """
    try:
        data = request.get_json()
        area_pastagem = data.get('area_pastagem', 0)
        
        creditos = calcular_creditos_carbono(area_pastagem)
        
        return jsonify({
            "area_pastagem_ha": area_pastagem,
            "potencial_credito_tco2e": round(creditos, 2),
            "valor_estimado_reais": round(creditos * 50, 2)  # Assuming R$50 per tCO2e
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/propriedades', methods=['GET'])
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

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)