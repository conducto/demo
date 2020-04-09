"""
### **Error Resolution**
Anyone who has spent time with complex CI/CD pipelines has spent _a lot_ of
that time resolving errors with them. Bugs are just a reality when you are
trying to do something hard. Conducto makes it as easy as possible to resolve
the three types of errors we think you are most likely to see:

* flaky errors that you should fix, but do not have time for now,
* pipeline specification errors, like a typo in command or missing env, and
* errors that require serious debugging

We think that our thoughtful approach to error surfacing and handling will
save you a ton of time and make you more productive.

Note: **_Errors in this node are intentional._** Follow the docs in each
subnode to debug each one as an exercise.

[Companion tutorial here.] (
https://medium.com/conducto/rapid-and-painless-debugging-ff2abdba44c1)
"""


import conducto as co


def flaky_error():
    """
    Sometimes your pipeline has a flaky test that fails sometimes for no good
    reason. You really should fix it, but you do not want it to block you now.
    In this scenario, select the errored node and click the _Skip_ button in
    the web app to let your pipeline continue.

    See our [debug tutorial](
    https://medium.com/conducto/rapid-and-painless-debugging-ff2abdba44c1#a9f4)
    for a full walkthrough with screenshots.
    """
    skip_doc = "**_Click the Skip button to let this pipeline continue!_**"
    image = co.Image("bash:5.0")
    with co.Serial(image=image, doc=co.util.magic_doc()) as test_and_deploy:
        with co.Parallel(name="test"):
            co.Exec("echo test microservice 1", name="test1")
            co.Exec(
                "echo test microservice 2 && force_fail", name="test2", doc=skip_doc
            )
            co.Exec("echo test microservice 3", name="test3")
        co.Exec("echo deploying all microservices", name="deploy")
    return test_and_deploy


def specification_error():
    """
    You are going to make typos or forget things like environment variables
    when you write your pipeline specification, that is just human. In this
    scenario, quickly fix an error by selecting the errored node and pressing
    the _Modify_ button in the web app, then fix the environment variable name
    (`CRATCH_DIR` -> `SCRATCH_DIR`), and reset the node to have it re-run
    immediately.

    See our [debug tutorial](
    https://medium.com/conducto/rapid-and-painless-debugging-ff2abdba44c1#19fe)
    for a full walkthrough with screenshots.
    """
    error_doc = (
        "**_Click the Modify button to fix the env variable name, then click Reset!_**"
    )
    image = co.Image("bash:5.0")
    env = {"CRATCH_DIR": "/tmp"}
    with co.Serial(image=image, env=env, doc=co.util.magic_doc()) as spec_error:
        co.Exec("echo first do this", name="do_this")
        co.Exec('ls -ltrd "$SCRATCH_DIR"', name="ls_scratch_dir", doc=error_doc)
        co.Exec("echo then do that", name="do_that")
    return spec_error


def debug_error():
    """
    Sometimes you have a real issue that you need to debug. You can use
    **_debug_** mode by clicking the _empty bug_ icon to immediately reproduce the
    execution environment and command in a local container. Or use **_livedebug_**
    mode by clicking the _lightning bug_ icon to do the same _and_ also mount
    your local code into the container to allow you to use your local editor
    and debug tools.

    To resolve the error in this example:
    * click the _livedebug_ lightning bug in the upper right hand corner of the
      node pane
    * run the copied command in a shell
    * run `sh /conducto.cmd` to reproduce the error
    * fix the trivial code bug in your own editor outside of the container
    * re-run `sh /conducto.cmd` to verify the bug is fixed
    * click _Rebuild and Reset_ in the upper right hand corner of the node pane
    * see the node run successfully

    See our [debug tutorial](
    https://medium.com/conducto/rapid-and-painless-debugging-ff2abdba44c1#4ec7)
    for a full walkthrough with screenshots.
    """
    image = co.Image("python:3.8-alpine", copy_dir="./code")
    return co.Exec("python debug_me.py", image=image, doc=co.util.magic_doc())


def examples() -> co.Parallel:
    ex = co.Parallel(doc=__doc__)
    ex["flaky_error"] = flaky_error()
    ex["specification_error"] = specification_error()
    ex["debug_error"] = debug_error()
    return ex


if __name__ == "__main__":
    print(__doc__)
    co.main(default=examples)
