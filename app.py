import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Dash, html, dcc, Output, Input
from utils import get_data, get_comparison_figure

# TODO - move to sys args
WEEK = 10
DEBUG = False

phi2017 = get_data("phi", 2017)
phi2022 = get_data("phi", 2022)

phi2017 = phi2017[:WEEK]
phi2022 = phi2022[:WEEK]

phi2017["point_diff"] = phi2017[("Score", "Tm")] - phi2017[("Score", "Opp")]
phi2022["point_diff"] = phi2022[("Score", "Tm")] - phi2022[("Score", "Opp")]


# comparison bar chart
# fill na to 0 to avoid edge case of bye week being last week in analysis
# TODO - remove this monkeypatch later
cumulative2017 = (
    phi2017[
        [
            ("Offense", "RushY"),
            ("Offense", "PassY"),
            ("Offense", "TotYd"),
            ("Score", "Tm"),
            ("Score", "Opp"),
            ("point_diff", ""),
        ]
    ]
    .fillna(0)
    .cumsum()
)
cumulative2017["season"] = 2017
cumulative2017["week"] = range(1, len(cumulative2017) + 1)
cumulative2022 = (
    phi2022[
        [
            ("Offense", "RushY"),
            ("Offense", "PassY"),
            ("Offense", "TotYd"),
            ("Score", "Tm"),
            ("Score", "Opp"),
            ("point_diff", ""),
        ]
    ]
    .fillna(0)
    .cumsum()
)
cumulative2022["season"] = 2022
cumulative2022["week"] = range(1, len(cumulative2022) + 1)

cumulative = pd.concat([cumulative2017, cumulative2022])
cumulative["week"] = cumulative["week"].astype(int)

# grab most recent week
cumulative = cumulative[cumulative["week"] == WEEK]

# rename cols
cumulative.columns = [
    c[1] if c[0] not in ["point_diff", "season", "week"] else c[0]
    for c in cumulative.columns
]
cumulative = cumulative.rename(columns={"Tm": "Points For", "Opp": "Points Against"})


data2017 = cumulative[cumulative["season"] == 2017].drop("week", axis=1)
data2022 = cumulative[cumulative["season"] == 2022].drop("week", axis=1)

x2017, y2017 = (
    data2017.melt(id_vars=["season"])["variable"],
    data2017.melt(id_vars=["season"])["value"],
)
x2022, y2022 = (
    data2022.melt(id_vars=["season"])["variable"],
    data2022.melt(id_vars=["season"])["value"],
)

fig = go.Figure(
    data=[
        go.Bar(name="2017", x=x2017, y=y2017, marker_color="grey"),
        go.Bar(name="2022", x=x2022, y=y2022, marker_color="green"),
    ]
)

fig.update_layout(
    barmode="group",
    title=f"Performance Comparison through Week {WEEK}",
    xaxis_title="Stat",
)


app = Dash(__name__)

app.layout = html.Div(
    children=[
        html.Div(
            className="container-xxl",
            children=[
                html.Div(
                    className="row bg-black text-white",
                    children=[
                        html.H1(children="Eagles Comparison Dashboard"),
                        html.Div(
                            children="""
                                Comparing the 2022 Philadelphia Eagles to the 2017 team
                            """
                        ),
                    ],
                ),
                html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className="col",
                            children=[
                                dcc.Graph(
                                    id="comparison-bar-graph",
                                    figure=fig,
                                    config={"displayModeBar": False},
                                )
                            ],
                        ),
                        html.Div(
                            className="col",
                            # FIXME
                            style={"margin-top": "25px"},
                            children=[
                                dcc.Graph(
                                    id="detailed-line-graph",
                                    config={"displayModeBar": False},
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="row justify-content-end",
                    children=[
                        html.Div(className="col-7"),
                        html.Div(
                            className="col",
                            children=[
                                dcc.Dropdown(
                                    [
                                        "Rush Yds",
                                        "Pass Yds",
                                        "Total Off. Yds",
                                        "Points For",
                                        "Points Against",
                                        "Point Diff",
                                    ],
                                    "Total Off. Yds",
                                    id="detailed-line-dropdown",
                                ),
                            ],
                        ),
                        html.Div(className="col-3"),
                    ],
                ),
            ],
        ),
    ]
)


@app.callback(
    Output("detailed-line-graph", "figure"), Input("detailed-line-dropdown", "value")
)
def update_output(value):
    if value is None:
        pass

    value_map = {
        "Rush Yds": ("Offense", "RushY"),
        "Pass Yds": ("Offense", "PassY"),
        "Total Off. Yds": ("Offense", "TotYd"),
        "Points For": ("Score", "Tm"),
        "Points Against": ("Score", "Opp"),
        "Point Diff": "point_diff",
    }

    col = value_map[value]
    fig = get_comparison_figure(phi2017, phi2022, col, f"Cumulative {value}")
    fig.update_layout(title="Week by Week Performance")
    return fig


if __name__ == "__main__":
    app.run_server(debug=DEBUG)
