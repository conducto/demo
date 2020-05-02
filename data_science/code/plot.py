import collections, json, re
import click
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import numpy as np
import conducto as co


# Data is downloaded from the United States Energy Information Administration.
# https://www.eia.gov/opendata/bulkfiles.php


@click.command()
@click.option("--dataset", required=True, help="dataset name")
def plot(dataset):
    """
    Read in the downloaded data, extract the specified datasets, and plot them.
    """
    data_text = co.data.user.gets("steo-data")
    all_data = [json.loads(line) for line in data_text.splitlines()]

    DATASETS = {
        "heating"   : r"^STEO.ZWHD_[^_]*\.M$",
        "cooling"   : r"^STEO.ZWCD_[^_]*.M$",
    }

    regex = DATASETS[dataset]
    subset_data = [d for d in all_data if "series_id" in d and re.search(regex, d["series_id"])]

    # Create a pandas DataFrame with the data grouped by month of the year.
    # This could be implemented with vectorized pandas logic but this data
    # is small enough not to worry.
    data = {}
    for i, d in enumerate(subset_data):
        by_month = collections.defaultdict(list)
        for yyyymm, value in d["data"]:
            month = int(yyyymm[-2:])
            by_month[month].append(value)
        y = [np.mean(by_month[month]) for month in range(1, 13)]
        data[d['name']] = y

    df = pd.DataFrame(data=data)
    df["Month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    df.set_index("Month", inplace=True)

    # Graph each dataset as one line on a single plot.
    colors = [cm.viridis(z) for z in np.linspace(0, .99, len(subset_data))]
    for i, column in enumerate(df.columns):
        y = df[column].values
        plt.plot(y, label=column, color=colors[i])
    plt.title(f"{dataset}, average by month")
    plt.legend(loc="best", fontsize="x-small")

    # Save to disk, and then to co.data.pipeline for url.
    filename = "/tmp/image.png"
    dataname = f"conducto/demo/data_science/{dataset}.png"
    plt.savefig(filename)
    co.data.pipeline.put(dataname, filename)

    # Print out results as markdown
    print(f"""<ConductoMarkdown>
![img]({co.data.pipeline.url(dataname)})

{df.transpose().round(2).to_markdown()}
</ConductoMarkdown>""")


if __name__ == "__main__":
    plot()
