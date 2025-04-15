from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, flash, session, send_file
from datetime import datetime
try:
    import requests
except ImportError:
    print("Erro ao importar o módulo requests. Instalando...")
    import subprocess
    subprocess.check_call(["pip", "install", "requests"])
    import requests
import json
import pdfkit
import os
import tempfile
from fpdf import FPDF

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    return render_template('index.html', config=current_app.config)

@views_bp.route('/dashboard')
def dashboard():
    response = requests.get(f"{current_app.config['BACKEND_URL']}/api/cenarios")
    cenarios = response.json()
    
    # Calcular totais
    total_cenarios = len(cenarios)
    total_creditos = sum(cenario.get('total_creditos', 0) for cenario in cenarios)
    valor_estimado = sum(cenario.get('valor_estimado', 0) for cenario in cenarios)
    
    # Calcular área total
    area_total = sum(
        cenario.get('area_pastagem', 0) +
        cenario.get('area_florestal', 0) +
        cenario.get('area_renovacao_cultura', 0) +
        cenario.get('area_integracao_lavoura', 0)
        for cenario in cenarios
    )
    
    # Calcular totais por metodologia
    totais = {
        'credito_pastagem': sum(cenario.get('credito_pastagem', 0) for cenario in cenarios),
        'credito_florestal': sum(cenario.get('credito_florestal', 0) for cenario in cenarios),
        'credito_renovacao': sum(cenario.get('credito_renovacao', 0) for cenario in cenarios),
        'credito_integracao': sum(cenario.get('credito_integracao', 0) for cenario in cenarios)
    }
    
    # Preparar dados para o gráfico de séries temporais
    datas = [cenario.get('data_calculo', '') for cenario in cenarios]
    creditos_acumulados = []
    acumulado = 0
    for cenario in cenarios:
        acumulado += cenario.get('total_creditos', 0)
        creditos_acumulados.append(acumulado)
    
    return render_template('dashboard.html', 
                         cenarios=cenarios,
                         total_cenarios=total_cenarios,
                         total_creditos=total_creditos,
                         valor_estimado=valor_estimado,
                         area_total=area_total,
                         totais=totais,
                         datas=datas,
                         creditos_acumulados=creditos_acumulados)

@views_bp.route('/creditos', methods=['GET', 'POST'])
def creditos():
    if request.method == 'POST':
        # Validação dos dados
        area_pastagem = float(request.form.get('area_pastagem', 0))
        area_florestal = float(request.form.get('area_florestal', 0))
        area_renovacao_cultura = float(request.form.get('area_renovacao_cultura', 0))
        area_integracao_lavoura = float(request.form.get('area_integracao_lavoura', 0))
        
        # Verifica se pelo menos uma área foi preenchida
        if area_pastagem == 0 and area_florestal == 0 and area_renovacao_cultura == 0 and area_integracao_lavoura == 0:
            return render_template('calculadora_creditos.html', error="Por favor, preencha pelo menos uma área.")
        
        # Dados para a API
        data = {
            "area_pastagem": area_pastagem,
            "area_florestal": area_florestal,
            "area_renovacao_cultura": area_renovacao_cultura,
            "area_integracao_lavoura": area_integracao_lavoura
        }
        
        # Faz a requisição para a API
        response = requests.post(
            f"{current_app.config['BACKEND_URL']}/api/calcular",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            resultados = response.json()
            # Armazena os resultados na sessão
            session['resultados'] = resultados
            return redirect(url_for('views.creditos'))
        else:
            return render_template('calculadora_creditos.html', error="Erro ao calcular créditos. Por favor, tente novamente.")
    
    # GET request - renderiza a página com os resultados da sessão se existirem
    resultados = session.get('resultados')
    if resultados:
        # Limpa os resultados da sessão após recuperá-los
        session.pop('resultados', None)
        
        # Adicionar a função now() para o template
        def now():
            return datetime.now()
            
        return render_template('creditos.html', 
                             resultados=resultados,
                             potencial_credito=resultados.get('total_creditos', 0),
                             valor_estimado=resultados.get('valor_estimado', 0),
                             area_pastagem=resultados.get('resultados', {}).get('pastagem', {}).get('area', 0),
                             area_florestal=resultados.get('resultados', {}).get('florestal', {}).get('area', 0),
                             area_renovacao_cultura=resultados.get('resultados', {}).get('renovacao', {}).get('area', 0),
                             area_integracao_lavoura=resultados.get('resultados', {}).get('integracao', {}).get('area', 0),
                             now=now)
    
    return render_template('calculadora_creditos.html')

@views_bp.route('/resultado')
def resultado():
    # Obter os resultados da sessão ou parâmetros
    nome_cenario = request.args.get('nome_cenario', '')
    resultados_json = request.args.get('resultados', '{}')
    
    # Converter a string JSON para dicionário
    import json
    try:
        resultados = json.loads(resultados_json)
    except:
        resultados = {}
    
    # Adicionar a função now() para o template
    def now():
        return datetime.now()
    
    return render_template('resultado.html', 
                         nome_cenario=nome_cenario,
                         resultados=resultados,
                         now=now)

@views_bp.route('/detalhes/<int:id>')
def detalhes_cenario(id):
    response = requests.get(f"{current_app.config['BACKEND_URL']}/api/cenarios/{id}")
    cenario = response.json()
    return render_template('detalhes.html', cenario=cenario)

@views_bp.route('/estudos-caso')
def estudos_caso():
    # Dados estáticos dos estudos de caso
    estudos = [
        {
            'id': 1,
            'titulo': 'Recuperação de Pastagens em MG',
            'localizacao': 'Minas Gerais',
            'area': 500,
            'metodologia': 'VCS VM0032',
            'resultados': {
                'creditos_gerados': 350,
                'valor_estimado': 17500,
                'periodo': '2023-2024'
            },
            'descricao': 'Projeto com 500 hectares de pastagens recuperadas, com sequestro médio de 0,7 tCO2e/ha/ano.',
            'contato': 'contato@fazendamg.com.br'
        },
        {
            'id': 2,
            'titulo': 'Reflorestamento no PR',
            'localizacao': 'Paraná',
            'area': 200,
            'metodologia': 'AR-ACM0003',
            'resultados': {
                'creditos_gerados': 2000,
                'valor_estimado': 100000,
                'periodo': '2022-2024'
            },
            'descricao': 'Reflorestamento de 200 hectares com espécies nativas, sequestro de 10 tCO2e/ha/ano.',
            'contato': 'contato@florestapr.com.br'
        },
        {
            'id': 3,
            'titulo': 'Integração Lavoura-Pecuária em MT',
            'localizacao': 'Mato Grosso',
            'area': 1200,
            'metodologia': 'VCS VM0017',
            'resultados': {
                'creditos_gerados': 3600,
                'valor_estimado': 180000,
                'periodo': '2021-2024'
            },
            'descricao': 'Implementação em 1.200 hectares, redução de fertilizantes e aumento da produtividade.',
            'contato': 'contato@ilpmt.com.br'
        }
    ]
    return render_template('estudos_caso.html', estudos=estudos)

@views_bp.route('/estudos-caso/<int:estudo_id>')
def detalhes_estudo(estudo_id):
    # Dados estáticos dos estudos de caso
    estudos = {
        1: {
            'id': 1,
            'titulo': 'Recuperação de Pastagens em MG',
            'localizacao': 'Minas Gerais',
            'area': 500,
            'metodologia': 'VCS VM0032',
            'resultados': {
                'creditos_gerados': 350,
                'valor_estimado': 17500,
                'periodo': '2023-2024'
            },
            'descricao': 'Projeto com 500 hectares de pastagens recuperadas, com sequestro médio de 0,7 tCO2e/ha/ano.',
            'contato': 'contato@fazendamg.com.br'
        },
        2: {
            'id': 2,
            'titulo': 'Reflorestamento no PR',
            'localizacao': 'Paraná',
            'area': 200,
            'metodologia': 'AR-ACM0003',
            'resultados': {
                'creditos_gerados': 2000,
                'valor_estimado': 100000,
                'periodo': '2022-2024'
            },
            'descricao': 'Reflorestamento de 200 hectares com espécies nativas, sequestro de 10 tCO2e/ha/ano.',
            'contato': 'contato@florestapr.com.br'
        },
        3: {
            'id': 3,
            'titulo': 'Integração Lavoura-Pecuária em MT',
            'localizacao': 'Mato Grosso',
            'area': 1200,
            'metodologia': 'VCS VM0017',
            'resultados': {
                'creditos_gerados': 3600,
                'valor_estimado': 180000,
                'periodo': '2021-2024'
            },
            'descricao': 'Implementação em 1.200 hectares, redução de fertilizantes e aumento da produtividade.',
            'contato': 'contato@ilpmt.com.br'
        }
    }
    
    estudo = estudos.get(estudo_id)
    if not estudo:
        flash('Estudo de caso não encontrado.', 'error')
        return redirect(url_for('views.estudos_caso'))
        
    return render_template('detalhes_estudo.html', estudo=estudo)

@views_bp.route('/impacto-real/<int:id>')
def impacto_real(id):
    # Buscar dados do cenário
    response = requests.get(f"{current_app.config['BACKEND_URL']}/api/cenarios/{id}")
    if response.status_code != 200:
        flash('Erro ao carregar o cenário.', 'error')
        return redirect(url_for('views.dashboard'))
    
    cenario = response.json()
    
    # Calcular impactos reais baseados nos créditos totais
    total_creditos = cenario.get('total_creditos', 0)
    
    impacto_real = {
        'transporte': {
            'impactos': [
                {
                    'nome': 'Carros por Ano',
                    'valor': total_creditos * 0.5,  # 1 carro emite ~2 tCO2e/ano
                    'unidade': 'carros'
                },
                {
                    'nome': 'Quilômetros Evitados',
                    'valor': total_creditos * 5000,  # ~200g CO2e/km
                    'unidade': 'km'
                },
                {
                    'nome': 'Voos SP-RJ',
                    'valor': total_creditos * 5,  # ~0.2 tCO2e/voo
                    'unidade': 'voos'
                }
            ]
        },
        'energia': {
            'impactos': [
                {
                    'nome': 'Residências/Ano',
                    'valor': total_creditos * 0.25,  # ~4 tCO2e/residência/ano
                    'unidade': 'casas'
                },
                {
                    'nome': 'Smartphones Carregados',
                    'valor': total_creditos * 100000,  # ~10g CO2e/carga
                    'unidade': 'cargas'
                },
                {
                    'nome': 'Lâmpadas LED',
                    'valor': total_creditos * 200,  # ~5kg CO2e economizado/lâmpada/ano
                    'unidade': 'lâmpadas'
                }
            ]
        },
        'natureza': {
            'impactos': [
                {
                    'nome': 'Árvores por 10 Anos',
                    'valor': total_creditos * 90,  # ~11kg CO2e/árvore/ano
                    'unidade': 'árvores'
                },
                {
                    'nome': 'Hectares Preservados',
                    'valor': total_creditos * 0.2,  # ~5 tCO2e/ha/ano
                    'unidade': 'hectares'
                },
                {
                    'nome': 'Área Preservada',
                    'valor': total_creditos * 2000,  # ~0.5kg CO2e/m²/ano
                    'unidade': 'm²'
                }
            ]
        },
        'consumo': {
            'impactos': [
                {
                    'nome': 'Refeições Vegetarianas',
                    'valor': total_creditos * 800,  # ~1.25kg CO2e/refeição com carne
                    'unidade': 'refeições'
                },
                {
                    'nome': 'Garrafas Plásticas',
                    'valor': total_creditos * 4000,  # ~0.25kg CO2e/garrafa
                    'unidade': 'garrafas'
                },
                {
                    'nome': 'Camisetas de Algodão',
                    'valor': total_creditos * 400,  # ~2.5kg CO2e/camiseta
                    'unidade': 'camisetas'
                }
            ]
        }
    }
    
    return render_template('impacto_real.html', cenario=cenario, impacto_real=impacto_real)

@views_bp.route('/apagar-cenario/<int:id>', methods=['POST'])
def apagar_cenario(id):
    try:
        response = requests.delete(f"{current_app.config['BACKEND_URL']}/api/cenarios/{id}")
        if response.status_code == 200:
            flash('Cenário excluído com sucesso!', 'success')
        else:
            flash('Erro ao excluir o cenário.', 'error')
    except Exception as e:
        flash(f'Erro ao excluir o cenário: {str(e)}', 'error')
    
    return redirect(url_for('views.dashboard'))

@views_bp.route('/apagar-todos-cenarios', methods=['POST'])
def apagar_todos_cenarios():
    try:
        # Buscar todos os cenários
        response = requests.get(f"{current_app.config['BACKEND_URL']}/api/cenarios")
        if response.status_code == 200:
            cenarios = response.json()
            # Excluir cada cenário
            for cenario in cenarios:
                requests.delete(f"{current_app.config['BACKEND_URL']}/api/cenarios/{cenario['id']}")
            flash('Todos os cenários foram excluídos com sucesso!', 'success')
        else:
            flash('Erro ao buscar os cenários.', 'error')
    except Exception as e:
        flash(f'Erro ao excluir os cenários: {str(e)}', 'error')
    
    return redirect(url_for('views.dashboard'))

@views_bp.route('/exportar-pdf/creditos/<int:id>')
def exportar_pdf_creditos(id):
    """Exporta relatório de créditos de carbono em PDF"""
    try:
        # Buscar dados do cenário
        response = requests.get(f"{current_app.config['BACKEND_URL']}/api/cenarios/{id}")
        if response.status_code != 200:
            flash('Erro ao buscar dados do cenário', 'error')
            return redirect(url_for('views.dashboard'))
            
        cenario = response.json()
        
        # Criar um arquivo temporário para o PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            # Renderizar o template para PDF
            html = render_template('pdf/relatorio_creditos.html', 
                                 cenario=cenario,
                                 data_geracao=datetime.now().strftime('%d/%m/%Y às %H:%M'))
            
            # Configurar opções do PDF
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': 'UTF-8',
                'no-outline': None
            }
            
            # Gerar o PDF
            pdfkit.from_string(html, tmp.name, options=options)
            
            # Enviar o arquivo
            return send_file(tmp.name,
                            mimetype='application/pdf',
                            as_attachment=True,
                            download_name=f'relatorio_creditos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
                            
    except Exception as e:
        flash(f'Erro ao gerar PDF: {str(e)}', 'error')
        return redirect(url_for('views.dashboard'))

@views_bp.route('/gerar-pdf/<int:id>')
def gerar_pdf(id):
    """Gera um PDF com os detalhes do cenário"""
    try:
        # Buscar dados do cenário
        response = requests.get(f"{current_app.config['BACKEND_URL']}/api/cenarios/{id}")
        if response.status_code != 200:
            flash('Erro ao buscar dados do cenário', 'error')
            return redirect(url_for('views.dashboard'))
            
        cenario = response.json()
        
        # Criar o PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Configurar fonte
        pdf.set_font('Arial', 'B', 16)
        
        # Título
        pdf.cell(0, 10, f'Relatório de Créditos de Carbono - {cenario["nome_cenario"]}', ln=True, align='C')
        pdf.ln(10)
        
        # Informações do cenário
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Informações do Cenário:', ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Localização: {cenario["localizacao"]}', ln=True)
        pdf.cell(0, 10, f'Área Total: {cenario["area_total"]} hectares', ln=True)
        pdf.cell(0, 10, f'Total de Créditos: {cenario["total_creditos"]} tCO₂e', ln=True)
        pdf.cell(0, 10, f'Valor Estimado: R$ {cenario["valor_estimado"]:,.2f}', ln=True)
        pdf.ln(10)
        
        # Metodologias
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Metodologias:', ln=True)
        pdf.set_font('Arial', '', 12)
        for metodologia in cenario['metodologias']:
            pdf.cell(0, 10, f'• {metodologia}', ln=True)
        pdf.ln(10)
        
        # Resultados por metodologia
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Resultados por Metodologia:', ln=True)
        pdf.set_font('Arial', '', 12)
        for metodologia, resultado in cenario['resultados'].items():
            if resultado:
                pdf.cell(0, 10, f'{metodologia.title()}:', ln=True)
                pdf.cell(0, 10, f'  Créditos: {resultado["creditos"]} tCO₂e', ln=True)
                pdf.cell(0, 10, f'  Valor: R$ {resultado["valor"]:,.2f}', ln=True)
                pdf.ln(5)
        
        # Salvar o PDF
        pdf_path = os.path.join(current_app.static_folder, 'pdfs', f'cenario_{id}.pdf')
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        pdf.output(pdf_path)
        
        # Retornar o arquivo
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'cenario_{id}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'Erro ao gerar PDF: {str(e)}', 'error')
        return redirect(url_for('views.dashboard')) 