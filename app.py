"""Matchstick game with Dash."""
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, callback, dcc, html

# Statistical fluctuation size
low_roll = 1
high_roll = 6

# Workcenter Data
workcenters = []
total_workcenters = 4
workcenter0 = pd.DataFrame({"inventory": [0]})
workcenter1 = pd.DataFrame({"inventory": [0]})
workcenter2 = pd.DataFrame({"inventory": [0]})
workcenter3 = pd.DataFrame({"inventory": [0]})
workcenters = [workcenter0, workcenter1, workcenter2, workcenter3]

performance0 = []
performance1 = []
performance2 = []
performance3 = []
performance0_avg = []
performance1_avg = []
performance2_avg = []
performance3_avg = []

# Initialize the app - incorporate a Dash Bootstrap theme
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = Dash(__name__, external_stylesheets=external_stylesheets)


def workcenter_fig(data):
    """Standardize workcenter figure data."""
    fig = px.bar(data, y="inventory")
    fig.update_xaxes(showticklabels=False)
    fig.update_xaxes(title=None)
    fig.update_yaxes(range=[0, 40])
    return fig


def completed_fig(data):
    """Create special figure for showing completed work units."""
    fig = px.bar(data, y="inventory", color_discrete_sequence=["green"])
    fig.update_xaxes(showticklabels=False, title=None)
    fig.update_yaxes(range=[0, 200], title_text="completed")
    return fig


def workcenter_stats(data):
    """Create a line chart of workcenter statistics."""
    fig = px.line(data, color_discrete_sequence=["purple"])
    fig.update_xaxes(title=None)
    fig.update_yaxes(range=[low_roll, high_roll], title=None)
    fig.update_layout(showlegend=False)
    return fig


def completed_stats(data):
    """Create a special line chart of completion statistics."""
    fig = px.line(data, color_discrete_sequence=["red"])
    fig.update_xaxes(title=None)
    fig.update_yaxes(range=[low_roll, high_roll], title=None)
    fig.update_layout(showlegend=False)
    return fig


# Build the button and figure rows
button_row = []
stats_row = []
for num, workcenter in enumerate(workcenters):
    button_row.append(
        dbc.Col(
            [
                dbc.Row(
                    [
                        html.Div(
                            dcc.Graph(
                                figure=completed_fig(workcenter3)
                                if num == 3
                                else workcenter_fig(workcenter0),
                            ),
                            id=f"workcenter{num}",
                        )
                    ]
                ),
                html.Div(
                    [
                        dbc.Button(
                            "Do Work",
                            color="primary",
                            className="me-2",
                            id=f"work_button{num}",
                            n_clicks=0,
                            disabled=False if num == 0 else True,
                        ),
                    ],
                    className="text-center",
                ),
                dbc.Row(
                    [html.Div(id=f"work_value{num}", className="text-center")],
                    align="end",
                ),
                dbc.Row(
                    [html.Div(id=f"transfer_value{num}", className="text-center")],
                    align="end",
                ),
            ],
            width=3,
        )
    )
    stats_row.append(
        dbc.Col(
            [
                dbc.Row(
                    [
                        html.Div(
                            dcc.Graph(
                                figure=completed_stats(performance0)
                                if num == 3
                                else workcenter_stats(performance0),
                            ),
                            id=f"performance_fig{num}",
                        )
                    ]
                ),
            ],
            width=3,
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
                    f"Each work center can do between {low_roll} and {high_roll} units of work.\n "
                    "However, work can only be passed down the line if there is enough inventory in the previous work center.\n"
                    "This is a 'perfectly balanced' system. Line balancing would tell us that the average throughput should be 3.5 units per cycle.\n"
                    "Is this what happens?\n",
                    className="text-center",
                ),
            ],
        ),
        html.Div(
            dbc.Button("Reset", color="danger", className="me-1", id="reset_button"),
            className="text-center",
        ),
        dbc.Row(button_row),
        # html.Div(
        #     dbc.Button(
        #         "Run all workcenters",
        #         color="info",
        #         className="me-1",
        #         id="iterate_button",
        #     ),
        #     className="text-center",
        # ),
        html.Div(
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P("Rolling Averages", className="text-center"),
                            dbc.Row(stats_row),
                        ],
                        title="Workcenter Stats",
                    )
                ],
                start_collapsed=True,
            )
        ),
    ]
)


@callback(
    Output("workcenter0", "children"),
    Output("work_value0", "children"),
    Output("performance_fig0", "children"),
    Output("work_button0", "disabled"),
    Output("work_button1", "disabled"),
    Input("work_button0", "n_clicks"),
    prevent_initial_call=True,
)
def dowork0(n_clicks):
    """Do some work at workcenter 0."""
    new_roll = None
    if n_clicks != 0:
        new_roll = np.random.randint(low_roll, high_roll)
        workcenter0["inventory"] += new_roll

    performance0.append(new_roll)
    performance0_avg.append(np.average(performance0))

    return (
        dcc.Graph(
            figure=workcenter_fig(workcenter0),
        ),
        f"Rolled {new_roll} unit(s) of work" if new_roll is not None else None,
        dcc.Graph(figure=workcenter_stats(performance0_avg)),
        True,
        False,
    )


@callback(
    Output("workcenter0", "children", allow_duplicate=True),
    Output("workcenter1", "children"),
    Output("work_value1", "children"),
    Output("transfer_value0", "children"),
    Output("performance_fig1", "children"),
    Output("work_button1", "disabled", allow_duplicate=True),
    Output("work_button2", "disabled"),
    Input("work_button1", "n_clicks"),
    prevent_initial_call=True,
)
def dowork1(n_clicks):
    """Do some work at workcenter 1."""
    new_roll = None
    if n_clicks != 0:
        new_roll = np.random.randint(low_roll, high_roll)

        # Only can pull inventory from workcenter 1 if there is enough inventory there
        if new_roll <= workcenter0["inventory"][0]:
            transfer = new_roll
        else:
            transfer = workcenter0["inventory"][0]

        workcenter1["inventory"] += transfer
        workcenter0["inventory"] -= transfer
        performance1.append(transfer)
        performance1_avg.append(np.average(performance1))

    return (
        dcc.Graph(figure=workcenter_fig(workcenter0)),
        dcc.Graph(figure=workcenter_fig(workcenter1)),
        f"Rolled {new_roll} unit(s) of work" if new_roll is not None else None,
        f"Transfered {transfer} -->" if new_roll is not None else None,
        dcc.Graph(figure=workcenter_stats(performance1_avg)),
        True,
        False,
    )


@callback(
    Output("workcenter1", "children", allow_duplicate=True),
    Output("workcenter2", "children"),
    Output("work_value2", "children"),
    Output("transfer_value1", "children"),
    Output("performance_fig2", "children"),
    Output("work_button2", "disabled", allow_duplicate=True),
    Output("work_button3", "disabled"),
    Input("work_button2", "n_clicks"),
    prevent_initial_call=True,
)
def dowork2(n_clicks):
    """Do some work in workcenter 2."""
    new_roll = None
    if n_clicks != 0:
        new_roll = np.random.randint(low_roll, high_roll)

        # Only can pull inventory from workcenter 1 if there is enough inventory there
        if new_roll <= workcenter1["inventory"][0]:
            transfer = new_roll
        else:
            transfer = workcenter1["inventory"][0]

        workcenter2["inventory"] += transfer
        workcenter1["inventory"] -= transfer
        performance2.append(transfer)
        performance2_avg.append(np.average(performance2))

    return (
        dcc.Graph(figure=workcenter_fig(workcenter1)),
        dcc.Graph(figure=workcenter_fig(workcenter2)),
        f"Rolled {new_roll} unit(s) of work" if new_roll is not None else None,
        f"Transfered {transfer} -->" if new_roll is not None else None,
        dcc.Graph(figure=workcenter_stats(performance2_avg)),
        True,
        False,
    )


@callback(
    Output("workcenter2", "children", allow_duplicate=True),
    Output("workcenter3", "children"),
    Output("work_value3", "children"),
    Output("transfer_value2", "children"),
    Output("transfer_value3", "children"),
    Output("performance_fig3", "children"),
    Output("work_button3", "disabled", allow_duplicate=True),
    Output("work_button0", "disabled", allow_duplicate=True),
    Input("work_button3", "n_clicks"),
    prevent_initial_call=True,
)
def dowork3(n_clicks):
    """Do some work at workcenter 3."""
    new_roll = None
    if n_clicks != 0:
        new_roll = np.random.randint(low_roll, high_roll)

        # Only can pull inventory from workcenter 1 if there is enough inventory there
        if new_roll <= workcenter2["inventory"][0]:
            transfer = new_roll
        else:
            transfer = workcenter2["inventory"][0]

        workcenter3["inventory"] += transfer
        workcenter2["inventory"] -= transfer
        performance3.append(transfer)
        performance3_avg.append(np.average(performance3))

    return (
        dcc.Graph(figure=workcenter_fig(workcenter2)),
        dcc.Graph(figure=completed_fig(workcenter3)),
        f"Rolled {new_roll} unit(s) of work" if new_roll is not None else None,
        f"Transfered {transfer} -->" if new_roll is not None else None,
        f"Completed {transfer} unit(s)!" if new_roll is not None else None,
        dcc.Graph(figure=completed_stats(performance3_avg)),
        True,
        False,
    )


@callback(
    Output("workcenter0", "children", allow_duplicate=True),
    Output("workcenter1", "children", allow_duplicate=True),
    Output("workcenter2", "children", allow_duplicate=True),
    Output("workcenter3", "children", allow_duplicate=True),
    Output("performance_fig0", "children", allow_duplicate=True),
    Output("performance_fig1", "children", allow_duplicate=True),
    Output("performance_fig2", "children", allow_duplicate=True),
    Output("performance_fig3", "children", allow_duplicate=True),
    Output("work_value0", "children", allow_duplicate=True),
    Output("work_value1", "children", allow_duplicate=True),
    Output("work_value2", "children", allow_duplicate=True),
    Output("work_value3", "children", allow_duplicate=True),
    Output("transfer_value0", "children", allow_duplicate=True),
    Output("transfer_value1", "children", allow_duplicate=True),
    Output("transfer_value2", "children", allow_duplicate=True),
    Output("transfer_value3", "children", allow_duplicate=True),
    Output("work_button0", "disabled", allow_duplicate=True),
    Output("work_button1", "disabled", allow_duplicate=True),
    Output("work_button2", "disabled", allow_duplicate=True),
    Output("work_button3", "disabled", allow_duplicate=True),
    Input("reset_button", "n_clicks"),
    prevent_initial_call=True,
)
def reset(n_clicks):
    """Reset all the work values and text."""
    if n_clicks != 0:
        for workcenter in workcenters:
            workcenter["inventory"] = 0

        performance0 = []
        performance1 = []
        performance2 = []
        performance3 = []
        performance0_avg = []
        performance1_avg = []
        performance2_avg = []
        performance3_avg = []

    return (
        dcc.Graph(figure=workcenter_fig(workcenter0)),
        dcc.Graph(figure=workcenter_fig(workcenter1)),
        dcc.Graph(figure=workcenter_fig(workcenter2)),
        dcc.Graph(figure=completed_fig(workcenter3)),
        dcc.Graph(figure=workcenter_stats(performance0_avg)),
        dcc.Graph(figure=workcenter_stats(performance1_avg)),
        dcc.Graph(figure=workcenter_stats(performance2_avg)),
        dcc.Graph(figure=completed_stats(performance3_avg)),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        False,
        True,
        True,
        True,
    )


# @callback(
#     Output("work_button0", "n_clicks"),
#     Output("work_button1", "n_clicks"),
#     Output("work_button2", "n_clicks"),
#     Output("work_button3", "n_clicks"),
#     Input("iterate_button", "n_clicks"),
#     prevent_initial_call=True,
# )
# def iterate(n_clicks):
#     """Iterate a multiple times through the workcenters."""
#     if n_clicks != 0:
#         return (1, 1, 1, 1)
#     return (0, 0, 0, 0)


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
