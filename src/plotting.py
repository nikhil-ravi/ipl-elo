import plotly.graph_objects as go
import pandas as pd

from .constants import TEAM_COLORS, DEFUNCT_TEAMS


def get_dt_breaks(team_elo):
    # build complete timepline from start date to end date
    dt_all = pd.date_range(
        start=team_elo["Date"].iloc[0], end=team_elo["Date"].iloc[-1]
    )

    # retrieve the dates that ARE in the original datset
    dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(team_elo["Date"])]

    # define dates with missing values
    dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]

    return dt_breaks


def plot_elo_ratings(team_elo, ignore_defunct_teams=True):
    """
    Plot the Elo ratings for each team over time.
    """
    data = []
    for key, grp in team_elo.groupby("Team"):
        if ignore_defunct_teams and key in DEFUNCT_TEAMS:
            continue
        data.append(
            go.Scatter(
                x=grp["Date"],
                y=grp["Elo"],
                mode="lines",
                name=key,
                line=dict(color=TEAM_COLORS[key]),
            )
        )

    fig = go.Figure(data=data)
    fig.update_xaxes(
        rangebreaks=[dict(values=get_dt_breaks(team_elo=team_elo))]
    )  # hide dates with no values
    # for key, grp in team_elo.groupby("Season"):
    #     # retrieve the dates
    #     start = grp["Date"].iloc[0].strftime("%Y-%m-%d")
    #     end = grp["Date"].iloc[-1].strftime("%Y-%m-%d")

    #     # add shaded region
    #     fig.add_vrect(
    #         x0=start,
    #         x1=end,
    #         fillcolor="grey",
    #         opacity=0.25,
    #         line_width=0,
    #         annotation_text=key,
    #         annotation_position="top left",
    #         annotation=dict(textangle=-90),
    #     )
    # y log scale
    fig.update_yaxes(type="log")
    fig.update_layout(
        title="IPL Elo Ratings",
        xaxis_title="Date",
        yaxis_title="Elo Rating",
        legend_title="Team",
        font=dict(family="Courier New, monospace", size=12, color="#7f7f7f"),
        margin=dict(l=0, r=0, t=50, b=0),
        width=1000,
        height=600,
        hovermode="x",
        template="plotly_dark",
    )
    return fig
