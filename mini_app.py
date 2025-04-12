from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "chave_secreta_temporaria"

# Função simplificada de cálculo de emissões
def calcular_emissoes(area_agricola, uso_fertilizante, num_bovinos, consumo_combustivel):
    """Calcula emissões de forma simplificada"""
    try:
        # Conversão explícita para números
        area_agricola = float(area_agricola or 0)
        uso_fertilizante = float(uso_fertilizante or 0)
        num_bovinos = int(num_bovinos or 0)
        consumo_combustivel = float(consumo_combustivel or 0)
        
        # Fatores de emissão simplificados
        emissao_agricultura = area_agricola * uso_fertilizante * 4.68
        emissao_pecuaria = num_bovinos * 1400  # 56 kg CH4 * 25 GWP
        emissao_combustivel = consumo_combustivel * 2.68
        
        total = emissao_agricultura + emissao_pecuaria + emissao_combustivel
        
        return {
            'total': total,
            'agricultura': emissao_agricultura,
            'pecuaria': emissao_pecuaria,
            'combustivel': emissao_combustivel
        }
    except Exception as e:
        print(f"Erro no cálculo de emissões: {str(e)}")
        return {'total': 0, 'agricultura': 0, 'pecuaria': 0, 'combustivel': 0}

# Função simplificada para gerar recomendações
def gerar_recomendacoes():
    """Gera recomendações estáticas"""
    return [
        {
            'acao': 'Manejo eficiente de fertilizantes',
            'descricao': 'Implementar técnicas de aplicação fracionada de fertilizantes.',
            'potencial_reducao': 500
        },
        {
            'acao': 'Suplementação alimentar para bovinos',
            'descricao': 'Adicionar aditivos na dieta animal para reduzir metano entérico.',
            'potencial_reducao': 800
        },
        {
            'acao': 'Eficiência no uso de combustível',
            'descricao': 'Otimizar uso de maquinário e implementar plantio direto.',
            'potencial_reducao': 300
        },
        {
            'acao': 'Recuperação de pastagens degradadas',
            'descricao': 'Aumentar o sequestro de carbono no solo.',
            'potencial_reducao': 500
        }
    ]

# Rota principal
@app.route('/')
def index():
    return render_template('novo_inicio.html')

@app.route('/inicio-novo')
def inicio_novo():
    return render_template('novo_inicio.html')

# Rota para cálculo
@app.route('/calcular', methods=['POST'])
def calcular():
    try:
        # Obter dados do formulário
        nome = request.form.get('nome', 'Propriedade')
        tamanho_total = request.form.get('tamanho_total', '0')
        area_agricola = request.form.get('area_agricola', '0')
        uso_fertilizante = request.form.get('uso_fertilizante', '0')
        area_pastagem = request.form.get('area_pastagem', '0')
        num_bovinos = request.form.get('num_bovinos', '0')
        consumo_combustivel = request.form.get('consumo_combustivel', '0')
        
        # Calcular emissões
        emissoes = calcular_emissoes(
            area_agricola=area_agricola,
            uso_fertilizante=uso_fertilizante,
            num_bovinos=num_bovinos,
            consumo_combustivel=consumo_combustivel
        )
        
        # Calcular potencial de crédito (simplificado)
        try:
            area_pastagem_float = float(area_pastagem or 0)
            potencial_credito = area_pastagem_float * 0.5  # 0.5 tCO2e/ha/ano
        except:
            potencial_credito = 0
            
        # Gerar recomendações padrão
        recomendacoes = gerar_recomendacoes()
        
        # Retornar página de resultados
        return render_template(
            'resultado.html',
            nome=nome,
            tamanho_total=float(tamanho_total or 0),
            area_agricola=float(area_agricola or 0),
            uso_fertilizante=float(uso_fertilizante or 0),
            area_pastagem=float(area_pastagem or 0),
            num_bovinos=int(num_bovinos or 0),
            consumo_combustivel=float(consumo_combustivel or 0),
            total_emissao=emissoes['total'],
            emissao_agricultura=emissoes['agricultura'],
            emissao_pecuaria=emissoes['pecuaria'],
            emissao_combustivel=emissoes['combustivel'],
            potencial_credito=potencial_credito,
            recomendacoes=recomendacoes
        )
        
    except Exception as e:
        print(f"Erro em /calcular: {str(e)}")
        flash(f"Erro ao calcular: {str(e)}", 'error')
        return redirect(url_for('index'))

# Rota para créditos de carbono
@app.route('/creditos', methods=['GET', 'POST'])
def creditos():
    if request.method == 'GET':
        return render_template('calculadora_creditos.html')
        
    try:
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
        credito_pastagem = area_pastagem * 0.5
        credito_florestal = area_florestal * 8.0
        credito_renovacao = area_renovacao_cultura * 1.2
        credito_integracao = area_integracao_lavoura * 3.0
        
        total_creditos = credito_pastagem + credito_florestal + credito_renovacao + credito_integracao
        valor_estimado = total_creditos * 50  # R$50 por tCO2e
        
        # Resultados para o template
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
        print(f"Erro em /creditos: {str(e)}")
        flash(f"Erro ao calcular créditos: {str(e)}", 'error')
        return redirect(url_for('creditos'))

# Rota para cadastro (apenas simulação, sem banco de dados)
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    try:
        flash("Propriedade cadastrada com sucesso!", 'success')
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Erro em /cadastrar: {str(e)}")
        flash(f"Erro ao cadastrar: {str(e)}", 'error')
        return redirect(url_for('index'))

# Rota para listar propriedades (simulação)
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

# Servir arquivos estáticos
@app.route('/static/<path:filename>')
def serve_static(filename):
    return app.send_static_file(filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)