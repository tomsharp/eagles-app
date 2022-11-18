import pandas as pd
import plotly.express as px
import plotly.graph_objs as go


def convert_multi_index_col(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [f"{c[0]}, {c[1]}" for c in df.columns]
    return df


def read_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    columns = [(c.split(", ")[0], c.split(", ")[1]) for c in df.columns]
    df.columns = pd.MultiIndex.from_tuples(columns)
    return df


def get_data(team_abbrev: str, year: int) -> pd.DataFrame:
    return read_data(f"{year}_{team_abbrev}_schedule_results.csv")


def get_comparison_figure(
    df1: pd.DataFrame, df2: pd.DataFrame, col, col_overwrite_name
) -> go.Figure:
    """Returns a bare-bones scatter plot comparing the cumulative metric in each of the two DFs passed.

    Note: To update the layout of the figure, use the ".update_layout" method on the returned object.
    See plotly docs for more details: https://plotly.com/python/reference/layout/
    """

    df1_season = df1["season"][0]
    df2_season = df2["season"][0]

    comparison_df = pd.DataFrame(
        {
            "Week": df1[("Unnamed: 0_level_0", "Week")].tolist(),
            df1_season: df1[col].cumsum(),
            df2_season: df2[col].cumsum(),
        }
    )
    comparison_df = comparison_df.melt(
        id_vars=["Week"], var_name="Team", value_name=col_overwrite_name
    )

    fig = px.line(
        comparison_df,
        x="Week",
        y=col_overwrite_name,
        color="Team",
        color_discrete_map={2017: "grey", 2022: "green"},
        markers=True,
    )
    # fig.update_layout(
    #     paper_bgcolor='rgba(255,255,255,255)',
    #     plot_bgcolor='rgba(255,255,255,255)'
    # )
    return fig
