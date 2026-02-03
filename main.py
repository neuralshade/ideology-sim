import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

from model import SocietyModel

model = SocietyModel()
history = []

# -------------------------------
# Simulação inicial
# -------------------------------
for _ in range(120):
    model.step()
    snap = model.snapshot()
    snap["t"] = model.t
    history.append(snap)

df = pd.DataFrame(history)

# -------------------------------
# Dash UI
# -------------------------------
app = Dash(__name__)

app.layout = html.Div([
    html.H2("Simulação Dinâmica de Ideologias Políticas"),

    dcc.Graph(id="ideology-area"),
    dcc.Graph(id="macro-vars"),

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
    Input("time-slider", "value")
)
def update_plots(t):
    dff = df.iloc[:t + 1]

    fig1 = px.area(
        dff,
        x="t",
        y=["Comunismo", "Social-democracia", "Capitalismo", "Libertarianismo"],
        title="Evolução Ideológica",
        labels={"value": "Proporção", "t": "Tempo"}
    )

    fig2 = px.line(
        dff,
        x="t",
        y=["Satisfação", "Mobilidade", "Gini"],
        title="Variáveis Macrossociais"
    )

    return fig1, fig2

if __name__ == "__main__":
    app.run(debug=True)
