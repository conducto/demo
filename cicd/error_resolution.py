"""
### **Error Resolution**
Anyone who has spent time with complex CI/CD pipelines has spent _a lot_ of
that time resolving errors with them. Bugs are just a reality when you are
trying to implement a complex system. Conducto makes it as easy as possible
to resolve the three types of errors that we think you are most likely to
encounter:

* flaky errors that you should fix, but do not have time for now,
* pipeline specification errors, like a typo in command or missing env, and
* errors that require serious debugging

We think that our thoughtful approach to error surfacing and handling will
save you a ton of time and make you more productive.

Note: **_Errors in this node are intentional._** Follow the docs in each
subnode to debug each one as an exercise.

[Companion tutorial here.] (
https://medium.com/conducto/easy-error-resolution-b9f2b54f22b7)

[Code for this pipeline here.](
https://github.com/conducto/demo/blob/master/cicd/error_resolution.py)
"""


import conducto as co
import utils

def flaky_error():
    """
    Sometimes your pipeline has a flaky test that periodically fails for no good
    reason. You really should fix it, but you do not want it to block you now.
    You have two options: you can **_reset_** the node to try again, or you can
    **_skip_** the node to ignore the error and move on.

    ### Reset
    If the test passes 80% of the time and fails 20% of the time, and you
    just want to run it again to give it a chance to pass, click the _Reset_
    button in the web app to try re-run the node. If it passes, then great,
    your pipeline will continue on.

    ### Skip
    In this scenario, the test keeps failing even after a few resets. In this
    case, you should just skip the node. Select the errored `test2` node and
    click the _Skip_ button in the web app to let your pipeline continue to
    the `deploy` node. Alternatively, you can select the errored parent `test`
    node, which will mark all subnodes as skipped, and let your pipeline
    continue to the `deploy` node.

    See our [tutorial](
    https://medium.com/conducto/easy-error-resolution-b9f2b54f22b7)
    for a full walkthrough with screenshots.
    """
    skip_doc = "**_Click the Skip button to let this pipeline continue!_**"
    with co.Serial(image=utils.IMG, doc=co.util.magic_doc()) as test_and_deploy:
        with co.Parallel(name="test"):
            co.Exec("echo test app 1", name="test1")
            co.Exec("echo test app 2 && force_fail", name="test2", doc=skip_doc)
            co.Exec("echo test app 3", name="test3")
        co.Exec("echo deploying all apps", name="deploy")
    return test_and_deploy


def specification_error():
    """
    You are going to make typos or forget things like environment variables
    when you write a pipeline specification, that is just human. In
    Conducto, quickly fix errors like these by selecting the errored node,
    click the _Modify_ button in the toolbar, fix the offending parameter,
    then click the _Reset_ button to immediately re-run the node.

    Fix the env_error node by correcting the typo in the environment variable
    name: `CRATH_DIR` -> `SCRATCH_DIR`.

    Fix the command_error node by correcting the typo in the command:
    `lss` -> `ls`.

    Note that these fixes are isolated to the live instance of the pipeline,
    and do not modify anything in the pipeline script. You need to port your
    fixes to the pipeline script so that future runs do not suffer from the
    same errors.

    See our [tutorial](
    https://medium.com/conducto/easy-error-resolution-b9f2b54f22b7)
    for a full walkthrough with screenshots.
    """
    error_doc = (
        "**_Click the Modify button, fix the error, then click Reset!_**"
    )
    env = {"CRATCH_DIR": "/tmp"}
    with co.Serial(image=utils.IMG, env=env, doc=co.util.magic_doc()) as spec_error:
        co.Exec("echo first do this", name="do_this")
        co.Exec('ls -ltrd "$SCRATCH_DIR"', name="env_error", doc=error_doc)
        co.Exec('lss -ltrd /root', name="command_error", doc=error_doc)
        co.Exec("echo then do that", name="do_that")
    return spec_error


def debug_error():
    """
    Sometimes you have a real issue that you need to debug. You can use
    **_debug_** mode by clicking the _empty bug_ icon or **_live debug_** mode
    by clicking the _lightning bug_ icon.

    ### Debug Mode
    This gives you a shell in a container with the node's command and execution
    environment, including environment variables and a _copy_ of your code. You
    can immediately reproduce the exact results you see in your pipeline. You can modify
    command, environment, and code in this container. Any changes are discarded
    when you exit this shell, so you must manually port your fixes back to your
    local code.

    ### Live Debug Mode
    This gives you the same shell as debug mode, but also mounts
    your local code so that you can edit code outside of the shell with your
    own editor. Conversely, any changes you make inside the livedebug container
    persist outside on your local host even after you exit the shell, allowing
    you to instantly commit any of your fixes to your repo.

    To resolve the error in this example:
    * click the _live debug_ lightning bug in the upper right hand corner of
      the node pane
    * run the copied command in a shell
    * run `sh /cmd.conducto` to reproduce the error
    * fix the trivial code bug in your own editor outside of the container
    * re-run `sh /cmd.conducto` to verify the bug is fixed
    * click _Rebuild and Reset_ in the upper right hand corner of the node pane
    * see the node run successfully

    See our [tutorial](
    https://medium.com/conducto/easy-error-resolution-b9f2b54f22b7)
    for a full walkthrough with screenshots.
    """
    return co.Exec("python code/debug_me.py", image=utils.IMG, doc=co.util.magic_doc())


def examples() -> co.Parallel:
    ex = co.Parallel(doc=__doc__)
    ex["flaky_error"] = flaky_error()
    ex["specification_error"] = specification_error()
    ex["debug_error"] = debug_error()
    return ex


if __name__ == "__main__":
    print(__doc__)
    co.Image.register_directory("CONDUCTO_DEMO", "..")
    co.main(default=examples)
