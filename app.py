import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Definir base para modelos SQLAlchemy
class Base(DeclarativeBase):
    pass

# Inicializar Flask e SQLAlchemy
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "chave_secreta_temporaria")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Definir modelos
class Propriedade(db.Model):
    """Modelo para dados de propriedade rural"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tamanho_total = db.Column(db.Float, nullable=False)  # em hectares
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    agricultura = db.relationship('Agricultura', backref='propriedade', lazy=True, uselist=False)
    pecuaria = db.relationship('Pecuaria', backref='propriedade', lazy=True, uselist=False)
    emissao = db.relationship('Emissao', backref='propriedade', lazy=True, uselist=False)
    recomendacoes = db.relationship('Recomendacao', backref='propriedade', lazy=True)
    
    def to_dict(self):
        """Converte modelo para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'tamanho_total': self.tamanho_total,
            'data_registro': self.data_registro.strftime('%Y-%m-%d %H:%M:%S'),
            'agricultura': self.agricultura.to_dict() if self.agricultura else None,
            'pecuaria': self.pecuaria.to_dict() if self.pecuaria else None,
            'emissao': self.emissao.to_dict() if self.emissao else None,
            'recomendacoes': [r.to_dict() for r in self.recomendacoes] if self.recomendacoes else []
        }

class Agricultura(db.Model):
    """Modelo para dados agrícolas"""
    id = db.Column(db.Integer, primary_key=True)
    propriedade_id = db.Column(db.Integer, db.ForeignKey('propriedade.id'), nullable=False)
    area_agricola = db.Column(db.Float, nullable=False)  # em hectares
    uso_fertilizante = db.Column(db.Float, nullable=False)  # em kg/ha/ano
    consumo_combustivel = db.Column(db.Float, nullable=False)  # em litros/ano
    area_pastagem = db.Column(db.Float, nullable=True)  # em hectares
    area_florestal = db.Column(db.Float, nullable=True, default=0)  # em hectares
    area_renovacao_cultura = db.Column(db.Float, nullable=True, default=0)  # em hectares
    area_integracao_lavoura = db.Column(db.Float, nullable=True, default=0)  # em hectares
    
    def to_dict(self):
        """Converte modelo para dicionário"""
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
    """Modelo para dados de pecuária"""
    id = db.Column(db.Integer, primary_key=True)
    propriedade_id = db.Column(db.Integer, db.ForeignKey('propriedade.id'), nullable=False)
    num_bovinos = db.Column(db.Integer, nullable=False)  # número de bovinos
    
    def to_dict(self):
        """Converte modelo para dicionário"""
        return {
            'id': self.id,
            'propriedade_id': self.propriedade_id,
            'num_bovinos': self.num_bovinos
        }

class Emissao(db.Model):
    """Modelo para resultados de cálculo de emissão"""
    id = db.Column(db.Integer, primary_key=True)
    propriedade_id = db.Column(db.Integer, db.ForeignKey('propriedade.id'), nullable=False)
    total_emissao = db.Column(db.Float, nullable=False)  # em kg CO2e
    emissao_agricultura = db.Column(db.Float, nullable=False)  # em kg CO2e
    emissao_pecuaria = db.Column(db.Float, nullable=False)  # em kg CO2e
    emissao_combustivel = db.Column(db.Float, nullable=False)  # em kg CO2e
    potencial_credito = db.Column(db.Float, nullable=True)  # em tCO2e
    data_calculo = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Converte modelo para dicionário"""
        return {
            'id': self.id,
            'propriedade_id': self.propriedade_id,
            'total_emissao': self.total_emissao,
            'emissao_agricultura': self.emissao_agricultura,
            'emissao_pecuaria': self.emissao_pecuaria,
            'emissao_combustivel': self.emissao_combustivel,
            'potencial_credito': self.potencial_credito,
            'data_calculo': self.data_calculo.strftime('%Y-%m-%d %H:%M:%S')
        }

class Recomendacao(db.Model):
    """Modelo para recomendações de mitigação"""
    id = db.Column(db.Integer, primary_key=True)
    propriedade_id = db.Column(db.Integer, db.ForeignKey('propriedade.id'), nullable=False)
    acao = db.Column(db.String(255), nullable=False)  # ação recomendada
    descricao = db.Column(db.Text, nullable=True)  # descrição detalhada
    potencial_reducao = db.Column(db.Float, nullable=False)  # em kg CO2e
    
    def to_dict(self):
        """Converte modelo para dicionário"""
        return {
            'id': self.id,
            'propriedade_id': self.propriedade_id,
            'acao': self.acao,
            'descricao': self.descricao,
            'potencial_reducao': self.potencial_reducao
        }

# Funções de cálculo
def calcular_emissoes(area_agricola, uso_fertilizante, num_bovinos, consumo_combustivel):
    """
    Calcula emissões de carbono usando metodologia Tier 1 do IPCC
    
    Parâmetros:
    - area_agricola: Área agrícola em hectares
    - uso_fertilizante: Uso de fertilizante em kg/ha/ano
    - num_bovinos: Número de bovinos
    - consumo_combustivel: Consumo de combustível em litros/ano
    
    Retorna:
    - Dicionário com detalhes de emissão
    """
    # Conversão segura para números
    try:
        area_agricola = float(area_agricola) if area_agricola is not None else 0.0
    except (ValueError, TypeError):
        area_agricola = 0.0
        
    try:
        uso_fertilizante = float(uso_fertilizante) if uso_fertilizante is not None else 0.0
    except (ValueError, TypeError):
        uso_fertilizante = 0.0
        
    try:
        num_bovinos = int(num_bovinos) if num_bovinos is not None else 0
    except (ValueError, TypeError):
        num_bovinos = 0
        
    try:
        consumo_combustivel = float(consumo_combustivel) if consumo_combustivel is not None else 0.0
    except (ValueError, TypeError):
        consumo_combustivel = 0.0
    
    # Fatores de emissão
    # Fertilizante: 1% do N aplicado é emitido como N2O (fator de GWP = 298)
    # Convertendo N2O para CO2e: 44/28 (razão molar) * 0.01 (fração emitida) * 298 (GWP) * quantidade de N
    fator_fertilizante = 4.68  # 44/28 * 0.01 * 298 = 4.68
    
    # Bovinos: 56 kg CH4/cabeça/ano (fator de GWP = 25)
    fator_bovino = 56 * 25  # kg CO2e/bovino/ano
    
    # Combustível: 2.68 kg CO2e/litro de diesel
    fator_combustivel = 2.68  # kg CO2e/litro
    
    # Cálculos de emissão
    emissao_fertilizante = area_agricola * uso_fertilizante * fator_fertilizante
    emissao_bovinos = num_bovinos * fator_bovino
    emissao_combustivel = consumo_combustivel * fator_combustivel
    
    # Total de emissões
    total_emissao = emissao_fertilizante + emissao_bovinos + emissao_combustivel
    
    return {
        'total': total_emissao,
        'agricultura': emissao_fertilizante,
        'pecuaria': emissao_bovinos,
        'combustivel': emissao_combustivel
    }

def calcular_creditos_carbono_simplificado(area_pastagem=0.0, area_florestal=0.0, area_renovacao_cultura=0.0, area_integracao_lavoura=0.0):
    """
    Versão simplificada da calculadora de créditos de carbono
    
    Parâmetros:
    - area_pastagem: Área de pastagem em hectares
    - area_florestal: Área florestal em hectares
    - area_renovacao_cultura: Área de renovação de cultura em hectares
    - area_integracao_lavoura: Área de integração lavoura-pecuária em hectares
    
    Retorna:
    - Dicionário com resultados dos cálculos de crédito de carbono
    """
    # Conversão segura para números
    try:
        area_pastagem = float(area_pastagem) if area_pastagem is not None else 0.0
    except (ValueError, TypeError):
        area_pastagem = 0.0
        
    try:
        area_florestal = float(area_florestal) if area_florestal is not None else 0.0
    except (ValueError, TypeError):
        area_florestal = 0.0
        
    try:
        area_renovacao_cultura = float(area_renovacao_cultura) if area_renovacao_cultura is not None else 0.0
    except (ValueError, TypeError):
        area_renovacao_cultura = 0.0
        
    try:
        area_integracao_lavoura = float(area_integracao_lavoura) if area_integracao_lavoura is not None else 0.0
    except (ValueError, TypeError):
        area_integracao_lavoura = 0.0
    
    # Fatores de sequestro de carbono (tCO2e/ha/ano)
    fator_pastagem = 0.5  # VCS VM0032 - Recuperação de pastagens
    fator_florestal = 8.0  # AR-ACM0003 - Florestamento
    fator_renovacao = 1.2  # CDM AMS-III.AU - Práticas agrícolas de baixo carbono
    fator_integracao = 3.0  # VCS VM0017 - Sistemas integrados
    
    # Cálculo por metodologia
    credito_pastagem = area_pastagem * fator_pastagem
    credito_florestal = area_florestal * fator_florestal
    credito_renovacao = area_renovacao_cultura * fator_renovacao
    credito_integracao = area_integracao_lavoura * fator_integracao
    
    # Total de créditos
    total_creditos = credito_pastagem + credito_florestal + credito_renovacao + credito_integracao
    
    # Construir resultado
    resultado = {
        "total": total_creditos,
        "metodologias": {}
    }
    
    # Adicionar detalhes por metodologia
    if area_pastagem > 0:
        resultado["metodologias"]["pastagem"] = {
            "area": area_pastagem,
            "fator": fator_pastagem,
            "creditos": credito_pastagem,
            "metodologia": "VCS VM0032 - Recuperação de pastagens degradadas"
        }
    
    if area_florestal > 0:
        resultado["metodologias"]["florestal"] = {
            "area": area_florestal,
            "fator": fator_florestal,
            "creditos": credito_florestal,
            "metodologia": "AR-ACM0003 - Florestamento e reflorestamento"
        }
    
    if area_renovacao_cultura > 0:
        resultado["metodologias"]["renovacao"] = {
            "area": area_renovacao_cultura,
            "fator": fator_renovacao,
            "creditos": credito_renovacao,
            "metodologia": "CDM AMS-III.AU - Práticas agrícolas de baixo carbono"
        }
    
    if area_integracao_lavoura > 0:
        resultado["metodologias"]["integracao"] = {
            "area": area_integracao_lavoura,
            "fator": fator_integracao,
            "creditos": credito_integracao,
            "metodologia": "VCS VM0017 - Sistemas de integração lavoura-pecuária"
        }
    
    return resultado

def gerar_recomendacoes(emissao_agricultura, emissao_pecuaria, emissao_combustivel, num_bovinos, uso_fertilizante):
    """
    Gera recomendações de mitigação com base nas fontes de emissão
    
    Parâmetros:
    - emissao_agricultura: Emissões agrícolas em kg CO2e
    - emissao_pecuaria: Emissões da pecuária em kg CO2e
    - emissao_combustivel: Emissões de combustível em kg CO2e
    - num_bovinos: Número de bovinos
    - uso_fertilizante: Uso de fertilizante em kg/ha/ano
    
    Retorna:
    - Lista de dicionários com recomendações
    """
    recomendacoes = []
    
    # Recomendações para agricultura
    if emissao_agricultura > 0 and uso_fertilizante > 0:
        reducao_potencial = emissao_agricultura * 0.2  # 20% de redução potencial
        recomendacoes.append({
            'acao': 'Manejo eficiente de fertilizantes',
            'descricao': 'Implementar técnicas de aplicação fracionada de fertilizantes e utilizar inibidores de nitrificação.',
            'potencial_reducao': reducao_potencial
        })
    
    # Recomendações para pecuária
    if emissao_pecuaria > 0 and num_bovinos > 0:
        reducao_potencial = emissao_pecuaria * 0.15  # 15% de redução potencial
        recomendacoes.append({
            'acao': 'Suplementação alimentar para bovinos',
            'descricao': 'Adicionar aditivos na dieta animal para reduzir a emissão de metano entérico.',
            'potencial_reducao': reducao_potencial
        })
    
    # Recomendações para combustível
    if emissao_combustivel > 0:
        reducao_potencial = emissao_combustivel * 0.3  # 30% de redução potencial
        recomendacoes.append({
            'acao': 'Eficiência no uso de combustível',
            'descricao': 'Otimizar o uso de maquinário agrícola e implementar técnicas de plantio direto.',
            'potencial_reducao': reducao_potencial
        })
    
    # Recomendações gerais
    recomendacoes.append({
        'acao': 'Recuperação de pastagens degradadas',
        'descricao': 'Recuperar pastagens degradadas para aumentar o sequestro de carbono no solo.',
        'potencial_reducao': 500  # Valor fixo em kg CO2e
    })
    
    recomendacoes.append({
        'acao': 'Implementação de sistemas agroflorestais',
        'descricao': 'Combinar a produção agrícola com espécies florestais para aumentar o sequestro de carbono.',
        'potencial_reducao': 1000  # Valor fixo em kg CO2e
    })
    
    return recomendacoes

# Rotas
@app.route('/')
def index():
    """Página inicial com formulário de cálculo"""
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    """Calcula pegada de carbono e exibe resultados"""
    try:
        # Obter dados do formulário com conversão segura
        nome = request.form.get('nome', 'Propriedade Teste')
        
        # Conversão segura para números
        try:
            tamanho_total = float(request.form.get('tamanho_total', 0))
        except ValueError:
            tamanho_total = 0.0
        
        try:
            area_agricola = float(request.form.get('area_agricola', 0))
        except ValueError:
            area_agricola = 0.0
        
        try:
            uso_fertilizante = float(request.form.get('uso_fertilizante', 0))
        except ValueError:
            uso_fertilizante = 0.0
        
        try:
            area_pastagem = float(request.form.get('area_pastagem', 0))
        except ValueError:
            area_pastagem = 0.0
        
        try:
            num_bovinos = int(request.form.get('num_bovinos', 0))
        except ValueError:
            num_bovinos = 0
        
        try:
            consumo_combustivel = float(request.form.get('consumo_combustivel', 0))
        except ValueError:
            consumo_combustivel = 0.0
        
        # Calcular emissões
        resultado_emissoes = calcular_emissoes(
            area_agricola=area_agricola,
            uso_fertilizante=uso_fertilizante,
            num_bovinos=num_bovinos,
            consumo_combustivel=consumo_combustivel
        )
        
        # Cálculo simplificado de créditos de carbono
        potencial_credito = area_pastagem * 0.5  # Fator para pastagens recuperadas
        
        # Gerar recomendações
        recomendacoes = gerar_recomendacoes(
            emissao_agricultura=resultado_emissoes['agricultura'],
            emissao_pecuaria=resultado_emissoes['pecuaria'],
            emissao_combustivel=resultado_emissoes['combustivel'],
            num_bovinos=num_bovinos,
            uso_fertilizante=uso_fertilizante
        )
        
        # Renderizar template de resultados
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
        # Registrar erro e redirecionar
        app.logger.error(f"Erro no cálculo: {str(e)}")
        flash(f"Erro ao calcular: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    """Cadastra uma nova propriedade no banco de dados"""
    try:
        # Obter dados do formulário com conversão segura
        nome = request.form.get('nome', 'Propriedade Sem Nome')
        
        # Conversão segura para números
        try:
            tamanho_total = float(request.form.get('tamanho_total', 0))
        except ValueError:
            tamanho_total = 0.0
        
        try:
            area_agricola = float(request.form.get('area_agricola', 0))
        except ValueError:
            area_agricola = 0.0
        
        try:
            uso_fertilizante = float(request.form.get('uso_fertilizante', 0))
        except ValueError:
            uso_fertilizante = 0.0
        
        try:
            area_pastagem = float(request.form.get('area_pastagem', 0))
        except ValueError:
            area_pastagem = 0.0
        
        try:
            num_bovinos = int(request.form.get('num_bovinos', 0))
        except ValueError:
            num_bovinos = 0
        
        try:
            consumo_combustivel = float(request.form.get('consumo_combustivel', 0))
        except ValueError:
            consumo_combustivel = 0.0
        
        # Dados opcionais para novas metodologias de crédito de carbono
        try:
            area_florestal = float(request.form.get('area_florestal', 0))
        except ValueError:
            area_florestal = 0.0
        
        try:
            area_renovacao_cultura = float(request.form.get('area_renovacao_cultura', 0))
        except ValueError:
            area_renovacao_cultura = 0.0
        
        try:
            area_integracao_lavoura = float(request.form.get('area_integracao_lavoura', 0))
        except ValueError:
            area_integracao_lavoura = 0.0
        
        # Criar propriedade
        nova_propriedade = Propriedade(
            nome=nome,
            tamanho_total=tamanho_total
        )
        db.session.add(nova_propriedade)
        db.session.flush()  # Obter ID sem commit
        
        # Criar dados agrícolas
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
        
        # Criar dados de pecuária
        pecuaria = Pecuaria(
            propriedade_id=nova_propriedade.id,
            num_bovinos=num_bovinos
        )
        db.session.add(pecuaria)
        
        # Calcular emissões
        resultado_emissoes = calcular_emissoes(
            area_agricola=area_agricola,
            uso_fertilizante=uso_fertilizante,
            num_bovinos=num_bovinos,
            consumo_combustivel=consumo_combustivel
        )
        
        # Cálculo direto de créditos de carbono (abordagem simplificada)
        credito_pastagem = area_pastagem * 0.5
        credito_florestal = area_florestal * 8.0
        credito_renovacao = area_renovacao_cultura * 1.2
        credito_integracao = area_integracao_lavoura * 3.0
        potencial_credito = credito_pastagem + credito_florestal + credito_renovacao + credito_integracao
        
        # Criar registro de emissão
        emissao = Emissao(
            propriedade_id=nova_propriedade.id,
            total_emissao=resultado_emissoes['total'],
            emissao_agricultura=resultado_emissoes['agricultura'],
            emissao_pecuaria=resultado_emissoes['pecuaria'],
            emissao_combustivel=resultado_emissoes['combustivel'],
            potencial_credito=potencial_credito
        )
        db.session.add(emissao)
        
        # Gerar e salvar recomendações
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
        
        # Commit de todas as alterações
        db.session.commit()
        
        # Redirecionar com mensagem de sucesso
        flash("Propriedade cadastrada com sucesso!", 'success')
        return redirect(url_for('index'))
    
    except Exception as e:
        # Registrar erro e reverter transação
        app.logger.error(f"Erro no cadastro: {str(e)}")
        db.session.rollback()
        flash(f"Erro ao cadastrar: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/creditos', methods=['GET', 'POST'])
def creditos():
    """Calculadora de créditos de carbono"""
    if request.method == 'GET':
        # Exibir formulário da calculadora de créditos
        return render_template('calculadora_creditos.html')
    
    try:
        # Para requisições POST, processar os dados do formulário
        app.logger.debug("Processando dados do formulário de créditos")
        
        # Obter dados do formulário com conversão segura
        try:
            area_pastagem = float(request.form.get('area_pastagem', 0))
        except ValueError:
            area_pastagem = 0.0
        
        try:
            area_florestal = float(request.form.get('area_florestal', 0))
        except ValueError:
            area_florestal = 0.0
        
        try:
            area_renovacao_cultura = float(request.form.get('area_renovacao_cultura', 0))
        except ValueError:
            area_renovacao_cultura = 0.0
        
        try:
            area_integracao_lavoura = float(request.form.get('area_integracao_lavoura', 0))
        except ValueError:
            area_integracao_lavoura = 0.0
        
        # Verificar se pelo menos uma área é fornecida
        if area_pastagem <= 0 and area_florestal <= 0 and area_renovacao_cultura <= 0 and area_integracao_lavoura <= 0:
            raise ValueError("Pelo menos uma área deve ser maior que zero")
        
        # Cálculo direto dos créditos de carbono
        credito_pastagem = area_pastagem * 0.5
        credito_florestal = area_florestal * 8.0
        credito_renovacao = area_renovacao_cultura * 1.2
        credito_integracao = area_integracao_lavoura * 3.0
        
        # Total de créditos
        total_creditos = credito_pastagem + credito_florestal + credito_renovacao + credito_integracao
        valor_estimado = total_creditos * 50  # R$50 por tCO2e
        
        # Organizar resultados para o template
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
        
        # Renderizar template de resultados
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
        # Registrar erro e redirecionar
        app.logger.error(f"Erro no cálculo de créditos: {str(e)}")
        flash(f"Erro ao calcular créditos: {str(e)}", 'error')
        return redirect(url_for('creditos'))

@app.route('/propriedades')
def listar_propriedades():
    """Lista todas as propriedades cadastradas"""
    propriedades = Propriedade.query.all()
    return render_template('propriedades.html', propriedades=propriedades)

# Rota para servir arquivos estáticos
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve arquivos estáticos"""
    return send_from_directory('static', filename)

# Criar tabelas e executar aplicação
with app.app_context():
    db.create_all()

# Inicializar aplicação
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)