"""
## Welcome to Conducto

Conducto is a tool for writing, visualizing, executing, and debugging
pipelines. A pipeline is just a sequence of commands that must be executed
in a specific order. See how easy it is to write and run a pipeline in
Conducto:

    python demo.py islands --local

Conducto is particularly powerful for **CI/CD** and **Data Science**. We have
dedicated demos and tutorials for each. Choose your own adventure!

### CI/CD
Read [Conducto for CI/CD](
https://medium.com/conducto/getting-started-with-conducto-for-ci-cd-b6afb626f410),
then run the demo.

    cd cicd
    python full_demo.py --local

### Data Science
Read [Conducto for Data Science](
https://medium.com/conducto/conducto-for-data-science-59f426ee57b),
then run the demo.

    cd data_science
    python full_demo.py --local

See the full code for this demo [here](
https://github.com/conducto/demo/blob/master/demo.py).
"""


import conducto as co
import sys


def hello() -> co.Exec:
    """Hello World Demo"""
    print(
        "If Conducto does not auto-open a browser page, "
        "copy the link below into a browser.\n"
    )
    idx = __doc__.find("Conducto is a tool")
    doc = __doc__[0:idx] + (
        "\n**Click the _Run_ button on the left side of your browser window "
        "to test your installation.** The pipeline should run successfully "
        "and finish in the green _done_ state.\n\n"
        ) + __doc__[idx:]
    return co.Exec("echo Hello world! Welcome to Conducto.", image="bash:5.0", doc=doc)


def islands() -> co.Serial:
    """
    ### Simple Pipeline Construction Demo

    A pipeline is a sequence of commands that must be executed in a specific
    order. Some steps can happen in parallel, while other must happen in
    serial. Conducto makes it easy to chain together shell commands in a
    pipeline using a simple python interface. This is a simple example that
    creates a pipeline consisting of `echo` commands.

    Click the _View_ button on the left to expand the pipeline. See how the
    pipeline tree structure mirrors the python specification below.

    Click the _Run_ button on the right to execute the pipeline. The
    pipeline should run successfully and finish in the green _done_ state.

    See the full code for this demo [here](
    https://github.com/conducto/demo/blob/master/demo.py).
    """
    with co.Serial(doc=co.util.magic_doc(), image="bash:5.0", tags=["demo_simple"]) as pipeline:
        pipeline["hawaii"] = co.Exec("echo big island")
        with co.Parallel(name="maui_county") as maui_county:
            maui_county["maui"] = co.Exec("echo valley isle")
            maui_county["lanai"] = co.Exec("echo pineapple isle")
            maui_county["molokai"] = co.Exec("echo friendly isle")
            maui_county["kahoolawe"] = co.Exec("echo target isle")
        pipeline["oahu"] = co.Exec("echo gathering place")
        with co.Serial(name="kauai_county") as kauai_county:
            kauai_county["kauai"] = co.Exec("echo garden isle")
            kauai_county["niihau"] = co.Exec("echo forbidden isle")
    return pipeline
            

if __name__ == "__main__":
    co.main()
