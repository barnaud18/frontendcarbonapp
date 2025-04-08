# Calculadora de Pegada de Carbono Agrícola

Uma aplicação web para calcular a pegada de carbono de propriedades rurais e estimar o potencial de créditos de carbono usando diversas metodologias reconhecidas internacionalmente.

## Funcionalidades

- Cálculo de emissões de gases de efeito estufa (GEE) com base em:
  - Área agrícola e uso de fertilizantes
  - Número de bovinos
  - Consumo de combustível (diesel)
- Cálculo do potencial de créditos de carbono com várias metodologias:
  - Recuperação de pastagens degradadas (VCS VM0032)
  - Florestamento e reflorestamento (AR-ACM0003)
  - Rotação de culturas (CDM AMS-III.AU)
  - Sistemas de integração lavoura-pecuária (VCS VM0017)
- Cadastro de propriedades rurais com armazenamento em banco de dados
- Visualização de recomendações para redução de emissões
- Dashboard para visualizar propriedades cadastradas

## Configuração Local

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. Clone este repositório:
   ```
   git clone https://github.com/seu-usuario/calculadora-pegada-carbono.git
   cd calculadora-pegada-carbono
   ```

2. (Opcional) Crie e ative um ambiente virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

### Executando a aplicação

1. Execute o seguinte comando para iniciar o servidor:
   ```
   python main.py
   ```

2. Acesse a aplicação no navegador:
   ```
   http://127.0.0.1:5000/
   ```

## Metodologia

### Cálculo de Emissões

Os cálculos de emissões são baseados na metodologia Tier 1 do IPCC (Painel Intergovernamental sobre Mudanças Climáticas):

- **Fertilizantes**: Emissões de N₂O calculadas com fator de emissão de 1% (44/28 * 0.01 * 298 GWP)
- **Bovinos**: Emissões de CH₄ estimadas em 56 kg CH₄/cabeça/ano (GWP = 25)
- **Combustível**: Fator de emissão de 2,68 kg CO₂e/litro de diesel

### Cálculo de Créditos de Carbono

Os fatores de sequestro de carbono usados são:

- **Recuperação de pastagens**: 0,5 tCO₂e/ha/ano (VCS VM0032)
- **Florestamento**: 8,0 tCO₂e/ha/ano (AR-ACM0003)
- **Rotação de culturas**: 1,2 tCO₂e/ha/ano (CDM AMS-III.AU)
- **Sistemas integrados**: 3,0 tCO₂e/ha/ano (VCS VM0017)

**Nota**: Estes valores são conservadores e baseados em literatura científica. Para projetos reais, é necessário seguir rigorosamente cada metodologia específica.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Contato

Para dúvidas ou sugestões, entre em contato pelo email seu-email@exemplo.com.

## Agradecimentos

- IPCC - pelos fatores de emissão e metodologias
- Verra (VCS) - pelas metodologias de crédito de carbono
- UNFCCC (CDM) - pelas metodologias de pequena escala