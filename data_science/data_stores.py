"""
### **Data Stores**
How to store artifacts and intermediate results:
* connect to your own data store (for example, redis)
* use conducto-temp-data as a pipeline-local key-value store
* use conducto-perm-data as a global persistent key-value store

[Companion tutorial here.](
https://medium.com/conducto/data-stores-cfb82460cb76)
"""


import conducto as co


def temp_data() -> co.Serial:
    """
    `conducto-temp-data` is a pipeline-local key-value store. This data is only visible
    to your pipeline and persists until your pipeline is deleted. It is useful for
    writing data in one pipeline step to be read in another.

    This example does a parameter search. In parallel it tries a few different
    parameterizations of an algorithm. Each one stores its results using `puts`. Once
    all the parallel tasks are done, read the results using `gets` and print a summary.
    """
    # Dockerfile installs golang and conducto.
    image = co.Image(dockerfile="docker/Dockerfile.temp_data", context=".", copy_dir="./code", reqs_py=["conducto"])
    data_dir = "demo/data_science/temp_data"

    with co.Serial(image=image, doc=co.util.magic_doc()) as output:
        output["parameter_search"] = ps = co.Parallel()

        for window in [25, 50, 100]:
            ps[f"window={window}"] = w = co.Parallel()

            for mean in [.05, .08, .11]:
                w[f"mean={mean}"] = m = co.Parallel()

                for volatility in [.1, .125, .15, .2]:
                    m[f"volatility={volatility}"] = co.Exec(
                        f"python temp_data.py --window={window} --mean={mean} "
                        f"--volatility={volatility} --data-dir={data_dir}"
                    )
        output["summarize"] = co.Exec(f"Rscript temp_data.R {data_dir}")
    return output


def perm_data() -> co.Serial:
    """
    `conducto-perm-data` is a global persistent key-value store.
    This is just like `conducto-temp-data`, but data is visible in all
    pipelines and persists beyond the lifetime of your pipeline. You
    are responsible for manually clearing your data. One useful application
    is restoring a python virtual env to avoid repeatedly installing it
    across nodes and pipelines. We exercise the various `cache` commands
    to do this.
    """

    create_and_save_cmd = """set -ex
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
checksum=$(md5sum requirements.txt | cut -d" " -f1)
conducto-perm-data save-cache \
    --name code_venv --checksum $checksum --save-dir venv
"""

    restore_and_test_cmd = """set -ex
checksum=$(md5sum requirements.txt | cut -d" " -f1)
conducto-perm-data restore-cache \
    --name code_venv --checksum $checksum --restore-dir restored_venv
. restored_venv/venv/bin/activate
pip list
"""

    clear_cmd = """set -ex
checksum=$(md5sum requirements.txt | cut -d" " -f1)
conducto-perm-data clear-cache --name code_venv --checksum $checksum
    """

    image = co.Image("python:3.8-alpine", copy_dir="./code", reqs_py=["conducto"])
    with co.Serial(image=image, doc=co.util.magic_doc()) as venv_test:
        co.Exec("conducto-perm-data --help", name="usage")
        co.Exec(create_and_save_cmd, name="create_and_save")
        co.Exec(restore_and_test_cmd, name="restore_and_test")
        co.Exec(clear_cmd, name="clear")
    return venv_test


def examples() -> co.Serial:
    ex = co.Serial(doc=__doc__)
    ex["temp_data"] = conducto_temp_data()
    ex["perm_data"] = conducto_perm_data()
    ex["lazy_py"] = lazy_py()
    return ex


if __name__ == "__main__":
    print(__doc__)
    co.main(default=examples)
