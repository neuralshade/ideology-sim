# Ideology Sim: Simulação Dinâmica de Ideologias Políticas
Este projeto implementa uma simulação baseada em agentes para modelar a evolução de ideologias políticas numa sociedade artificial. Utiliza um modelo matemático de feedback entre variáveis microeconómicas (indivíduos) e macrossociais, visualizado num dashboard interativo construído com **Dash** e **Plotly**.

## 📋 Sobre o Projeto
O `ideology-sim` simula uma sociedade de 5.000 agentes onde cada indivíduo toma decisões ideológicas baseadas na sua utilidade percebida. O modelo explora como fatores como rendimento, satisfação social e inércia ideológica influenciam a adesão a quatro correntes políticas principais:
* Comunismo
* Social-democracia
* Capitalismo
* Libertarianismo
A simulação corre ao longo do tempo (t), gerando dados históricos que são visualizados num dashboard web.

## ⚙️ Como Funciona o Modelo
O núcleo da simulação está definido em `model.py`.

### Nível Micro (Agentes)
Cada agente possui:
* **Rendimento:** Distribuído conforme uma distribuição de Pareto (simulando desigualdade real).
* **Ideologia:** Um valor contínuo entre -1 e 1, inicialmente uniforme.
A decisão de mudar de ideologia depende de uma função de **Utilidade**, que pondera:
1. **Benefício Material:** Os mais pobres tendem a preferir a esquerda (redistribuição), enquanto os mais ricos preferem a direita (menor taxação).
2. **Inércia:** Resistência natural à mudança de opinião.
3. **Satisfação Social:** O "centro" atua como um atrator quando a satisfação social é alta.
4. **Variáveis Macro:** Desemprego e crescimento económico.

### Nível Macro (Sociedade)
A sociedade possui variáveis globais que evoluem e retroalimentam as decisões dos agentes:
* **Satisfação (S):** Afeta a mobilidade ideológica. Baixa satisfação aumenta a vontade de mudar (maior volatilidade).
* **Desigualdade (Gini):** Calculada com base no desvio padrão dos rendimentos.
* **Polarização:** Variância das ideologias da população.

## 🚀 Instalação e Requisitos
Este projeto requer **Python 3.12** ou superior.

### Dependências
As principais bibliotecas utilizadas são:
* `dash` (Interface Web)
* `plotly` (Gráficos)
* `pandas` (Manipulação de dados)
* `numpy` & `scipy` (Cálculos matemáticos)

### Configuração do Ambiente
1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/ideology-sim.git
cd ideology-sim
```

2. Instale as dependências (baseado no `pyproject.toml`):
```bash
pip install dash numpy pandas plotly scipy
```

## ▶️ Utilização
Para iniciar a simulação e o dashboard:
1. Execute o ficheiro principal:
```bash
python main.py
```

2. O terminal indicará que o servidor está a correr (geralmente em `http://127.0.0.1:8050/`).

3. Abra o navegador nesse endereço para interagir com a visualização.
**Nota:** O `main.py` executa inicialmente 120 passos de simulação antes de carregar a interface.

## 📊 Estrutura do Dashboard
A interface apresenta dois gráficos principais:
1. **Evolução Ideológica:** Um gráfico de área que mostra a proporção da população em cada quadrante ideológico ao longo do tempo.
2. **Variáveis Macrossociais:** Um gráfico de linhas monitorizando a Satisfação, Mobilidade e o Índice de Gini.
Inclui também um **slider temporal** que permite recuar na história da simulação.

## 📂 Estrutura de Ficheiros

* `main.py`: Script principal que executa a simulação, gera o histórico e inicia a aplicação Dash.
* `model.py`: Contém a classe `SocietyModel` com a lógica matemática, agentes e regras de transição.
* `pyproject.toml`: Ficheiro de configuração do projeto e dependências.
