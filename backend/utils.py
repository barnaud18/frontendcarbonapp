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
    # IPCC Tier 1 emission factors
    # N2O from fertilizer: 44/28 * 0.01 = N2O emission factor
    fator_emissao_fertilizante = (44/28) * 0.01  # kg N2O-N/kg N
    
    # GWP of N2O: 298 (AR5)
    gwp_n2o = 298
    
    # Enteric methane from cattle: 56 kg CH4/head/year
    fator_emissao_bovino = 56 * 365 / 1000  # tCO2e/head/year, converted to kg
    
    # Diesel: 3.17 kg CO2e/liter
    fator_emissao_diesel = 3.17  # kg CO2e/liter
    
    # Calculate emissions
    # Agriculture: N fertilizer emissions
    emissao_fertilizante = area_agricola * uso_fertilizante * fator_emissao_fertilizante * gwp_n2o
    
    # Livestock: Enteric fermentation
    emissao_bovinos = num_bovinos * fator_emissao_bovino
    
    # Fuel: Diesel consumption
    emissao_combustivel = consumo_combustivel * fator_emissao_diesel
    
    # Total emissions
    total_emissao = emissao_fertilizante + emissao_bovinos + emissao_combustivel
    
    return {
        'total': total_emissao,
        'agricultura': emissao_fertilizante,
        'pecuaria': emissao_bovinos,
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
    # VCS factor for pasture recovery: 0.5 tCO2e/ha/year
    fator_sequestro_pastagem = 0.5  # tCO2e/ha/year
    
    return area_pastagem * fator_sequestro_pastagem


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
    
    # Livestock recommendations
    if emissao_pecuaria > 0:
        # Improved feed quality to reduce enteric methane
        reducao_potencial_dieta = emissao_pecuaria * 0.15  # 15% reduction potential
        recomendacoes.append({
            'acao': 'Melhorar qualidade da dieta animal',
            'descricao': 'Adição de concentrados e melhoramento da qualidade dos volumosos reduz a produção de metano entérico.',
            'potencial_reducao': reducao_potencial_dieta
        })
        
        # Biodigesters for manure management
        if num_bovinos >= 50:  # Only recommend for larger herds
            reducao_potencial_biodigestor = num_bovinos * 0.5 * 25  # Approx. 0.5 kg CH4/head/year from manure, CH4 GWP = 25
            recomendacoes.append({
                'acao': 'Implementar biodigestores',
                'descricao': 'Captura de metano dos dejetos animais para geração de energia.',
                'potencial_reducao': reducao_potencial_biodigestor
            })
    
    # Agricultural recommendations
    if emissao_agricultura > 0:
        # Precision agriculture for fertilizer optimization
        reducao_potencial_precisao = emissao_agricultura * 0.2  # 20% reduction potential
        recomendacoes.append({
            'acao': 'Adotar agricultura de precisão',
            'descricao': 'Aplicação de fertilizantes nitrogenados com tecnologias de taxa variável reduz emissões de N2O.',
            'potencial_reducao': reducao_potencial_precisao
        })
        
        # No-till farming
        reducao_potencial_plantio_direto = emissao_agricultura * 0.1  # 10% reduction potential
        recomendacoes.append({
            'acao': 'Implementar plantio direto',
            'descricao': 'Manutenção de cobertura vegetal e mínimo revolvimento do solo aumenta sequestro de carbono.',
            'potencial_reducao': reducao_potencial_plantio_direto
        })
        
        # Biological nitrogen fixation
        if uso_fertilizante > 100:  # High fertilizer use
            reducao_potencial_fixacao = emissao_agricultura * 0.3  # 30% reduction potential
            recomendacoes.append({
                'acao': 'Utilizar fixação biológica de nitrogênio',
                'descricao': 'Rotação com leguminosas e uso de inoculantes para reduzir necessidade de fertilizantes nitrogenados.',
                'potencial_reducao': reducao_potencial_fixacao
            })
    
    # Fuel recommendations
    if emissao_combustivel > 0:
        # Fuel efficiency
        reducao_potencial_eficiencia = emissao_combustivel * 0.1  # 10% reduction potential
        recomendacoes.append({
            'acao': 'Melhorar eficiência de máquinas agrícolas',
            'descricao': 'Manutenção preventiva e uso de tecnologias de economia de combustível.',
            'potencial_reducao': reducao_potencial_eficiencia
        })
        
        # Renewable energy
        reducao_potencial_renovaveis = emissao_combustivel * 0.5  # 50% reduction potential
        recomendacoes.append({
            'acao': 'Adotar energia renovável',
            'descricao': 'Implementação de energia solar ou biodiesel para reduzir uso de combustíveis fósseis.',
            'potencial_reducao': reducao_potencial_renovaveis
        })
    
    return recomendacoes
