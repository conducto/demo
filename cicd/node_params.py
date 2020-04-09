"""
### **Node Parameters**
Exec, Serial, and Parallel Nodes support several parameters that make
pipeline specification in Conducto extremely powerful. You have already
learned about `image` and `env`. You can also specify:

* `cpu` and `mem` to constrain resources
* `requires_docker` to run docker commands
* `stop_on_error` to implement the _finally_ pattern
* `same_container` to control container sharing
* `doc` to show pretty documentation in the web app
* `skip` to default skip a node

Note: **_Errors in this node are intentional._**

[Companion tutorial here.](https://medium.com/conducto/node-parameters-baf95e136437)
"""


import conducto as co


def cpu_and_mem() -> co.Exec:
    """
    The `cpu` and `mem` parameters limit the cpu and memory that get assigned
    to an Exec node. The default values are `cpu=1` cpu and `mem=2` GB of
    memory. Allocate less if your commands require very little cpu or
    memory to allow your local pipeline to launch more nodes in parallel.
    Allocate more if necessary. You can also modify these parameters
    for any node in a live pipeline from the web app and re-run in place.
    """
    image = co.Image("bash:5.0")
    return co.Exec(
        "echo not doing much", cpu=0.25, mem=0.25, image=image, doc=co.util.magic_doc()
    )


def requires_docker() -> co.Exec:
    """
    To enable running docker commands like `docker build`, `docker run`, etc. in
    a node, you must set `requires_docker=True`. This is because your commands
    run within a docker container already, and running docker within docker
    requires non-trivial setup that Conducto will not do by default. Also,
    note that your image must have docker installed.
    """
    image = co.Image("docker:19.03")
    cmd = "docker run --rm hello-world"
    return co.Exec(cmd, requires_docker=True, image=image, doc=co.util.magic_doc())


def stop_on_error() -> co.Parallel:
    """
    A Serial node defaults to `stop_on_error=True`, which means it stops and
    reports itself as errored as soon as any child node encounters an error.
    If `stop_on_error=False`, then it will run _all_ child nodes, but will
    still report itself as errored if any child encountered an error. This
    is useful for implementing a **finally** pattern to guarantee that your
    pipeline always runs a cleanup step.
    """
    error_doc = "**_Intentional error in this node!_**"
    image = co.Image("bash:5.0")
    with co.Parallel(image=image, doc=co.util.magic_doc()) as stop_on_error_example:
        with co.Serial(name="stop_on_error_default"):
            co.Exec("echo doing some setup", name="setup")
            co.Exec("this_command_will_fail", name="bad_command", doc=error_doc)
            co.Exec("echo doing some cleanup", name="cleanup")
        with co.Serial(name="stop_on_error_false", stop_on_error=False):
            co.Exec("echo doing some setup", name="setup")
            co.Exec("this_command_will_fail", name="bad_command", doc=error_doc)
            co.Exec("echo doing some cleanup", name="finally_cleanup")
    return stop_on_error_example


def same_container():
    """
    Exec nodes are not guaranteed to run in the same containers, although
    Conducto will re-use containers when possible for efficiency. You can
    force commands to run in the same container with the argument
    `same_container=co.SameContainer.NEW`. All child nodes will have
    the default `same_container=co.SameContainer.INHERIT` and will share
    the container with the parent. This is useful if you want greater
    visibility into a command that chains together multiple subcommands.
    An error in a single subcommand will be easier to identify than an
    error in the long command.
    """
    error_doc = "**_Intentional error in this node!_**"
    long_command = """set -ex
echo This is a long command.
echo First I do this.
echo Then I do that.
oops_this_is_not_a_valid_command
echo Then I go home.
"""
    image = co.Image("bash:5.0")
    with co.Parallel(image=image, doc=co.util.magic_doc()) as same_container_example:
        co.Exec(long_command, name="long_command", doc=error_doc)
        with co.Serial(name="same_container", same_container=co.SameContainer.NEW):
            co.Exec("echo This is a long command.", name="intro")
            co.Exec("echo First I do this.", name="do_this")
            co.Exec("echo Then I do that.", name="do_that")
            co.Exec("oops_this_is_not_a_valid_command", name="oops", doc=error_doc)
            co.Exec("echo Then I go home.", name="go_home")
    return same_container_example


def doc():
    """
    Nodes can be documented with the `doc` parameter. It supports Markdown
    and is rendered at the top of the node pane. Nodes with docs are marked
    with a _doc_ icon in the pipeline pane. We make extensive use of this feature
    in all of our demos.
    """
    image = co.Image("bash:5.0")
    command = "echo doc example"
    unformatted_doc = "I can have unformatted text."
    markdown_doc = "### I _can_ **use** `markdown`."
    more_markdown_doc = """
Markdown even supports [links](https://www.conducto.com) and images
![alt text](http://cdn.loc.gov/service/pnp/highsm/21700/21778r.jpg "a pretty picture")
"""
    with co.Parallel(image=image, doc=co.util.magic_doc()) as doc_example:
        co.Exec(command, name="unformatted", doc=unformatted_doc)
        co.Exec(command, name="markdown", doc=markdown_doc)
        co.Exec(command, name="more_markdown", doc=more_markdown_doc)
    return doc_example


def skip():
    """
    Nodes can be skipped in the web app or with `skip=True`. This is useful,
    for example, if you have a pipeline that has reasonable default way to
    run, but you want the ability to manually enable (unskip) additional steps
    from the web app. A specific example might be deploying a production
    environment. You could skip the final deployment node by default, and
    require that someone manually review the output of the pipeline before
    unskipping and running the node to complete the deployment.
    """
    image = co.Image("bash:5.0")
    with co.Serial(image=image, doc=co.util.magic_doc()) as skip_example:
        co.Exec("echo build some stuff", name="build", image=image)
        co.Exec("echo test some stuff", name="test", image=image)
        co.Exec("echo deploy staging", name="deploy staging", image=image)
        co.Exec("echo deploy prod", name="deploy prod", skip=True, image=image)
        co.Exec("echo send status email", name="send email", image=image)
    return skip_example


def examples() -> co.Parallel:
    ex = co.Parallel(doc=__doc__)
    ex["cpu_and_mem"] = cpu_and_mem()
    ex["requires_docker"] = requires_docker()
    ex["stop_on_error"] = stop_on_error()
    ex["same_container"] = same_container()
    ex["doc"] = doc()
    ex["skip"] = skip()
    return ex


if __name__ == "__main__":
    print(__doc__)
    co.main(default=examples)
