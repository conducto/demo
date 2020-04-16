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


def download_and_plot() -> co.Serial:
    # Download data from the United States Energy Information Administration.
    download_command = """set -ex
curl http://api.eia.gov/bulk/STEO.zip > data.zip
unzip -cq data.zip | conducto-perm-data puts --name steo-data
"""

    # Specify simple pipeline that downloads data, then plots two datasets.
    image = co.Image(dockerfile="./docker/Dockerfile.first", copy_dir="./code")
    with co.Serial(image=image, doc=co.util.magic_doc()) as pipeline:
        co.Exec(download_command, name="download")
        with co.Parallel(name="plot"):
            co.Exec("python plot.py --dataset heating", name="heating")
            co.Exec("python plot.py --dataset cooling", name="cooling")
    return pipeline


if __name__ == "__main__":
    print(__doc__)
    co.main(default=download_and_plot)
