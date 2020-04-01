# Coronavirus Plots

# %% Imports
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
counties[(counties.state == "Georgia") & (counties.date == latest_date)].sort_values(
    "deaths", ascending=False
).head(10)

# %% Add state to county
counties["county"] = counties.apply(lambda x: f"{x['state']} - {x['county']}", axis=1)

# %% Plot over time


def plot_over_time(
    df, geo, stat, n_geo=11, n_date=10, latest_date=latest_date, geo_to_rm=None
):

    """ 
    Generate line plot of cases or deaths reported in top states or counties  
    """

    plt.style.use("seaborn-whitegrid")

    # Get top states or counties on latest date
    geo_list = list(
        df[df.date == latest_date].sort_values(stat, ascending=False).head(n_geo)[geo]
    )
    if geo_to_rm:
        for g in geo_to_rm:
            geo_list.remove(g)
        n_geo = n_geo - len(geo_to_rm)

    # Get most recent dates
    date_list = df.date.sort_values(ascending=False).unique()[0:n_date]

    # Make wide table
    df_wide = (
        df[df[geo].isin(geo_list) & df.date.isin(date_list)]
        .pivot(index="date", columns=geo, values=stat)
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

    plot_title = f"Number of Reported {stat.title()} by {geo.title()}"
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

    plt.xticks(ticks=np.arange(n_date), labels=reversed(date_list))

    # Make legend
    patches, labels = ax.get_legend_handles_labels()
    patches_dict = dict(zip(labels, patches))
    new_patches = []
    for _, g in enumerate(geo_list):
        new_patches.append(patches_dict[g])
    ax.legend(new_patches, geo_list, loc="best")
    ax.set_xlabel("Date")
    ax.set_ylabel(f"Reported {stat.title()}")

    plt.text(5, 0, "Source: NYT https://github.com/nytimes/covid-19-data")

    plt.savefig(f"plots/{geo}_{stat}.png", bbox_inches="tight")

    return plt.show()


# %% State Plots
states_to_rm = ["New York"]
plot_over_time(df=states, geo="state", stat="cases", geo_to_rm=states_to_rm)

plot_over_time(df=states, geo="state", stat="deaths", geo_to_rm=states_to_rm)

# %% County Plots
counties_to_rm = ["New York - New York City"]
plot_over_time(
    df=counties, geo="county", stat="cases", n_geo=11, geo_to_rm=counties_to_rm
)

counties_to_rm = ["New York - New York City", "Washington - King"]
plot_over_time(
    df=counties, geo="county", stat="deaths", n_geo=12, geo_to_rm=counties_to_rm
)


# %%
