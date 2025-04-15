# Frontend da Calculadora de Pegada de Carbono e Créditos de Carbono Agrícolas

Interface de usuário intuitiva e interativa para cálculo, visualização e gestão de pegada de carbono e potencial de créditos de carbono para propriedades rurais.

## Visão Geral

Este frontend foi desenvolvido para oferecer uma experiência de usuário rica e informativa, permitindo que produtores rurais, consultores ambientais e empresas agrícolas possam:

- Calcular emissões de carbono de suas atividades agrícolas
- Estimar o potencial de geração de créditos de carbono usando diversas metodologias
- Visualizar o impacto real de suas reduções de carbono de forma tangível
- Gerenciar diferentes cenários de cálculo
- Exportar relatórios detalhados em PDF

## Funcionalidades Principais

### Calculadora de Pegada de Carbono
- Formulário intuitivo para entrada de dados sobre propriedade rural
- Cálculo imediato de emissões de diferentes fontes (agricultura, pecuária, combustível)
- Visualização de gráficos informativos mostrando a distribuição de emissões

### Calculadora de Créditos de Carbono
- Interface para estimativa de potencial de créditos de carbono
- Suporte a múltiplas metodologias reconhecidas internacionalmente
- Cálculo automático de valor monetário estimado dos créditos

### Dashboard Analítico
- Visão consolidada de todos os cenários calculados
- Gráficos interativos mostrando distribuição de créditos por metodologia
- Linha do tempo mostrando evolução dos cálculos
- Estatísticas consolidadas (total de créditos, valor estimado, área total)

### Visualizador de Impacto Real
- Tradução visual de toneladas de CO₂e em impactos tangíveis
- Categorias de impacto organizadas por setor (Transporte, Energia, Natureza, Consumo)
- Visualizações informativas com contexto e comparações

### Gestão de Cenários
- Lista completa de cenários calculados
- Funcionalidades para visualizar detalhes de cada cenário
- Opções para excluir cenários individualmente ou em massa
- Exportação de relatórios em PDF

## Tecnologias Utilizadas

- **HTML5/CSS3**: Estrutura e estilização responsiva da interface
- **JavaScript**: Interatividade e manipulação de dados no lado do cliente
- **Bootstrap**: Framework CSS para design responsivo e componentes pré-estilizados
- **Chart.js**: Biblioteca para criação de gráficos interativos
- **Templates Jinja2**: Renderização HTML no servidor com Flask

## Destaques da Interface

- **Modo Escuro**: Interface com tema escuro para redução de fadiga visual
- **Design Responsivo**: Adaptação para diferentes tamanhos de tela e dispositivos
- **Visualizações Interativas**: Gráficos e elementos visuais ricos para melhor compreensão
- **Formulários Intuitivos**: Entrada de dados simplificada e validação em tempo real
- **Feedback Visual**: Notificações e alertas para manter o usuário informado

## Integração com o Backend

O frontend se comunica com a API da Calculadora de Pegada de Carbono através de:

- Solicitações HTTP para cálculo de emissões e créditos
- Armazenamento de cenários na base de dados
- Recuperação de dados históricos para o dashboard
- Geração de relatórios PDF via servidor

## Próximos Passos

- Implementação de gráficos de comparação entre múltiplos cenários
- Adição de mapas interativos para visualização geográfica das propriedades
- Suporte a mais idiomas para internacionalização
- Melhorias de acessibilidade para usuários com necessidades especiais

## Passo a Passo para Execução

### Pré-requisitos
- Python 3.8 ou superior
- Node.js 14 ou superior
- pip (gerenciador de pacotes Python)
- npm (gerenciador de pacotes Node.js)

### 1. Configuração do Ambiente Virtual
```powershell
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\Activate
```

### 2. Instalação das Dependências
```powershell
# Instalar dependências do backend
cd backend
pip install -r requirements.txt

# Instalar dependências do frontend
cd ../frontend
npm install
```

### 3. Configuração do Banco de Dados
```powershell
# Voltar para a pasta raiz
cd ..

# Inicializar o banco de dados
python -m backend.app.db.init_db
```

### 4. Execução da Aplicação
```powershell
# Iniciar o servidor backend (em um terminal)
cd backend
python run.py

# Iniciar o servidor frontend (em outro terminal)
cd frontend
npm start
```

### 5. Acessando a Aplicação
- Frontend: http://localhost:3000
- API Backend: http://localhost:5000
- Documentação Swagger: http://localhost:5000/api/docs

### 6. Testando a Aplicação
1. Acesse a página inicial
2. Use a calculadora rápida para testar o cálculo básico
3. Acesse a calculadora completa para testes mais detalhados
4. Verifique o dashboard para visualização dos resultados
5. Teste a exportação de relatórios em PDF

### 7. Solução de Problemas Comuns
- Se o backend não iniciar, verifique se a porta 5000 está disponível
- Se o frontend não iniciar, verifique se a porta 3000 está disponível
- Para problemas com o banco de dados, tente reinicializar com `python -m backend.app.db.init_db`
- Para atualizar dependências, execute `pip install -r requirements.txt --upgrade`

### 8. Desenvolvimento
- Para desenvolvimento, recomenda-se usar o modo debug do Flask:
  ```powershell
  $env:FLASK_ENV = "development"
  python run.py
  ```
  