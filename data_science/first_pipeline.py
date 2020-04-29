"""
### **First Data Science Pipeline**

* `co.Exec`, `co.Serial`, and `co.Parallel` node classes
* `co.Image` to specify execution environment
* `co.main()` to make the pipeline executable

It downloads some data, then plots two datasets from it.

[Companion tutorial here.](
https://medium.com/conducto/your-first-data-science-pipeline-cc9ceac142f6)
"""


import conducto as co
import utils


def download_and_plot() -> co.Serial:
    # Download data from the United States Energy Information 
    # Administration. This uses `conducto-perm-data` as a data
    # store as detailed in our data-stores demo.
    download_command = """set -ex
curl http://api.eia.gov/bulk/STEO.zip > data.zip
unzip -cq data.zip | conducto-perm-data puts --name steo-data
"""

    # A simple pipeline that downloads data, then plots two datasets.
    with co.Serial(image=utils.IMG, doc=co.util.magic_doc()) as pipeline:
        co.Exec(download_command, name="download")
        with co.Parallel(name="plot"):
            co.Exec("python code/plot.py --dataset heating", name="heating")
            co.Exec("python code/plot.py --dataset cooling", name="cooling")
    return pipeline


if __name__ == "__main__":
    print(__doc__)
    co.main(default=download_and_plot)
