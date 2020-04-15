"""
## Welcome to Conducto
This is a trivial pipeline to confirm that Conducto runs. If Conducto
does not auto-open a browser page, copy the link below into a browser.

**Test your installation by clicking the _Run_ button on the left.**

Conducto is good for any pipeline task, and is particularly powerful for
**CI/CD** and **Data Science**. We have dedicated demos and tutorials for each
of these applications. Choose your own adventure!

### CI/CD
Read [Conducto for CI/CD](
https://medium.com/conducto/getting-started-with-conducto-for-ci-cd-b6afb626f410),
then run the demo.

    cd cicd
    python full_demo.py --local

### Data Science
Read [Conducto for Data Science](https://medium.com/conducto/data/home),
then run the demo.

    cd data_science
    python full_demo.py --local
"""


import conducto as co


def hello_world() -> co.Exec:
    image = co.Image(image="bash:5.0")
    return co.Exec("echo Hello world! Welcome to Conducto.", doc=__doc__)


if __name__ == "__main__":
    print(__doc__)
    co.main(default=hello_world)
