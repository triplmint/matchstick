"""Matchstick game with Dash."""
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, callback, dcc, html

# Statistical fluctuation size
low_roll = 1
high_roll = 7
avg_roll = 3.5
# avg_roll = np.average([low_roll, (high_roll - 1)])

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
quota_offset0 = [0]
quota_offset1 = [0]
quota_offset2 = [0]
quota_offset3 = [0]

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


def quota_fig(data):
    fig = px.scatter(data, color_discrete_sequence=["purple"])
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    fig.update_layout(showlegend=False)
    return fig


# Build the button and figure rows
button_row = []
avgs_row = []
quota_row = []
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
    avgs_row.append(
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
    quota_row.append(
        dbc.Col(
            [
                dbc.Row(
                    [
                        html.Div(
                            dcc.Graph(figure=quota_fig(quota_offset0)),
                            id=f"quota_fig{num}",
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
                    f"Each work center can do between {low_roll} and {6} units of work.\n "
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
        html.Div(
            dbc.Button(
                "Run all workcenters",
                color="info",
                className="me-1",
                id="run_all",
            ),
            className="text-center",
        ),
        html.Div(
            dbc.Accordion(
                [
                    dbc.AccordionItem([dbc.Row(avgs_row)], title="Rolling Averages"),
                    dbc.AccordionItem([dbc.Row(quota_row)], title="Cummulative Quotas"),
                ],
                start_collapsed=True,
            )
        ),
    ]
)


def do_work(
    workcenter, previous_workcenter, performance, performance_avg, quota_offset
):
    """Do work on a workcenter and update the values."""
    new_roll = np.random.randint(low_roll, high_roll)
    if not isinstance(previous_workcenter, pd.DataFrame):
        work_done = new_roll
    else:
        # Only can pull inventory from previous workcenter if there is enough inventory there
        if new_roll <= previous_workcenter["inventory"][0]:
            work_done = new_roll
        else:
            work_done = previous_workcenter["inventory"][0]

        previous_workcenter["inventory"] -= work_done

    workcenter["inventory"] += work_done
    performance.append(work_done)
    performance_avg.append(np.average(performance))

    # The quotas are cummulative, so add the offset to the old value
    old_quota_value = quota_offset[-1]
    quota_offset.append(old_quota_value + (performance[-1] - avg_roll))

    return new_roll, work_done


@callback(
    Output("workcenter0", "children"),
    Output("work_value0", "children"),
    Output("performance_fig0", "children"),
    Output("quota_fig0", "children"),
    Output("work_button0", "disabled"),
    Output("work_button1", "disabled"),
    Input("work_button0", "n_clicks"),
    prevent_initial_call=True,
)
def dowork0(n_clicks):
    """Do some work at workcenter 0."""
    new_roll = None
    if n_clicks != 0:
        new_roll, work_done = do_work(
            workcenter0, None, performance0, performance0_avg, quota_offset0
        )
    return (
        dcc.Graph(
            figure=workcenter_fig(workcenter0),
        ),
        f"Rolled {new_roll}, did {work_done} unit(s) of work"
        if new_roll is not None
        else None,
        dcc.Graph(figure=workcenter_stats(performance0_avg)),
        dcc.Graph(figure=quota_fig(quota_offset0)),
        True,
        False,
    )


@callback(
    Output("workcenter0", "children", allow_duplicate=True),
    Output("workcenter1", "children"),
    Output("work_value1", "children"),
    Output("transfer_value0", "children"),
    Output("performance_fig1", "children"),
    Output("quota_fig1", "children"),
    Output("work_button1", "disabled", allow_duplicate=True),
    Output("work_button2", "disabled"),
    Input("work_button1", "n_clicks"),
    prevent_initial_call=True,
)
def dowork1(n_clicks):
    """Do some work at workcenter 1."""
    new_roll = None
    if n_clicks != 0:
        new_roll, work_done = do_work(
            workcenter1, workcenter0, performance1, performance1_avg, quota_offset1
        )

    return (
        dcc.Graph(figure=workcenter_fig(workcenter0)),
        dcc.Graph(figure=workcenter_fig(workcenter1)),
        f"Rolled {new_roll}, did {work_done} unit(s) of work"
        if new_roll is not None
        else None,
        f"Transfered {work_done} -->" if new_roll is not None else None,
        dcc.Graph(figure=workcenter_stats(performance1_avg)),
        dcc.Graph(figure=quota_fig(quota_offset1)),
        True,
        False,
    )


@callback(
    Output("workcenter1", "children", allow_duplicate=True),
    Output("workcenter2", "children"),
    Output("work_value2", "children"),
    Output("transfer_value1", "children"),
    Output("performance_fig2", "children"),
    Output("quota_fig2", "children"),
    Output("work_button2", "disabled", allow_duplicate=True),
    Output("work_button3", "disabled"),
    Input("work_button2", "n_clicks"),
    prevent_initial_call=True,
)
def dowork2(n_clicks):
    """Do some work in workcenter 2."""
    new_roll = None
    if n_clicks != 0:
        new_roll, work_done = do_work(
            workcenter2, workcenter1, performance2, performance2_avg, quota_offset2
        )
    return (
        dcc.Graph(figure=workcenter_fig(workcenter1)),
        dcc.Graph(figure=workcenter_fig(workcenter2)),
        f"Rolled {new_roll}, did {work_done} unit(s) of work"
        if new_roll is not None
        else None,
        f"Transfered {work_done} -->" if new_roll is not None else None,
        dcc.Graph(figure=workcenter_stats(performance2_avg)),
        dcc.Graph(figure=quota_fig(quota_offset2)),
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
    Output("quota_fig3", "children"),
    Output("work_button3", "disabled", allow_duplicate=True),
    Output("work_button0", "disabled", allow_duplicate=True),
    Input("work_button3", "n_clicks"),
    prevent_initial_call=True,
)
def dowork3(n_clicks):
    """Do some work at workcenter 3."""
    new_roll = None
    if n_clicks != 0:
        new_roll, work_done = do_work(
            workcenter3, workcenter2, performance3, performance3_avg, quota_offset3
        )

    return (
        dcc.Graph(figure=workcenter_fig(workcenter2)),
        dcc.Graph(figure=completed_fig(workcenter3)),
        f"Rolled {new_roll}, did {work_done} unit(s) of work"
        if new_roll is not None
        else None,
        f"Transfered {work_done} -->" if new_roll is not None else None,
        f"Completed {work_done} unit(s)!" if new_roll is not None else None,
        dcc.Graph(figure=completed_stats(performance3_avg)),
        dcc.Graph(figure=quota_fig(quota_offset3)),
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
    Output("quota_fig0", "children", allow_duplicate=True),
    Output("quota_fig1", "children", allow_duplicate=True),
    Output("quota_fig2", "children", allow_duplicate=True),
    Output("quota_fig3", "children", allow_duplicate=True),
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

        performance0.clear()
        performance1.clear()
        performance2.clear()
        performance3.clear()
        performance0_avg.clear()
        performance1_avg.clear()
        performance2_avg.clear()
        performance3_avg.clear()

        quota_offset0.clear()
        quota_offset1.clear()
        quota_offset2.clear()
        quota_offset3.clear()
        quota_offset0.append(0)
        quota_offset1.append(0)
        quota_offset2.append(0)
        quota_offset3.append(0)

    return (
        dcc.Graph(figure=workcenter_fig(workcenter0)),
        dcc.Graph(figure=workcenter_fig(workcenter1)),
        dcc.Graph(figure=workcenter_fig(workcenter2)),
        dcc.Graph(figure=completed_fig(workcenter3)),
        dcc.Graph(figure=workcenter_stats(performance0_avg)),
        dcc.Graph(figure=workcenter_stats(performance1_avg)),
        dcc.Graph(figure=workcenter_stats(performance2_avg)),
        dcc.Graph(figure=completed_stats(performance3_avg)),
        dcc.Graph(figure=quota_fig(quota_offset0)),
        dcc.Graph(figure=quota_fig(quota_offset1)),
        dcc.Graph(figure=quota_fig(quota_offset2)),
        dcc.Graph(figure=quota_fig(quota_offset3)),
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


@callback(
    Output("workcenter0", "children", allow_duplicate=True),
    Output("workcenter1", "children", allow_duplicate=True),
    Output("workcenter2", "children", allow_duplicate=True),
    Output("workcenter3", "children", allow_duplicate=True),
    Output("performance_fig0", "children", allow_duplicate=True),
    Output("performance_fig1", "children", allow_duplicate=True),
    Output("performance_fig2", "children", allow_duplicate=True),
    Output("performance_fig3", "children", allow_duplicate=True),
    Output("quota_fig0", "children", allow_duplicate=True),
    Output("quota_fig1", "children", allow_duplicate=True),
    Output("quota_fig2", "children", allow_duplicate=True),
    Output("quota_fig3", "children", allow_duplicate=True),
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
    Input("run_all", "n_clicks"),
    prevent_initial_call=True,
)
def run_all(n_clicks):
    """Run all the workcenters at once"""
    new_roll0, work_done0 = do_work(
        workcenter0, None, performance0, performance0_avg, quota_offset0
    )
    new_roll1, work_done1 = do_work(
        workcenter1, workcenter0, performance1, performance1_avg, quota_offset1
    )
    new_roll2, work_done2 = do_work(
        workcenter2, workcenter1, performance2, performance2_avg, quota_offset2
    )
    new_roll3, work_done3 = do_work(
        workcenter3, workcenter2, performance3, performance3_avg, quota_offset3
    )

    return (
        dcc.Graph(figure=workcenter_fig(workcenter0)),
        dcc.Graph(figure=workcenter_fig(workcenter1)),
        dcc.Graph(figure=workcenter_fig(workcenter2)),
        dcc.Graph(figure=completed_fig(workcenter3)),
        dcc.Graph(figure=workcenter_stats(performance0_avg)),
        dcc.Graph(figure=workcenter_stats(performance1_avg)),
        dcc.Graph(figure=workcenter_stats(performance2_avg)),
        dcc.Graph(figure=completed_stats(performance3_avg)),
        dcc.Graph(figure=quota_fig(quota_offset0)),
        dcc.Graph(figure=quota_fig(quota_offset1)),
        dcc.Graph(figure=quota_fig(quota_offset2)),
        dcc.Graph(figure=quota_fig(quota_offset3)),
        f"Rolled {new_roll0},did {work_done0} unit(s) of work",
        f"Rolled {new_roll1},did {work_done1} unit(s) of work",
        f"Rolled {new_roll2},did {work_done2} unit(s) of work",
        f"Rolled {new_roll3},did {work_done3} unit(s) of work",
        f"Transfered {work_done1} -->",
        f"Transfered {work_done2} -->",
        f"Transfered {work_done3} -->",
        f"Completed {work_done3} unit(s)!",
        False,
        True,
        True,
        True,
    )


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
