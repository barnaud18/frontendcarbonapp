# API da Calculadora de Pegada de Carbono e Créditos de Carbono Agrícolas

API RESTful para cálculo, armazenamento e gestão de dados relacionados à pegada de carbono e potencial de créditos de carbono para propriedades rurais, com foco em metodologias científicas reconhecidas internacionalmente.

## Visão Geral

Esta API foi desenvolvida para oferecer funcionalidades robustas de back-end para aplicações de cálculo de pegada de carbono e créditos de carbono no setor agrícola. A arquitetura foi projetada para ser escalável, flexível e aderente a padrões científicos internacionais.

## Endpoints Principais

### Propriedades Rurais
- `POST /api/propriedades`: Registra uma nova propriedade rural
- `GET /api/propriedades`: Lista todas as propriedades cadastradas
- `GET /api/propriedades/<id>`: Recupera dados de uma propriedade específica

### Cálculo de Emissões
- `POST /api/calcular`: Calcula emissões de carbono para uma propriedade
- `GET /api/cenarios`: Lista todos os cenários de cálculo
- `GET /api/cenarios/<id>`: Recupera um cenário específico

### Créditos de Carbono
- `POST /api/calcular-creditos`: Calcula potencial de créditos de carbono
- `GET /api/referencias`: Lista metodologias e referências de cálculo

### Documentação
- `GET /api/docs`: Documentação Swagger da API

## Modelos de Dados

### Propriedade
Armazena dados básicos da propriedade rural:
- ID (chave primária)
- Nome
- Tamanho total (hectares)
- Data de registro

### Agricultura
Dados agrícolas relacionados à propriedade:
- Área agrícola (hectares)
- Uso de fertilizantes (kg/ha/ano)
- Consumo de combustível (litros/ano)
- Áreas para cálculo de crédito (pastagem, florestal, etc.)

### Pecuária
Dados de pecuária da propriedade:
- Número de bovinos
- Outros dados de manejo animal

### Emissão
Resultados dos cálculos de emissão:
- Total de emissões (kg CO₂e)
- Emissões por fonte (agricultura, pecuária, combustível)
- Potencial de crédito de carbono
- Data do cálculo

### CalculoCarbono
Dados específicos para cenários de cálculo de créditos:
- Nome do cenário
- Áreas por metodologia
- Créditos calculados por tipo
- Total de créditos e valor estimado

## Metodologias Implementadas

### Cálculo de Emissões
- Metodologia Tier 1 do IPCC para cálculo de emissões agrícolas
- Fatores de emissão para fertilizantes nitrogenados (N₂O)
- Fatores de emissão para fermentação entérica de bovinos (CH₄)
- Fatores de emissão para combustível (diesel)

### Cálculo de Créditos de Carbono
- VCS VM0032: Metodologia para recuperação de pastagens degradadas
- AR-ACM0003: Metodologia para florestamento e reflorestamento
- CDM AMS-III.AU: Metodologia para práticas agrícolas de baixo carbono
- VCS VM0017: Metodologia para sistemas de integração lavoura-pecuária

## Tecnologias Utilizadas

- **Linguagem**: Python 3.8+
- **Framework Web**: Flask
- **ORM**: SQLAlchemy
- **Banco de Dados**: PostgreSQL
- **Documentação**: Swagger/OpenAPI
- **Geração de PDF**: WeasyPrint

## Segurança e Boas Práticas

- Validação de entrada de dados
- Tratamento de exceções
- Logs detalhados para auditoria
- Estrutura modular para fácil manutenção
- Testes unitários e de integração

## Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- PostgreSQL
- Dependências listadas em requirements.txt

### Variáveis de Ambiente
- `DATABASE_URL`: URL de conexão com o banco de dados
- `FLASK_ENV`: Ambiente de execução (development/production)
- `FLASK_SECRET_KEY`: Chave secreta para sessões Flask

## Exemplos de Uso

### Exemplo: Calculando Emissões

```python
import requests
import json

url = "https://api.calculadora-carbono.com/api/calcular"
payload = {
    "area_agricola": 100.0,
    "uso_fertilizante": 200.0,
    "num_bovinos": 50,
    "consumo_combustivel": 5000.0
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, data=json.dumps(payload), headers=headers)
result = response.json()

print(f"Total de emissões: {result['total_emissao']} kg CO₂e")
```

### Exemplo: Calculando Créditos de Carbono

```python
import requests
import json

url = "https://api.calculadora-carbono.com/api/calcular-creditos"
payload = {
    "nome_cenario": "Recuperação de Pastagens 2025",
    "area_pastagem": 50.0,
    "area_florestal": 20.0,
    "area_renovacao_cultura": 30.0,
    "area_integracao_lavoura": 15.0
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, data=json.dumps(payload), headers=headers)
result = response.json()

print(f"Total de créditos: {result['total_creditos']} tCO₂e")
print(f"Valor estimado: R$ {result['valor_estimado']}")
```

## Desenvolvimento e Contribuição

Para contribuir com o desenvolvimento:

1. Clone o repositório
2. Crie um ambiente virtual Python
3. Instale as dependências com `pip install -r requirements.txt`
4. Execute os testes com `pytest`
5. Envie um pull request com suas alterações

## Próximos Passos

- Implementação de autenticação OAuth2
- Endpoints adicionais para análises estatísticas
- Suporte a mais metodologias de cálculo de crédito de carbono
- Integração com APIs externas de certificadoras