"""
### **Data Stores**
You will need to store downloaded data and intermediate results. You cannot
simply persist these files on the local filesystem, because each command
runs in a container with its own filesystem that disappears when the container
exits. And, in cloud mode, containers run on different machines, so there is
no shared filesystem to mount. So, Conducto supports a few different approaches
that work in a containerized world.

* Connect to your own data store (for example, AWS S3 or a database).
* Use `co.data.user` as a user-wide key-value store.
* Use `co.data.pipeline` as a pipeline-local key-value store.

[Companion tutorial here.](
https://medium.com/conducto/data-stores-f6dc90104029)

[Code for this pipeline here.](
https://github.com/conducto/demo/blob/master/data_science/data_stores.py)
"""

import conducto as co
import utils
from code import btc


def data_pipeline() -> co.Serial:
    """
    ### **`co.data.pipeline`**
    `co.data.pipeline` is a pipeline-local key-value store. This data is only
    visible to your pipeline and persists until your pipeline is deleted. It
    is useful for writing data in one pipeline step, and reading it in another.

    `co.data.pipeline` has both a python and command line interface as
    `conducto-data-pipeline`. The first node of the example prints the command line
    usage to show the full interface.

    ### Example: Parameter Search
    One useful application is performing and summarizing a parameter search.
    In this example, we try different parameterizations of an algorithm in
    parallel. Each one stores its results using `co.data.pipeline.puts()`. Once
    all of the parallel tasks are done, it reads the results using
    `co.data.pipeline.gets()` and prints a summary.
    """
    # Dockerfile installs python, R, and conducto.
    image = co.Image(
        dockerfile="docker/Dockerfile.data", context=".", copy_dir="./code", reqs_py=["conducto"]
    )

    data_dir = "demo/data_science/data"

    output = co.Serial(image=image, doc=co.util.magic_doc())
    output["usage"] = co.Exec("conducto-data-pipeline --help")

    output["parameter_search"] = ps = co.Parallel()

    for window in [25, 50, 100]:
        ps[f"window={window}"] = w = co.Parallel()

        for mean in [.05, .08, .11]:
            w[f"mean={mean}"] = m = co.Parallel()

            for volatility in [.1, .125, .15, .2]:
                m[f"volatility={volatility}"] = co.Exec(
                    f"python data.py --window={window} --mean={mean} "
                    f"--volatility={volatility} --data-dir={data_dir}"
                )

    output["summarize"] = co.Exec(f"Rscript data.R {data_dir}")

    return output


def data_user() -> co.Serial:
    """
    ### **`co.data.user`**
    `co.data.user` is a key-value store like `co.data.pipeline` but scoped to
    your user, persisting beyond the lifetime of your pipeline. You are
    responsible for manually clearing this data.

    `co.data.user` has both a python and command line interface as
    `conducto-data-user`. The first node of the example prints the command line
    usage to show the full interface. Note that this interface is the same as
    `co.data.pipeline`/`conducto-data-pipeline`.

    ### Example: Cache Downloaded Data
    One useful application in data science is storing downloaded data. In
    this example we download data from the Bitcoin blockchain. This can be
    time-consuming so we want to avoid downloading the same data twice. By storing
    the data in `co.data.user`, we pull it once and persist it across pipelines.

    Notice there are three 'download' nodes with overlapping ranges. They each
    download that range and skip any blocks that are already downloaded.

    #### Reset
    After this runs, click the _Reset_ button to re-run this pipeline. You will
    see these nodes finish very quickly, because the data is already stored.

    #### Clear
    To clear the downloaded data and see these nodes in action again, select
    the "clear" node and click the _Unskip_ button.
    """
    with co.Serial(image=utils.IMG, doc=co.util.magic_doc()) as out:
        doc = co.util.magic_doc(func=btc.download)
        cleardoc = co.util.magic_doc(func=btc.clear)
        out["usage"] = co.Exec("conducto-data-user --help")
        out["download_20-11"] = co.Exec("python code/btc.py download --start=-20 --end=-11", doc=doc)
        out["download_15-6"] = co.Exec("python code/btc.py download --start=-15 --end=-6", doc=doc)
        out["download_10-now"] = co.Exec("python code/btc.py download --start=-10 --end=-1", doc=doc)
        out["clear"] = co.Exec("python code/btc.py clear", skip=True, doc=cleardoc)
    return out


def examples() -> co.Serial:
    ex = co.Serial(doc=__doc__)
    ex["co.data.pipeline"] = data_pipeline()
    ex["co.data.user"] = data_user()
    return ex


if __name__ == "__main__":
    print(__doc__)
    co.main(default=examples)
