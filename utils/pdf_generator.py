"""
Módulo para geração de relatórios em PDF
"""
import os
from datetime import datetime
from weasyprint import HTML, CSS
from flask import render_template, url_for


def gerar_pdf_relatorio_creditos(cenario, config=None):
    """
    Gera um relatório em PDF com detalhes de créditos de carbono
    
    Args:
        cenario: O objeto de cenário do banco de dados
        config: Configurações adicionais para o PDF
        
    Returns:
        Caminho para o arquivo PDF gerado
    """
    # Gerar HTML a partir do template
    html_content = render_template(
        'pdf/relatorio_creditos.html',
        cenario=cenario,
        data_geracao=datetime.now().strftime('%d/%m/%Y %H:%M'),
        config=config or {}
    )
    
    # Definir o nome do arquivo PDF
    relatorio_nome = f"relatorio_creditos_{cenario.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    os.makedirs('static/relatorios', exist_ok=True)
    pdf_path = os.path.join('static/relatorios', relatorio_nome)
    
    # Definir estilos do PDF
    css = CSS(string='''
        body { 
            font-family: Arial, sans-serif;
            color: #333;
            line-height: 1.5;
            margin: 1cm;
        }
        h1, h2, h3 { color: #2c3e50; }
        .container { max-width: 800px; margin: 0 auto; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .destaque { background-color: #e8f4f8; font-weight: bold; }
        .logo { text-align: center; margin-bottom: 20px; }
        footer { text-align: center; font-size: 0.8em; color: #777; margin-top: 50px; }
        .pagina { page-break-after: always; }
        .grafico { text-align: center; margin: 20px 0; }
        .info-box { background-color: #f8f9fa; border-left: 4px solid #4caf50; padding: 10px; margin: 15px 0; }
        .data-geracao { text-align: right; font-size: 0.8em; color: #777; }
    ''')
    
    # Gerar o PDF com WeasyPrint
    HTML(string=html_content).write_pdf(pdf_path, stylesheets=[css])
    
    return pdf_path


def gerar_pdf_relatorio_emissoes(propriedade, emissao, agricultura, pecuaria, recomendacoes=None, config=None):
    """
    Gera um relatório em PDF com detalhes de emissões de carbono
    
    Args:
        propriedade: O objeto de propriedade do banco de dados
        emissao: O objeto de emissão do banco de dados
        agricultura: O objeto de agricultura do banco de dados
        pecuaria: O objeto de pecuária do banco de dados
        recomendacoes: Lista de recomendações
        config: Configurações adicionais para o PDF
        
    Returns:
        Caminho para o arquivo PDF gerado
    """
    # Gerar HTML a partir do template
    html_content = render_template(
        'pdf/relatorio_emissoes.html',
        propriedade=propriedade,
        emissao=emissao,
        agricultura=agricultura,
        pecuaria=pecuaria,
        recomendacoes=recomendacoes or [],
        data_geracao=datetime.now().strftime('%d/%m/%Y %H:%M'),
        config=config or {}
    )
    
    # Definir o nome do arquivo PDF
    relatorio_nome = f"relatorio_emissoes_{propriedade.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    os.makedirs('static/relatorios', exist_ok=True)
    pdf_path = os.path.join('static/relatorios', relatorio_nome)
    
    # Definir estilos do PDF
    css = CSS(string='''
        body { 
            font-family: Arial, sans-serif;
            color: #333;
            line-height: 1.5;
            margin: 1cm;
        }
        h1, h2, h3 { color: #2c3e50; }
        .container { max-width: 800px; margin: 0 auto; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .destaque { background-color: #e8f4f8; font-weight: bold; }
        .logo { text-align: center; margin-bottom: 20px; }
        footer { text-align: center; font-size: 0.8em; color: #777; margin-top: 50px; }
        .pagina { page-break-after: always; }
        .grafico { text-align: center; margin: 20px 0; }
        .info-box { background-color: #f8f9fa; border-left: 4px solid #4caf50; padding: 10px; margin: 15px 0; }
        .data-geracao { text-align: right; font-size: 0.8em; color: #777; }
        .recomendacao { background-color: #fff8dc; padding: 10px; margin: 5px 0; border-left: 3px solid #ffd700; }
    ''')
    
    # Gerar o PDF com WeasyPrint
    HTML(string=html_content).write_pdf(pdf_path, stylesheets=[css])
    
    return pdf_path