# Coronavirus Plots

# %% Imports
from datetime import datetime
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

counties = pd.read_csv("us-counties.csv")
states = pd.read_csv("us-states.csv")

# %% Get latest date
latest_date = states.date.sort_values(ascending=True).tail(1).values[0]
print(f"Latest date in data set: {latest_date}")

# %% States with the most deaths
states[states.date == latest_date].sort_values("deaths", ascending=False).head(10)

# %% Counties with the most deaths
counties[counties.date == latest_date].sort_values("deaths", ascending=False).head(10)

# %% Unknown counties are people whose residence isn't known yet
counties[(counties.county == "Unknown") & (counties.date == latest_date)].sort_values(
    "deaths", ascending=False
).head(10)

# %% Remove unknown counties
counties = counties[counties.county != "Unknown"]

# %% Add state to county
counties["county"] = counties.apply(lambda x: f"{x['state']} - {x['county']}", axis=1)

# %% Plot over time


def plot_over_time(
    df, geo, stat, n_geo=11, n_date=6, latest_date=latest_date, geo_to_rm=None
):

    """ 
    Generate line plot of cases or deaths reported in top states or counties  
    """

    plt.style.use("seaborn-whitegrid")

    # Get most recent dates
    date_list = df.date.sort_values(ascending=False).unique()[0 : (n_date * 7)]

    # New cases / deaths
    df[f"new_cases"] = df.groupby([geo])["cases"].diff(periods=7)
    df[f"new_deaths"] = df.groupby([geo])["deaths"].diff(periods=7)
    today_weekday = datetime.strptime(latest_date, "%Y-%m-%d").strftime("%A")
    df["day_of_week"] = pd.to_datetime(df["date"]).dt.day_name()
    df = df[df.day_of_week == today_weekday]

    # Get top states or counties by new cases in last week
    geo_list = list(
        df[df.date == latest_date]
        .sort_values("new_cases", ascending=False)
        .head(n_geo)[geo]
    )
    if geo_to_rm:
        for g in geo_to_rm:
            geo_list.remove(g)
        n_geo = n_geo - len(geo_to_rm)

    # Make wide table
    df_wide = (
        df[df[geo].isin(geo_list) & df.date.isin(date_list)]
        .pivot(index="date", columns=geo, values=f"new_{stat}")
        .fillna(0)
    )

    # Line chart
    marker_list = ["o", "v", "^", "<", ">", "s", "P", "D", "H", "X"]

    fig, ax = plt.subplots()
    cm = plt.get_cmap("tab10")

    ax.set_prop_cycle(
        color=[cm(1.0 * i / n_geo) for i in range(n_geo)],
        marker=[marker_list[i] for i in range(n_geo)],
    )

    plot_title = f"Number of Reported {stat.title()} Each Week by {geo.title()}"
    if geo_to_rm:
        geo_except = geo_to_rm.copy()
        if len(geo_except) > 1:
            geo_except[-1] = f"and {geo_except[-1]}"
        sep = ", " if len(geo_except) > 2 else " "
        plot_title = f"{plot_title}\n(excluding {sep.join(geo_except)})"

    df_wide.plot(
        kind="line",
        figsize=(10, 8),
        ax=ax,
        legend=False,
        title=plot_title,
        lw=2,
        ms=10,
    )

    # Make legend
    patches, labels = ax.get_legend_handles_labels()
    patches_dict = dict(zip(labels, patches))
    new_patches = []
    for g in geo_list:
        new_patches.append(patches_dict[g])
    ax.legend(new_patches, geo_list, loc="upper left")
    ax.set_ylim(ymin=0)
    ax.set_xlabel("Date")
    ax.set_ylabel(f"Reported {stat.title()} in the Last Seven Days")

    plt.text(
        2.8,
        ax.get_ylim()[1] * -0.07,
        "Source: NYT https://github.com/nytimes/covid-19-data",
    )

    plt.savefig(f"plots/{geo}_{stat}.png", bbox_inches="tight")

    # return plt.show()
    return


# %% State Plots
states_to_rm = []
plot_over_time(
    df=states,
    geo="state",
    stat="cases",
    n_geo=10 + len(states_to_rm),
    # geo_to_rm=states_to_rm,
)

plot_over_time(
    df=states,
    geo="state",
    stat="deaths",
    n_geo=10 + len(states_to_rm),
    # geo_to_rm=states_to_rm,
)

# %% County Plots
counties_to_rm = []
plot_over_time(
    df=counties,
    geo="county",
    stat="cases",
    n_geo=10 + len(counties_to_rm),
    # geo_to_rm=counties_to_rm,
)

plot_over_time(
    df=counties,
    geo="county",
    stat="deaths",
    n_geo=10 + len(counties_to_rm),
    # geo_to_rm=counties_to_rm,
)


# %%
