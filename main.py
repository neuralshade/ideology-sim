import argparse

import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

from model import SocietyModel

def build_app(steps=120, seed=42, agents=5000):
    model = SocietyModel(N=agents, seed=seed)
    history = []

    # -------------------------------
    # Simulação inicial
    # -------------------------------
    for _ in range(steps):
        model.step()
        snap = model.snapshot()
        snap["t"] = model.t
        history.append(snap)

    df = pd.DataFrame(history)
    ideology_options = model.labels
    macro_options = [
        "Satisfação",
        "Mobilidade",
        "Gini",
        "Polarização",
        "Ideologia média",
        "Desemprego",
        "Crescimento",
    ]

    # -------------------------------
    # Dash UI
    # -------------------------------
    app = Dash(__name__)

    app.layout = html.Div([
        html.H2("Simulação Dinâmica de Ideologias Políticas"),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Ideologias visíveis"),
                        dcc.Dropdown(
                            id="ideology-select",
                            options=[{"label": name, "value": name} for name in ideology_options],
                            value=ideology_options,
                            multi=True,
                        ),
                    ],
                    style={"flex": "1", "minWidth": "240px"},
                ),
                html.Div(
                    [
                        html.Label("Variáveis macrossociais"),
                        dcc.Dropdown(
                            id="macro-select",
                            options=[{"label": name, "value": name} for name in macro_options],
                            value=["Satisfação", "Mobilidade", "Gini"],
                            multi=True,
                        ),
                    ],
                    style={"flex": "1", "minWidth": "240px"},
                ),
                html.Div(
                    [
                        html.Label("Modo do gráfico ideológico"),
                        dcc.RadioItems(
                            id="ideology-mode",
                            options=[
                                {"label": "Área", "value": "area"},
                                {"label": "Linhas", "value": "line"},
                            ],
                            value="area",
                            inline=True,
                        ),
                    ],
                    style={"flex": "1", "minWidth": "200px"},
                ),
                html.Div(
                    [
                        html.Label("Suavização (janela)"),
                        dcc.Slider(
                            id="smooth-window",
                            min=1,
                            max=15,
                            step=1,
                            value=1,
                            marks={1: "1", 5: "5", 10: "10", 15: "15"},
                        ),
                    ],
                    style={"flex": "1", "minWidth": "220px"},
                ),
            ],
            style={"display": "flex", "gap": "16px", "flexWrap": "wrap"},
        ),

        dcc.Graph(id="ideology-area"),
        dcc.Graph(id="macro-vars"),
        dcc.Graph(id="ideology-snapshot"),

        dcc.Slider(
            min=0,
            max=len(df) - 1,
            step=1,
            value=len(df) - 1,
            id="time-slider",
            marks={i: str(i) for i in range(0, len(df), 20)}
        )
    ])

    # -------------------------------
    # Callbacks
    # -------------------------------
    @app.callback(
        Output("ideology-area", "figure"),
        Output("macro-vars", "figure"),
        Output("ideology-snapshot", "figure"),
        Input("time-slider", "value"),
        Input("ideology-select", "value"),
        Input("macro-select", "value"),
        Input("ideology-mode", "value"),
        Input("smooth-window", "value"),
    )
    def update_plots(t, ideology_selected, macro_selected, ideology_mode, smooth_window):
        dff = df.iloc[:t + 1]
        ideology_selected = ideology_selected or ideology_options
        macro_selected = macro_selected or macro_options

        if smooth_window and smooth_window > 1:
            smooth_cols = list(set(ideology_selected + macro_selected))
            dff = dff.copy()
            dff[smooth_cols] = dff[smooth_cols].rolling(
                window=smooth_window, min_periods=1
            ).mean()

        if ideology_mode == "line":
            fig1 = px.line(
                dff,
                x="t",
                y=ideology_selected,
                title="Evolução Ideológica",
                labels={"value": "Proporção", "t": "Tempo"}
            )
        else:
            fig1 = px.area(
                dff,
                x="t",
                y=ideology_selected,
                title="Evolução Ideológica",
                labels={"value": "Proporção", "t": "Tempo"}
            )

        fig2 = px.line(
            dff,
            x="t",
            y=macro_selected,
            title="Variáveis Macrossociais"
        )

        snapshot_row = df.iloc[t]
        fig3 = px.bar(
            x=ideology_options,
            y=[snapshot_row[label] for label in ideology_options],
            title=f"Distribuição ideológica (t={t})",
            labels={"x": "Ideologia", "y": "Proporção"},
        )

        return fig1, fig2, fig3

    return app


app = build_app()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ideology simulation dashboard.")
    parser.add_argument("--steps", type=int, default=120, help="Número de passos iniciais")
    parser.add_argument("--seed", type=int, default=42, help="Seed para reprodutibilidade")
    parser.add_argument("--agents", type=int, default=5000, help="Número de agentes")
    args = parser.parse_args()

    app = build_app(steps=args.steps, seed=args.seed, agents=args.agents)
    app.run(debug=True)
