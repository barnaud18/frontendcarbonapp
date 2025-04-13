# Calculadora de Pegada de Carbono e Créditos de Carbono Agrícolas

Uma plataforma web avançada para calcular, analisar e visualizar a pegada de carbono e o potencial de créditos de carbono para propriedades rurais, com foco em sustentabilidade ambiental e geração de valor para produtores agrícolas.

## Descrição do Projeto

Este sistema foi desenvolvido para ajudar produtores rurais, consultores ambientais e empresas agrícolas a:

1. **Calcular emissões de carbono** para diferentes fontes agrícolas (fertilizantes, pecuária, combustíveis)
2. **Estimar potencial de créditos de carbono** usando múltiplas metodologias reconhecidas internacionalmente
3. **Visualizar impactos reais** das reduções de carbono em termos tangíveis e compreensíveis
4. **Obter recomendações personalizadas** para redução de emissões
5. **Gerar relatórios detalhados** para documentação e certificação

## Funcionalidades Principais

### 1. Calculadora de Pegada de Carbono
- Cálculo de emissões baseado na metodologia Tier 1 do IPCC
- Avaliação de diferentes fontes: agricultura, pecuária e consumo de combustível
- Resultados apresentados em CO₂e (dióxido de carbono equivalente)

### 2. Calculadora de Créditos de Carbono
- Suporte a múltiplas metodologias:
  - Recuperação de pastagens degradadas (VCS VM0032)
  - Florestamento e reflorestamento (AR-ACM0003)
  - Rotação de culturas (CDM AMS-III.AU)
  - Sistemas de integração lavoura-pecuária (VCS VM0017)
- Estimativa de valor monetário dos créditos de carbono

### 3. Visualizador de Impacto Real
- Tradução de créditos de carbono em equivalências tangíveis do mundo real
- Categorias de impacto: Transporte, Energia, Natureza e Consumo
- Visualizações interativas e contextualizadas

### 4. Dashboard Analítico
- Gráficos interativos de distribuição de créditos por metodologia
- Evolução temporal dos cálculos realizados
- Estatísticas consolidadas de área, créditos totais e valor estimado

### 5. Sistema de Gestão de Cenários
- Cadastro e armazenamento de múltiplos cenários de cálculo
- Exportação de relatórios em PDF
- Funcionalidades de exclusão individual e em massa

## Tecnologias Utilizadas

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap, Chart.js
- **Banco de Dados**: PostgreSQL
- **Geração de PDFs**: WeasyPrint
- **API**: RESTful API com documentação Swagger

## Metodologia e Referências

Os cálculos implementados baseiam-se em metodologias científicas reconhecidas:

- **Emissões Agrícolas**: Baseadas em fatores de emissão do IPCC para fertilizantes nitrogenados (N₂O)
- **Emissões Pecuárias**: Baseadas em fatores de emissão para fermentação entérica de bovinos (CH₄)
- **Combustíveis**: Fatores de emissão para diesel utilizado em maquinário agrícola
- **Créditos de Carbono**: Baseados em metodologias VCS (Verified Carbon Standard) e CDM (Clean Development Mechanism) da UNFCCC

## Próximos Passos

- Implementação de mais metodologias de crédito de carbono
- Integração com sensores e sistemas de monitoramento em tempo real
- Marketplace para comercialização de créditos de carbono
- Aplicativo móvel para coleta de dados em campo

## Equipe

Desenvolvido como parte do projeto de sustentabilidade agrícola, esta plataforma visa democratizar o acesso a ferramentas de análise de carbono para produtores de todos os portes, contribuindo para práticas agrícolas mais sustentáveis e a mitigação das mudanças climáticas.