"""Matchstick game with Dash."""
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, callback, dcc, html

# Workcenter Data
# workcenter = pd.DataFrame(columns=["", "inventory"])
workcenters = []
total_workcenters = 4
workcenter0 = pd.DataFrame({"inventory": [0]})
workcenter1 = pd.DataFrame({"inventory": [0]})
workcenter2 = pd.DataFrame({"inventory": [0]})
workcenter3 = pd.DataFrame({"inventory": [0]})
workcenters = [workcenter0, workcenter1, workcenter2, workcenter3]

# Initialize the app - incorporate a Dash Bootstrap theme
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = Dash(__name__, external_stylesheets=external_stylesheets)


def workcenter_fig(data):
    """Standardize workcenter figure data."""
    fig = px.bar(data, y="inventory")
    fig.update_xaxes(showticklabels=False)
    fig.update_xaxes(title=None)
    fig.update_yaxes(range=[0, 50])

    return fig


# Build the button and figure rows
button_row = []
for num in range(total_workcenters):
    button_row.append(
        dbc.Col(
            [
                html.Div(
                    [
                        dbc.Button(
                            "Do Work",
                            color="primary",
                            className="me-2",
                            id=f"work{num}",
                            n_clicks=0,
                            disabled=False if num == 0 else True,
                        ),
                    ],
                    className="text-center",
                ),
                dbc.Row(
                    [
                        html.Div(
                            dcc.Graph(
                                figure=workcenter_fig(workcenter0),
                            ),
                            id=f"workcenter{num}",
                        )
                    ]
                ),
                dbc.Row(
                    [html.Div(id=f"work_value{num}", className="text-center")],
                    align="end",
                ),
            ]
        )
    )

# App layout
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                html.Div(
                    "Dependent Events and Statistical Fluctuations",
                    className="text-primary text-center fs-3",
                ),
                html.Div(
                    "Each work center can 'do' between 1 and 6 units of work. However, work can only be passed down the line if there is enough inventory in the previous work center.",
                    className="text-center",
                ),
            ]
        ),
        dbc.Row(button_row),
    ]
)


@callback(
    Output("workcenter0", "children"),
    Output("work_value0", "children"),
    Output("work0", "disabled"),
    Output("work1", "disabled"),
    Input("work0", "n_clicks"),
    prevent_initial_call=True,
)
def work0(n):
    """Do some work at workcenter 0."""
    new_roll = None
    if n != 0:
        new_roll = np.random.randint(1, 7)
        workcenter0["inventory"] += new_roll

    return (
        dcc.Graph(
            figure=workcenter_fig(workcenter0),
        ),
        f"Did {new_roll} unit(s) of work" if new_roll is not None else None,
        True,
        False,
    )


@callback(
    Output("workcenter0", "children", allow_duplicate=True),
    Output("workcenter1", "children"),
    Output("work_value1", "children"),
    Output("work1", "disabled", allow_duplicate=True),
    Output("work2", "disabled"),
    Input("work1", "n_clicks"),
    prevent_initial_call=True,
)
def work1(n):
    """Do some work at workcenter 1."""
    new_roll = None
    if n != 0:
        new_roll = np.random.randint(1, 7)

        # Only can pull inventory from workcenter 1 if there is enough inventory there
        if new_roll <= workcenter0["inventory"][0]:
            workcenter1["inventory"] += new_roll
            workcenter0["inventory"] -= new_roll
        else:
            workcenter1["inventory"] = workcenter0["inventory"]
            workcenter0["inventory"] = 0

    return (
        dcc.Graph(figure=workcenter_fig(workcenter0)),
        dcc.Graph(figure=workcenter_fig(workcenter1)),
        f"Did {new_roll} unit(s) of work" if new_roll is not None else None,
        True,
        False,
    )


@callback(
    Output("workcenter1", "children", allow_duplicate=True),
    Output("workcenter2", "children"),
    Output("work_value2", "children"),
    Output("work2", "disabled", allow_duplicate=True),
    Output("work3", "disabled"),
    Input("work2", "n_clicks"),
    prevent_initial_call=True,
)
def work2(n):
    """Do some work in workcenter 2."""
    new_roll = None
    if n != 0:
        new_roll = np.random.randint(1, 7)

        # Only can pull inventory from workcenter 1 if there is enough inventory there
        if new_roll <= workcenter1["inventory"][0]:
            workcenter2["inventory"] += new_roll
            workcenter1["inventory"] -= new_roll
        else:
            workcenter2["inventory"] = workcenter0["inventory"]
            workcenter1["inventory"] = 0

    return (
        dcc.Graph(figure=workcenter_fig(workcenter1)),
        dcc.Graph(figure=workcenter_fig(workcenter2)),
        f"Did {new_roll} unit(s) of work" if new_roll is not None else None,
        True,
        False,
    )


@callback(
    Output("workcenter2", "children", allow_duplicate=True),
    Output("workcenter3", "children"),
    Output("work_value3", "children"),
    Output("work3", "disabled", allow_duplicate=True),
    Output("work0", "disabled", allow_duplicate=True),
    Input("work3", "n_clicks"),
    prevent_initial_call=True,
)
def work3(n):
    """Do some work at workcenter 3."""
    new_roll = None
    if n != 0:
        new_roll = np.random.randint(1, 7)

        # Only can pull inventory from workcenter 1 if there is enough inventory there
        if new_roll <= workcenter3["inventory"][0]:
            workcenter3["inventory"] += new_roll
            workcenter2["inventory"] -= new_roll
        else:
            workcenter3["inventory"] = workcenter0["inventory"]
            workcenter2["inventory"] = 0

    return (
        dcc.Graph(figure=workcenter_fig(workcenter2)),
        dcc.Graph(figure=workcenter_fig(workcenter3)),
        f"Did {new_roll} unit(s) of work" if new_roll is not None else None,
        True,
        False,
    )


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
