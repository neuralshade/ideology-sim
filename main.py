import argparse
import time
import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, callback_context
import plotly.express as px
import plotly.graph_objects as go

# Importa o modelo original
from model import SocietyModel

# =============================================================================
# FUNÇÃO DE SIMULAÇÃO EM LOTE ("A Mente da IA")
# =============================================================================
def run_multiverse_simulation(num_realities, steps, agents, base_seed):
    """
    Roda N simulações independentes e retorna um DataFrame consolidado.
    """
    all_history = []
    
    for i in range(num_realities):
        # Cria uma seed única para cada realidade baseada na seed mestre
        current_seed = base_seed + i
        model = SocietyModel(N=agents, seed=current_seed)
        
        # Loop da simulação
        for _ in range(steps):
            model.step()
            snap = model.snapshot()
            snap["t"] = model.t
            snap["reality_id"] = f"Realidade {i+1}" # Identificador da linha temporal
            all_history.append(snap)
            
    return pd.DataFrame(all_history)

# =============================================================================
# LAYOUTS
# =============================================================================

# --- Layout da Página Principal (Cópia adaptada do original) ---
def get_home_layout():
    return html.Div([
        html.H1("Simulação Única (Home)"),
        html.P("Esta é a visualização padrão de uma única linha do tempo."),
        html.A("Ir para Calculadora de Multiverso (/calc-reality)", href="/calc-reality", className="link-button"),
        html.Hr(),
        html.Div("Para ver esta simulação, execute o modo padrão ou use o menu acima.")
    ])

# --- Layout da Calculadora de Realidades (/calc-reality) ---
def get_calc_reality_layout():
    return html.Div([
        html.H2("🪐 Calculadora de Realidades Alternativas"),
        html.P("Configure a IA para projetar múltiplos futuros possíveis baseados em condições estocásticas."),
        
        # Área de Controles
        html.Div([
            html.Div([
                html.Label("Número de Realidades (Cenários):"),
                dcc.Input(id="input-n-realities", type="number", value=5, min=1, max=10),
            ], style={"marginRight": "20px"}),
            
            html.Div([
                html.Label("Duração (Passos/Anos):"),
                dcc.Input(id="input-steps", type="number", value=30, min=10, max=200),
            ], style={"marginRight": "20px"}),

            html.Div([
                html.Label("População por Realidade:"),
                dcc.Input(id="input-agents", type="number", value=1000, min=100, max=5000),
            ], style={"marginRight": "20px"}),
            
            html.Button('CALCULAR TRAJETÓRIAS', id='btn-calc', n_clicks=0, 
                        style={'backgroundColor': '#2a9d8f', 'color': 'white', 'fontWeight': 'bold'})
        ], style={"display": "flex", "alignItems": "end", "padding": "20px", "backgroundColor": "#f0f0f0", "borderRadius": "8px"}),
        
        html.Br(),
        
        # Área de Loading e Gráficos
        dcc.Loading(
            id="loading-multiverse",
            type="cube",
            children=[
                html.Div(id="multiverse-output")
            ]
        )
    ])

# =============================================================================
# APP DASH & ROUTING
# =============================================================================
app = Dash(__name__, suppress_callback_exceptions=True)

# Layout Mestre com Roteamento
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', style={'padding': '20px', 'fontFamily': 'Arial, sans-serif'})
])

# Callback de Roteamento (Router)
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/calc-reality':
        return get_calc_reality_layout()
    else:
        # Por padrão mostra uma versão simplificada ou o app original
        # Aqui, apenas para exemplo, mostramos um link. 
        # (Você poderia integrar o app original inteiro aqui se quisesse)
        return get_home_layout()

# Callback da Calculadora (/calc-reality)
@app.callback(
    Output("multiverse-output", "children"),
    Input("btn-calc", "n_clicks"),
    State("input-n-realities", "value"),
    State("input-steps", "value"),
    State("input-agents", "value"),
    prevent_initial_call=True
)
def update_multiverse_graphs(n_clicks, n_realities, steps, agents):
    if not n_clicks:
        return html.Div()

    start_time = time.time()
    
    # 1. Executa as simulações
    df = run_multiverse_simulation(
        num_realities=n_realities, 
        steps=steps, 
        agents=agents, 
        base_seed=42
    )
    
    elapsed = time.time() - start_time
    
    # 2. Gera os Gráficos Comparativos
    
    # Gráfico A: Comparação de Polarização
    fig_polar = px.line(
        df, x="t", y="Polarização", color="reality_id",
        title="Divergência de Polarização entre Realidades",
        labels={"t": "Tempo (anos)", "Polarização": "Índice de Variância"}
    )
    fig_polar.update_layout(hovermode="x unified")

    # Gráfico B: Comparação de Satisfação Social
    fig_sat = px.line(
        df, x="t", y="Satisfação", color="reality_id",
        title="Níveis de Satisfação Social",
        labels={"t": "Tempo (anos)", "Satisfação": "Índice (0-1)"}
    )

    # Gráfico C: Média Ideológica (Esquerda vs Direita)
    fig_avg = px.line(
        df, x="t", y="Ideologia média", color="reality_id",
        title="Deriva Ideológica Média (-1 Esq / +1 Dir)",
    )
    # Adiciona linha de centro
    fig_avg.add_hline(y=0, line_dash="dot", annotation_text="Centro", annotation_position="bottom right")

    return html.Div([
        html.Div(f"Simulação concluída em {elapsed:.2f} segundos. {len(df)} pontos de dados gerados.", 
                 style={"color": "gray", "marginBottom": "10px"}),
        
        dcc.Graph(figure=fig_polar),
        html.Div([
            dcc.Graph(figure=fig_sat, style={"width": "48%", "display": "inline-block"}),
            dcc.Graph(figure=fig_avg, style={"width": "48%", "display": "inline-block"}),
        ])
    ])

if __name__ == "__main__":
    # Roda o servidor
    print("Servidor rodando...")
    print("Acesse a Home em: http://127.0.0.1:8050/")
    print("Acesse a Calculadora em: http://127.0.0.1:8050/calc-reality")
    app.run(debug=True)