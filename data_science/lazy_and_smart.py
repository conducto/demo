import conducto as co, json, os, re, urllib.request
from datetime import date, timedelta, datetime

# Data is downloaded from the United States Energy Information Administration.
PERM_DATA_ROOT = "conducto/demo/data_science/electricity/"
START_DATE = date(2018, 1, 1)
END_DATE = datetime.now().date()
IMG = co.Image("python:3.8", copy_dir=".", reqs_py=["conducto", "pandas", "matplotlib", "tabulate"])


def download(start: date = START_DATE, end: date = END_DATE) -> co.Parallel:
    """
    Create pipeline that downloads data for every day between `start` and `end`.
    """
    _set_secrets()

    # Find dates where the data isn't present yet
    dates = []
    dt = start
    while dt <= end:
        if not co.perm_data.exists(_data_path(dt)):
            dates.append(dt)
        dt += timedelta(days=1)

    # For each of those dates, call `download_day(dt)` in an Exec node.
    output = co.Parallel(image=IMG, doc=co.util.magic_doc())
    for node, dt in co.util.makedatenodes(output, dates):
        # Exec nodes can call both shell commands and Python functions.
        node[str(dt)] = co.Exec(download_day, dt)

    return output


def download_day(dt: date):
    """Download the data for a single day."""
    api_key = os.environ["EIA_API_KEY"]

    print("Requesting EIA data for", dt)
    url = f"http://api.eia.gov/series/?api_key={api_key}&series_id=EBA.US48-ALL.NG.H&start={dt.strftime('%Y%m%d')}&end={dt.strftime('%Y%m%d')}"
    text = urllib.request.urlopen(url).read()

    print(f"Got {len(text)} bytes in response. Saving.")
    co.perm_data.puts(_data_path(dt), text)
    print("Done.")


def display(start: date = START_DATE, end: date = END_DATE):
    """
    Read the data for every day between `start` and `end` and display it.
    """
    import matplotlib.pyplot as plt
    import itertools

    data = []
    c = itertools.cycle(range(30))
    dt = start
    while dt <= end:
        if next(c) == 0:
            print("Running on", dt, flush=True)
        text = co.perm_data.gets(_data_path(dt))
        d = json.loads(text)
        data += d["series"][0]["data"]
        dt += timedelta(days=1)

    plt.plot([y for x,y in data])
    plt.title(f"Net electric generation for US, hourly, from {start} to {end}")

    # Save to disk, and then to co.temp_data
    filename = "/tmp/image.png"
    dataname = f"conducto/demo/data_science/lazy_and_smart.png"
    plt.savefig(filename)
    co.temp_data.put(dataname, filename)

    # Print out results as markdown
    print(f"""
<ConductoMarkdown>
![img]({co.temp_data.url(dataname)})
</ConductoMarkdown>
    """)


def run(start: date = START_DATE, end: date = END_DATE) -> co.Serial:
    """
    Download the data first, then display it.

    The "Download" step can take a long time to generate the pipeline as it checks what
    is already in the cache. Lazily generate it using [`co.lazy_py`](https://conducto.com/docs/#lazy-pipeline-creation),
    which creates a "Generate" step that runs `download()` to build the download
    pipeline, and an "Execute" step that runs the newly generated pipeline.
    """
    _set_secrets()

    with co.Serial(image=IMG, doc=co.util.magic_doc()) as output:
        output["Download"] = co.lazy_py(download, start, end)
        output["Display"] = co.Exec(display, start, end)
    return output


def _data_path(dt: date):
    return f"{PERM_DATA_ROOT}/{dt.strftime('%Y%m%d')}.json"


def _set_secrets():
    token = co.api.Auth().get_token_from_shell()
    api = co.api.Secrets()
    if "EIA_API_KEY" not in api.get_user_secrets(token):
        api_key = {"EIA_API_KEY": "430037788f060481623a32234e964e1f"}
        co.api.Secrets().put_user_secrets(token, api_key, replace=False)


if __name__ == "__main__":
    co.main()
