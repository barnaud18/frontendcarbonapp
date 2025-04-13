"""
Utilitários para calcular e visualizar o impacto de créditos de carbono no mundo real
"""

def calcular_impacto_real(total_co2e):
    """
    Calcula o impacto equivalente de uma determinada quantidade de CO2e em termos do mundo real.
    
    Parâmetros:
    - total_co2e: Total de toneladas CO2 equivalente
    
    Retorna:
    - Dicionário com diferentes métricas de impacto
    """
    # Fatores de conversão baseados em pesquisas científicas
    # Fonte: EPA, IPCC, e outros estudos científicos
    
    impactos = {
        # Transporte
        "carros_ano": round(total_co2e / 4.6, 1),  # Carros retirados de circulação por 1 ano (4.6 tCO2e/carro/ano)
        "km_carro": round(total_co2e * 3863, 0),  # Km não dirigidos de carro (260g CO2e/km)
        "voos": round(total_co2e / 0.6, 1),  # Voos de ida São Paulo-Rio evitados (0.6 tCO2e/voo)
        
        # Energia
        "casas_energia": round(total_co2e / 1.5, 1),  # Casas brasileiras abastecidas com energia por 1 ano
        "celulares_carga": round(total_co2e * 183000, 0),  # Cargas completas de celular (5.5g CO2e/carga)
        "lampadas": round(total_co2e * 35, 0),  # Lâmpadas incandescentes substituídas por LED
        
        # Natureza
        "arvores": round(total_co2e * 15, 0),  # Árvores crescendo por 10 anos (1 árvore absorve ~67kg CO2 em 10 anos)
        "hectares_floresta": round(total_co2e / 6, 2),  # Hectares de floresta preservada por 1 ano
        "m2_vegetacao": round(total_co2e * 250, 0),  # Metros quadrados de vegetação nativa preservada
        
        # Consumo
        "refeicoes_carne": round(total_co2e * 600, 0),  # Refeições de carne substituídas por vegetarianas
        "garrafas_agua": round(total_co2e * 8500, 0),  # Garrafas plásticas de água de 1L não produzidas
        "roupas": round(total_co2e * 30, 0)  # Camisetas de algodão não produzidas
    }
    
    # Categorização para visualização
    categorias = {
        "transporte": {
            "icone": "bi-car-front",
            "titulo": "Transporte",
            "cor": "primary",
            "impactos": [
                {"nome": "Carros retirados por 1 ano", "valor": impactos["carros_ano"], "unidade": "carros"},
                {"nome": "Km não dirigidos", "valor": impactos["km_carro"], "unidade": "km"},
                {"nome": "Voos SP-RJ evitados", "valor": impactos["voos"], "unidade": "voos"}
            ]
        },
        "energia": {
            "icone": "bi-lightbulb",
            "titulo": "Energia",
            "cor": "warning",
            "impactos": [
                {"nome": "Casas abastecidas por 1 ano", "valor": impactos["casas_energia"], "unidade": "residências"},
                {"nome": "Cargas de celular", "valor": impactos["celulares_carga"], "unidade": "cargas"},
                {"nome": "Lâmpadas LED substituídas", "valor": impactos["lampadas"], "unidade": "lâmpadas"}
            ]
        },
        "natureza": {
            "icone": "bi-tree",
            "titulo": "Natureza",
            "cor": "success",
            "impactos": [
                {"nome": "Árvores crescendo por 10 anos", "valor": impactos["arvores"], "unidade": "árvores"},
                {"nome": "Hectares de floresta preservada", "valor": impactos["hectares_floresta"], "unidade": "hectares"},
                {"nome": "Área de vegetação preservada", "valor": impactos["m2_vegetacao"], "unidade": "m²"}
            ]
        },
        "consumo": {
            "icone": "bi-cart",
            "titulo": "Consumo",
            "cor": "info",
            "impactos": [
                {"nome": "Refeições vegetarianas", "valor": impactos["refeicoes_carne"], "unidade": "refeições"},
                {"nome": "Garrafas plásticas evitadas", "valor": impactos["garrafas_agua"], "unidade": "garrafas"},
                {"nome": "Camisetas não produzidas", "valor": impactos["roupas"], "unidade": "camisetas"}
            ]
        }
    }
    
    return categorias