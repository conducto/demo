import collections, conducto as co, json, re

# Data is downloaded from the United States Energy Information Administration.
# https://www.eia.gov/opendata/bulkfiles.php

PERM_DATA_PATH = "conducto/demo/data_science/steo.txt"

DOWNLOAD_COMMAND = f"""
echo "Downloading"
curl http://api.eia.gov/bulk/STEO.zip > steo.zip
unzip -cq steo.zip | conducto-perm-data puts --name {PERM_DATA_PATH}
""".strip()

DATASETS = {
    "Heating Degree Days"   : r"^STEO.ZWHD_[^_]*\.M$",
    "Cooling Degree Days"   : r"^STEO.ZWCD_[^_]*.M$",
    "Electricity Generation": r"^STEO.NGEPGEN_[^_]*\.M$"
}

IMG = co.Image("python:3.8", copy_dir=".", reqs_py=["conducto", "pandas", "matplotlib", "tabulate"])


def intro() -> co.Serial:
    with co.Serial(image=IMG) as output:
        # First download some data from the US Energy Information Administration.
        output["Download"] = co.Exec(DOWNLOAD_COMMAND)

        # Then display
        output["Display"] = co.Parallel()
        for dataset in DATASETS.keys():
            output["Display"][dataset] = co.Exec(f"python intro.py display --dataset='{dataset}'")
    return output


def display(dataset):
    data_text = co.perm_data.gets(PERM_DATA_PATH)
    all_data = [json.loads(line) for line in data_text.splitlines()]

    regex = DATASETS[dataset]
    subset_data = [d for d in all_data if "series_id" in d and re.search(regex, d["series_id"])]

    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import pandas as pd
    import numpy as np

    # Create a pandas DataFrame with the data grouped by month of the year
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

    # Plot it
    colors = [cm.viridis(z) for z in np.linspace(0, .99, len(subset_data))]
    for i, column in enumerate(df.columns):
        y = df[column].values
        plt.plot(y, label=column, color=colors[i])
    plt.title(f"{dataset}, average by month")
    plt.legend(loc="best", fontsize="x-small")

    filename = "/tmp/image.png"
    plt.savefig(filename)

    dataname = f"conducto/demo/data_science/{dataset.lower().replace(' ', '_')}.png"
    co.temp_data.put(dataname, filename)

    print(f"""
<ConductoMarkdown>
![img]({co.temp_data.url(dataname)})

{df.transpose().round(2).to_markdown()}
</ConductoMarkdown>
    """)


if __name__ == "__main__":
    co.main(default=intro)