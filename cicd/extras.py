"""
### **Extras**
These are some nice extras for CI/CD that did not fit into other demos, but we
wanted to share them in case they help.

* Pass a python function to an Exec node.
* Put Markdown in stdout/stderr.
* Check out our internal CI/CD configuration.

[Companion tutorial here.](
https://medium.com/conducto/ci-cd-extras-77a9c5ac8289)
"""

import conducto as co
import subprocess
import datetime
import typing


def no_types(name, thing):
    """
    Simple function with arguments. Both have no types so Conducto assumes they are `str`s.
    """
    print(f"Hello {name}, goodnight {thing}.")


def simple_types(price: float, count=3, show_sum=True):
    """
    Conducto looks at default values and type hints to infer types of each argument. It
    understands basic types: `str`, `bytes`, `int`, `float`, and `bool`.
    """
    total = 0
    for i in range(count):
        total += price
        if show_sum:
            print(f"Item #{i}: ${price}. Total: {total}")
        else:
            print(f"Item #{i}: ${price}.")


def complex_types(prices: typing.List[float], date: datetime.date):
    """
    Conducto also understands lists of basic types, and some complex types like
    `datetime`'s `date`, `time`, and `datetime`. For custom types, define an object
    with a `to_str` method and a `from_str` staticmethod.
    """
    tomorrow = date + datetime.timedelta(days=1)
    print(f"Today is {date}. Tomorrow is {tomorrow}.")
    total = 0
    for price in prices:
        total += price
        print(f"This item costs {price}, total so far: {total}")


def exec_python() -> co.Parallel:
    """
    You can pass a python function and its arguments to an Exec node instead
    of a shell command. This comes with a few caveats:
    * The function name cannot start with an underscore (_).
    * The image must include the file with the function. In this example we
      achieve that with `copy_dir="."`.
    * The image must install `conducto`. In this example we achieve that with
      `reqs_py=["conducto"]`.
    * You must set typical node arguments like `image`, `env`, `doc`, etc.
      outside of the constructor, either in a parent node or by setting the
      fields directly, like `example.image = image`.

    The shell command that ends up being constructed looks like this:
    ```
    conducto [file_with_function].py [function_name] --arg1=val1 --arg2=val2 ...
    ```
    """
    image = co.Image("python:3.8-alpine", copy_dir=".", reqs_py=["conducto"])
    output = co.Parallel(image=image, doc=co.util.magic_doc())

    output["no_types"] = co.Exec(no_types, "world", thing="moon")
    output["no_types"].doc = co.util.magic_doc(func=no_types)

    output["simple_types"] = co.Exec(simple_types, 3.5, count=4, show_sum=True)
    output["simple_types"].doc = co.util.magic_doc(func=simple_types)

    today = datetime.datetime.now().date()
    output["complex_types"] = co.Exec(complex_types, [3.5, 7.6, 10.0], date=today)
    output["complex_types"].doc = co.util.magic_doc(func=complex_types)

    return output


def markdown_in_stdout() -> co.Exec:
    """
    You can use Markdown in the stdout and stderr of any command. Just wrap
    output with `<ConductoMarkdown>...</ConductoMarkdown>`. This is especially
    useful if you need to show something like a plot, image, or table.

    **_Scroll down to stdout to see Markdown!_**
    """
    image = co.Image(
        "python:3.8-slim",
        reqs_py=["matplotlib", "numpy", "conducto"],
        copy_dir="./code",
    )
    return co.Exec("python plot.py", image=image, doc=co.util.magic_doc())


def our_cicd_config() -> co.Exec:
    """
    ### **Our CI/CD Scenario**
    We think our CI/CD needs are probably fairly typical for anyone with a
    monorepo, so here we share our approach. Our CI/CD scenario is:

    * We have a github repo with all of our code, including CI/CD pipeline scripts.
    * We always launch our ci/cd pipeline from a local checkout of this repo.
    * We want our images to always include a full checkout of the repo.
    * We want two modes in which to run our ci/cd pipeline:
      1. **dev mode**: Just copy the local checkout of our code into each
         image, including any of my local unstaged and uncommitted changes.
      2. **pr mode**: _Pull Request_, given a branch, `git clone` that
         branch from github into the image.
    * In both cases we want _livedebug_ to work for easier debugging.

    The logic to do this is encapsulated in `cicd/code/image_factory.py`.
    Notice that `ImageFactory` allows the dev_mode and pr_mode pipeline
    configurations to be almost identical.

    ### **Our Dockerfile**
    Finally, as a convenience, we specify a single Dockerfile that installs
    the most common libraries and tools that we need for running and debugging
    our ci/cid pipeline, and use that for almost all of our nodes. That file
    is located in `cicd/docker/Dockerfile.conducto`.
    """
    from code.image_factory import ImageFactory

    with co.Parallel(doc=co.util.magic_doc()) as image_factory_example:
        ImageFactory.init()
        dockerfile = f"{ImageFactory.context}/cicd/docker/Dockerfile.conducto"
        dev_image = ImageFactory.get(dockerfile=dockerfile, reqs_py=["conducto"])
        with co.Serial(image=dev_image, name="dev_mode"):
            # Some dummy commands to show that our image is configured.
            co.Exec("ls -l cicd", name="ls_code_from_local")
            co.Exec("cat cicd/docker/Dockerfile.conducto", name="show_dockerfile")
            co.Exec("python cicd/extras.py --help", name="show_extras_help")

        ImageFactory.init(branch="master")
        pr_image = ImageFactory.get(dockerfile=dockerfile, reqs_py=["conducto"])
        with co.Serial(image=pr_image, name="pr_mode"):
            # Some dummy commands to show that our image is configured.
            co.Exec("ls -l cicd", name="ls_code_from_git_clone")
            co.Exec("cat cicd/docker/Dockerfile.conducto", name="show_dockerfile")
            co.Exec("python cicd/extras.py --help", name="show_extras_help")

    return image_factory_example


def examples() -> co.Parallel:
    ex = co.Parallel(doc=__doc__)
    ex["exec_python"] = exec_python()
    ex["markdown_in_stdout"] = markdown_in_stdout()

    has_git = True
    try:
        subprocess.run(["git"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        has_git = False
    if has_git:
        ex["our_cicd_config"] = our_cicd_config()
    return ex


if __name__ == "__main__":
    print(__doc__)
    co.main(default=examples)
